"""Exercise the independent matrix auditor against actual completed receipts."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]


class CapacityAuditTests(unittest.TestCase):
    def test_real_matrix_and_resource_scope_mutations(self):
        source=ROOT/'data/derived/scale_capacity_region_20261023_v1'
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for variant in ('valid','wrong_limit','missing_cell','wrong_result'):
                directory=root/variant;shutil.copytree(source,directory)
                if variant=='wrong_limit':
                    path=directory/'worker_000.submission.json';d=json.loads(path.read_text())
                    d['command'][1]='--as=999999999:999999999';path.write_text(json.dumps(d))
                elif variant=='missing_cell':
                    path=directory/'report.json';d=json.loads(path.read_text());d['records'].pop();path.write_text(json.dumps(d))
                elif variant=='wrong_result':
                    for path in directory.glob('worker_*.receipt.json'):
                        d=json.loads(path.read_text())
                        if d['exit_code']==0:
                            output=json.loads(d['stdout']);output['unknown_rows']=0;d['stdout']=json.dumps(output)
                            path.write_text(json.dumps(d));break
                    else:self.fail('No successful real scan to mutate')
                result=subprocess.run([sys.executable,str(ROOT/'scripts/check_scale_capacity.py'),str(directory),
                    '--output',str(root/(variant+'.json'))],capture_output=True,text=True)
                with self.subTest(variant=variant):
                    self.assertEqual(result.returncode==0,variant=='valid',result.stderr)


if __name__=='__main__':unittest.main()
