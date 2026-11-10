"""Independently audit bounded checker outcomes, including expected failures."""
from pathlib import Path
import json
import re
import sys
from host_edit_system_common_v1 import ROOT, BASE, read, sha, identity


def main():
    p=Path(sys.argv[1]).resolve()
    assert p==BASE/'stage_static_cp_shadow_clock_stateful_controls_v1'
    m=read(p/'manifest.json')
    assert m['status']=='observed' and m['stage']=='complete' and not m.get('active_process')
    assert identity(m['runner_pid'])!=str(m['runner_start_ticks'])
    assert m['runner_sha256']==sha(ROOT/'scripts/run_stage_static_cp_shadow_clock_stateful_controls_v1.py')
    assert m['shadow_sha256']==sha(ROOT/'hardware/variants/stage_static_cp_shadow_clock_v2/shadow.sv')
    modes=['matching','known_mismatch','x_mismatch','z_mismatch','short_reset']
    assert set(m['cases'])==set(modes)
    outcomes={}
    for mode in modes:
        d=p/mode;c=m['cases'][mode]
        assert c['status']=='observed'
        for name,h in c['inputs'].items():assert sha(d/name)==h
        assert sha(d/'shadow.sv')==m['shadow_sha256']
        assert (d/'run.tcl').read_text()=='run 2us\nquit\n'
        assert [e['stage'] for e in c['commands']]==['compile','elaborate','simulate']
        for cmd in c['commands']:
            assert cmd['exit_code']==0
            assert sha(d/(cmd['stage']+'.stdout.log'))==cmd['stdout_sha256']
        log=(d/'simulate.stdout.log').read_text()
        fatal=re.findall(r'^Fatal:.*$',log,re.M)
        if mode=='matching':
            assert not fatal
            assert log.count('FULL_SHADOW_PASS outputs=346 bits=14384 checks=190 reset_edges=5 original_end=1000000 last_checked=1201000')==1
            assert '$finish called at time : 1202 ns' in log
            outcomes[mode]=dict(checks=190,reset_edges=5,finish_ns=1202)
        else:
            assert len(fatal)==1 and 'FULL_SHADOW_PASS' not in log
            if mode=='short_reset':
                assert 'FULL_SHADOW_INCOMPLETE reset=2 checks=0 last=0 end=1000000' in fatal[0]
            else:
                expected={'known_mismatch':'0','x_mismatch':'x','z_mismatch':'z'}[mode]
                assert f'FULL_SHADOW_MISMATCH port=boot_pending time=301000 actual={expected} expected=1' in fatal[0]
            assert 'transport first transition lost' not in log
            outcomes[mode]=dict(expected_fatal=fatal[0])
    result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(__file__),
                outcomes=outcomes,full_system_functional_netlist_validated=False,
                scope='Stateful checker control integrity and outcomes only; clocked counter and registered stream drive all known outputs. Equal X/Z outputs accepted, different known/X/Z outputs rejected, insufficient reset rejected, rapid input transport and full output drain exercised. No real FPGA DUT/netlist validation.')
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('STATEFUL_SHADOW_CHECKER_CONTROLS_AUDITED',len(outcomes))


if __name__=='__main__':main()
