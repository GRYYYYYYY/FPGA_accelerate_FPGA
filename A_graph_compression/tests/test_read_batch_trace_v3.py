from pathlib import Path
import struct
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from read_batch_trace_v2 import decode_file as old_batch
from read_batch_trace_v3 import decode_file as new_batch
from read_compressed_search_trace import decode_words
from read_search_trace import decode_file as old_search
LOCAL=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def read(p):
    raw=p.read_bytes();return list(struct.unpack('<%dQ'%(len(raw)//8),raw))
def single(frame):return [0x4154524143453031,512,len(frame),1,0,2,0,0]+frame
class CompressedTraceTests(unittest.TestCase):
    def test_both_modes_all_raw_fields_equal(self):
        for mode in [0,1]:
            for case in [0,1,2]:
                name=f'trace_mode_{mode}_case_{case}.bin'
                old=old_batch(ROOT/'data/derived/search_batch_trace_cpu_20261025_v1'/name,4)
                new=new_batch(LOCAL/'trace_v2_cpu'/name,4)
                for key in ['batch_control','terminal','searches','nets','rounds','complete_batch','initial_state_verified']:
                    self.assertEqual(old[key],new[key])
            with self.assertRaises(ValueError):new_batch(LOCAL/'trace_v2_cpu'/f'trace_mode_{mode}_case_3.bin',4)
    def test_literal_search_and_maximum_bitmap(self):
        w=read(LOCAL/'search_trace_v3_cpu/fixture.bin');at=8;records=[]
        while at<len(w):
            size=w[at+1];records+=decode_words(single(w[at:at+size]),66)['records'];at+=size
        self.assertEqual(records,old_search(ROOT/'build/search_trace_cpu_20261025_v2/fixture.bin',66)['records'])
        w=read(LOCAL/'search_trace_v3_cpu/fixture.bin.maximum.bin');r=decode_words(w,1048576)['records'][0]
        self.assertEqual(len(r['unknown_nodes']),1048576)
        self.assertEqual(r['unknown_nodes'][0],0);self.assertEqual(r['unknown_nodes'][-1],1048575)
    def test_descriptor_and_codec_corruptions(self):
        w=read(LOCAL/'search_trace_v3_cpu/fixture.bin');f=w[8:8+w[9]]
        for index,value in [(0,1),(1,1),(6,3),(7,2),(8,2),(9,0),(10,2),(11,0), (len(f)-2,0), (len(f)-2,1<<40)]:
            with self.subTest(index=index):
                b=f.copy();self.assertNotEqual(b[index],value);b[index]=value
                with self.assertRaises(ValueError):decode_words(single(b),66)
if __name__=='__main__':unittest.main()
