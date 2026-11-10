"""Independent route-recovery provenance, reopened-DCP and timing audit."""
from pathlib import Path
import csv
import json
import re
import sys
from run_checkpoint_authority import ROOT, sha
from audit_state_ooc_physical_v2 import utilization, timing_summary, route_status
from parse_state_timing_paths import parse_report

def commands(path):
    return [line.strip() for line in path.read_text().splitlines() if line.strip() and not line.lstrip().startswith('#')]

def checks(path):
    result={key:int(n) for key,n in re.findall(r'^\d+\. checking (\w+) \((\d+)\)',path.read_text(),re.M)}
    assert all(key in result for key in ['no_clock','unconstrained_internal_endpoints','loops','latch_loops','no_input_delay','no_output_delay'])
    return result

def methodology(path):
    rows=re.findall(r'^\|\s*([A-Z]+-\d+)\s*\|\s*([^|]+)\|[^|]+\|\s*(\d+)\s*\|',path.read_text(),re.M)
    assert rows, path
    return {rule:dict(severity=severity.strip(),count=int(n)) for rule,severity,n in rows}

def drc(path):
    match=re.search(r'Violations found:\s*(\d+)',path.read_text())
    if match: return int(match[1])
    assert 'No DRC violations were found' in path.read_text(),path
    return 0

