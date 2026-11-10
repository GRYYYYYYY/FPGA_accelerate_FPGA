import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from binary_fsm_full44_prerequisites_v1 import REPORTS, validate


class SerializedGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'results').mkdir()
        self.proof = self.root/'proof.bin'
        self.proof.write_bytes(b'fixture evidence')
        self.files = {str(self.proof): hashlib.sha256(self.proof.read_bytes()).hexdigest()}
        for name,status in REPORTS.items():
            report = dict(status=status,files=self.files)
            if name.startswith('compact_native'):
                report.update(rtl_verified=True,snapshots=[{}, {}, {}, {}])
            if name.startswith('fsm_binary_four'):
                report.update(samples=1280,input_level_cases=64,all_seven_states_observed=True)
            (self.root/'results'/name).write_text(json.dumps(report))

    def test_complete_serial_evidence_bindings(self):
        result = validate(self.root)
        self.assertEqual(result[str(self.proof)],self.files[str(self.proof)])
        self.assertTrue(all(str(self.root/'results'/name) in result for name in REPORTS))

    def test_missing_original_acceptance_and_tampered_evidence(self):
        native = self.root/'results'/next(iter(REPORTS))
        original = native.read_text()
        native.unlink()
        with self.assertRaisesRegex(ValueError,'prerequisite missing'):
            validate(self.root)
        native.write_text(original)
        self.proof.write_bytes(b'changed evidence')
        with self.assertRaisesRegex(ValueError,'Changed binary-FSM prerequisite'):
            validate(self.root)

    def test_unaccepted_partial_or_empty_reports(self):
        native = self.root/'results'/next(iter(REPORTS))
        original = json.loads(native.read_text())
        for field,value in [('status','running'),('rtl_verified',False),('snapshots',[{}]),('files',{})]:
            report = dict(original)
            report[field] = value
            native.write_text(json.dumps(report))
            with self.subTest(field=field),self.assertRaises(ValueError):
                validate(self.root)
        native.write_text(json.dumps(original))
        mechanism = self.root/'results/fsm_binary_four_state_regression_20261025_v1.json'
        report = json.loads(mechanism.read_text())
        report['samples'] = 1279
        mechanism.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError,'Mechanism matrix incomplete'):
            validate(self.root)


if __name__=='__main__':
    unittest.main()
