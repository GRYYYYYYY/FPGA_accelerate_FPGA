"""Check rejection of altered accounting and graph scope on a completed trial."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/derived/packed_conversion_statistics_20261023_v1'

class ConversionAuditTests(unittest.TestCase):
    def test_real_worker_and_altered_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            shutil.copyfile(SOURCE/'plan.json',directory/'plan.json')
            for suffix in ('.json','.receipt.json','.submission.json','.log'):
                shutil.copyfile(SOURCE/('worker_000'+suffix),directory/('worker_000'+suffix))
            # The test only reads the image, never writes through this symlink.
            (directory/'worker_000.agr').symlink_to(SOURCE/'worker_000.agr')
            path=directory/'worker_000.submission.json';submission=json.loads(path.read_text())
            submission['command'][-3]=str(directory);path.write_text(json.dumps(submission))
            command=[sys.executable,str(ROOT/'scripts/check_packed_conversion.py'),str(directory),'--partial']
            def run(name):return subprocess.run([*command,'--output',str(directory/(name+'.json'))],capture_output=True,text=True)
            self.assertEqual(run('valid').returncode,0)
            receipt_path=directory/'worker_000.receipt.json';receipt=json.loads(receipt_path.read_text())
            bad=dict(receipt,process_wall_ms=1);receipt_path.write_text(json.dumps(bad))
            self.assertNotEqual(run('bad_wall').returncode,0);self.assertFalse((directory/'bad_wall.json').exists())
            receipt_path.write_text(json.dumps(receipt))
            record_path=directory/'worker_000.json';record=json.loads(record_path.read_text())
            record['graph_counts']['nodes']+=1;record_path.write_text(json.dumps(record))
            self.assertNotEqual(run('bad_scope').returncode,0);self.assertFalse((directory/'bad_scope.json').exists())

if __name__=='__main__':unittest.main()
