"""Small parser fixtures test rejection logic, not hardware behavior."""
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_site_occupancy_rtl_setup_v2 import vector_file


class VectorDepthTests(unittest.TestCase):
    def test_binary_depth_records_every_transaction(self):
        frame=(2).to_bytes(8,'big')+bytes.fromhex('00ff')
        data=frame*2+bytes.fromhex('5a5aa5a50f0ff0f0')
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'input.dat';p.write_bytes(data)
            self.assertEqual(vector_file(p,2,2,2)['format'],'binary_be_depth_records')
            corruptions=[data[:-1],data+b'\x00',data[:-8]+b'\x00'*8,
                         (2).to_bytes(8,'little')+data[8:],
                         data[:10]+(1).to_bytes(8,'big')+data[18:],data[1:]]
            for value in corruptions:
                p.write_bytes(value)
                with self.subTest(value=value),self.assertRaises(ValueError):vector_file(p,2,2,2)

    def test_full_depth_every_transaction(self):
        text='[[[runtime]]]\n[[transaction]] 0\n0x00\n0xff\n[[/transaction]]\n[[transaction]] 1\n0xxx\n0x01\n[[/transaction]]\n[[[/runtime]]]\n'
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'input.dat';p.write_text(text)
            self.assertEqual(vector_file(p,2,2,2)['words_per_transaction'],2)
            for value in [text.replace('0xff\n',''),text.replace('0xff','0xfff'),text.replace('0x01','0xz1'),
                          text.replace('0x00','0x'),text.replace('[[transaction]] 1','[[transaction]] 2'),
                          text.replace('[[[/runtime]]]',''),text+'0x00\n',text.replace('0xff\n','0xff\n0x00\n')]:
                p.write_text(value)
                with self.subTest(value=value),self.assertRaises(ValueError):vector_file(p,2,2,2)


if __name__=='__main__':unittest.main()
