import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from binary_nonzero_full44_prerequisites_v1 import native_scope,encoded_scope,validate,NATIVE_STATUS,ENCODED_STATUS


class TypedFull44Prerequisites(unittest.TestCase):
    def snapshots(self):return [dict(transaction=i,bytes=946498280,sha256='0'*64) for i in range(4)]
    def test_native_full_scope_rejects_partial_or_old_environment(self):
        r=dict(status=NATIVE_STATUS,rtl_verified=True,transactions=4,pointers=44,models=30,pages=4,dut_unchanged=True,pointer_address_offset=4096,cycles=[1,2,3,4],snapshots=self.snapshots())
        native_scope(r)
        for field,value in [('status','compact_native_stack256_full4tx_full44_rtl_and_original_postcheck_verified'),('rtl_verified',False),('transactions',1),('pointers',43),('models',29),('pages',1),('dut_unchanged',False),('pointer_address_offset',0),('cycles',[1,2,3,0]),('snapshots',self.snapshots()[:3])]:
            with self.subTest(field=field),self.assertRaises(ValueError):native_scope({**r,field:value})
        bad=copy.deepcopy(r);bad['snapshots'][3]['bytes']-=1
        with self.assertRaises(ValueError):native_scope(bad)
    def test_encoded_mode_full_outputs_and_identity_required(self):
        r=dict(status=ENCODED_STATUS,rtl_verified=True,graph_mode=0,transactions=4,ports=44,models=30,pages=4,candidate_encoding_changed=True,native_cycle_parity_claimed=False,pointer_address_offset=4096,encoded_modules=43,cycles=[1,2,3,4],snapshots=self.snapshots())
        encoded_scope(r,0)
        for field,value in [('graph_mode',1),('ports',43),('models',29),('encoded_modules',42),('pointer_address_offset',0),('candidate_encoding_changed',False),('native_cycle_parity_claimed',True),('cycles',[1,2,3]),('status','prepared')]:
            with self.subTest(field=field),self.assertRaises(ValueError):encoded_scope({**r,field:value},0)
    def test_missing_native_refuses_both_modes(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'results').mkdir()
            for mode in [0,1]:
                with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'prerequisite missing: compact_nonzero_native'):validate(mode,p)


if __name__=='__main__':unittest.main()
