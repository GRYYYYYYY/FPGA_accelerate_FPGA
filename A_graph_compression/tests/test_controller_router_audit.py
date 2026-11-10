import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_controller_router import validate_counters

class ControllerCounterAudit(unittest.TestCase):
    def setUp(self):
        self.plan={'capacity':8,'label_capacity':16,'index_slots':32}
        self.rows=[[i,10,30,20,5,7,0,0,8,12,3] for i in range(2)]
        self.prior={'full_batches_verified':2,
                    'queue_counters':[[i,10,30,20,0,8] for i in range(2)],
                    'label_counters':[[i,10,40,25,0,12,3,2,1,1] for i in range(2)],
                    'record_counters':[[i,10,25,5,7,0,12] for i in range(2)]}
    def check(self,rows,prior=None):
        return validate_counters(''.join('CONTROLLER_COUNTERS '+' '.join(map(str,r))+'\n' for r in rows),self.plan,prior or self.prior,10,7)
    def test_valid(self):self.assertEqual(len(self.check(self.rows)),2)
    def test_corrupt_each_field(self):
        for field in range(11):
            with self.subTest(field=field):
                rows=copy.deepcopy(self.rows)
                for row in rows:row[field]+=1
                with self.assertRaises(ValueError):self.check(rows)
    def test_missing_duplicate_and_resident_drift(self):
        for rows in [self.rows[:1],self.rows*2,[self.rows[0],self.rows[0]]]:
            with self.assertRaises(ValueError):self.check(rows)
        rows=copy.deepcopy(self.rows);rows[1][2]+=1
        with self.assertRaises(ValueError):self.check(rows)
    def test_truncated_predecessor(self):
        for key in ['queue_counters','label_counters','record_counters']:
            prior=copy.deepcopy(self.prior);prior[key]=prior[key][:1]
            with self.assertRaises(ValueError):self.check(self.rows,prior)

if __name__=='__main__':unittest.main()
