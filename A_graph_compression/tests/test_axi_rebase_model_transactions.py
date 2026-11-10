import tempfile
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_axi_rebase_model_regression_v3 import transactions


class FullPayloadParser(unittest.TestCase):
    def test_original_formats_and_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'words.dat'
            text=''.join('[[transaction]] '+str(i)+'\n0x'+format(i,'x')+'\n[[/transaction]]\n' for i in range(4))
            binary=b''.join((1).to_bytes(8,'big')+i.to_bytes(4,'big') for i in range(4))
            valid=[text.encode(),('[[[runtime]]]\n'+text+'[[[/runtime]]]\n').encode(),binary,binary+bytes.fromhex('5a5aa5a50f0ff0f0')]
            for raw in valid:
                p.write_bytes(raw); self.assertEqual(transactions(p,32,1),[[0],[1],[2],[3]])
            bad=[text.replace('0x3','0xx').encode(),text.replace('0x3','0x100000000').encode(),text.replace('[[transaction]] 3','[[transaction]] 2').encode(),text.rsplit('[[/transaction]]',1)[0].encode(),(text+'0x0\n').encode(),binary[:-1],binary+b'12345678',binary[:40]+(2).to_bytes(8,'big')]
            for raw in bad:
                with self.subTest(raw=raw):
                    p.write_bytes(raw)
                    with self.assertRaises((RuntimeError,ValueError,IndexError,AssertionError)): transactions(p,32,1)


if __name__=='__main__': unittest.main()
