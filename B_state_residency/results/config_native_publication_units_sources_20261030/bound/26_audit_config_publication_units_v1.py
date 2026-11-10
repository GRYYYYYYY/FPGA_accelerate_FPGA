"""Audit every recorded four-state bit, original stimulus event and actual command."""
from pathlib import Path
from decimal import Decimal
import json
import sys
from config_publication_units_common_v1 import (ROOT,TARGET,VARIANT,CASES,PAIRS,sha,read,
    identity,load,host_pair_evidence,source_evidence,commands)
from check_config_publication_bank_trace_v1 import observation as bank_observation, compare


def bank_invariants(text,native):
    result=bank_observation(text);prepared=0;mismatches=0
    for line in text.splitlines():
        state=line.split()[3]
        # MSB-first concatenation:105 control bits,2304 descriptor bits,
        # prepared,2304 shadow bits,64 shadow-design and32 shadow-checkpoint.
        if state[2409]=='1':
            prepared+=1;assert state[:3]=='000' and state[3]=='1'
            descriptor,shadow=state[105:2409],state[2410:4714]
            equal=descriptor[:32]+descriptor[64:]==shadow[:32]+shadow[64:]
            if not equal:mismatches+=1
    assert prepared>0 and result['x_bit_observations']>0 and result['z_bit_observations']>0
    if native:assert mismatches==0,'Native prepared non-version bank mismatch'
    else:assert mismatches>0,'Generic unaliased X/Z counterexample was not observed'
    result.update(prepared_edges=prepared,nonversion_mismatch_edges=mismatches)
    return result


def time_ns(text):
    value,unit=text.split();return Decimal(value)*{'ps':Decimal('.001'),'ns':Decimal(1),'us':Decimal(1000)}[unit]


def main():
    p=Path(sys.argv[1]).resolve();assert p==TARGET
    m=read(p/'manifest.json');assert m['status']=='observed' and m['stage']=='complete' and not m.get('active_process')
    assert identity(m['runner_pid'])!=str(m['runner_start_ticks'])
    assert m['runner_sha256']==sha(ROOT/'scripts/run_config_publication_units_v1.py')
    assert m['predecessors']==host_pair_evidence()
    prep,references,files=source_evidence();assert m['references']==references and set(m['cases'])==set(CASES)
    expected={str(f) for f in files+list(map(Path,m['predecessors']))}
    assert {e['source'] for e in m['bound'].values()}==expected
    for name,e in m['bound'].items():assert sha(e['source'])==e['sha256']==sha(p/'bound'/name)
    parsers={'generic':load('publication_generic_observation',ROOT/'scripts/audit_config_publication_probe_v1.py'),
             'native':load('publication_native_observation',ROOT/'scripts/audit_config_native_feedback_probe_v1.py')}
    results={}
    for name in CASES:
        d=p/name;c=m['cases'][name];kind,mode=name.split('_',1);original=Path(references[kind]['root'])
        assert c['status']=='observed' and c['top']==prep['cases'][name]['top'] and c['parameter']==prep['cases'][name]['parameter']
        role='baseline' if mode=='original' else 'fixed'
        assert sha(d/'config_restore_controller.sv')==c['dut_sha256']==sha(VARIANT/role/'config_restore_controller.sv')
        assert sha(d/'tb.sv')==c['tb_sha256']==prep['cases'][name]['testbench_sha256']
        assert (d/'run.tcl').read_text()=='run 100us\nquit\n' and sha(d/'run.tcl')==c['run_tcl_sha256']
        admission=c['memory_admission'];assert admission['stable_seconds']>=60 and admission['current_bytes']*4<=admission['limit_bytes']*3
        expected_commands=commands(d,c['top']);assert len(c['commands'])==3
        for actual,(stage,argv) in zip(c['commands'],expected_commands):
            assert actual['stage']==stage and actual['argv']==argv and actual['exit_code']==0
            if actual['start_ticks'] is not None:assert identity(actual['pid'])!=str(actual['start_ticks'])
            stdout=d/(stage+'.stdout.log');assert sha(stdout)==actual['stdout_sha256']
            text=stdout.read_text();assert 'ERROR:' not in text and 'FATAL_ERROR:' not in text
            assert ('[VRFC ' in text) if stage=='compile' else ('2022.2' in text)
        assert set(c['artifacts'])=={'events.txt','bank_trace.txt','simulate.log'}
        for file,h in c['artifacts'].items():assert sha(d/file)==h
        events,log=(d/'events.txt').read_text(),(d/'simulate.log').read_text()
        parsed=parsers[kind].observation(events,log)
        golden=parsers[kind].observation((original/'events.txt').read_text(),(original/'simulate.log').read_text())
        assert parsed==golden and (d/'events.txt').read_bytes()==(original/'events.txt').read_bytes()
        bank=bank_invariants((d/'bank_trace.txt').read_text(),kind=='native')
        expected_edges=int((time_ns(parsed['finish_time'])-Decimal('5.1'))//10)+1
        assert bank['edges']==expected_edges
        if kind=='native':assert bank['prepared_edges']==parsed['prepared_checks']
        results[name]=dict(observation=parsed,bank=bank,events_sha256=sha(d/'events.txt'),
            original_events_sha256=sha(original/'events.txt'),dut_sha256=c['dut_sha256'],tb_sha256=c['tb_sha256'])
    comparisons=[]
    for reference,candidate in PAIRS:
        bank=compare((p/reference/'bank_trace.txt').read_text(),(p/candidate/'bank_trace.txt').read_text())
        assert (p/reference/'events.txt').read_bytes()==(p/candidate/'events.txt').read_bytes()
        assert results[reference]['observation']==results[candidate]['observation']
        comparisons.append(dict(reference=reference,candidate=candidate,bank=bank,
            events_sha256=sha(p/reference/'events.txt'),finish_time=results[reference]['observation']['finish_time']))
    result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),
        bank_parser_sha256=sha(ROOT/'scripts/check_config_publication_bank_trace_v1.py'),
        cases=results,comparisons=comparisons,full_bank_cycle_comparisons=3,exact_event_comparisons=3,
        state_bits=4810,output_bits=7238,native_prepared_full_nonversion_invariant=True,
        generic_default_preserves_unaliased_xz_counterexample=True,
        candidate_manifest_sha256=sha(VARIANT/'manifest.json'),predecessors=m['predecessors'],
        timing_qualified=False,board_acceptance=False,
        scope='Five isolated original/default/native-enabled modes with exact entire binary state/output/event/finish comparison,0/1/X/Z and actual native alias monitors. Not arbitrary formal equivalence, full-system acceptance or measured timing benefit; actual archive/restore still required.')
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PUBLICATION_UNITS_AUDITED',len(results),'cases',len(comparisons),'complete bit/cycle/event comparisons')


if __name__=='__main__':main()
