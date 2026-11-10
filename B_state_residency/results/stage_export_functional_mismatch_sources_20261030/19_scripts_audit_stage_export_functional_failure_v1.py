"""Preserve a reproduced RTL/netlist mismatch; passed means evidence integrity."""
from pathlib import Path
import json
import re
import sys
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity


def main():
    p=Path(sys.argv[1]).resolve();assert p==BASE/'stage_export_functional_pair_v1'
    m=read(p/'manifest.json')
    assert m['status']=='failed' and m['stage']=='functional_simulate'
    assert identity(m['runner_pid'])!=str(m['runner_start_ticks']) and not m.get('active_process')
    assert m['runner_sha256']==sha(ROOT/'scripts/run_stage_export_functional_pair_v1.py')
    for n,h in m['reference_sources'].items():assert sha(n)==h
    assert sha(BASE/'stage_export_reset_synth_v1/manifest.json')==m['synthesis_manifest_sha256']
    artifacts={}
    for mode in ['rtl','functional']:
        c=m['cases'][mode]
        assert [x['stage'] for x in c['commands']]==['compile','elaborate','simulate']
        assert all(x['exit_code']==0 for x in c['commands'])
        for n,h in c['inputs'].items():assert sha(p/mode/n)==h
        for n in list(c['inputs'])+['compile.stdout.log','elaborate.stdout.log','simulate.stdout.log']:
            artifacts[mode+'/'+n]=sha(p/mode/n)
    assert sha(p/'rtl/tb.sv')==sha(p/'functional/tb.sv')==m['tb_sha256']
    assert sha(p/'rtl/glbl.v')==sha(p/'functional/glbl.v')==m['glbl_sha256']
    rtl=(p/'rtl/simulate.stdout.log').read_text();gate=(p/'functional/simulate.stdout.log').read_text()
    assert 'PROBE_IMPORT_PASS words=30 slots=01' in rtl and 'PROBE_IMPORT_PASS words=30 slots=01' in gate
    assert 'STAGE_EXPORT_AFTER_RESET_PASS imports=30 exports=30 crc=395d7a27' in rtl
    assert 'Fatal: export mismatch word=0 index=0 data=00000001 last=0' in gate
    assert 'Time: 1630 ns' in gate and 'STAGE_EXPORT_AFTER_RESET_PASS' not in gate
    result=dict(status='passed',audit_kind='failed experiment evidence integrity, not functional acceptance',
        manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),
        artifact_sha256=artifacts,rtl_probe_passed=True,functional_netlist_probe_passed=False,
        import_passed_in_both=True,first_failed_export_word=0,expected_word='00000000',actual_word='00000001',
        failure_time_ns=1630,simulator_exit_zero_did_not_mean_test_pass=True,
        classification='observed narrow original-controller RTL versus synthesized functional mismatch; root cause unresolved',
        timing_qualified=False,scope=m['scope'],
        limitations=['No conclusion yet about simulator defect versus synthesis mapping or source/tool interaction.',
                     'Not a reproduced full-system post-synthesis failure; previous RTL-only tests retain their limited scope.'])
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('STAGE_EXPORT_FUNCTIONAL_MISMATCH_EVIDENCE_AUDITED')


if __name__=='__main__':main()
