import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from paired_binary_rtl_prerequisites_v1 import REPORTS as PAIR
from read_control_pipeline_prerequisites_v1 import REPORTS, validate_prerequisites


class ReadControlPipelineGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.directory = self.root/'results'
        self.directory.mkdir()
        self.proof = self.root/'proof.bin'
        self.proof.write_bytes(b'pipeline fixture')
        files = {str(self.proof):hashlib.sha256(self.proof.read_bytes()).hexdigest()}
        for name,status in {**PAIR,**REPORTS}.items():
            report = dict(status=status,files=files)
            if name in PAIR:
                report.update(ports=44,models=30,snapshots=[{}, {}, {}, {}],candidate_encoding_changed=True,cycles=[1,2,3,4])
            elif name.startswith('snapshot'):
                report.update(rtl_verified=True,transactions=30,pointers=13,models=10,cycles=list(range(1,31)))
            else:
                report.update(transactions=2,models=7,output_files=5,cycles=[2132461,12404])
            (self.directory/name).write_text(json.dumps(report))

    def test_complete_current_pipeline_and_byte_bindings(self):
        self.assertIn(str(self.proof),validate_prerequisites(self.directory))
        self.proof.write_bytes(b'changed')
        with self.assertRaises(ValueError):
            validate_prerequisites(self.directory)

    def test_full30_and_original_search_contracts_cannot_be_reduced(self):
        path = self.directory/'snapshot_dpi_rtl_audit_20261025_v3.json'
        original = path.read_text()
        path.unlink()
        with self.assertRaisesRegex(ValueError,'serialized prerequisite missing'):
            validate_prerequisites(self.directory)
        for key,value in [('rtl_verified',False),('transactions',29),('pointers',12),('models',9),('cycles',list(range(1,30))),('cycles',[0]*30),('files',{})]:
            report = json.loads(original)
            report[key] = value
            path.write_text(json.dumps(report))
            with self.subTest(key=key),self.assertRaises(ValueError):
                validate_prerequisites(self.directory)
        path.write_text(original)
        core = self.directory/'search_axi_dpi_replay_audit_20261025_v3.json'
        report = json.loads(core.read_text())
        report['cycles'] = [1,2]
        core.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError,'Wrong original search-core oracle'):
            validate_prerequisites(self.directory)


if __name__=='__main__':
    unittest.main()
