from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from read_round_trace import decode_words as old
from read_round_trace_v2 import decode_words

def incomplete_round(nets):
    size=44+(nets+1)//2
    frame=[3,size,0,0,1,nets,0,0,0]+[0]*7
    frame += [1,nets,0,1,8,0,0,0]+[0,0,nets,1,0,0,0,1]
    frame += [0x414e4f44454f5731,1,1,1]+[0x41534954454f5731,0,0,0,0,1]+[1,0]+[0]*((nets+1)//2)
    return [0x4154524143453031,16777216,size,1,0,2,0,0]+frame
class IncompleteDecisionTests(unittest.TestCase):
    def test_multiple_incomplete_is_one_action(self):
        for count in [2,3,65536]:
            w=incomplete_round(count)
            with self.assertRaisesRegex(ValueError,'Wrong round decision'):old(w)
            r=decode_words(w)['records'][0]
            self.assertEqual(r['result'][2],count);self.assertEqual(r['result'][3],1)
    def test_count_is_not_action(self):
        for action in [0,2,3,65536]:
            w=incomplete_round(3);w[8+16+8+3]=action
            with self.assertRaises(ValueError):decode_words(w)
if __name__=='__main__':unittest.main()
