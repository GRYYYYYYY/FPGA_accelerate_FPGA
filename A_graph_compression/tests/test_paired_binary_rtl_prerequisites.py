import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from paired_binary_rtl_prerequisites_v1 import REPORTS, validate


class PairedRtlGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'results').mkdir()
        self.proof = self.root/'proof.bin'
        self.proof.write_bytes(b'full pair fixture')
        for name,status in REPORTS.items():
            report = dict(status=status,ports=44,models=30,snapshots=[{}, {}, {}, {}],cycles=[1,2,3,4],candidate_encoding_changed=True,
                          files={str(self.proof):hashlib.sha256(self.proof.read_bytes()).hexdigest()})
            (self.root/'results'/name).write_text(json.dumps(report))

    def test_both_typed_results_and_current_bindings_required(self):
        self.assertIn(str(self.proof),validate(self.root))
        path = self.root/'results'/list(REPORTS)[1]
        original = path.read_text()
        path.unlink()
        with self.assertRaisesRegex(ValueError,'prerequisite missing'):
            validate(self.root)
        path.write_text(original)
        self.proof.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'Changed paired full44 RTL evidence'):
            validate(self.root)

    def test_partial_wrong_mode_and_wrong_scope_rejected(self):
        path = self.root/'results'/next(iter(REPORTS))
        original = json.loads(path.read_text())
        for key,value in [('status',list(REPORTS.values())[1]),('ports',43),('models',29),('snapshots',[{}]),('candidate_encoding_changed',False),('cycles',[1,2,3]),('cycles',[1,2,0,4]),('files',{})]:
            report = dict(original)
            report[key] = value
            path.write_text(json.dumps(report))
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):
                validate(self.root)


if __name__=='__main__':
    unittest.main()
