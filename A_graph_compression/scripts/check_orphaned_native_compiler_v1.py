#!/usr/bin/env python3
"""Audit observed compiler completion after owner loss without inventing wait status."""
import json
from pathlib import Path
import re
import shlex
from check_vitis_kernel import digest, require
from experiment_status_v6 import process
from owned_sim_resource_policy_v1 import abort_reason
from observe_orphaned_native_compiler_v1 import ROOT, TRIAL, OUT as OBSERVER

REPORT = ROOT/'results/collision_safe_native_recovered_compiler_audit_20261030_v1.json'


def audit():
    state = json.loads((OBSERVER/'state.json').read_text())
    require(state['status'] == 'complete' and state['stage'] == 'compiler_terminal_evidence_pending_independent_recovery_audit',
            'Existing compiler has not reached observed successful termination')
    observation_plan = json.loads((OBSERVER/'plan.json').read_text())
    terminal = json.loads((OBSERVER/'terminal.json').read_text())
    original_plan = json.loads((TRIAL/'plan.json').read_text())
    original_state = json.loads((TRIAL/'state.json').read_text())
    actual = json.loads((TRIAL/'elaborate.actual_limits.json').read_text())
    require(process(original_state['owner_pid']) is None, 'Original owner unexpectedly present')
    for identity in [observation_plan['compiler'],observation_plan['timer']]:
        live = process(identity['pid'])
        require(not (live and live['state'] != 'Z' and live['start_ticks'] == identity['start_ticks']), 'Observed process still live')
    require(terminal['compiler_identity'] == observation_plan['compiler'] and
            terminal['timer_identity'] == observation_plan['timer'] and
            observation_plan['actual_limits'] == actual, 'Changed observed identities')
    require(all(actual[k] == observation_plan['compiler'][k] for k in ['pid','start_ticks','command']), 'Compiler identity mismatch')
    require((actual['address_space'],actual['stack'],actual['core']) ==
            ([192*1024**3]*2,[256*1024**2]*2,[0,0]), 'Different actual finite compiler limits')
    command = original_plan['commands'][0]
    require(command['phase'] == 'elaborate' and command['cwd'] == actual['cwd'] == str(TRIAL/'sim/verilog'), 'Different compile cwd/phase')
    require(shlex.split(observation_plan['timer']['command']) == command['command'][5:] and
            shlex.split(actual['command'])[1:] == command['command'][8:], 'Different actual compiler invocation')
    require(observation_plan['initial_memory'] == original_plan['initial_memory'] and
            abort_reason(original_plan['initial_memory'],terminal['final_memory']) is None, 'OOM/reset during original compiler interval')
    files = {}
    def bind(path):
        checksum = digest(path)
        require(str(path) not in files or files[str(path)] == checksum, 'Conflicting evidence binding')
        files[str(path)] = checksum
        return checksum
    for name, checksum in original_plan['files'].items(): require(bind(name) == checksum, 'Original input changed '+name)
    gate_path = ROOT/'results/collision_safe_native_preparation_audit_20261030_v1.json'
    gate = json.loads(gate_path.read_text())
    require(gate['status'] == 'collision_safe_native_full44_inputs_all30_guards_all44_relocations_independently_verified', 'Missing preparation gate')
    for name, checksum in gate['files'].items(): require(bind(name) == checksum, 'Prepared input changed '+name)
    expected_sources = {name for name in gate['files'] if '/collision_safe_native_rtl_preparation_v1/sim/' in name}
    copied = original_plan['copied']
    require({row['source'] for row in copied.values()} == expected_sources and len(copied) == len(expected_sources), 'Incomplete copied simulation inputs')
    for name, row in copied.items():
        relative = Path(row['source']).relative_to(Path('/tmp/A_graph_compression_recovery_20261025_v1/collision_safe_native_rtl_preparation_v1/sim'))
        require(Path(name) == TRIAL/'sim'/relative and row['sha256'] == gate['files'][row['source']] and
                bind(name) == row['sha256'], 'Changed actual compiled input '+name)
    log = TRIAL/'elaborate.log'; text = log.read_text(errors='replace')
    require(bind(log) == terminal['log_sha256'], 'Compiler log changed')
    require(re.findall(r'^\s*Exit status:\s*(\d+)\s*$',text,re.M) == ['0'] and
            text.splitlines().count('Built simulation snapshot search_batch_trace_top_v2') == 1,
            'Missing actual time exit0 and completed snapshot')
    require(not any(x in text for x in ['ERROR:', 'Fatal:', 'LLVM ERROR', 'Command terminated by signal']), 'Compiler error')
    require(terminal['timer_reported_exit_statuses'] == ['0'] and terminal['snapshot_built_markers'] == 1 and
            terminal['errors'] == [] and terminal['snapshot_exists'] is True, 'Terminal observation contradicts log')
    snapshot = TRIAL/'sim/verilog/xsim.dir/search_batch_trace_top_v2/xsimk'
    require(snapshot.stat().st_size > 0 and bind(snapshot) == terminal['snapshot_sha256'], 'Compiled snapshot missing/changed')
    generated = TRIAL/'sim/verilog/xsim.dir'
    for p in generated.rglob('*'):
        if p.is_file(): bind(p)
    observer_script = ROOT/'scripts/observe_orphaned_native_compiler_v1.py'
    require(bind(observer_script) == observation_plan['script_sha256'], 'Observer changed')
    incident_path = ROOT/'results/collision_safe_native_owner_loss_20261030_v1.json'
    incident = json.loads(incident_path.read_text())
    require(incident['driver_tool_exit_code'] == 143 and incident['driver'] is None, 'Wrong interruption evidence')
    for name, checksum in incident['files'].items(): require(bind(name) == checksum, 'Changed interruption evidence')
    for p in [incident_path,OBSERVER/'plan.json',OBSERVER/'state.json',OBSERVER/'terminal.json',TRIAL/'plan.json',
              TRIAL/'state.json',TRIAL/'elaborate.actual_limits.json',Path(__file__).resolve()]:bind(p)
    return dict(status='surviving_original_native_compiler_exit0_snapshot_and_full_inputs_independently_verified_RTL_pending',
                files=files, actual_compiler=actual, compiler_exit_evidence='Original surviving /usr/bin/time -v footer and successful xelab snapshot marker',
                original_driver_exit_code=143, fabricated_wait_receipt=False, transactions_required=4, pointers=44, models=30,
                rtl_verified=False, physical_verified=False, board_verified=False,
                limits=['Compiler recovery only; original driver remains interrupted.',
                        'Fresh owned execution of all four RTL transactions, original C postcheck and full44 output comparison remains mandatory.'])


if __name__ == '__main__':
    require(not REPORT.exists(), 'Refuse overwrite')
    result = audit()
    with REPORT.open('x') as stream: json.dump(result,stream,indent=2); stream.write('\n')
    print(result['status'])
