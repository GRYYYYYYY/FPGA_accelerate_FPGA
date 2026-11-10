"""Audit the immutable-snapshot valid/ready probe; never declare DUT acceptance."""
from pathlib import Path
import json
import re
import sys
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity


def main():
    p=Path(sys.argv[1]).resolve();assert p==BASE/'stage_static_cp_shadow_failure_probe_v1'
    m=read(p/'manifest.json');assert m['status']=='observed' and m['stage']=='complete' and m['exit_code']==0
    assert not m.get('active_process') and identity(m['runner_pid'])!=str(m['runner_start_ticks'])
    assert m['runner_sha256']==sha(ROOT/'scripts/probe_stage_static_cp_shadow_failure_v1.py')
    ref=BASE/'stage_static_cp_shadow_system_v3';rm=read(ref/'manifest.json')
    assert rm['status']=='failed' and m['reference_manifest_sha256']==sha(ref/'manifest.json')
    assert m['command']==[a.replace(str(ref),str(p)) for a in rm['cases']['full']['commands'][-1]['argv']]
    assert sha(p/'full/run.tcl')==m['tcl_sha256']
    for name,digest in m['snapshot_sha256'].items():
        assert sha(p/'full/xsim.dir/iter2'/name)==sha(ref/'full/xsim.dir/iter2'/name)==digest
    log=p/'full/simulate.log';assert sha(log)==m['log_sha256']
    text=log.read_text()
    assert re.findall(r'^Fatal:.*$',text,re.M)==['Fatal: FULL_SHADOW_MISMATCH port=cp_m_data time=256000 actual=00000000 expected=xxxxxxxx']
    rows=re.findall(r'^SHADOW_PROBE (before_255ns|after_256ns) (\w+) (\S+)$',text,re.M)
    values={label:{name:value.lower() for lab,name,value in rows if lab==label} for label in ['before_255ns','after_256ns']}
    assert len(rows)==30 and all(len(v)==15 for v in values.values())
    for label,v in values.items():
        for name in ['actual_cp_m_valid','expected_cp_m_valid','actual_cp_m_last','expected_cp_m_last','drive_cp_m_ready','drive_cp_valid','drive_cp_restore','drive_k_cold_rst']:
            assert v[name]=='0',(label,name,v[name])
        assert v['actual_cp_m_data']=='00000000' and v['expected_cp_m_data']=='xxxxxxxx'
        assert v['actual_cp_m_index']==v['expected_cp_m_index']=='00000000'
        assert v['armed']=='1' and v['reset_edges']=='00000005'
    assert values['before_255ns']['checks']=='00000000' and values['after_256ns']['checks']=='00000001'
    result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(__file__),
                observations=values,first_failure_ns=256,strict_pin_verdict='failed',
                same_failure_reproduced=True,snapshot_and_checker_unchanged=True,
                no_export_transfer_at_failure=True,full_system_functional_netlist_validated=False,
                scope='Read-only copied-snapshot probe proves both valid outputs and ready low at strict data mismatch. Not a valid-export mismatch, protocol pass, full pin equivalence or RTL/tool-defect root-cause proof.')
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('SHADOW_FAILURE_VALID_PROBE_AUDITED')


if __name__=='__main__':main()
