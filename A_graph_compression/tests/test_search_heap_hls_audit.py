import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_search_heap_hls import golden,transactions

class HeapAudit(unittest.TestCase):
    def test_golden_coverage(self):
        valid='HEAP_TOP_BATCH_PASS 0 operations=4096\nHEAP_TOP_BATCH_PASS 1 operations=4096\nHEAP_TOP_ALL_PASS\n'
        golden(valid,1);golden(valid*2,2)
        for bad in [valid.replace('4096','4095'),valid.replace('HEAP_TOP_ALL_PASS',''),valid*2,valid+'ERROR: failed\n',valid.replace('PASS 1','PASS 0'),valid+'HEAP_TOP_MISMATCH\n']:
            with self.assertRaises(ValueError):golden(bad,1)
    def test_transaction_coverage(self):
        self.assertEqual(transactions('transaction 0: 100\ntransaction 1: 200\n'),[100,200])
        for bad in ['transaction 0: 1\n','transaction 0: 1\ntransaction 0: 2\n','transaction 0: 0\ntransaction 1: 2\n','transaction 1: 1\ntransaction 0: 2\n']:
            with self.assertRaises(ValueError):transactions(bad)

if __name__=='__main__':unittest.main()
