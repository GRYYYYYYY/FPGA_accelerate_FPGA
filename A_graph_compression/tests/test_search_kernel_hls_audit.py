import importlib.util
from pathlib import Path
import unittest
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_search_kernel_hls import golden

class SearchKernelGoldenAudit(unittest.TestCase):
    def setUp(self):
        self.good='SEARCH_KERNEL_TOP_TRANSACTION_PASS mode=0 transaction=0 status=0 cost=35 path=2\nSEARCH_KERNEL_TOP_TRANSACTION_PASS mode=0 transaction=1 status=3 cost=0 path=0\nSEARCH_KERNEL_TOP_ALL_PASS transactions=2 full_workspace_limits=1\n'
    def test_complete(self):
        golden(self.good,0,1);golden(self.good*2,0,2)
    def test_incomplete_and_drift(self):
        bad=[self.good.splitlines()[0]+'\n',self.good*2,self.good.replace('mode=0','mode=1'),self.good.replace('cost=35','cost=34'),self.good.replace('path=2','path=1'),self.good.replace('status=3','status=1'),self.good.replace('full_workspace_limits=1','full_workspace_limits=0'),self.good+'ERROR: failed\n']
        for content in bad:
            with self.subTest(content=content):
                with self.assertRaises(ValueError):golden(content,0,1)
    def test_second_rtl_copy_required(self):
        with self.assertRaises(ValueError):golden(self.good,0,2)

if __name__=='__main__':unittest.main()
