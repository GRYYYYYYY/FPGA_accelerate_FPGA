#!/usr/bin/env python3
"""Independently audit isolated packet64 post-route optimization artifacts."""
import argparse
import json
import os
import re
import zipfile
from pathlib import Path
from check_vitis_kernel import digest, require
from check_search_csr_physopt import utc
from check_search_kernel_physical_mode import timing, coverage, constraints, utilization, summary, quality_gates
from check_netlist_quality import route_status, drc_status

ROOT=Path(__file__).resolve().parents[1]

def active_constraints(text):
    return sorted(line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith('#'))

def audit(bundle, observation_path, history_path, output):
    require(not output.exists(), 'Refuse overwrite')
    plan=json.loads((bundle/'plan.json').read_text())
    state=json.loads((bundle/'state.json').read_text())
    observation=json.loads(observation_path.read_text()); status=observation['status']
    require(state['status']=='complete' and state['stage']=='physopt_complete_pending_independent_audit', 'Flow incomplete')
    require(status['is_command_running'] is False and status['last_completed_code']==0 and status['queue_length']==0, 'No successful idle terminal')
    require(status['process_id']==state['owner_pid'], 'Wrong owner')
    require(Path(status['working_dir']).resolve()==bundle, 'Wrong working directory')
    require(utc(observation['observed_utc'])>=utc(state['updated_utc']), 'Stale terminal')
    command='source {'+str(bundle/'run_flow.tcl')+'}'
    prefix=status.get('last_completed',''); prefix=prefix[:-3] if prefix.endswith('...') else prefix
    require(len(prefix)>20 and command.startswith(prefix), 'Wrong completed source')
    entries=[x for x in json.loads(history_path.read_text())['history'] if x['command']==command]
    require(len(entries)==1 and entries[0]['code']==0, 'Missing unique successful source history')
    entry=entries[0]
    require(utc(entry['timestamp'])>=utc(state['updated_utc']) and abs(entry['elapsed']-status['last_completed_elapsed'])<.01, 'History/terminal mismatch')
    truncated=entry['output'].endswith('... [Output truncated. Full output in vivado.log]')
    marker=r'^PACKET64_PHYSOPT_FLOW_COMPLETE[ \t]*$'
    require(len(re.findall(marker,entry['output'],re.M))==1 or truncated, 'No history completion or explicit truncation')
    files=dict(plan['files'])
    for p,h in files.items(): require(digest(p)==h, 'Changed frozen input '+p)
    require(plan['part']=='xcu280-fsvh2892-2L-e' and plan['clock_period_ns']==5, 'Wrong target')
    require(plan['operations']==['phys_opt_design -directive AggressiveFanoutOpt','route_design -directive Explore -tns_cleanup'], 'Unexpected strategy')
    baseline_path=ROOT/'results/search_packet_width64_physical_audit_20261025_v2.json'
    baseline=json.loads(baseline_path.read_text())
    old=baseline['stages']['routed']
    reports=bundle/'reports'
    before=timing((reports/'before_timing.rpt').read_text())
    for key in ['setup','hold','pulse_width']:
        a=before[key]; b=old['timing'][key]
        require(abs(a['slack_ns']-b['slack_ns'])<=.0011 and a['failing_endpoints']==b['failing_endpoints'] and a['total_endpoints']==b['total_endpoints'], 'Reopened timing differs '+key)
    baseline_xdc=ROOT/'data/derived/search_packet_width64_physical_20261025_v1/csr/reports/routed_timing.xdc'
    require(digest(baseline_xdc)==baseline['files'][str(baseline_xdc)], 'Changed original constraints')
    for name in ['before_timing.xdc','routed_timing.xdc']:
        written=(reports/name).read_text(); constraints(written)
        require(active_constraints(written)==active_constraints(baseline_xdc.read_text()), 'Changed active constraints '+name)
    after=timing((reports/'routed_timing.rpt').read_text())
    require(after['coverage']==coverage((reports/'routed_check_timing.rpt').read_text()), 'Coverage mismatch')
    resources=utilization((reports/'routed_utilization.rpt').read_text())
    tool_summary=summary((reports/'routed_summary.tcllist').read_text(),after)
    for name in ['timing','utilization','drc','methodology']:
        text=(reports/('routed_'+name+'.rpt')).read_text()
        require(re.search(r'\| Design\s*:\s*search_kernel_top\s*$',text,re.M) is not None and 'Vivado v.2022.2' in text and 'xcu280-fsvh2892' in text, 'Wrong report design/tool/device')
    route=route_status(reports/'route_status.rpt')
    drc=drc_status(reports/'routed_drc.rpt'); method=drc_status(reports/'routed_methodology.rpt')
    gates=quality_gates(after,route,drc,method)
    log_path=Path(status['log_file']); log=log_path.read_text(errors='replace')
    require(command in log and len(re.findall(marker,log,re.M))==1, 'Missing unique log completion')
    segment=log[log.index('PACKET64_PHYSOPT_STAGE csr running prepare'):]
    require(not re.search(r'^ERROR:',segment,re.M) and not (bundle/'error.txt').exists(), 'Flow error present')
    for name in ['baseline_routed.dcp','optimized.dcp','optimized_routed.dcp']:
        with zipfile.ZipFile(bundle/name) as z: require(z.testzip() is None, 'Corrupt checkpoint '+name)
    paths=[baseline_xdc,bundle/'plan.json',bundle/'state.json',observation_path,history_path,log_path,Path(__file__).resolve(),
           ROOT/'scripts/check_search_csr_physopt.py',ROOT/'scripts/check_search_kernel_physical_mode.py',
           ROOT/'scripts/check_netlist_quality.py',ROOT/'scripts/check_vitis_kernel.py',
           *reports.iterdir(),bundle/'optimized.dcp',bundle/'optimized_routed.dcp']
    for p in paths:
        require(p.is_file() and p.stat().st_size>0,'Missing artifact '+str(p)); files[str(p)]=digest(p)
    passed=all(gates.values())
    result=dict(status='packet64_physopt_all_quality_gates_verified' if passed else 'packet64_physopt_complete_quality_gates_not_met',
                before=before,after=after,resources=resources,route=route,drc=drc,methodology=method,
                quality_gates=gates,setup_slack_improvement_ns=after['setup']['slack_ns']-before['setup']['slack_ns'],
                resource_delta={k:resources[k]-old['resources'][k] for k in resources},tool_summary=tool_summary,
                history_output_truncated=truncated,files=files,
                limitations=['OOC without platform shell; external timing incomplete',
                             'No functional netlist equivalence or board verification inferred from physical reports',
                             'No DRC or methodology waivers'])
    temporary=output.with_suffix(output.suffix+'.tmp')
    with temporary.open('x') as f:
        json.dump(result,f,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.replace(temporary,output)
    print(result['status']); return 0 if passed else 1

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['bundle','session-status','history','output']:p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args()
    raise SystemExit(audit(a.bundle.resolve(),a.session_status.resolve(),a.history.resolve(),a.output.resolve()))
