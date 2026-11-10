from pathlib import Path
import struct
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from read_trace_set_codec import decode
class CodecTests(unittest.TestCase):
    def test_actual_cpp_fixtures(self):
        raw=(ROOT/'build/trace_set_codec_cpu_20261025_v1/fixtures.bin').read_bytes();at=0;cases=0;encodings=set()
        while at<len(raw):
            count,encoding,nbytes=struct.unpack_from('<3Q',raw,at);at+=24
            keys=list(struct.unpack_from('<%dQ'%count,raw,at));at+=8*count
            nwords=(nbytes+7)//8;words=list(struct.unpack_from('<%dQ'%nwords,raw,at));at+=8*nwords
            self.assertEqual(decode(words,encoding,nbytes,count),keys)
            encodings.add(encoding);cases+=1
        self.assertEqual(cases,506);self.assertEqual(encodings,{0,1})
    def test_literal_byte_order_and_boundaries(self):
        # Literal runs [0..3], [127..128], [256]; 128 crosses a LEB byte.
        raw=bytes([0,4,124,2,128,1,1])
        words=[int.from_bytes(raw+b'\0','little')]
        self.assertEqual(decode(words,1,7,7),[0,1,2,3,127,128,256])
        self.assertEqual(decode([],0,0,0),[])
    def test_corruptions(self):
        def packed(raw):return [int.from_bytes(raw[i:i+8].ljust(8,b'\0'),'little') for i in range(0,len(raw),8)]
        bad=[(b'\0',1,1),(b'\0\0',1,1),(b'\0\1\1\1',1,2),
             (b'\x80\0\1',1,1),(b'\xff'*9+b'\2\1',1,1),
             (b'\xff'*9+b'\1\2',1,2),(b'\0\2',1,1),
             (b'\0\1\2\1',1,3)]
        for raw,encoding,count in bad:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):decode(packed(raw),encoding,len(raw),count)
        for words,encoding,size,count in [([0],0,8,1),([0x1000100],1,2,1),([],2,0,0),([],0,0,1100755),([1],0,0,0)]:
            with self.assertRaises(ValueError):decode(words,encoding,size,count)
if __name__=='__main__':unittest.main()
