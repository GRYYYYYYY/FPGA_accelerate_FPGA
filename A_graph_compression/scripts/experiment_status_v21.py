#!/usr/bin/env python3
"""Observe the single new-HLS audit/setup owner without treating preparation as RTL."""
import argparse
import json
from pathlib import Path
from experiment_status_v20 import collect as previous
from experiment_status_v6 import ROOT,BASE,workflow


def collect(root=ROOT,base=BASE,proc_root=Path('/proc')):
    result=previous(root,base,proc_root)
    for label,folder,script in [
        ('collision_safe_compact_setup_supervisor',root/'data/derived/collision_safe_compact_setup_supervision_20261030_v1',
         'supervise_collision_safe_compact_setup_v1.py'),
        ('collision_safe_compact_fresh_setup',base/'collision_safe_compact_cosim_setup_v1',
         'prepare_collision_safe_compact_cosim_v1.py')]:
        row=workflow(label,folder,script,proc_root)
        if row['owner_verified'] and str(row.get('stage','')).startswith('waiting_'):
            row['status']='waiting_hls_dependency_only'
        row['rtl_executed']=False
        row['evidence_note']='Live local audit/setup workflow only. No RTL or physical job is launched by these entries.'
        result['tasks'].append(row)
    result['new_chain_note']='One new local owner waits for the current HLS, then runs the independent9-connection/interface audit and fresh full44 C/RTL setup. It stops on any failure; it does not launch RTL or physical.'
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--json',action='store_true')
    args=parser.parse_args();result=collect()
    if args.json:print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        for row in result['tasks']:
            if row['task'].startswith('collision_safe_'):
                print(f"{row['task']}: {row['status']} ({row.get('stage')})")
        print(result['new_chain_note'])
        print('Full experiment completion remains unproven.')
