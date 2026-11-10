"""Real captured rows: dictionary scope changes must preserve full resource semantics."""
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/p) for p in ('src', 'scripts', 'adapters')]
from heldout import fit_bank, select_sources, source_slr
from import_vivado import read_export
from packed_graph import PackedGraph, write_packed
from template_scope import write_scoped
from check_template_scope import check_layout


class TemplateScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(); cls.path = Path(cls.temp.name)
        cfg = json.loads((ROOT/'configs/region_query.json').read_text())
        training = read_export(ROOT/cfg['training']['path'])
        bank = fit_bank(select_sources(training, [r for r in training['roots'] if source_slr(training, r) == 0]))
        cls.graph = read_export(ROOT/cfg['heldout']['path'])
        cls.original_path = cls.path/'original.agr'
        write_packed(cls.original_path, cls.graph, 'compact', bank)
        cls.original = PackedGraph(cls.original_path)
        cls.binary = cls.path/'native_check'
        subprocess.run(['g++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror',
                        str(ROOT/'src/native/template_scope_check.cpp'), '-o', str(cls.binary)], check=True)

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def test_complete_real_rows_all_scopes(self):
        for span in (None, 16, 4, 1):
            with self.subTest(span=span):
                output = self.path/f'span_{span}.agr'
                write_scoped(self.original, output, span)
                candidate = PackedGraph(output)
                check_layout(self.original, candidate, span)
                for node, info in enumerate(self.original.nodes):
                    if info[3] < 0:
                        with self.assertRaises(KeyError): candidate.numeric_neighbors(node)
                    else:
                        self.assertEqual(self.original.numeric_neighbors(node), candidate.numeric_neighbors(node))
                result = subprocess.run([str(self.binary), str(self.original_path), str(output)],
                                        text=True, capture_output=True, check=True)
                raw = json.loads(result.stdout)
                self.assertEqual(raw['directed_edges'], len(self.graph['edges']))
                self.assertEqual(raw['nodes'], len(self.graph['nodes']))
                self.assertEqual(raw['known_rows'], len(self.graph['roots']))

    def test_equivalent_global_is_not_claimed_local(self):
        with self.assertRaisesRegex(ValueError, 'crosses group'):
            check_layout(self.original, self.original, 1)

    def test_changed_static_alias_rejected(self):
        data = bytearray(self.original.data)
        offset = self.original.layout['ALIAS'][0]
        node = struct.unpack_from('<I', data, offset+8)[0]
        struct.pack_into('<I', data, offset+8, (node+1) % len(self.original.nodes))
        output = self.path/'bad_alias.agr'; output.write_bytes(data)
        with self.assertRaises(ValueError): check_layout(self.original, PackedGraph(output), None)

    def test_native_detects_changed_actual_edge_attributes(self):
        data = bytearray(self.original.data)
        self.assertGreater(self.original.layout['ADD'][2], 0)
        offset = self.original.layout['ADD'][0]+20
        attr = struct.unpack_from('<I', data, offset)[0]
        struct.pack_into('<I', data, offset, (attr+1) % (len(self.original.attr_offsets)-1))
        output = self.path/'bad_edge.agr'; output.write_bytes(data)
        result = subprocess.run([str(self.binary), str(self.original_path), str(output)], capture_output=True)
        self.assertEqual(result.returncode, 2)

    def test_invalid_span_csr_and_overwrite_rejected(self):
        for span in (0, -1, 1.5, True):
            with self.subTest(span=span), self.assertRaises(ValueError):
                write_scoped(self.original, self.path/'invalid.agr', span)
        with self.assertRaises(FileExistsError): write_scoped(self.original, self.original_path)
        csr = self.path/'csr.agr'; write_packed(csr, self.graph, 'csr')
        with self.assertRaises(ValueError): write_scoped(csr, self.path/'invalid_csr.agr', 4)


if __name__ == '__main__': unittest.main()
