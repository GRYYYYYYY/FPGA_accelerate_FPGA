"""Seeded experiment blocks preserve repetitions and provider outcomes."""
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from netlist_runtime_benchmark import make_jobs,normalized


class RuntimeDesignTests(unittest.TestCase):
    def test_seeded_blocks_have_every_condition_once(self):
        jobs=make_jobs(['csr','direct','prepared','expanded'],[0,64,4096],7,20261022)
        self.assertEqual(jobs,make_jobs(['csr','direct','prepared','expanded'],[0,64,4096],7,20261022))
        expected={(m,c) for m in ['csr','direct','prepared','expanded'] for c in [0,64,4096]}
        for repeat in range(7):
            block=[j for j in jobs if j['repeat']==repeat]
            self.assertEqual(len(block),12)
            self.assertEqual({(j['mode'],j['capacity']) for j in block},expected)

    def test_normalization_preserves_failure_and_counter_evidence(self):
        first={'status':'incomplete','conflicts':{'node':2},'wall_ms':1}
        second={'status':'incomplete','conflicts':{'node':3},'wall_ms':2}
        self.assertNotEqual(normalized(first),normalized(second))
        self.assertEqual(normalized(first),normalized(dict(first,wall_ms=99)))

    def test_duplicate_or_empty_conditions_rejected(self):
        for modes,capacities,repeats in [(['csr','csr'],[0],1),(['csr'],[0,0],1),([], [0],1),(['csr'],[0],0)]:
            with self.assertRaises(ValueError):make_jobs(modes,capacities,repeats,1)


if __name__=='__main__':unittest.main()
