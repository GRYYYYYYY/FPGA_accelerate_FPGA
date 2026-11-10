"""Audit the isolated post-route experiment against the frozen negative baseline."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import re
from check_vitis_kernel import digest,require
from check_search_kernel_physical import timing,coverage,constraints,utilization,summary,quality_gates
from check_netlist_quality import route_status,drc_status


def utc(value):
    return datetime.fromisoformat(re.sub(r'(\.\d{6})\d+(?=Z|[+-])',r'\1',value).replace('Z','+00:00'))


def terminal(plan,state,snapshot,history,bundle):
    s=snapshot['status'];require(snapshot['session_id']==plan['session_id'],'Wrong session')
    require(state['status']=='complete' and state['stage']=='physopt_complete_pending_independent_audit','Experiment incomplete')
    require(s.get('is_command_running') is False and s.get('last_completed_code')==0 and s.get('queue_length')==0,'Flow not successfully idle')
    require(s['process_id']==state['owner_pid']==plan['owner_pid'],'Owner mismatch')
    require(Path(s['working_dir']).resolve()==bundle and utc(snapshot['observed_utc'])>=utc(state['updated_utc']),'Wrong/stale terminal observation')
    prefix=s['last_completed'];prefix=prefix[:-3] if prefix.endswith('...') else prefix
    require(len(prefix)>20 and plan['source_command'].startswith(prefix),'Wrong completed source prefix')
    entries=[x for x in history['history'] if x['command']==plan['source_command']]
    require(len(entries)==1 and entries[0]['code']==0,'Missing successful exact source history')
    e=entries[0]
    require(utc(e['timestamp'])>=utc(state['updated_utc']) and abs(e['elapsed']-s['last_completed_elapsed'])<0.01,'History/state mismatch')
    require(len(re.findall(r'^CSR_PHYSOPT_FLOW_COMPLETE[ \t]*$',e['output'],re.M))==1,'Missing completion marker')


def audit(bundle,snapshot_path,history_path,output):
    require(not output.exists(),'Existing optimization audit')
    plan_path=bundle/'plan.json';plan=json.loads(plan_path.read_text());state_path=bundle/'state.json';state=json.loads(state_path.read_text())
    snapshot=json.loads(snapshot_path.read_text());history=json.loads(history_path.read_text())
    terminal(plan,state,snapshot,history,bundle)
    require(plan['clock_ns']==5 and plan['setup_uncertainty_ns']==1.35 and plan['part']=='xcu280-fsvh2892-2L-e' and plan['vivado_version']=='2022.2','Wrong target')
    require(plan['strategy']==['resume_verified_optimized_checkpoint','route_design -directive Explore -tns_cleanup'],'Different optimization experiment')
    files=dict(plan['files'])
    for path,h in files.items():require(digest(path)==h,'Changed experiment input '+path)
    baseline_path=next(Path(p) for p in files if Path(p).name=='search_kernel_physical_csr_audit_20261024_v1.json')
    baseline=json.loads(baseline_path.read_text());require(baseline['selected_mode']=='csr','Wrong baseline')
    for path,h in baseline['files'].items():require(digest(path)==h,'Changed frozen baseline '+path)
    original=baseline['modes']['csr'];before=timing(Path(plan['baseline_timing_report']).read_text())
    constraints(Path(plan['baseline_xdc']).read_text())
    resume_input=timing((bundle/'reports/resume_input_timing.rpt').read_text())
    constraints((bundle/'reports/resume_input_timing.xdc').read_text())
    for kind in ['setup','hold','pulse_width']:
        expected=original['stages']['routed']['timing'][kind];actual=before[kind]
        require(abs(actual['slack_ns']-expected['slack_ns'])<=0.0011 and actual['failing_endpoints']==expected['failing_endpoints'] and actual['total_endpoints']==expected['total_endpoints'],'Reopened baseline differs '+kind)
    reports=bundle/'reports';after=timing((reports/'routed_timing.rpt').read_text())
    require(after['coverage']==coverage((reports/'routed_check_timing.rpt').read_text()),'Coverage mismatch')
    constraints((reports/'routed_timing.xdc').read_text());tool_summary=summary((reports/'routed_summary.tcllist').read_text(),after)
    resources=utilization((reports/'routed_utilization.rpt').read_text());routed=route_status(reports/'route_status.rpt')
    drc=drc_status(reports/'routed_drc.rpt');method=drc_status(reports/'routed_methodology.rpt');gates=quality_gates(after,routed,drc,method)
    log_path=Path(snapshot['status']['log_file']);log=log_path.read_text(errors='replace')
    require(plan['source_command'] in log and len(re.findall(r'^CSR_PHYSOPT_FLOW_COMPLETE[ \t]*$',log,re.M))==1,'Session log does not bind completed source')
    run=log[log.index('CSR_PHYSOPT_STAGE csr running prepare'):];require(not re.search(r'^ERROR:',run,re.M),'Flow error in log')
    for path in [plan_path,state_path,snapshot_path,history_path,log_path,Path(__file__).resolve(),Path(__file__).parent/'check_search_kernel_physical.py',Path(__file__).parent/'check_netlist_quality.py',Path(__file__).parent/'check_vitis_kernel.py',*reports.iterdir(),bundle/'optimized_routed.dcp']:
        require(path.is_file() and path.stat().st_size>0,'Missing artifact '+str(path));files[str(path)]=digest(path)
    passed=all(gates.values());old=original['stages']['routed']['resources']
    result=dict(status='csr_postroute_recovery_all_quality_gates_verified' if passed else 'csr_postroute_recovery_completed_quality_gates_not_met',all_quality_gates_pass=passed,
                files=files,baseline_audit_sha256=digest(baseline_path),before=before,resume_input=resume_input,after=after,quality_gates=gates,route=routed,drc=drc,methodology=method,
                setup_slack_improvement_ns=after['setup']['slack_ns']-before['setup']['slack_ns'],resources=resources,resource_delta={k:resources[k]-old[k] for k in resources},tool_summary=tool_summary,
                full_two_mode_physical_complete=False,platform_timing_verified=False,functional_netlist_equivalence_proven=False,board_verified=False,limitations=plan['limitations'])
    with output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(result['status'],result['setup_slack_improvement_ns']);return 0 if passed else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--session-status',type=Path,required=True);p.add_argument('--history',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();raise SystemExit(audit(a.bundle.resolve(),a.session_status.resolve(),a.history.resolve(),a.output.resolve()))
