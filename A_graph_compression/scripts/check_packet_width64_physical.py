#!/usr/bin/env python3
"""Independently audit width64 OOC evidence and compare the frozen CSR baseline."""
import argparse,json,re
from datetime import datetime,timezone
from pathlib import Path
from check_vitis_kernel import digest,require
from check_search_kernel_physical_mode import timing,coverage,constraints,summary,utilization,quality_gates
from check_netlist_quality import drc_status,route_status
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--status',type=Path,required=True,help='Saved {observed_utc,status: raw MCP status}')
    parser.add_argument('--history',type=Path,required=True,help='Saved raw MCP command history JSON')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();require(not args.output.exists(),'Refuse overwrite')
    bundle=ROOT/'data/derived/search_packet_width64_physical_20261025_v1';work=bundle/'csr'
    state=json.loads((work/'state.json').read_text())
    require(state['status']=='complete' and state['stage']=='ooc_complete_pending_independent_audit','Physical run not complete')
    plan=json.loads((bundle/'plan.json').read_text());session=json.loads((bundle/'session.json').read_text())
    observation=json.loads(args.status.read_text());status=observation['status']
    require(status['is_command_running'] is False and status['last_completed_code']==0 and status['queue_length']==0,'No successful terminal MCP observation')
    require(status['process_id']==state['owner_pid']==session['pid'],'Owner changed')
    require(Path(status['working_dir']).resolve()==work.resolve(),'Wrong working directory')
    completed=datetime.fromisoformat(state['updated_utc'].replace('Z','+00:00'))
    require(datetime.fromisoformat(observation['observed_utc'].replace('Z','+00:00'))>=completed,'Stale observation')
    command='source {'+str(work/'run_flow.tcl')+'}'
    history=json.loads(args.history.read_text());entries=[e for e in history['history'] if e['command']==command]
    require(len(entries)==1 and entries[0]['code']==0,'Missing exact successful source history')
    require('SEARCH_PHYSICAL_FLOW_COMPLETE' in entries[0]['output'],'Missing history completion')
    files={}
    def bind(p):files[str(p)]=digest(p)
    for group in ['inputs','generated']:
        for p,h in plan[group].items():require(digest(p)==h,'Changed frozen input '+p);files[p]=h
    baseline_dir=ROOT/'data/derived/search_kernel_physical_20261024_v1/csr'
    for name in ['run_flow.tcl','clock.xdc']:
        require(digest(work/name)==digest(baseline_dir/name),'Different baseline flow/constraints');bind(baseline_dir/name)
    log=Path(status['log_file']);text=log.read_text(errors='replace')
    require(command in text and len(re.findall(r'^SEARCH_PHYSICAL_FLOW_COMPLETE\s*$',text,re.M))==1,'Missing/duplicate complete flow')
    segment=text[text.index('SEARCH_PHYSICAL_STAGE csr running prepare'):]
    require(not re.search(r'^ERROR:',segment,re.M),'Flow error present')
    require('Got license for feature' in segment and "device 'xcu280'" in segment,'Device synthesis checkout absent')
    for p in [bundle/'plan.json',bundle/'session.json',bundle/'start_raw.json',work/'state.json',log,args.status,args.history,Path(__file__).resolve(),ROOT/'scripts/check_search_kernel_physical_mode.py',ROOT/'scripts/check_netlist_quality.py']:bind(p)
    require(not (work/'error.txt').exists(),'Flow error receipt exists')
    for name in ['synthesized.dcp','placed.dcp','routed.dcp']:
        p=work/name;require(p.stat().st_size>0,'Missing checkpoint');bind(p)
    stages={};reports=work/'reports'
    for stage in ['synthesis','routed']:
        paths={name:reports/(stage+'_'+name) for name in ['timing.rpt','check_timing.rpt','utilization.rpt','drc.rpt','methodology.rpt','timing.xdc','summary.tcllist','methodology_properties.tcllist']}
        texts={name:p.read_text() for name,p in paths.items()}
        for p in paths.values():bind(p)
        for name in ['timing.rpt','utilization.rpt','drc.rpt','methodology.rpt']:
            require(re.search(r'\| Design\s*:\s*search_kernel_top\s*$',texts[name],re.M) is not None,'Different report design')
            require('Vivado v.2022.2' in texts[name] and 'xcu280-fsvh2892' in texts[name],'Different tool/device')
        t=timing(texts['timing.rpt']);require(t['coverage']==coverage(texts['check_timing.rpt']),'Coverage disagrees');constraints(texts['timing.xdc'])
        stages[stage]=dict(timing=t,resources=utilization(texts['utilization.rpt']),summary=summary(texts['summary.tcllist'],t),drc=drc_status(paths['drc.rpt']),methodology=drc_status(paths['methodology.rpt']))
    require(re.search(r'\| Design State\s*:\s*(?:Fully )?Routed\s*$',texts['utilization.rpt'],re.M) is not None,'Not post-route utilization')
    routefile=reports/'route_status.rpt';bind(routefile);route=route_status(routefile)
    current=stages['routed'];gates=quality_gates(current['timing'],route,current['drc'],current['methodology'])
    baseline_path=ROOT/'results/search_kernel_physical_csr_audit_20261024_v1.json';baseline=json.loads(baseline_path.read_text());bind(baseline_path)
    old=baseline['modes']['csr']['stages']['routed']
    delta={k:current['resources'][k]-v for k,v in old['resources'].items()}
    report=dict(status='width64_ooc_complete_all_quality_gates_verified' if all(gates.values()) else 'width64_ooc_complete_with_quality_failures_or_review_required',stages=stages,route=route,quality_gates=gates,resource_delta_from_baseline=delta,setup_slack_delta_ns=current['timing']['setup']['slack_ns']-old['timing']['setup']['slack_ns'],files=files,created_utc=datetime.now(timezone.utc).isoformat(),limits=['OOC whole device, no platform shell; external IO timing incomplete','No implicit DRC/methodology waivers','Two synthetic CSR functional transactions proven separately; no full real workload/compact/integrated-batch RTL or board claim'])
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'])
if __name__=='__main__':main()
