import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from compact_binary_fsm_full44_prerequisites_v1 import REPORTS, validate


class PairedCompactGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'results').mkdir()
        self.proof = self.root/'proof.bin'
        self.proof.write_bytes(b'paired evidence fixture')
        bindings = {str(self.proof):hashlib.sha256(self.proof.read_bytes()).hexdigest()}
        for name,status in REPORTS.items():
            report = dict(status=status,files=bindings)
            if name.startswith('compressed_bus64_binary'):
                report.update(ports=44,models=30,snapshots=[{}, {}, {}, {}],candidate_encoding_changed=True)
            elif name.startswith('paired_binary'):
                report.update(shared_pointer_ports=44,shared_axi_models=30,transactions_per_mode=4,candidates=[dict(graph_mode=0),dict(graph_mode=1)])
            else:
                report['modules'] = [{} for _ in range(45)]
            (self.root/'results'/name).write_text(json.dumps(report))

    def test_complete_typed_pair_and_all_bindings(self):
        self.assertIn(str(self.proof),validate(self.root))

    def test_missing_csr_or_changed_payload_rejected(self):
        path = self.root/'results'/next(iter(REPORTS))
        original = path.read_text()
        path.unlink()
        with self.assertRaisesRegex(ValueError,'prerequisite missing'):
            validate(self.root)
        path.write_text(original)
        self.proof.write_bytes(b'corrupted')
        with self.assertRaisesRegex(ValueError,'Changed paired compact evidence'):
            validate(self.root)

    def test_wrong_variant_scope_and_partial_proofs_rejected(self):
        path = self.root/'results'/next(iter(REPORTS))
        original = json.loads(path.read_text())
        for field,value in [('status','running'),('candidate_encoding_changed',False),('ports',43),('models',29),('snapshots',[{}]),('files',{})]:
            report = dict(original)
            report[field] = value
            path.write_text(json.dumps(report))
            with self.subTest(field=field),self.assertRaises(ValueError):
                validate(self.root)
        path.write_text(json.dumps(original))
        paired = self.root/'results/paired_binary_fsm_candidates_preparation_audit_20261025_v1.json'
        report = json.loads(paired.read_text())
        original_pair = paired.read_text()
        report['candidates'].reverse()
        paired.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError,'Wrong graph-mode pair'):
            validate(self.root)
        paired.write_text(original_pair)
        shape = self.root/'results/hls_compact_binary_fsm_candidate_edit_audit_20261025_v1.json'
        report = json.loads(shape.read_text())
        report['modules'].pop()
        shape.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError,'Incomplete compact encoding proof'):
            validate(self.root)


if __name__=='__main__':
    unittest.main()
