#!/usr/bin/env python3
"""Read-only workflow status; verify owned processes and honor resource-abort sidecars."""
import argparse
import datetime
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')

def process(pid,proc_root=Path('/proc')):
    p=proc_root/str(pid)
    try:
        fields=(p/'stat').read_text().rsplit(')',1)[1].split()
        command=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
        return dict(pid=pid,state=fields[0],start_ticks=fields[19],command=command)
    except FileNotFoundError:return None

def workflow(label,folder,script,proc_root=Path('/proc')):
    if (folder/'handoff.json').exists():
        handoff=json.loads((folder/'handoff.json').read_text())
        return dict(task=label,status=handoff['status'],stage=None,owner_verified=False,replacement=handoff['replacement'])
    path=folder/'state.json'
    if not path.exists():return dict(task=label,status='not_started',stage=None,owner_verified=False)
    state=json.loads(path.read_text());pid=state.get('owner_pid');owner=process(pid,proc_root) if pid else None
    verified=bool(owner and owner['state']!='Z' and script in owner['command'])
    status=state['status']
    if status=='running':
        if not verified:status='owner_missing_or_mismatched_no_terminal_receipt'
        elif owner['state'] in ['T','t']:status='process_suspended'
        elif state.get('stage','').startswith('waiting'):status='waiting_dependency_or_memory'
    result=dict(task=label,status=status,stage=state.get('stage'),owner_pid=pid,owner_verified=verified,
                owner_process_state=owner['state'] if verified else None,state_file=str(path))
    return result

