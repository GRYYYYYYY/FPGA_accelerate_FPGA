"""Audit observed functional outcomes separately from artifact integrity."""
from pathlib import Path
import json
import re
import sys
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity,restored
from audit_stage_bank_matrix_rtl_v2 import check_trace


def main():
    p=Path(sys.argv[1]).resolve();assert p==BASE/'stage_bank_functional_matrix_v1'
    m=read(p/'manifest.json')
    assert m['status']=='observed' and m['stage']=='complete' and m['exit_code']==0
    assert identity(m['runner_pid'])!=str(m['runner_start_ticks']) and not m.get('active_process')
    assert m['runner_sha256']==sha(ROOT/'scripts/run_stage_bank_functional_matrix_v1.py')
    prep=ROOT/'results/stage_bank_functional_matrix_preparation_20261030.json'
    assert sha(prep)==m['preparation_sha256']
    for name,digest in read(prep)['bound'].items():assert sha(name)==digest
    reference=BASE/'stage_bank_matrix_rtl_v2';rm,ra,_=restored(reference)
    assert sha(reference/'source_bound_audit.json')==m['reference_audit_sha256']
    variant=ROOT/'hardware/variants/stage_static_cp_v1';vm=read(variant/'manifest.json')
    artifacts={};outcomes={};passed=[];failed=[]
    assert set(m['cases'])=={'original','default','static'}
    for mode in ['original','default','static']:
        c=m['cases'][mode];assert c['status']=='observed'
        assert [x['stage'] for x in c['commands']]==['synthesis','compile','elaborate','simulate']
        assert all(x['exit_code']==0 for x in c['commands'])
        assert '--O0' in c['commands'][2]['argv'] and 'unisims_ver' in c['commands'][2]['argv']
        for n,h in {**c['inputs'],**c['artifact_sha256']}.items():assert sha(p/mode/n)==h
        assert sha(p/mode/'controller.sv')==vm['baseline_sha256' if mode=='original' else 'fixed_sha256']
        assert sha(p/mode/'tb.sv')==rm['tb_sha256']
        assert sha(p/mode/'glbl.v')==sha(p/'original/glbl.v')
        assert sha(p/mode/'functional.v')==c['functional_netlist_sha256']
        assert sha(p/mode/'synth.dcp')==c['dcp_sha256']
        tcl=(p/mode/'synth.tcl').read_text()
        for token in ['-generic MAX_PATH=32','-generic MAX_CYCLES=256','-generic PATH_SLOTS=4','-generic PATH_SLOT_BITS=2','xcu280-fsvh2892-2L-e','-flatten_hierarchy rebuilt','-period 10.000']:
            assert token in tcl
        if mode=='original':assert 'STATIC_STAGE_WRITES' not in tcl
        else:assert '-generic STATIC_STAGE_WRITES='+('1' if mode=='static' else '0') in tcl
        log=(p/mode/'simulate.stdout.log').read_text()
        trace='\n'.join(re.findall(r'^(?:EVT |CASE |STAGE_BANK_MATRIX_PASS).*$',log,re.M))+'\n'
        assert trace==(p/mode/'events.txt').read_text()
        fatals=re.findall(r'^Fatal:.*$',log,re.M)
        assert fatals==c['fatal_messages']
        baseline=(reference/mode/'events.txt').read_text()
        if c['functional_passed']:
            assert not fatals
            coverage=check_trace(trace)
            assert trace==baseline
            assert re.findall(r'\$finish called at time : (\d+) ns',log)==['232450']
            outcomes[mode]=dict(functional_passed=True,coverage=coverage,exact_rtl_cycle_event_match=True)
            passed.append(mode)
        else:
            assert len(fatals)==1 and 'STAGE_BANK_MATRIX_PASS' not in log
            assert re.search(r'\$finish called at time :|Time:',log)
            observed=trace.splitlines();expected=baseline.splitlines()
            prefix=0
            for actual,want in zip(observed,expected):
                if actual!=want:break
                prefix+=1
            outcomes[mode]=dict(functional_passed=False,fatal=fatals[0],
                recorded_trace_lines=len(observed),common_rtl_prefix_lines=prefix,
                first_recorded_event_difference=None if prefix==len(observed) else
                    dict(actual=observed[prefix],expected=expected[prefix] if prefix<len(expected) else None),
                termination=c['finish_records'])
            failed.append(mode)
        for n,h in {**c['inputs'],**c['artifact_sha256']}.items():artifacts[mode+'/'+n]=h
    assert m['all_functional_cases_passed']==(not failed)
    result=dict(status='passed',audit_kind='source and outcome integrity; inspect per-case functional_passed',
        manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),
        trace_parser_sha256=sha(ROOT/'scripts/audit_stage_bank_matrix_rtl_v2.py'),
        artifact_sha256=artifacts,outcomes=outcomes,functional_passed_modes=passed,functional_failed_modes=failed,
        all_functional_cases_passed=not failed,timing_qualified=False,full_system_acceptance=False,
        scope=m['scope'])
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('STAGE_BANK_FUNCTIONAL_MATRIX_AUDITED','passed',passed,'failed',failed)


if __name__=='__main__':main()
