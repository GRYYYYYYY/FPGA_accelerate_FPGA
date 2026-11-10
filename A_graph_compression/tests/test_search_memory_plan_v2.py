import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from search_kernel_memory_plan import parse_source as original
from search_kernel_memory_plan_v2 import parse_source
class StrictOptionalWidening(unittest.TestCase):
    def setUp(self):
        self.path=ROOT/'hardware/vitis/search_batch_trace_top_v2.cpp';self.text=self.path.read_text()
        self.anchor='#pragma HLS INTERFACE m_axi port=packet offset=slave bundle=input_mem depth=4194304'
    def parse(self,text):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'top.cpp';p.write_text(text);return parse_source(p)
    def test_canonical_abi_unchanged(self):self.assertEqual(parse_source(self.path),original(self.path))
    def test_width_metadata_does_not_change_identity_capacity_or_order(self):
        before=original(self.path);after=self.parse(self.text.replace(self.anchor,self.anchor+' max_widen_bitwidth=64'))
        self.assertEqual(len(after),45)
        self.assertEqual(sum(p['pointer'] for p in after),44)
        actual=next(p for p in after if p['name']=='packet');self.assertEqual(actual.pop('max_widen_bitwidth'),64)
        self.assertEqual(after,before)
    def test_bad_or_ambiguous_options_rejected(self):
        for suffix in [' max_widen_bitwidth=32',' max_widen_bitwidth=0',' max_widen_bitwidth=64 max_widen_bitwidth=64',' mystery=64',' max_widen_bitwidth=64 garbage',' depth=8',' max_widen_bitwidth=64;']:
            with self.subTest(suffix=suffix),self.assertRaises(ValueError):self.parse(self.text.replace(self.anchor,self.anchor+suffix))
if __name__=='__main__':unittest.main()
