"""Binary-layout and independent native-decoder regressions on real resources."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / p) for p in ["src", "adapters", "scripts"]]
from canonical_graph import compare
from heldout import fit_bank, select_sources, source_slr
from import_vivado import read_export
from packed_graph import DIRECTORY, HEADER, PackedGraph, write_packed
from packed_experiment import expected_dump, verify_native
from search_experiment import ExplicitCSR, make_queries, search


class PackedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.temp.name)
        cfg = json.loads((ROOT / "configs/region_query.json").read_text())
        raw = read_export(ROOT / cfg["training"]["path"])
        cls.bank = fit_bank(select_sources(raw, [n for n in raw["roots"] if source_slr(raw, n) == 0]))
        cls.graph = read_export(ROOT / cfg["heldout"]["path"])
        cls.paths = {}
        for name, mode, patch in [("csr", "csr", True), ("compact", "compact", True), ("whole", "compact", False)]:
            cls.paths[name] = cls.dir / (name+".agr")
            write_packed(cls.paths[name], cls.graph, mode, cls.bank if mode == "compact" else None, patch)
        cls.reader = PackedGraph(cls.paths["compact"])

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_exact_roundtrip_all_modes(self):
        for name, path in self.paths.items():
            with self.subTest(name):
                self.assertTrue(compare(self.graph, PackedGraph(path).materialize())["equal"])

    def test_attribute_patches_reduce_rule_payload(self):
        patched, whole = self.reader, PackedGraph(self.paths["whole"])
        self.assertGreater(patched.layout["PATCH"][2], 0)
        self.assertEqual(0, whole.layout["PATCH"][2])
        self.assertLess(patched.layout["ADD"][2], whole.layout["ADD"][2])
        self.assertLess(len(patched.data), len(whole.data))

    def test_no_overwrite_or_training_leakage(self):
        with self.assertRaises(FileExistsError):
            write_packed(self.paths["csr"], self.graph, "csr")
        bank = deepcopy(self.bank)
        bank["training_sources"].append(next(iter(self.graph["roots"])))
        with self.assertRaisesRegex(ValueError, "overlap"):
            write_packed(self.dir / "leak.agr", self.graph, "compact", bank)

    def test_truncated_and_extra_bytes_rejected(self):
        data = self.reader.data
        for length in [0, 23, len(data)-1, len(data)+1]:
            path = self.dir / "bad-size.agr"
            path.write_bytes(data[:length] if length <= len(data) else data+b"x")
            with self.subTest(length), self.assertRaises(ValueError):
                PackedGraph(path)

    def test_overlapping_section_rejected(self):
        data = bytearray(self.reader.data)
        first = DIRECTORY.unpack_from(data, HEADER.size)
        second = list(DIRECTORY.unpack_from(data, HEADER.size+DIRECTORY.size))
        second[1] = first[1]
        DIRECTORY.pack_into(data, HEADER.size+DIRECTORY.size, *second)
        path = self.dir / "overlap.agr"
        path.write_bytes(data)
        with self.assertRaisesRegex(ValueError, "Overlapping"):
            PackedGraph(path)

    def test_bad_patch_and_alias_rejected(self):
        data = bytearray(self.reader.data)
        struct.pack_into("<I", data, self.reader.layout["PATCH"][0], 0xffffffff)
        path = self.dir / "patch.agr"
        path.write_bytes(data)
        with self.assertRaisesRegex(ValueError, "Exception index"):
            PackedGraph(path)
        data = bytearray(self.reader.data)
        struct.pack_into("<I", data, self.reader.layout["ALIAS"][0]+8, 0xffffffff)
        path.write_bytes(data)
        with self.assertRaisesRegex(ValueError, "alias reference"):
            PackedGraph(path)

    def test_unknown_row_is_not_empty_sink(self):
        node = next(i for i, row in enumerate(self.reader.nodes) if row[3] == -1)
        with self.assertRaises(KeyError):
            self.reader.numeric_neighbors(node)

    def test_property_corruption_does_not_pass_equivalence(self):
        reader = PackedGraph(self.paths["csr"])
        data = bytearray(reader.data)
        off = reader.layout["CSR_EDGE"][0]
        attrs = struct.unpack_from("<I", data, off+20)[0]
        struct.pack_into("<I", data, off+20, (attrs+1) % (len(reader.attr_offsets)-1))
        path = self.dir / "property.agr"
        path.write_bytes(data)
        try:
            result = compare(self.graph, PackedGraph(path).materialize())
        except ValueError:
            return
        self.assertFalse(result["equal"])

    @unittest.skipUnless(shutil.which("g++"), "g++ required for independent native reader")
    def test_native_all_edges_paths_statuses_and_cache(self):
        binary = self.dir / "bench"
        subprocess.run(["g++", "-std=c++17", "-O2", str(ROOT / "src/native/packed_bench.cpp"), "-o", str(binary)], check=True)
        cfg = json.loads((ROOT / "configs/region_query.json").read_text())["search_domain"]
        graph = read_export(ROOT / cfg["path"])
        queries = make_queries(graph, cfg["seeds"], cfg["max_depth"], 10000)
        ids = {n:i for i,n in enumerate(sorted(graph["nodes"]))}
        query_path = self.dir / "queries.bin"
        query_path.write_bytes(b"".join(struct.pack("<4I", ids[q["source"]], ids[q["target"]], q["max_expansions"], int(q["kind"] == "reachable_by_exported_edges")) for q in queries))
        provider = ExplicitCSR(graph)
        references = [search(provider, q["source"], q["target"], q["max_expansions"]) for q in queries]
        for mode in ["csr", "compact"]:
            path = self.dir / (mode+"-closure.agr")
            write_packed(path, graph, mode, self.bank if mode == "compact" else None)
            reader = PackedGraph(path)
            for cache, execution in [(0, "direct"), (16, "direct"), (0, "expanded")]:
                with self.subTest(mode=mode, cache=cache, execution=execution):
                    dump = self.dir / "native-edges.bin"
                    proc = subprocess.run([str(binary), str(path), str(query_path), str(cache), "2", str(dump), execution], text=True, capture_output=True, check=True)
                    self.assertEqual(expected_dump(reader), dump.read_bytes())
                    verify_native(reader, json.loads(proc.stdout), references)
        truncated = self.dir / "native-truncated.agr"
        truncated.write_bytes(path.read_bytes()[:-1])
        proc = subprocess.run([str(binary), str(truncated), str(query_path), "0", "1", str(dump), "direct"], capture_output=True)
        self.assertEqual(2, proc.returncode)


if __name__ == "__main__":
    unittest.main()