def main():
    p=Path(sys.argv[1]).resolve(); m=json.loads((p/'manifest.json').read_text())
    assert m['status']=='observed' and m['stage']=='complete' and m['exit_code']==0
    assert [r['stage'] for r in m['commands']]==['route','inspect'] and all(r['exit_code']==0 for r in m['commands'])
    assert sha(p/'runner.py')==m['runner_sha256']==sha(ROOT/'scripts/run_state_route_recovery_v2.py')
    assert sha(ROOT/'scripts/prepare_state_route_recovery_v2.py')==m['preparer_sha256']
    for name,digest in {**m['inputs'],**m['artifact_sha256']}.items(): assert sha(p/name)==digest,name
    for name,template,key in [('run.tcl','resume_state_route_v1.tcl','tcl_sha256'),('inspect.tcl','inspect_state_route_v1.tcl','inspect_tcl_sha256')]:
        assert sha(p/name)==m[key]
        assert sha(p/'tools'/template)==sha(ROOT/'hardware/scripts'/template)
        assert (p/name).read_text()==(p/'tools'/template).read_text().replace('@OUT@',str(p))
    prior=json.loads((p/'prior/manifest.json').read_text()); failed=Path(m['failed_attempt'])
    assert prior['status']=='failed' and prior['exit_code']==134 and prior['reference']==m['reference']
    assert sha(failed/'manifest.json')==sha(p/'prior/manifest.json')
    assert sha(failed/'placed.dcp')==m['saved_placement_sha256']==sha(p/'inputs/resume_placed.dcp')
    assert sha(failed/'run.tcl')==prior['tcl_sha256']==sha(p/'prior/run.tcl')
    assert sha(p/'routed.dcp')==m['routed_checkpoint_sha256_before_reopen']
    assert prior['parameters']==m['parameters'] and prior['rtl']==m['rtl']
    rm=json.loads((p/'inputs/synthesis_manifest.json').read_text())
    sa=json.loads((p/'inputs/synthesis_audit.json').read_text())
    sr=json.loads((p/'inputs/synthesis_restoration.json').read_text())
    fa=json.loads((p/'inputs/full_system_audit.json').read_text())
    fr=json.loads((p/'inputs/full_system_restoration.json').read_text())
    assert sa['status']==sr['status']==fa['status']==fr['status']=='passed'
    assert sr['audit_byte_identical'] and fr['audit_byte_identical'] and len(fa['exact_comparisons'])==27
    assert sa['manifest_sha256']==sha(p/'inputs/synthesis_manifest.json')
    assert sr['audit_sha256']==m['synthesis_audit_sha256']==sha(p/'inputs/synthesis_audit.json')==sha(Path(m['reference'])/'source_bound_audit.json')
    assert fr['audit_sha256']==m['full_system_audit_sha256']==sha(p/'inputs/full_system_audit.json')==sha(Path(m['full_system_reference'])/'source_bound_audit.json')
    assert rm['status']=='observed' and rm['exit_code']==0 and len(m['rtl'])==133 and m['rtl']==rm['rtl']
    assert m['part']==rm['part']=='xcu280-fsvh2892-2L-e' and m['parameters']==rm['parameters']
    assert sha(p/'inputs/synthesized.dcp')==sa['artifact_sha256']['synth.dcp']
    assert sa['check_timing_counts']['loops']==0 and not sa['timing_loop_warnings'] and not sa['critical_warnings']
    for name in m['rtl']:
        assert sha(p/'sources'/name)==rm['sources'][name]==sha(Path(m['full_system_reference'])/'sources'/name)
    runtime=json.loads((p/'inputs/runtime_audit.json').read_text()); rr=json.loads((p/'inputs/runtime_restoration.json').read_text())
    assert runtime['status']==rr['status']=='passed' and rr['audit_byte_identical']
    assert rr['audit_sha256']==m['runtime_audit_sha256']==sha(p/'inputs/runtime_audit.json')
    assert runtime['vivado_controls']['preloaded_udev']['reopened']
    assert m['runtime_library_sha256']==runtime['runtime_library_sha256']
    assert m['runtime_preload']==':'.join(m['runtime_library_sha256'])
    for name,digest in m['runtime_library_sha256'].items(): assert sha(Path(name))==digest
    maps=(p/'runtime_maps.txt').read_text(); assert 'libtcmalloc.so.4' in maps and 'libudev.so.' in maps
    assert (p/'inputs/clock.xdc').read_text()=='create_clock -name core_clk -period 10.000 [get_ports clk]\n'
    original_constraints=commands(p/'prior/constraints_input.xdc')
    assert 'create_clock -period 10.000 -name core_clk [get_ports clk]' in original_constraints
    for name in ['constraints_resume.xdc','constraints_routed.xdc','inspection/constraints.xdc']:
        assert commands(p/name)==original_constraints,(name,commands(p/name))
    for name in ['clocks_resume.rpt','clocks_routed.rpt']:
        assert re.search(r'^core_clk\s+10\.000\b',(p/name).read_text(),re.M)
    assert 'STATE_ROUTE_RECOVERY_DONE version=2022.2 part=xcu280-fsvh2892-2L-e period=10.' in (p/'completed.txt').read_text()
    for name,marker in [('stdout.log','STATE_ROUTE_RECOVERY_DONE'),('inspection/stdout.log','STATE_ROUTE_RECOVERY_REOPENED')]:
        text=(p/name).read_text(); assert marker in text and not re.search(r'^ERROR:',text,re.M)
    route=route_status(p/'route_status.rpt'); assert route==route_status(p/'inspection/route_status.rpt')
    assert route['routable nets']>0
    complete=route['routable nets']==route['fully routed nets'] and route['nets with routing errors']==0
    resources={stage:utilization(p/name) for stage,name in [
        ('input','prior/utilization_input.rpt'),('placed','prior/utilization_placed.rpt'),
        ('resume','utilization_resume.rpt'),('routed','utilization_routed.rpt'),('reopened','inspection/utilization.rpt')]}
    assert resources['placed']==resources['resume'] and resources['routed']==resources['reopened']
    assert all(resources['input'][key]==sa['utilization'][key] for key in resources['input'])
    timings={stage:timing_summary(p/name) for stage,name in [('placed','prior/timing_placed.rpt'),
        ('resume','timing_resume.rpt'),('routed','timing_routed.rpt'),('reopened','inspection/timing.rpt')]}
    assert timings['placed']==timings['resume'] and timings['routed']==timings['reopened']
    parsed={stage:parse_report((p/name).read_text(),'core_clk') for stage,name in [
        ('routed','timing_routed.rpt'),('reopened','inspection/timing.rpt')]}
    path_fields=['path_type','source','destination','slack_ns','logic_levels','data_delay_ns','logic_delay_ns','net_delay_ns','net_placement_counts']
    assert [{k:x[k] for k in path_fields} for x in parsed['routed']]==[{k:x[k] for k in path_fields} for x in parsed['reopened']]
    timing_checks={stage:checks(p/name) for stage,name in [('input','prior/check_timing_input.rpt'),
        ('routed','check_timing_routed.rpt'),('reopened','inspection/check_timing.rpt')]}
    assert timing_checks['routed']==timing_checks['reopened']
    methods={stage:methodology(p/name) for stage,name in [('input','prior/methodology_input.rpt'),
        ('routed','methodology_routed.rpt'),('reopened','inspection/methodology.rpt')]}
    assert methods['routed']==methods['reopened']
    drc_count=drc(p/'drc_routed.rpt'); assert drc_count==drc(p/'inspection/drc.rpt')
    with (p/'internal_paths.tsv').open() as handle: paths=list(csv.DictReader(handle,delimiter='\t'))
    assert len(paths)==20
    worst={}
    for dtype,kind,key,period in [('max','Setup','WNS_ns',10),('min','Hold','WHS_ns',0)]:
        selected=[x for x in paths if x['delay_type']==dtype]; assert len(selected)==10
        assert all(float(x['requirement_ns'])==period for x in selected)
        worst[dtype]=min(float(x['slack_ns']) for x in selected)
        assert worst[dtype]==timings['routed'][key]
        report_worst=min((x for x in parsed['routed'] if x['path_type']==kind),key=lambda x:x['slack_ns'])
        assert report_worst['slack_ns']==worst[dtype]
        assert any(x['startpoint']==report_worst['source'] and x['endpoint']==report_worst['destination'] and float(x['slack_ns'])==worst[dtype] for x in selected)
    critical=[line for name in ['stdout.log','inspection/stdout.log'] for line in (p/name).read_text().splitlines() if line.startswith('CRITICAL WARNING:')]
    qualified_checks=all(timing_checks['routed'][k]==0 for k in ['no_clock','unconstrained_internal_endpoints','loops','latch_loops'])
    met=(complete and drc_count==0 and qualified_checks and resources['routed']['latches']==0
         and worst['max']>=0 and worst['min']>=0 and not critical and all(n==0 for n in timings['routed']['failing_endpoints'].values()))
    result=dict(status='passed',audit_kind='route recovery and independently reopened physical artifacts, not platform acceptance',
        manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),
        parser_sha256=sha(ROOT/'scripts/parse_state_timing_paths.py'),report_parser_sha256=sha(ROOT/'scripts/audit_state_ooc_physical_v2.py'),
        failed_attempt_manifest_sha256=sha(p/'prior/manifest.json'),saved_placement_sha256=m['saved_placement_sha256'],
        synthesis_audit_sha256=m['synthesis_audit_sha256'],full_system_audit_sha256=m['full_system_audit_sha256'],
        runtime_audit_sha256=m['runtime_audit_sha256'],route=route,complete_route=complete,drc_violation_count=drc_count,
        resources=resources,timing_summaries=timings,timing_checks=timing_checks,methodology=methods,
        independent_reopened_dcp_matches=True,internal_paths=paths,sampled_internal_setup_slack_ns=worst['max'],
        sampled_internal_hold_slack_ns=worst['min'],constrained_internal_10ns_setup_hold_met=met,critical_warnings=critical,
        artifact_sha256=m['artifact_sha256'],timing_qualified=False,board_acceptance=False,full_behavior_matrix_complete=False,
        scope=m['scope'],limitations=['External I/O budgets, HD.PARTPIN_LOCS and physical clock-source location remain unspecified.',
        'Routable-net counts do not certify external port integration or board clock timing.',
        'Recovered placement; not an independent placement seed or proof of identical routing to the crashed process.',
        'No new full behavior matrix, post-route functional simulation, board result or acceleration proof.'])
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('STATE_ROUTE_RECOVERY_AUDITED',complete,timings['routed'],'internal_met',met)

if __name__=='__main__': main()
