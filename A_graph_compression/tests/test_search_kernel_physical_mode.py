"""Terminal MCP/history gates: reject stale, running and forged completions."""
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_search_kernel_physical_mode import session_gate


class TerminalHistory(unittest.TestCase):
    def test_real_nanosecond_history_and_rejected_corruptions(self):
        bundle=ROOT/'data/derived/search_kernel_physical_20261024_v1'
        snapshot=json.loads((bundle/'session_observation_20261024_csr_terminal.json').read_text())['csr']
        history=json.loads((bundle/'csr_terminal_mcp_history.json').read_text())
        plan=json.loads((bundle/'plan.json').read_text());job=next(x for x in plan['jobs'] if x['mode']=='csr')
        start=next(x for x in json.loads((bundle/'observation_0001.json').read_text())['observations'] if x['mode']=='csr')
        state=json.loads((bundle/'csr/state.json').read_text())
        session_gate(snapshot,job,state,bundle/'csr',start,history)
        def running(s,h):s['status']['is_command_running']=True
        def failed(s,h):s['status']['last_completed_code']=1
        def queued(s,h):s['status']['queue_length']=1
        def stale(s,h):s['observed_utc']='2026-10-23T00:00:00Z'
        def wrong_owner(s,h):s['status']['process_id']+=1
        def wrong_command(s,h):s['status']['last_completed']='source {some_other_flow.tcl}'
        def wrong_history(s,h):h['history'][-1]['command']='puts fake'
        def history_failed(s,h):h['history'][-1]['code']=1
        def history_no_marker(s,h):h['history'][-1]['output']='no completion'
        def history_duplicate(s,h):h['history'].append(copy.deepcopy(h['history'][-1]))
        def duration(s,h):h['history'][-1]['elapsed']+=10
        for change in [running,failed,queued,stale,wrong_owner,wrong_command,wrong_history,history_failed,history_no_marker,history_duplicate,duration]:
            with self.subTest(case=change.__name__):
                s=copy.deepcopy(snapshot);h=copy.deepcopy(history);change(s,h)
                with self.assertRaises(ValueError):session_gate(s,job,state,bundle/'csr',start,h)


if __name__=='__main__':unittest.main()
