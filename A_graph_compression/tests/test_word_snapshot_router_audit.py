import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_word_snapshot_router import validate_counters
from test_snapshot_router_audit import SnapshotRouterAudit

class WordSnapshotAudit(unittest.TestCase):
    def setUp(self):
        base=SnapshotRouterAudit();base.setUp()
        self.plan,self.reference,self.cc,self.sc=base.plan,base.reference,base.cc,base.sc
    def check(self,cc,sc):
        log=''.join(name+' '+' '.join(map(str,row))+'\n' for name,rows in [('CONTROLLER_COUNTERS',cc),('SNAPSHOT_COUNTERS',sc)] for row in rows)
        return validate_counters(log,self.plan,{'controller_counters':self.cc,'snapshot_counters':self.sc},self.reference)
    def test_valid(self):self.assertEqual(len(self.check(self.cc,self.sc)[1]),2)
    def test_any_counter_drift(self):
        for family in ['cc','sc']:
            for index in range(len(getattr(self,family)[0])):
                with self.subTest(family=family,index=index):
                    cc,sc=copy.deepcopy(self.cc),copy.deepcopy(self.sc)
                    for row in cc if family=='cc' else sc:row[index]+=1
                    with self.assertRaises(ValueError):self.check(cc,sc)
    def test_truncated_and_duplicate(self):
        for sc in [self.sc[:1],self.sc*2,[self.sc[0],self.sc[0]]]:
            with self.assertRaises(ValueError):self.check(self.cc,sc)

if __name__=='__main__':unittest.main()
