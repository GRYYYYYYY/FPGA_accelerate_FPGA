#!/usr/bin/env python3
"""Compare complete route status, DRC and constrained internal timing to baseline."""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'adapters'),str(ROOT/'src')]
from import_vivado import sha256
from real_experiment import write_new


def route_status(path):
    text=path.read_text()
    labels=['logical nets','routable nets','fully routed nets','nets with routing errors']
    result={}
    for label in labels:
        matches=re.findall(r'# of '+re.escape(label)+r'\.+\s*:\s*(\d+)\s*:',text)
        if len(matches)!=1:raise ValueError('Missing/ambiguous route status: '+label)
        result[label]=int(matches[0])
    return result


def drc_status(path):
    text=path.read_text()
    total=int(re.search(r'Violations found:\s*(\d+)',text)[1])
    issues={}
    for line in text.splitlines():
        columns=[s.strip() for s in line.split('|')]
        if len(columns)==7 and re.fullmatch(r'[A-Z][A-Z0-9_]*-\d+',columns[1]) and columns[4].isdigit():
            issues[columns[1]]={'severity':columns[2],'count':int(columns[4])}
        elif len(columns)==6 and re.fullmatch(r'[A-Z][A-Z0-9_]*-\d+',columns[1]) and columns[4].isdigit():
            issues[columns[1]]={'severity':columns[2],'count':int(columns[4])}
    if sum(v['count'] for v in issues.values())!=total:raise ValueError('DRC detail counts differ')
    return {'total':total,'issues':issues}


def timing_status(path):
    text=path.read_text()
    match=re.search(r'WNS\(ns\).*\n\s*[- ]+\n\s*([0-9.\-]+)\s+([0-9.\-]+)\s+(\d+)\s+(\d+)\s+([0-9.\-]+)\s+([0-9.\-]+)\s+(\d+)\s+(\d+)',text)
    if not match:raise ValueError('No final timing table')
    keys=['WNS','TNS','setup_failing_endpoints','setup_total_endpoints','WHS','THS','hold_failing_endpoints','hold_total_endpoints']
    result={k:(int(v) if 'endpoints' in k else float(v)) for k,v in zip(keys,match.groups())}
    for name in ['no_clock','unconstrained_internal_endpoints','no_input_delay','no_output_delay']:
        value=re.search(r'checking '+name+r' \((\d+)\)',text)
        if not value:raise ValueError('Missing constraint coverage check: '+name)
        result[name]=int(value[1])
    result['constrained_internal_timing_met']=result['WNS']>=0 and result['WHS']>=0 and not result['setup_failing_endpoints'] and not result['hold_failing_endpoints']
    return result


def compare_quality(baseline, candidate):
    before,after=baseline['route'],candidate['route']
    complete=after['fully routed nets']==after['routable nets'] and after['nets with routing errors']==0
    unchanged_net_counts=before['logical nets']==after['logical nets'] and before['routable nets']==after['routable nets']
    new_issues={}
    for rule,issue in candidate['drc']['issues'].items():
        old=baseline['drc']['issues'].get(rule,{'count':0,'severity':issue['severity']})
        if issue['count']>old['count'] or issue['severity']!=old['severity']:
            new_issues[rule]=issue
    coverage_keys=['no_clock','unconstrained_internal_endpoints','no_input_delay','no_output_delay','setup_total_endpoints','hold_total_endpoints']
    coverage_same=all(baseline['timing'][key]==candidate['timing'][key] for key in coverage_keys)
    return {'all_routable_nets_complete_without_errors':complete,'logical_and_routable_net_counts_unchanged':unchanged_net_counts,
            'new_or_increased_drc_issues':new_issues,'timing_constraint_coverage_unchanged':coverage_same,
            'constrained_internal_timing_met':candidate['timing']['constrained_internal_timing_met'],
            'WNS_change_ns':candidate['timing']['WNS']-baseline['timing']['WNS'],
            'WHS_change_ns':candidate['timing']['WHS']-baseline['timing']['WHS'],
            'quality_gates_pass':complete and unchanged_net_counts and not new_issues and coverage_same and candidate['timing']['constrained_internal_timing_met']}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('candidate',type=Path)
    args=p.parse_args()
    baseline=ROOT/'data/netlist/routeracc_cost_u280_20261022_v1'
    def load(directory,drc):
        return {'route':route_status(directory/'route_status.rpt'),'drc':drc_status(drc),
                'timing':timing_status(directory/'timing_summary.rpt')}
    before=load(baseline,ROOT/'results/netlist_baseline_drc_20261022.rpt')
    after=load(args.candidate,args.candidate/'drc.rpt')
    report={'baseline':before,'candidate':after,'comparison':compare_quality(before,after),
            'scope':'OOC routing workload, constrained internal paths only; external IO delays remain unconstrained.'}
    paths=[args.candidate/name for name in ['route_status.rpt','drc.rpt','timing_summary.rpt']]
    report['candidate_report_sha256']={p.name:sha256(p) for p in paths}
    write_new(args.candidate/'quality_check.json',report)
    print(json.dumps(report,indent=2))
    return 0 if report['comparison']['quality_gates_pass'] else 1


if __name__=='__main__':raise SystemExit(main())
