import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import run_full_scope_phase_v1 as runner


class OwnedAbortTest(unittest.TestCase):
    def test_injected_new_oom_stops_only_disposable_owned_child_and_saves_failure(self):
        initial=dict(policy=runner.POLICY,events={'oom':0,'oom_kill':2},raw_free_bytes=0)
        changed=copy.deepcopy(initial);changed['events']['oom']=1
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory);(out/'plan.json').write_text('{}')
            state=dict(owner_pid=os.getpid(),status='running')
            command=['prlimit','--core=0:0','--','python3','-c','import time; time.sleep(30)']
            with patch.object(runner,'observe',side_effect=[initial,changed,changed]):
                with self.assertRaisesRegex(ValueError,'Full-scope phase failed'):
                    runner.run_phase(out,'postcheck',command,out,state,initial,os.environ.copy(),120)
            receipt=json.loads((out/'postcheck.receipt.json').read_text())
            self.assertEqual(receipt['exit_code'],-15)
            self.assertTrue(receipt['resource_admission_abort'])
            self.assertEqual(receipt['resource_abort_observation']['reason'],'new_cgroup_oom')
            self.assertFalse(Path('/proc',str(state['child_pid'])).exists())


if __name__=='__main__':unittest.main()
