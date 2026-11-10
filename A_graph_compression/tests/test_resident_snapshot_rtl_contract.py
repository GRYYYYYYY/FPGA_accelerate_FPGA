"""Parser fixtures test rejection only; they are not RTL execution evidence."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from resident_snapshot_rtl_contract import ROWS,TERMINAL,golden,transactions


class Contract(unittest.TestCase):
    def test_golden_rejects_mutations(self):
        lines=['SNAPSHOT_RTL_TX '+' '.join(map(str,(i,*r))) for i,r in enumerate(ROWS)]
        valid='\n'.join(lines+[TERMINAL])+'\n';golden(valid)
        for i in range(30):
            with self.assertRaises(Exception):golden('\n'.join(lines[:i]+lines[i+1:]+[TERMINAL]))
            for field in range(10):
                row=list((i,*ROWS[i]));row[field]+=1;bad=lines.copy();bad[i]='SNAPSHOT_RTL_TX '+' '.join(map(str,row))
                with self.assertRaises(Exception):golden('\n'.join(bad+[TERMINAL]))
        for bad in [valid+lines[0]+'\n',valid+TERMINAL+'\n',valid.replace(TERMINAL,''),valid+'ERROR: bad\n']:
            with self.assertRaises(Exception):golden(bad)

    def test_performance_rejects_missing_or_bad_cycles(self):
        rows=[f'transaction {i}: {100+i} x' for i in range(30)]
        self.assertEqual(transactions('\n'.join(rows)),list(range(100,130)))
        for i in range(30):
            with self.assertRaises(Exception):transactions('\n'.join(rows[:i]+rows[i+1:]))
        for bad in ['\n'.join(rows+[rows[0]]),'\n'.join(rows).replace('0: 100','0: 0'),'\n'.join(rows[::-1])]:
            with self.assertRaises(Exception):transactions(bad)


if __name__=='__main__':unittest.main()
