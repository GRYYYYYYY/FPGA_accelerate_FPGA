"""Preserve the observed failed strict-pin experiment as failure evidence."""
from pathlib import Path
import json
import re
import sys
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity


def main():
    p=Path(sys.argv[1]).resolve();assert p==BASE/'stage_static_cp_shadow_system_v3'
    m=read(p/'manifest.json')
    assert m['status']=='failed' and m['stage']=='simulate' and not m.get('active_process')
    assert identity(m['runner_pid'])!=str(m['runner_start_ticks'])
    assert m['runner_sha256']==sha(ROOT/'scripts/run_stage_static_cp_shadow_system_v3.py')
    assert m['parameters']['SLOTS']==32 and m['mode']=='full_netlist_shadow'
    for name,e in m['sources'].items():assert sha(p/'sources'/name)==e['sha256']
    for name,digest in m['shadow_inputs'].items():assert sha(p/'sources'/name)==digest
    for name,e in m['bound'].items():assert sha(e['source'])==sha(p/'bound'/name)==e['sha256']
    ns=read(p/'namespace.json');assert sha(p/'namespace.json')==m['namespace_sha256']
    pre=read(ROOT/'results/stage_static_cp_shadow_v2_namespace_preflight_20261030.json')
    assert ns['exact_inverse'] and ns['output_sha256']==m['shadow_inputs']['shadow_netlist.v']==pre['output_sha256']
    commands=m['cases']['full']['commands'];assert [c['stage'] for c in commands]==['compile','elaborate','simulate']
    for c in commands:
        assert c['exit_code']==0 and sha(p/'full'/(c['stage']+'.stdout.log'))==c['stdout_sha256']
        if c['start_ticks'] is not None:assert identity(c['pid'])!=str(c['start_ticks'])
    log=(p/'full/simulate.log').read_text()
    failure='Fatal: FULL_SHADOW_MISMATCH port=cp_m_data time=256000 actual=00000000 expected=xxxxxxxx'
    assert re.findall(r'^Fatal:.*$',log,re.M)==[failure]
    assert '$finish called at time : 256 ns' in log and 'FULL_SHADOW_PASS' not in log
    probe=BASE/'stage_static_cp_shadow_failure_probe_v1';pm=read(probe/'manifest.json');pa=read(probe/'source_bound_audit.json')
    assert pm['status']=='observed' and pa['status']=='passed' and pa['no_export_transfer_at_failure']
    assert pa['manifest_sha256']==sha(probe/'manifest.json')
    result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(__file__),
                audit_kind='Failure evidence integrity; strict all-pin functional verdict remains failed',
                strict_pin_verdict='failed',first_failure=failure,first_failure_ns=256,
                validity_probe_audit_sha256=sha(probe/'source_bound_audit.json'),
                no_export_transfer_at_failure=True,full_system_functional_netlist_validated=False,
                artifact_sha256={name:sha(p/name) for name in ['namespace.json','full/compile.stdout.log','full/elaborate.stdout.log','full/simulate.stdout.log','full/simulate.log']},
                scope='Original failed strict checker retained. CP data differs while both cp_m_valid and ready are0. This does not prove an active-export mismatch, full protocol equivalence, physical timing or simulator defect.')
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('SHADOW_STRICT_PIN_FAILURE_EVIDENCE_AUDITED')


if __name__=='__main__':main()
