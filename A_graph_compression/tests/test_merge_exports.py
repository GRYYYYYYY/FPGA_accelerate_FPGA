"""Partition boundaries cannot change canonical identities or outgoing rows."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'adapters')]
from canonical_graph import compare
from heldout import select_sources
from import_vivado import read_export
from merge_exports import merge_graphs,write_tsv


class MergeExportsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        graph=read_export(ROOT/'data/raw/netlist_u280_20261022_v1/reference_domain.tsv')
        edge=next(e for e in graph['edges'] if e['src']!=e['dst'] and e['dst'] in graph['roots'])
        cls.roots=[edge['src'],edge['dst']]
        cls.expected=select_sources(graph,cls.roots)
        cls.parts=[select_sources(graph,[r]) for r in cls.roots]
        cls.metadata={'part':graph['metadata']['part']}

    def test_shared_physical_node_and_complete_rows_roundtrip(self):
        merged=merge_graphs(self.parts,self.roots,self.metadata)
        self.assertTrue(compare(self.expected,merged)['equal'])
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'merged.tsv'
            write_tsv(path,merged)
            self.assertTrue(compare(self.expected,read_export(path))['equal'])

    def test_duplicate_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'Duplicate source'):
            merge_graphs([self.parts[0],self.parts[0]],self.roots,self.metadata)

    def test_missing_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'source domain'):
            merge_graphs(self.parts[:1],self.roots,self.metadata)

    def test_shared_node_property_conflict_is_rejected(self):
        parts=deepcopy(self.parts)
        shared=next(iter(set(parts[0]['nodes'])&set(parts[1]['nodes'])))
        parts[1]['nodes'][shared]['SPEED_INDEX']='-12345'
        with self.assertRaisesRegex(ValueError,'Conflicting nodes'):
            merge_graphs(parts,self.roots,self.metadata)


if __name__=='__main__':unittest.main()