def collect(root=ROOT,base=BASE,proc_root=Path('/proc')):
    definitions=[('snapshot',base/'snapshot_rtl_local_recovery','resident_snapshot_rtl_local_recovery.py'),
        ('compact_batch',base/'compressed_batch_compact_rtl_guarded_v1','run_compressed_batch_compact_rtl_guarded.py'),
        ('compact_memory_controller',root/'data/derived/compact_rtl_memory_serialization_20261025_v1','serialize_compact_rtl_memory.py'),
        ('search_dpi',root/'data/derived/search_axi_dpi_serialized_supervision_20261025_v3','supervise_search_axi_dpi_v3.py'),
        ('search_dpi_audit',root/'data/derived/search_axi_dpi_final_audit_supervision_20261025_v3','supervise_search_axi_dpi_final_audit_v3.py'),
        ('batch_dpi',root/'data/derived/compressed_bus64_dpi_supervision_20261025_v1','supervise_compressed_bus64_dpi_rtl_v1.py')]
    if (root/'data/derived/search_axi_dpi_capped_supervision_20261025_v4/state.json').exists():
        definitions=[(label,root/'data/derived/search_axi_dpi_capped_supervision_20261025_v4','supervise_search_axi_dpi_capped_replay_v4.py') if label=='search_dpi' else (label,folder,script) for label,folder,script in definitions]
    if (root/'data/derived/compressed_bus64_dpi_supervision_20261025_v2/state.json').exists():
        definitions=[(label,root/'data/derived/compressed_bus64_dpi_supervision_20261025_v2','supervise_compressed_bus64_dpi_rtl_v2.py') if label=='batch_dpi' else (label,folder,script) for label,folder,script in definitions]
    if (root/'data/derived/search_axi_dpi_capped_supervision_20261025_v5/state.json').exists():
        definitions=[(label,root/'data/derived/search_axi_dpi_capped_supervision_20261025_v5','supervise_search_axi_dpi_capped_replay_v5.py') if label=='search_dpi' else (label,folder,script) for label,folder,script in definitions]
    if (root/'data/derived/compressed_bus64_dpi_supervision_20261025_v3/state.json').exists():
        definitions=[(label,root/'data/derived/compressed_bus64_dpi_supervision_20261025_v3','supervise_compressed_bus64_dpi_rtl_v3.py') if label=='batch_dpi' else (label,folder,script) for label,folder,script in definitions]
    if (root/'data/derived/search_axi_dpi_capped_supervision_20261025_v6/state.json').exists():
        definitions=[(label,root/'data/derived/search_axi_dpi_capped_supervision_20261025_v6','supervise_search_axi_dpi_capped_replay_v6.py') if label=='search_dpi' else (label,folder,script) for label,folder,script in definitions]
    if (root/'data/derived/compressed_bus64_dpi_supervision_20261025_v4/state.json').exists():
        definitions=[(label,root/'data/derived/compressed_bus64_dpi_supervision_20261025_v4','supervise_compressed_bus64_dpi_rtl_v4.py') if label=='batch_dpi' else (label,folder,script) for label,folder,script in definitions]
    if (root/'data/derived/search_axi_dpi_serial_capped_supervision_20261025_v7/state.json').exists():
        definitions=[(label,root/'data/derived/search_axi_dpi_serial_capped_supervision_20261025_v7','supervise_search_axi_dpi_serial_capped_replay_v7.py') if label=='search_dpi' else (label,folder,script) for label,folder,script in definitions]
    if (root/'data/derived/compressed_bus64_dpi_supervision_20261025_v6/state.json').exists():
        definitions=[(label,root/'data/derived/compressed_bus64_dpi_supervision_20261025_v6','supervise_compressed_bus64_dpi_rtl_v6.py') if label=='batch_dpi' else (label,folder,script) for label,folder,script in definitions]
    if (root/'data/derived/snapshot_dpi_supervision_20261025_v3/state.json').exists():
        definitions.append(('snapshot_dpi',root/'data/derived/snapshot_dpi_supervision_20261025_v3','supervise_snapshot_dpi_rtl_v3.py'))
    for label, folder, script in [
        ('compact_batch_execution',base/'compressed_batch_compact_rtl_guarded_execution_v1','supervise_compressed_batch_compact_rtl_guarded.py'),
        ('compact_batch_final_audit',base/'compressed_batch_compact_guarded_final_audit_v1','supervise_compressed_batch_compact_guarded_audit.py'),
        ('search_dpi_attempt_v7',base/'search_axi_dpi_replay_v7','replay_search_axi_dpi_v7.py'),
        ('compact_native_stack_recovery',base/'compact_native_stack_recovery_v2','run_compact_native_stack_recovery_v2.py'),
        ('compact_bus64_hls',base/'compressed_batch_compact_bus64_hls','compressed_batch_compact_bus64_hls_v3.py'),
        ('compact_bus64_hls_audit',base/'compressed_batch_compact_bus64_hls/audit_supervisor','supervise_compact_bus64_hls_v1.py'),
        ('compact_bus64_cosim_setup',base/'compressed_batch_compact_bus64_cosim_setup','prepare_compressed_batch_compact_bus64_cosim.py'),
        ('compact_bus64_cosim_setup_audit',base/'compressed_batch_compact_bus64_cosim_setup/audit_supervisor','supervise_compact_bus64_cosim_setup_v1.py'),
        ('compact_native_stack_audit',base/'compact_native_stack_final_audit_v2','supervise_compact_native_stack_recovery_audit_v2.py'),
    ]:
        if (folder/'state.json').exists():
            definitions.append((label,folder,script))
    definitions.append(('batch_dpi_execution',base/'compressed_batch_bus64_dpi_rtl_v3','run_compressed_bus64_dpi_rtl_v3.py'))
    definitions.append(('post_snapshot_rtl',root/'data/derived/post_snapshot_rtl_supervision_20261025_v1','supervise_post_snapshot_rtl_v1.py'))
    definitions.extend([('csr_binary_fsm_full44',root/'data/derived/binary_fsm_full44_supervision_20261025_v1','supervise_binary_fsm_full44_v1.py'),('compact_binary_fsm_full44',root/'data/derived/compact_binary_fsm_full44_supervision_20261025_v1','supervise_compact_binary_fsm_full44_v1.py'),('snapshot_dpi_execution_v3',base/'snapshot_dpi_rtl_v3','run_snapshot_dpi_rtl_v3.py')])
    definitions.extend([('read_control_staging_rtl',root/'data/derived/read_control_staging_rtl_supervision_20261025_v2','supervise_read_control_staging_rtl_v2.py'),('read_control_staging_execution_v2',base/'search_read_control_staging_dpi_rtl_v2','run_search_read_control_staging_dpi_rtl_v2.py')])
    rows=[workflow(*definition,proc_root) for definition in definitions]
    compact_control=root/'data/derived/compact_rtl_memory_serialization_20261025_v1/state.json'
    if compact_control.exists():
        target=json.loads(compact_control.read_text()).get('target',{})
        actual=process(target.get('pid'),proc_root) if target.get('pid') else None
        verified=bool(actual and actual['start_ticks']==target.get('start_ticks') and actual['command']==target.get('command'))
        row=next(r for r in rows if r['task']=='compact_batch')
        row['compiler_identity_verified']=verified
        if verified:
            row.update(compiler_pid=actual['pid'],compiler_process_state=actual['state'])
            if actual['state'] in ['T','t'] and row['status']=='running':row['status']='process_suspended'
    abort=root/'data/derived/bus64_physical_resource_abort_20261025_v1/terminal.json'
    if abort.exists():
        record=json.loads(abort.read_text());owner=process(record['physical_pid'],proc_root)
        rows.append(dict(task='integrated_physical_original',status='resource_aborted',
                         recorded_physical_pid=record['physical_pid'],pid_currently_exists=owner is not None,
                         authority=str(abort),note='Historical original running state does not override terminal resource-abort sidecar; no completion inferred'))
    for name,path in [('integrated_physical_recovery',root/'data/derived/compressed_batch_bus64_physical_recovery_20261025_v4'),
                      ('packet64_physical_optimization',root/'data/derived/search_packet64_physopt_20261025_v1')]:
        rows.append(dict(task=name,status='prepared_not_started' if (path/'plan.json').exists() and not (path/'csr/state.json').exists() and not (path/'state.json').exists() else 'inspect_physical_state',plan_file=str(path/'plan.json')))
    return dict(observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),goal='实现完整实验',
                completion_proven=False,tasks=rows,scope='Read-only local workflow observation; not a cluster scheduler queue or semantic acceptance audit')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--json',action='store_true');a=p.parse_args();result=collect()
    if a.json:print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        for task in result['tasks']:print(f"{task['task']}: {task['status']}"+(f" ({task['stage']})" if task.get('stage') else ''))
        print('Full experiment completion remains unproven. Local task dependencies only; no cluster queue inferred.')
if __name__=='__main__':main()
