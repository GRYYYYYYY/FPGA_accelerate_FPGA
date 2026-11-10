"""Audit replay-driver outcomes on byte-identical fake sequential models."""
from pathlib import Path
import json
import re
import sys
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity


def main():
    p=Path(sys.argv[1]).resolve();assert p.name in ['shadow_transport_nba_control_v1','shadow_transport_nba_control_v2'] and p.parent==BASE
    version=p.name.rsplit('_',1)[1]
    m=read(p/'manifest.json');assert m['status']=='observed' and m['stage']=='complete' and not m.get('active_process')
    assert identity(m['runner_pid'])!=str(m['runner_start_ticks'])
    assert m['runner_sha256']==sha(ROOT/'scripts'/f'run_shadow_transport_nba_control_{version}.py')
    assert m['identical_models_except_names'] and set(m['cases'])=={'negedge_nba','posedge_nba'}
    outcomes={}
    for mode in ['negedge_nba','posedge_nba']:
        d=p/mode;c=m['cases'][mode];assert c['status']=='observed'
        for name,h in c['inputs'].items():assert sha(d/name)==h
        assert sha(d/'shadow.sv')==m['shadow_sha256']
        source=(d/'control.sv').read_text()
        models=[re.search(r'module '+name+r'\b.*?endmodule',source,re.S).group() for name in ['checker_stub_rtl','checker_stub_gate']]
        assert models[1].replace('checker_stub_gate','checker_stub_rtl')==models[0]
        edge=mode.split('_')[0]
        assert f'always @({edge} clk)if(cold)stream<=0;else stream<=stream+1;' in source
        assert [v['stage'] for v in c['commands']]==['compile','elaborate','simulate']
        for command in c['commands']:
            assert command['exit_code']==0
            assert sha(d/(command['stage']+'.stdout.log'))==command['stdout_sha256']
        log=(d/'simulate.stdout.log').read_text();fatal=re.findall(r'^Fatal:.*$',log,re.M)
        should_match=version=='v2' or mode=='negedge_nba'
        assert c['checker_reported_match']==should_match
        if should_match:
            assert not fatal
            assert log.count('FULL_SHADOW_PASS outputs=346 bits=14384 checks=190 reset_edges=5 original_end=1000000 last_checked=1201000')==1
            assert '$finish called at time : 1202 ns' in log
            outcomes[mode]=dict(match=True,checks=190,finish_ns=1202)
        else:
            assert fatal==['Fatal: FULL_SHADOW_MISMATCH port=qc_cp_crc time=256000 actual=00000001 expected=00000000']
            assert 'FULL_SHADOW_PASS' not in log
            outcomes[mode]=dict(match=False,first_failure=fatal[0],failure_ns=256)
    result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(__file__),
                outcomes=outcomes,replay_sampling_valid_for_both_controls=version=='v2',
                identical_models_verified=True,full_system_functional_netlist_validated=False,
                scope='Controlled sequential-model sampling evidence only. v1 posedge NBA fails despite identical models; v2 must pass both without output comparison changes. Not FPGA or arbitrary event-scheduling equivalence.')
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('NBA_REPLAY_CONTROL_AUDITED',version,outcomes)


if __name__=='__main__':main()
