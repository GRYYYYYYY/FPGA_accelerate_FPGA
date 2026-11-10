import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import route_tree_serial_prerequisites_v1 as contract
from binary_nonzero_full44_prerequisites_v2 import ENCODED_STATUS, POLICY


class TreeSerialPrerequisites(unittest.TestCase):
    def test_full_compact_identity_predecessor_binding_and_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'results').mkdir();bindings={}
            for name in [contract.NATIVE,contract.CSR]:
                p=root/'results'/name;p.write_text('{}');bindings[str(p)]=contract.digest(p)
            payload=root/'evidence';payload.write_text('verified')
            report=dict(status=ENCODED_STATUS,resource_policy=POLICY,rtl_verified=True,
                        graph_mode=1,transactions=4,ports=44,models=30,pages=4,
                        candidate_encoding_changed=True,native_cycle_parity_claimed=False,
                        pointer_address_offset=4096,encoded_modules=45,cycles=[1,2,3,4],
                        snapshots=[dict(transaction=i,bytes=946498280,sha256='0'*64) for i in range(4)],
                        files={**bindings,str(payload):contract.digest(payload)})
            out=root/'results'/contract.COMPACT
            with patch.object(contract,'validate',side_effect=lambda mode,r:dict(bindings)):
                out.write_text(json.dumps(report));contract.validate_predecessors(root)
                for field,value in [('graph_mode',0),('transactions',3),('encoded_modules',43),('cycles',[1,2,3])]:
                    out.write_text(json.dumps({**report,field:value}))
                    with self.subTest(field=field),self.assertRaises(ValueError):contract.validate_predecessors(root)
                bad={**report,'files':{**report['files'],str(root/'results'/contract.CSR):'1'*64}}
                out.write_text(json.dumps(bad))
                with self.assertRaises(ValueError):contract.validate_predecessors(root)
                out.write_text(json.dumps(report));payload.write_text('changed')
                with self.assertRaises(ValueError):contract.validate_predecessors(root)

    def test_actual_missing_native_refuses_tree(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'results').mkdir()
            with self.assertRaisesRegex(ValueError,'prerequisite missing'):
                contract.validate_predecessors(root)


if __name__=='__main__':unittest.main()
