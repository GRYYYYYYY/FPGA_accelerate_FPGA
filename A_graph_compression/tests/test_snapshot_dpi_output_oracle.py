import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from snapshot_dpi_output_oracle_v1 import binary_records,text_records

class SnapshotOutputTests(unittest.TestCase):
    def test_every_binary_word_and_optional_eof(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'expected';b=Path(d)/'actual'
            body=b''.join((3).to_bytes(8,'big')+bytes([i,2,3,4,5,6]) for i in range(2));marker=bytes.fromhex('5a5aa5a50f0ff0f0')
            a.write_bytes(body+marker)
            for ending in [b'',marker]:b.write_bytes(body+ending);binary_records(a,b,3,2,2)
            corrupted=bytearray(body);corrupted[11]^=1;b.write_bytes(corrupted)
            with self.assertRaises(ValueError):binary_records(a,b,3,2,2)
            b.write_bytes(body[:-1])
            with self.assertRaises(ValueError):binary_records(a,b,3,2,2)

    def test_text_framing_values_and_unknowns(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'data';text='[[[runtime]]]\n[[transaction]] 0\n0x0001\n[[/transaction]]\n[[transaction]] 1\n0xFF\n[[/transaction]]\n[[[/runtime]]]\n'
            p.write_text(text);self.assertEqual(text_records(p,1,2,8),[[1],[255]])
            p.write_text(text.replace('[[transaction]] 0','[[transaction]]           0'));self.assertEqual(text_records(p,1,2,8),[[1],[255]])
            for bad in [text.replace('0xFF','0xFX'),text.replace('[[transaction]] 1','[[transaction]] 0'),text.replace('0xFF','0x100')]:
                p.write_text(bad)
                with self.assertRaises(ValueError):text_records(p,1,2,8)

if __name__=='__main__':unittest.main()
