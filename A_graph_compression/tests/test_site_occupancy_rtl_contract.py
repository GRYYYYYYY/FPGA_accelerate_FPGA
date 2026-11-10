"""Proof parser negatives; the positive fixture is actual sanitizer CPU output."""
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from site_occupancy_rtl_contract import golden,transactions


class SiteRtlContractTests(unittest.TestCase):
    def test_actual_cpu_sequence_and_corruptions(self):
        text=(ROOT/'tests/fixtures/site_occupancy_rtl_cpu_20261024_v1.log').read_text()
        golden(text);line=text.splitlines()[35]
        corruptions=[text.replace(line+'\n',''),text+line+'\n',
            text.replace('transaction=22 op=3 status=3','transaction=22 op=3 status=0'),
            text.replace('transaction=30 op=1','transaction=30 op=4'),
            text.replace('owners=65536','owners=65535',1),
            text.replace('history=65536','history=65535',1),
            text.replace('version=18446744073709551615','version=0',1),
            text.replace('groups=32768','groups=65536',1),
            text.replace('snapshot=65536','snapshot=65535',1),
            text.replace('full_depth=1','full_depth=0',1),
            text.replace('all_state=1','all_state=0',1),
            text.replace('guards=1','guards=0',1),
            text.replace('SITE_OCCUPANCY_RTL_ALL_PASS','NO_TERMINAL'),
            text+'ERROR: simulator failed\n',text+'SITE_OCCUPANCY_RTL_CASE_PASS malformed\n']
        for i,corrupt in enumerate(corruptions):
            with self.subTest(case=i),self.assertRaises(ValueError):golden(corrupt)

    def test_performance_parser_fixture_is_not_rtl_proof(self):
        text='\n'.join('transaction %d: %d x'%(i,100+i) for i in range(52))+'\n'
        self.assertEqual(transactions(text),list(range(100,152)))
        corruptions=[text.replace('transaction 0: 100','transaction 0: 0'),
            text.replace('transaction 1: 101 x\n',''),text+'transaction 51: 151 x\n',
            text.replace('transaction 51:','transaction 52:'),text+'transaction 52: invalid\n']
        for corrupt in corruptions:
            with self.subTest(corrupt=corrupt[:80]),self.assertRaises(ValueError):transactions(corrupt)


if __name__=='__main__':unittest.main()
