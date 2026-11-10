"""Protocol fixtures only; no synthetic fixture is physical-result evidence."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_search_csr_physopt_recovery import terminal,utc


class Protocol(unittest.TestCase):
    def test_nanoseconds(self):
        self.assertEqual(utc('2026-10-24T22:00:00.123456789Z'),utc('2026-10-24T22:00:00.123456Z'))

    def test_terminal_requires_exact_complete_command(self):
        b=Path('/unit/isolated_physical_experiment');command='source {/unit/isolated_physical_experiment/run_flow.tcl}'
        plan={'session_id':'test','owner_pid':42,'source_command':command}
        state={'status':'complete','stage':'physopt_complete_pending_independent_audit','owner_pid':42,'updated_utc':'2026-10-24T22:00:00Z'}
        snapshot={'session_id':'test','observed_utc':'2026-10-24T22:00:02Z','status':{'is_command_running':False,'last_completed_code':0,'queue_length':0,'process_id':42,'working_dir':str(b),'last_completed':command,'last_completed_elapsed':20.0}}
        history={'history':[{'command':command,'code':0,'timestamp':'2026-10-24T22:00:00.123456789Z','elapsed':20.0,'output':'CSR_PHYSOPT_FLOW_COMPLETE\n'}]}
        terminal(plan,state,snapshot,history,b)
        for field,value in [('is_command_running',True),('last_completed_code',1),('queue_length',1),('process_id',43),('last_completed','source {wrong/flow.tcl}'),('last_completed_elapsed',21.0)]:
            s=copy.deepcopy(snapshot);s['status'][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):terminal(plan,state,s,history,b)
        for field,value in [('command','puts fake'),('code',1),('output','no completion'),('timestamp','2026-10-23T22:00:00Z')]:
            h=copy.deepcopy(history);h['history'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):terminal(plan,state,snapshot,h,b)
        h=copy.deepcopy(history);h['history']*=2
        with self.assertRaises(ValueError):terminal(plan,state,snapshot,h,b)
        s=copy.deepcopy(snapshot);s['observed_utc']='2026-10-23T22:00:00Z'
        with self.assertRaises(ValueError):terminal(plan,state,s,history,b)
        s=copy.deepcopy(state);s['status']='running'
        with self.assertRaises(ValueError):terminal(plan,s,snapshot,history,b)


if __name__=='__main__':unittest.main()
