"""Preserve the observed failed strict-pin experiment as failure evidence."""
from pathlib import Path
import json
import re
import sys
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity


def main():
    p=Path(sys.argv[1]).resolve();assert p==BASE/'stage_static_cp_shadow_system_v4'
    m=read(p/'manifest.json')
    assert m['status']=='failed' and m['stage']=='simulate' and not m.get('active_process')
    assert identity(m['runner_pid'])!=str(m['runner_start_ticks'])
    assert m['runner_sha256']==sha(ROOT/'scripts/run_stage_static_cp_shadow_system_v4.py')
    assert m['parameters']['SLOTS']==32 and m['mode']=='full_netlist_shadow_cp_export_contract'
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
    failure='Fatal: FULL_SHADOW_MISMATCH port=k_a_net time=256000 actual=00000000 expected=xxxxxxxx'
    assert re.findall(r'^Fatal:.*$',log,re.M)==[failure]
    assert '$finish called at time : 255999 ps' in log and 'FULL_SHADOW_PROTOCOL_PASS' not in log
    probe=BASE/'stage_static_cp_shadow_failure_probe_v2';pm=read(probe/'manifest.json');pa=read(probe/'source_bound_audit.json')
    assert pm['status']=='observed' and pa['status']=='passed' and pa['no_cp_export_transfer_at_failure']
    assert pa['manifest_sha256']==sha(probe/'manifest.json')
    assert (p/'full/shadow_cp_export.log').read_text()==''
    assert re.findall(r'^CP_TRANSFER_MONITOR_END words=(\d+)$',log,re.M)==['0']
    result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(__file__),
                audit_kind='Failure evidence integrity; v4 protocol shadow functional verdict remains failed',
                shadow_verdict='failed',first_failure=failure,first_failure_ps=255999,all_pin_strict_equivalence=False,
                validity_probe_audit_sha256=sha(probe/'source_bound_audit.json'),
                authority_request_valid_zero_at_failure=True,no_export_transfer_at_failure=True,full_system_functional_netlist_validated=False,
                artifact_sha256={name:sha(p/name) for name in ['namespace.json','full/compile.stdout.log','full/elaborate.stdout.log','full/simulate.stdout.log','full/simulate.log']},
                scope='Original failed v4 checker retained. k_a_net differs while both k_a_valid outputs are0; no CP export transfer occurred. All ports recorded by read-only exact-snapshot probe. This does not establish active-request/export correctness or permit changing output checks. No full protocol equivalence, physical timing or simulator defect proof.')
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('SHADOW_V4_FAILURE_EVIDENCE_AUDITED')


if __name__=='__main__':main()
