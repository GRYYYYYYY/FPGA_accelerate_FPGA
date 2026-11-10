from pathlib import Path
import struct
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from read_batch_trace import decode_words
BUNDLE=ROOT/'data/derived/search_batch_trace_cpu_20261025_v1'
def words(mode,case):
    raw=(BUNDLE/f'trace_mode_{mode}_case_{case}.bin').read_bytes()
    return list(struct.unpack('<%dQ'%(len(raw)//8),raw))
def frames(w):
    out=[];at=8
    while at<len(w):out.append(w[at:at+w[at+1]]);at+=w[at+1]
    return out
def rebuild(fs):
    payload=[v for f in fs for v in f]
    return [0x4154524143453031,262144,len(payload),len(fs),0,len(fs)+1,0,0]+payload
class BatchTraceTests(unittest.TestCase):
    def test_both_modes_actual_top(self):
        for mode in [0,1]:
            for case in [0,1,2]:
                d=decode_words(words(mode,case),4)
                self.assertEqual(d['complete_batch'],case!=1)
                self.assertEqual(d['terminal'][3],2 if case==1 else 1)
                self.assertEqual(len(d['searches']),6 if case==1 else 3)
                self.assertEqual(d['terminal'][7],int(case==0))
                self.assertEqual(d['terminal'][11],2 if case==1 else 0)
            with self.assertRaises(ValueError):decode_words(words(mode,3),4)
    def test_isolated_corruptions(self):
        original=frames(words(0,0));changes=[]
        # Recompute container metadata so record count checks cannot hide the
        # required schedule/order/semantic checks.
        for index in range(len(original)):
            changes.append(original[:index]+original[index+1:])
        changes.append(original+[original[-1]])
        changes.append([original[-1]]+original[:-1])
        for index in range(1,len(original)-2):
            f=[x.copy() for x in original];f[index],f[index+1]=f[index+1],f[index];changes.append(f)
        for index,value in [(3,3),(24,8),(25,3),(27,2)]:
            f=[x.copy() for x in original];f[0][index]=value;changes.append(f)
        for index in range(8,20):
            f=[x.copy() for x in original];f[-1][index]+=1;changes.append(f)
        # Scheduled target and search ordinal mutations.
        for index in [2,3,4]:
            f=[x.copy() for x in original];f[1][index]+=1;changes.append(f)
        for i,f in enumerate(changes):
            with self.subTest(mutation=i):
                with self.assertRaises(ValueError):decode_words(rebuild(f),4)
        seeded=frames(words(0,1))
        post=next(i for i,f in enumerate(seeded) if f[0]==3 and f[3]==1)
        with self.assertRaises(ValueError):decode_words(rebuild(seeded[:post]+seeded[post+1:]),4)
if __name__=='__main__':unittest.main()
