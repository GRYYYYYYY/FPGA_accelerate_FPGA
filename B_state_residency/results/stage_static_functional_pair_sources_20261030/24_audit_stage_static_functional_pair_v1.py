"""Accept only the narrow identical RTL/functional static-stage port probe."""
from pathlib import Path
import json
import re
import sys
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity


def main():
    p=Path(sys.argv[1]).resolve();assert p==BASE/'stage_export_static_cp_functional_pair_v1'
    m=read(p/'manifest.json');assert m['status']=='observed' and m['stage']=='complete' and m['exit_code']==0
    assert identity(m['runner_pid'])!=str(m['runner_start_ticks']) and not m.get('active_process')
    assert m['runner_sha256']==sha(ROOT/'scripts/run_stage_export_static_cp_functional_pair_v1.py')
    ref=BASE/'stage_export_static_cp_synth_v1';sm=read(ref/'manifest.json')
    assert sha(ref/'manifest.json')==m['synthesis_manifest_sha256']
    assert sm['status']=='observed' and sm['exit_code']==0
    assert '-generic STATIC_STAGE_WRITES=1' in (ref/'synth.tcl').read_text()
    assert sha(ref/'controller.sv')==sha(ROOT/'hardware/variants/stage_static_cp_v1/fixed.sv')
    for n,h in m['reference_sources'].items():assert sha(n)==h
    artifacts={};events={};finishes={}
    for mode in ['rtl','functional']:
        c=m['cases'][mode];assert c['status']=='observed'
        assert [x['stage'] for x in c['commands']]==['compile','elaborate','simulate']
        assert all(x['exit_code']==0 for x in c['commands'])
        for n,h in c['inputs'].items():assert sha(p/mode/n)==h
        for n in list(c['inputs'])+['compile.stdout.log','elaborate.stdout.log','simulate.stdout.log']:
            artifacts[mode+'/'+n]=sha(p/mode/n)
        log=(p/mode/'simulate.stdout.log').read_text()
        events[mode]=re.findall(r'^(?:PROBE_IMPORT_PASS|STAGE_EXPORT_AFTER_RESET_PASS).*$',log,re.M)
        assert events[mode]==['PROBE_IMPORT_PASS words=30 slots=01',
            'STAGE_EXPORT_AFTER_RESET_PASS imports=30 exports=30 crc=395d7a27']
        finishes[mode]=re.findall(r'\$finish called at time : (\d+) ns',log)
        assert finishes[mode]==['2870'] and not re.search(r'Fatal:|^ERROR:',log,re.M)
    assert sha(p/'rtl/tb.sv')==sha(p/'functional/tb.sv')==m['tb_sha256']
    assert sha(p/'rtl/glbl.v')==sha(p/'functional/glbl.v')==m['glbl_sha256']
    expected=(ROOT/'hardware/tests/tb_stage_export_after_reset_v3.sv').read_text().replace(
        'route_commit_controller #(.MAX_PATH(8),.MAX_CYCLES(256))dut(.*);',
        'route_commit_controller #(.STATIC_STAGE_WRITES(1),.MAX_PATH(8),.MAX_CYCLES(256))dut(.*);',1)
    assert (p/'rtl/tb.sv').read_text()==expected
    result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),
        artifact_sha256=artifacts,events=events,finish_ns=2870,narrow_original_counterexample_eliminated=True,
        baseline_failure_report_sha256=sha(ROOT/'results/stage_export_functional_mismatch_20261030.json'),
        timing_qualified=False,full_system_functional_acceptance=False,
        scope='Only2-slot/MAX_PATH8 static-stage enabled original import/reset/export port probe, matched RTL versus functional netlist. No arbitrary parameter/XZ/formal/full-system or timing claim.')
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('STATIC_STAGE_FUNCTIONAL_PAIR_AUDITED',2870)


if __name__=='__main__':main()
