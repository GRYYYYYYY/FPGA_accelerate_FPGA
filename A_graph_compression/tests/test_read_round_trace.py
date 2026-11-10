from pathlib import Path
import struct
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from read_round_trace import decode_words

class RoundTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw=(ROOT/'build/round_trace_cpu_20261025_v1/fixture.bin').read_bytes()
        cls.w=list(struct.unpack('<%dQ'%(len(raw)//8),raw))
    def test_literal_last_conflict_round(self):
        d=decode_words(self.w);self.assertFalse(d['complete_batch'])
        a,b=d['records']
        self.assertEqual(a['result'],[0,2,0,1,0,0,1,1])
        self.assertEqual(a['node_history'],[0,9,0,4])
        self.assertEqual(b['node_history'],[0,11,0,5])
        self.assertEqual(a['site_history'],[])
        self.assertEqual(b['site_history'],[[3,2]])
        self.assertEqual(a['summaries'],[[3,3]])
    def test_corruptions(self):
        changes=[(0,0),(2,131),(3,1),(4,2),(5,4),(8,2),(9,64),
                 (11,1),(17,1),(24,3),(26,1),(27,0),(29,0),
                 (33,1),(35,0),(38,0),(39,0),(40,1),(41,2),
                 (43,5),(45,2),(47,2),(50,0),(51,1<<32),
                 (58,0),(60,2),(62,1),(63,1),(71,4),(72,2),
                 (76,0),(105,0),(108,0),(112,0),(114,0),
                 (116,1),(118,10),(122,4),(124,4),(136,4),(137,3),(139,2)]
        for index,value in changes:
            with self.subTest(index=index):
                w=self.w.copy();self.assertNotEqual(w[index],value);w[index]=value
                with self.assertRaises(ValueError):decode_words(w)
        # A valid pre frame is insufficient when its decision advances histories.
        w=self.w[:73];w[2]=65;w[3]=1;w[5]=2
        with self.assertRaises(ValueError):decode_words(w)
        for w in [self.w[:-1],self.w+[0]]:
            with self.assertRaises(ValueError):decode_words(w)
if __name__=='__main__':unittest.main()
