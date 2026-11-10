"""Semantic regressions using real sampled resources; no performance assertions."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "adapters")]
from canonical_graph import compare, validate
from import_vivado import read_export
from template_codec import DirectDecoder, encode
from real_validation import ablate_exceptions, fault_injections, occupancy_checks


class RealGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = json.loads((ROOT / "configs/real_sample.json").read_text())
        cls.source = ROOT / cls.settings["raw_path"]
        cls.graph = read_export(cls.source)
        cls.compact = encode(cls.graph)

    def test_real_round_trip(self):
        self.assertTrue(compare(self.graph, DirectDecoder(self.compact).materialize())["equal"])

    def test_edge_and_oracle_order_are_not_semantics(self):
        g = deepcopy(self.graph)
        g["edges"].reverse()
        for children in g["oracle_children"].values():
            children.reverse()
        self.assertTrue(compare(self.graph, g)["equal"])

    def test_encoding_is_deterministic_under_edge_order(self):
        g = deepcopy(self.graph)
        g["edges"].reverse()
        self.assertEqual(encode(g), self.compact)

    def test_corruptions_are_detected(self):
        outcomes = fault_injections(self.graph, self.compact)
        self.assertEqual(11, len(outcomes))
        for outcome in outcomes:
            with self.subTest(outcome["fault"]):
                self.assertTrue(outcome["detected"])

    def test_exception_ablation_has_topology_and_attribute_failures(self):
        outcome = ablate_exceptions(self.graph, self.compact)
        self.assertGreater(outcome["counts"]["connection_rule_difference"], 0)
        self.assertGreater(outcome["counts"]["attributes_only"], 0)

    def test_occupancy_semantics(self):
        self.assertTrue(all(occupancy_checks(self.graph, self.compact).values()))

    def test_unexpanded_target_is_not_sink(self):
        node = next(n for n in self.graph["nodes"] if n not in self.graph["roots"])
        with self.assertRaises(KeyError):
            list(DirectDecoder(self.compact).neighbors(node))

    def test_unknown_alias_and_missing_canonical_wire_rejected(self):
        g = deepcopy(self.graph)
        node = next(iter(g["nodes"]))
        del g["aliases"][node]
        with self.assertRaises(ValueError):
            validate(g)

    def test_interrupted_export_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "truncated.tsv"
            p.write_text("meta\tschema\tvivado_graph_tsv_v1\n")
            with self.assertRaisesRegex(ValueError, "Incomplete"):
                read_export(p)

    def test_duplicate_raw_record_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "duplicate.tsv"
            p.write_text("meta\tschema\tvivado_graph_tsv_v1\nmeta\tschema\tvivado_graph_tsv_v1\n")
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                read_export(p)

    def test_existing_report_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "existing.json"
            p.write_text("preserve me\n")
            result = subprocess.run([sys.executable, str(ROOT / "scripts/run.py"), "real-check", "--output", str(p)],
                                    capture_output=True, text=True)
            self.assertEqual(2, result.returncode)
            self.assertEqual("preserve me\n", p.read_text())


if __name__ == "__main__":
    unittest.main()
