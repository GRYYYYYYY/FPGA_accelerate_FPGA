#!/usr/bin/env python3
"""Observe the new collision-safe native RTL owner and its actual simulator phase."""
import argparse
import json
from pathlib import Path
from experiment_status_v21 import collect as previous
from experiment_status_v6 import ROOT,BASE,workflow,process


def collect(root=ROOT,base=BASE,proc_root=Path('/proc')):
    result=previous(root,base,proc_root)
    bundle=base/'collision_safe_native_rtl_v1'
    row=workflow('collision_safe_native_rtl_v1',bundle,'run_collision_safe_native_rtl_v1.py',proc_root)
    phase=row.get('stage');limits=bundle/(str(phase)+'.actual_limits.json')
    row['phase_process_verified']=False
    if limits.exists():
        recorded=json.loads(limits.read_text());live=process(recorded['pid'],proc_root)
        row['phase_process_verified']=bool(live and live['state']!='Z' and
            live['start_ticks']==recorded['start_ticks'] and live['command']==recorded['command'])
        row['phase_process_pid']=recorded['pid']
        row['phase_address_space_bytes']=recorded['address_space']
    row['scope']=dict(transactions=4,pointers=44,models=30)
    row['full_experiment_accepted']=False
    row['evidence_note']='Read-only process observation, not a functional acceptance audit.'
    result['tasks'].append(row)
    result['new_chain_note']='New native compile→full4tx RTL→original C postcheck→full44 snapshot equality; independent final RTL audit is still required. No new physical/board execution is implied.'
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--json',action='store_true')
    args=parser.parse_args();result=collect()
    if args.json:print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        for row in result['tasks']:
            if row['task'] in {'collision_safe_native_rtl_v1','collision_safe_compact_fresh_setup','collision_safe_compact_setup_supervisor'}:
                extra=f" phase_process_verified={row['phase_process_verified']}" if 'phase_process_verified' in row else ''
                print(f"{row['task']}: {row['status']} ({row.get('stage')}){extra}")
        print(result['new_chain_note'])
        print('Full experiment completion remains unproven.')
