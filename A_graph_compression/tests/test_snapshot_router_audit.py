import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_snapshot_router import validate_counters

class SnapshotRouterAudit(unittest.TestCase):
    def setUp(self):
        self.plan={'capacity':8,'label_capacity':16,'index_slots':32,'config_owners':8,'config_history':8}
        self.cc=[[i,6,20,10,0,6,0,0,3,4,2] for i in range(2)]
        self.sc=[[i,4,3,2,3,2,4,0,3,1] for i in range(2)]
        connections=[[{'status':'found'},{'status':'found'}],[{'status':'found'}]]
        self.reference={'routes':[{'demands':[[1],[],[]]},{'demands':[[2],[],[]]}],
                        'iterations':[{'connections':connections,'conflicts':[[3,[0,1]]],'site_conflicts':[[0,1,[0,1]]]},
                                      {'connections':connections,'conflicts':[],'site_conflicts':[]}]}
    def check(self,cc=None,sc=None,reference=None,prior=None):
        cc=self.cc if cc is None else cc;sc=self.sc if sc is None else sc
        log=''.join(name+' '+' '.join(map(str,row))+'\n' for name,rows in [('CONTROLLER_COUNTERS',cc),('SNAPSHOT_COUNTERS',sc)] for row in rows)
        return validate_counters(log,self.plan,prior or {'controller_counters':self.cc},reference or self.reference)
    def test_valid_and_zero_site_history(self):
        self.assertEqual(len(self.check()[0]),2)
        ref=copy.deepcopy(self.reference);ref['iterations'][0]['site_conflicts']=[]
        sc=copy.deepcopy(self.sc)
        for row in sc:row[5]=row[9]=0
        self.check(sc=sc,reference=ref)
    def test_missing_current_occupancy_history_and_errors(self):
        for field,value in [(1,3),(2,4),(3,0),(5,0),(6,0),(7,1),(8,9),(9,0)]:
            with self.subTest(field=field):
                sc=copy.deepcopy(self.sc)
                for row in sc:row[field]=value
                with self.assertRaises(ValueError):self.check(sc=sc)
    def test_dynamic_site_coverage_and_capacity(self):
        for owner_count,peak in [(0,0),(0,3),(5,3),(3,0)]:
            sc=copy.deepcopy(self.sc)
            for row in sc:row[4]=owner_count;row[8]=peak
            with self.assertRaises(ValueError):self.check(sc=sc)
    def test_incomplete_duplicate_resident_and_predecessor(self):
        for sc in [self.sc[:1],self.sc*2,[self.sc[0],self.sc[0]]]:
            with self.assertRaises(ValueError):self.check(sc=sc)
        sc=copy.deepcopy(self.sc);sc[1][4]+=1
        with self.assertRaises(ValueError):self.check(sc=sc)
        cc=copy.deepcopy(self.cc);cc[0][2]+=1;cc[1][2]+=1
        with self.assertRaises(ValueError):self.check(cc=cc)
        cc=copy.deepcopy(self.cc)
        for row in cc:row[8]=9
        with self.assertRaises(ValueError):self.check(cc=cc,prior={'controller_counters':cc})
    def test_reference_is_not_finished(self):
        ref=copy.deepcopy(self.reference);ref['iterations'][-1]['conflicts']=[[1,[0,1]]]
        with self.assertRaises(ValueError):self.check(reference=ref)

if __name__=='__main__':unittest.main()
