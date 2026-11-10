from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_search_heap_external import golden

class ExternalHeapAudit(unittest.TestCase):
    def test_cases_and_rejections(self):
        rows=[(0,0,4096,2,0),(1,73388,4096,73329,0),(2,73329,4096,73223,0),
              (3,131072,128,131071,0),(4,131073,8,131073,1),(5,131071,4097,131071,2),(6,131071,0,131071,0)]
        valid=''.join(f'EXTERNAL_HEAP_BATCH_PASS {b} initial={i} operations={n} final={f} status={s}\n' for b,i,n,f,s in rows)+'EXTERNAL_HEAP_ALL_PASS\n'
        self.assertEqual(golden(valid,1),rows);self.assertEqual(golden(valid*2,2),rows)
        bad=[valid.replace('initial=73388','initial=1023'),valid.replace('initial=73329','initial=0'),
             valid.replace('operations=4097','operations=4096'),valid.replace('status=2','status=0'),
             valid.replace('final=131073','final=131072'),valid.replace('EXTERNAL_HEAP_ALL_PASS',''),
             valid.replace('PASS 3','PASS 4'),valid*2,valid+'ERROR: failure\n',valid+'EXTERNAL_HEAP_MISMATCH\n']
        for text in bad:
            with self.assertRaises(ValueError):golden(text,1)

if __name__=='__main__':unittest.main()
