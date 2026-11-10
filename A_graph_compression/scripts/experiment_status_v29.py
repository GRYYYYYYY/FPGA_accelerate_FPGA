#!/usr/bin/env python3
"""Read-only status separating process activity, last simulation progress and acceptance."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import time

from experiment_status_v28 import collect as previous
from experiment_status_v6 import ROOT, BASE, process
from owned_sim_resource_policy_v1 import observe, abort_reason


def native_health(base=BASE):
    folder = base/'collision_safe_native_owner_recovery_v2'
    row = dict(identity_verified=False, functional_acceptance_inferred=False)
    try:
        recorded = json.loads((folder/'rtl.actual_limits.json').read_text())
        actual = process(recorded['pid'])
        row['identity_verified'] = bool(actual and actual['state'] != 'Z'
            and actual['start_ticks'] == str(recorded['start_ticks'])
            and actual['command'] == recorded['command'])
        if row['identity_verified']:
            proc = Path('/proc')/str(recorded['pid'])
            stat = (proc/'stat').read_text().rsplit(')',1)[1].split()
            if stat[19] != str(recorded['start_ticks']):
                raise ValueError('Process identity changed during observation')
            ticks = os.sysconf('SC_CLK_TCK')
            elapsed = float(Path('/proc/uptime').read_text().split()[0])-int(stat[19])/ticks
            cpu = (int(stat[11])+int(stat[12]))/ticks
            row.update(pid=recorded['pid'], elapsed_hours=elapsed/3600,
                       cpu_hours=cpu/3600, lifetime_cpu_percent=100*cpu/elapsed)
            status = (proc/'status').read_text()
            rss = re.search(r'^VmRSS:\s+(\d+) kB$',status,re.M)
            row['rss_gib'] = int(rss[1])/1024**2 if rss else None
        log = folder/'rtl.log'
        content = log.read_text(errors='replace')
        progress = re.findall(r'RTL Simulation\s*:\s*(\d+)\s*/\s*(\d+).*?@\s*"(\d+)"',content)
        if progress:
            done,total,ps = map(int,progress[-1])
            row.update(last_logged_completed=done, total_transactions=total,
                       last_logged_simulation_ms=ps/1e9)
        row['log_file_age_hours'] = (time.time()-log.stat().st_mtime)/3600
        row['rtl_receipt_exists'] = (folder/'rtl.receipt.json').is_file()
        row['output_snapshot_files'] = len(list(folder.glob('rtl_*.bin')))
        initial = json.loads((folder/'plan.json').read_text())['initial_memory']
        current = observe()
        row['resource_abort_reason_since_start'] = abort_reason(initial,current)
        row['memory_events'] = current['events']
        row['memory_pressure'] = current['pressure']
        row['cpu_pressure'] = Path('/sys/fs/cgroup/cpu.pressure').read_text()
    except (OSError,ValueError,KeyError,TypeError,IndexError) as exc:
        row['observation_error'] = str(exc)
    row['note'] = ('CPU activity is not simulation progress. Last logged time is not the '
                   'current internal simulation time. Output files and exit receipts alone '
                   'do not grant acceptance; the independent checker is required.')
    return row


def cycle_context(root=ROOT):
    path = root/'results/native_trace_cycle_floor_20261102_v1.json'
    row = dict(report=str(path), bindings_verified=False, functional_acceptance=False)
    try:
        raw = path.read_bytes()
        # Bind this interpretation to the reviewed report, not arbitrary JSON numbers.
        if hashlib.sha256(raw).hexdigest() != '8409c863f1a56e9da7040264de6d821641a9acb3980c144b04af44f5a7ebb4af':
            raise ValueError('Cycle-floor report changed')
        report = json.loads(raw)
        for name, checksum in report['files'].items():
            if hashlib.sha256(Path(name).read_bytes()).hexdigest() != checksum:
                raise ValueError('Cycle-floor source changed: '+name)
        row.update(bindings_verified=True,
                   success_path_floor_ms=report['reset_plus_trace_ms_floor'],
                   assumptions=report['assumptions'],exclusions=report['exclusions'])
    except (OSError,ValueError,KeyError,TypeError) as exc:
        row['observation_error'] = str(exc)
    return row


def collect(root=ROOT,base=BASE):
    result = previous(root,base)
    result['native_health'] = native_health(base)
    result['native_cycle_context'] = cycle_context(root)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json',action='store_true')
    args=parser.parse_args();result=collect()
    if args.json:
        print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        h=result['native_health'];c=result['native_cycle_context']
        for label,keys in [
            ('Native process',('pid','identity_verified','elapsed_hours','cpu_hours','rss_gib')),
            ('Last recorded progress',('last_logged_completed','total_transactions',
                                      'last_logged_simulation_ms','log_file_age_hours')),
            ('Outputs/resources',('rtl_receipt_exists','output_snapshot_files',
                                  'resource_abort_reason_since_start','observation_error'))]:
            print(label+': '+', '.join(f'{k}={h[k]:.3f}' if isinstance(h[k],float)
                                      else f'{k}={h[k]}' for k in keys if k in h))
        print('Conditional static cycle floor: '+json.dumps({k:c[k] for k in
              ('bindings_verified','success_path_floor_ms','observation_error') if k in c}))
        print(h['note'])
        print('Static floor applies to the reference first-call success path; it is not measured latency or a live-state observation.')
        current={'native_directory_recovery_supervisor_v2','native_directory_recovery_RTL_v2',
                 'bus64_pair_execution_v2','bus64_audit_recovery_supervisor_v3',
                 'bus64_full_rtl_supervisor_v3','route_tree_recovery_supervisor_v3',
                 'snapshot_read_serial_supervisor_v2'}
        for row in result['tasks']:
            if row['task'] not in current:continue
            stage=row.get('stage')
            if row['task']=='bus64_pair_execution_v2' and row['status']=='complete':
                stage='C_and_HLS_execution_complete'
            print(f"{row['task']}: {row['status']} ({stage}) owner_verified={row.get('owner_verified')}")
        for row in result['audit_receipts']:
            print(f"{row['step']}: report_receipt_verified={row['report_receipt_verified']}")
        print(result['audit_receipt_note'])
        print(result['new_chain_note'])
