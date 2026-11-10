from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'tests'))
from read_batch_trace import decode_words as v1
from read_batch_trace_v2 import decode_words, preserves
from test_read_batch_trace import words, frames, rebuild
class StrongerReaderTests(unittest.TestCase):
    def test_actual_both_modes(self):
        for mode in [0,1]:
            for case in [0,1,2]:
                self.assertEqual(decode_words(words(mode,case),4)['complete_batch'],case!=1)
    def test_previous_reader_accepted_demand_loss(self):
        fs=frames(words(0,0))
        first=fs[1]
        # Search raw result demand header at frame[24], signal lanes at[25].
        # Add signal4 to the first search; later searches silently drop it.
        first[24]+=1<<32;first[25]|=4<<32
        w=rebuild(fs)
        self.assertTrue(v1(w,4)['complete_batch'])
        with self.assertRaisesRegex(ValueError,'inherited demand'):decode_words(w,4)
    def test_previous_reader_accepted_global_total_corruptions(self):
        for offset in [96,100,102,106,108,112]:
            fs=frames(words(0,0));net=next(f for f in fs if f[0]==2)
            # Header16/result8/demand65/tree5 => node metadata starts94.
            net[offset]+=1
            if offset==106:net[23]+=1 # result.global_edges follows the same corruption
            w=rebuild(fs)
            self.assertTrue(v1(w,4)['complete_batch'])
            with self.assertRaises(ValueError):decode_words(w,4)
    def test_mask_and_category_inheritance(self):
        old=dict(signals=[3],bits=[[4,3,1]],values=[[5,2]])
        self.assertTrue(preserves(old,dict(signals=[3,9],bits=[[4,7,5]],values=[[5,2],[6,7]])))
        for new in [dict(signals=[],bits=[[4,3,1]],values=[[5,2]]),dict(signals=[3],bits=[[4,1,1]],values=[[5,2]]),dict(signals=[3],bits=[[4,3,0]],values=[[5,2]]),dict(signals=[3],bits=[[4,3,1]],values=[[5,3]])]:
            self.assertFalse(preserves(old,new))
if __name__=='__main__':unittest.main()
