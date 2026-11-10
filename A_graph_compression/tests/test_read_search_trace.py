"""Independent reader checks actual C++-written records and rejects byte/field damage."""
from pathlib import Path
import struct
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from read_search_trace import decode_file,decode_words
class Reader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path=ROOT/'build/search_trace_cpu_20261025_v2/fixture.bin'
        cls.raw=cls.path.read_bytes();cls.words=list(struct.unpack('<'+str(len(cls.raw)//8)+'Q',cls.raw))
    def test_actual_writer_payload_and_zero_count_stale_array(self):
        r=decode_file(self.path,66);self.assertFalse(r['complete_batch']);self.assertTrue(r['requires_terminal_record'])
        self.assertEqual(len(r['records']),2);a,b=r['records']
        self.assertEqual(a['roots'],[0,2]);self.assertEqual(a['unknown_nodes'],[3,64]);self.assertEqual(a['unknown_pips'],[(0xffffffff<<32)|11])
        self.assertEqual(a['path'],[[0,1,0xffffffff,7,1,2,0xabcdef01,1],[1,65,0,8,2,3,0xffffffff,0]])
        self.assertEqual(b['result'][0],6);self.assertEqual(b['unknown_nodes'],[]);self.assertEqual(b['unknown_pips'],[]);self.assertIsNone(b['demands'])
    def test_corruptions(self):
        changes=[(0,0),(4,2),(5,7),(9,100),(11,8),(12,66),(23,524289),(24,3),(31,2),(32,65|(33<<32)),(97,0),(102,2|(65<<32)),(105,0xffffffff|(2<<32)),(106,66),(107,3),(112,7),(198,1<<32)]
        for index,value in changes:
            data=self.words.copy();data[index]=value
            with self.subTest(index=index),self.assertRaises(ValueError):decode_words(data,66)
        data=self.words.copy();data[3]=3;data[5]=4
        with self.assertRaises(ValueError):decode_words(data,66)
        data=self.words.copy();data[32]=65|(1<<40);data[73]=1
        with self.assertRaises(ValueError):decode_words(data,66)
        data=self.words.copy();data[2]+=1;data[9]+=1;data[15]+=1;data[25]+=1;data.insert(109,data[108])
        with self.assertRaises(ValueError):decode_words(data,66)
    def test_file_truncation_endian_and_extra_words(self):
        invalid=[self.raw[:-1],self.raw+b'\0'*8,struct.pack('>'+str(len(self.words))+'Q',*self.words)]
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'trace.bin'
            for raw in invalid:
                p.write_bytes(raw)
                with self.assertRaises(ValueError):decode_file(p,66)
if __name__=='__main__':unittest.main()
