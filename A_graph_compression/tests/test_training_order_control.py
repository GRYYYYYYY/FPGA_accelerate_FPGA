import copy
import json
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from training_order_control_contract_v1 import schedule,validate_schedule,AS_BYTES,POLICY
from check_training_order_control_v1 import summarize
from supervise_training_order_control_v1 import run_phase


class OrderControlTests(unittest.TestCase):
    def test_complete_counterbalance_and_reject_prior_random_schedule(self):
        rows=schedule();validate_schedule(rows)
        self.assertEqual(len(set(map(tuple,rows))),6)
        for position in range(3):
            for condition in range(3):self.assertEqual(sum(r[position]==condition for r in rows),2)
        for bad in [rows[:-1],rows+[rows[0]],rows[:-1]+[rows[0]],[[0,2,1],[2,1,0],[2,1,0],[2,1,0],[2,1,0],[2,1,0]]]:
            with self.assertRaises(ValueError):validate_schedule(bad)
        bad=copy.deepcopy(rows);bad[0][0]=True
        with self.assertRaises(ValueError):validate_schedule(bad)

    def records(self):
        return [dict(repeat=r,condition=dict(mode=m,execution=e),application_wall_ms=(r+1)*scale,
                     worker_process_wall_ms=(r+1)*scale+10,parent_pre_native_peak_kib=1024,native_child_peak_kib=1024,
                     stage_ms=dict(native_process_ms=(r+1)*scale-1))
                for r in range(6) for m,e,scale in [('csr','direct',100),('compact','direct',200),('compact','expanded',50)]]

    def test_full18_matched_ratios_and_partial_duplicate_wrong_mode_rejection(self):
        rows=self.records();summary,paired=summarize(rows)
        self.assertEqual([x['n'] for x in summary],[6]*3)
        self.assertEqual([x['ratios_by_repeat'] for x in paired],[[2]*6,[.5]*6])
        for bad in [rows[:-1],rows[:-1]+[rows[0]],rows+rows[:3]]:
            with self.assertRaises(ValueError):summarize(bad)
        bad=copy.deepcopy(rows);bad[0]['condition']['execution']='different'
        with self.assertRaises(ValueError):summarize(bad)
        for value in [0,-1,float('nan'),float('inf')]:
            bad=copy.deepcopy(rows);bad[0]['application_wall_ms']=value
            with self.assertRaises(ValueError):summarize(bad)

    def fixture(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);control=Path(tmp.name)
        (control/'plan.json').write_text('{}')
        initial=dict(policy=POLICY,events=dict(oom=0,oom_kill=2),raw_free_bytes=0)
        command=['prlimit',f'--as={AS_BYTES}:{AS_BYTES}','--core=0:0','--',sys.executable,'-c','import time; time.sleep(2)']
        return control,initial,command,dict(owner_pid=123,status='running',stage='fixture')

    def test_zero_rawfree_without_new_oom_does_not_abort_real_child(self):
        control,initial,command,state=self.fixture()
        run_phase('fixture',command,initial,control,state,observer=lambda:copy.deepcopy(initial))
        receipt=json.loads((control/'fixture.receipt.json').read_text())
        self.assertEqual(receipt['exit_code'],0);self.assertFalse(receipt['resource_abort'])
        self.assertEqual(receipt['actual_owner_limits']['address_space'],[AS_BYTES]*2)

    def test_new_oom_stops_only_owned_group_and_saves_failure(self):
        control,initial,command,state=self.fixture();calls=0
        command[-1]='import time; time.sleep(60)'
        unrelated=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'])
        def sample():
            nonlocal calls
            calls+=1;result=copy.deepcopy(initial)
            if calls>=3:result['events']['oom']=1
            return result
        try:
            with self.assertRaisesRegex(ValueError,'failed; no retry'):
                run_phase('fixture',command,initial,control,state,observer=sample)
            receipt=json.loads((control/'fixture.receipt.json').read_text())
            self.assertEqual(receipt['exit_code'],-signal.SIGTERM)
            self.assertTrue(receipt['resource_abort']);self.assertEqual(receipt['resource_abort_observation']['reason'],'new_cgroup_oom')
            self.assertIsNone(unrelated.poll())
        finally:unrelated.terminate();unrelated.wait(timeout=5)

if __name__=='__main__':unittest.main()
