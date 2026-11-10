#!/usr/bin/env python3
"""Audit recovered existing route, retaining conflicts and failed timing as evidence."""
import argparse,json,re,zipfile
from pathlib import Path
from datetime import datetime
from check_vitis_kernel import digest,require
from check_search_kernel_physical_mode import timing,coverage,constraints,summary,utilization,quality_gates
from check_netlist_quality import drc_status,route_status
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--status',type=Path,required=True);p.add_argument('--history',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();require(not a.output.exists(),'Refuse overwrite')
    out=ROOT/'data/derived/search_kernel_compact_route_export_recovery_20261025_v1'
    state=json.loads((out/'state.json').read_text());require(state['status']=='complete' and state['stage']=='exported_existing_route_pending_independent_quality_audit','Export not terminal')
    incident=json.loads((out/'incident.json').read_text());plan=json.loads((out/'export_plan.json').read_text());files={}
    def bind(p):files[str(p)]=digest(p)
    for group in [incident['files'],plan['files']]:
        for p,h in group.items():require(digest(p)==h,'Changed frozen evidence '+p);files[p]=h
    oldstate=json.loads((out/'failed_original_state.json').read_text());require(oldstate['status']=='failed' and oldstate['stage']=='routing','Original failure altered')
    original_log=next(Path(p) for p in incident['files'] if p.endswith('.log'));text=original_log.read_text();require('route_design completed successfully' in text and 'Designutils 20-2054' in text,'Different failure')
    observed=json.loads(a.status.read_text());status=observed['status']
    require(status['is_command_running'] is False and status['last_completed_code']==0 and status['queue_length']==0,'Export not successful idle')
    require(status['process_id']==state['owner_pid']==incident['owner_pid']==4159154,'Different resident design owner')
    require(datetime.fromisoformat(observed['observed_utc'].replace('Z','+00:00'))>=datetime.fromisoformat(state['updated_utc'].replace('Z','+00:00')),'Stale terminal observation')
    command='source {'+str(out/'export_existing.tcl')+'}';history=json.loads(a.history.read_text());entries=[e for e in history['history'] if e['command']==command]
    require(len(entries)==1 and entries[0]['code']==0 and 'COMPACT_ROUTE_EXPORT_RECOVERY_COMPLETE' in entries[0]['output'],'Exact successful export history missing')
    export=(out/'export_existing.tcl').read_text();require(not re.search(r'^\s*(?:synth_design|opt_design|place_design|phys_opt_design|route_design)\b',export,re.M),'Recovery reran design transformation')
    checkpoint=out/'routed.dcp'
    with zipfile.ZipFile(checkpoint) as z:require(z.testzip() is None,'Corrupt checkpoint archive')
    reports=out/'reports';texts={}
    for name in ['timing.rpt','check_timing.rpt','utilization.rpt','drc.rpt','methodology.rpt','timing.xdc','summary.tcllist','methodology_properties.tcllist']:
        path=reports/('routed_'+name);texts[name]=path.read_text();bind(path)
    for name in ['timing.rpt','utilization.rpt','drc.rpt','methodology.rpt']:
        require(re.search(r'\| Design\s*:\s*search_kernel_top\s*$',texts[name],re.M) is not None,'Wrong report design');require('Vivado v.2022.2' in texts[name] and 'xcu280-fsvh2892' in texts[name],'Wrong version/device')
    t=timing(texts['timing.rpt']);require(t['coverage']==coverage(texts['check_timing.rpt']),'Timing coverage inconsistent');constraints(texts['timing.xdc']);s=summary(texts['summary.tcllist'],t)
    resource=utilization(texts['utilization.rpt']);drc=drc_status(reports/'routed_drc.rpt');methodology=drc_status(reports/'routed_methodology.rpt');route=route_status(reports/'route_status.rpt');bind(reports/'route_status.rpt')
    gates=quality_gates(t,route,drc,methodology)
    for path in [checkpoint,out/'state.json',out/'incident.json',out/'export_plan.json',a.status,a.history,Path(__file__).resolve(),ROOT/'scripts/check_search_kernel_physical_mode.py',ROOT/'scripts/check_netlist_quality.py']:bind(path)
    result=dict(status='existing_compact_route_export_recovered_quality_verified' if all(gates.values()) else 'existing_compact_route_export_recovered_with_quality_failures',original_flow_status='failed_checkpoint_export',rerouted=False,timing=t,summary=s,resources=resource,route=route,drc=drc,methodology=methodology,quality_gates=gates,files=files,limits=['Recovery exports the existing design only; original failed flow remains failed','Route conflicts and negative slack remain failures even when write_checkpoint/export succeeds','Bare-device OOC only, no platform shell, complete external IO constraints, board or acceleration proof'])
    with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({k:result[k] for k in ['status','route','quality_gates']}))
if __name__=='__main__':main()
