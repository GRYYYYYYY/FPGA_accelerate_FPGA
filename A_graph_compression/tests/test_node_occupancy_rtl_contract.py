"""Reject incomplete or altered RTL proof; the positive log is an actual CPU preflight."""
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from node_occupancy_rtl_contract import golden,transactions


class OccupancyRtlContractTests(unittest.TestCase):
    def test_actual_cpu_sequence_and_corruptions(self):
        text=(ROOT/'data/derived/node_occupancy_rtl_20261024_v2/cpu.log').read_text()
        golden(text)
        line=text.splitlines()[10]
        corruptions=[text.replace(line+'\n',''),text+line+'\n',
            text.replace('transaction=8 status=4','transaction=8 status=0'),
            text.replace('transaction=0 status=0 nodes=1048576','transaction=0 status=0 nodes=64'),
            text.replace('pairs=6 version=3','pairs=5 version=3'),
            text.replace('version=18446744073709551615','version=0'),
            text.replace('full_depth=1','full_depth=0',1),
            text.replace('all_state=1','all_state=0',1),
            text.replace('NODE_OCCUPANCY_RTL_ALL_PASS','NO_TERMINAL'),
            text+'ERROR: simulator failed\n']
        for i,corrupt in enumerate(corruptions):
            with self.subTest(case=i),self.assertRaises(ValueError):golden(corrupt)

    def test_synthetic_performance_shape_not_hardware_proof(self):
        text='\n'.join('transaction %d: %d x'%(i,100+i) for i in range(28))+'\n'
        self.assertEqual(transactions(text),list(range(100,128)))
        for corrupt in [text.replace('transaction 0: 100','transaction 0: 0'),
                        text.replace('transaction 1: 101 x\n',''),text+'transaction 27: 127 x\n',
                        text.replace('transaction 27:','transaction 28:')]:
            with self.subTest(corrupt=corrupt[:80]),self.assertRaises(ValueError):transactions(corrupt)


if __name__=='__main__':unittest.main()
