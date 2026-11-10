#!/usr/bin/env python3
"""Audit complete paired/candidate OOC measurements; retain negative quality results."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import zipfile

from check_vitis_kernel import digest, require
from check_search_kernel_physical_mode import timing, coverage, constraints, summary, utilization, quality_gates
from check_netlist_quality import drc_status, route_status
from collision_safe_physical_entry_v1 import validate_bundle, validate_functional, verify_files, validate_accepted_sources, PHYSICAL_AS_BYTES
from owned_sim_resource_policy_v1 import POLICY,abort_reason

ROOT = Path(__file__).resolve().parents[1]


def terminal_receipts(observation, history, state, owner, work):
    status = observation['status']
    require(state['status'] == 'complete' and state['stage'] == 'ooc_complete_pending_independent_audit',
            'Physical flow incomplete')
    require(status['is_command_running'] is False and status['last_completed_code'] == 0 and
            status['queue_length'] == 0, 'No successful terminal MCP observation')
    require(status['process_id'] == state['owner_pid'] == owner['pid'], 'Physical owner changed')
    require(Path(status['working_dir']).resolve() == work.resolve(), 'Wrong physical working directory')
    completed = datetime.fromisoformat(state['updated_utc'].replace('Z', '+00:00'))
    observed = datetime.fromisoformat(observation['observed_utc'].replace('Z', '+00:00'))
    require(observed.tzinfo is not None and observed >= completed, 'Stale physical observation')
    command = 'source {'+str(work/'entry.tcl')+'}'
    entries = [e for e in history['history'] if e['command'] == command]
    require(len(entries) == 1 and entries[0]['code'] == 0, 'Missing/duplicate successful exact entry history')
    entry = entries[0]
    truncated = entry['output'].endswith('... [Output truncated. Full output in vivado.log]')
    require('SEARCH_PHYSICAL_FLOW_COMPLETE' in entry['output'] or truncated, 'No declared history completion/truncation')
    require(abs(entry['elapsed']-status['last_completed_elapsed']) < 0.01, 'History/status duration mismatch')
    stamp = datetime.fromisoformat(re.sub(r'(\.\d{6})\d+(?=Z|[+-])', r'\1', entry['timestamp']).replace('Z', '+00:00'))
    require(stamp >= completed, 'History predates terminal flow state')
    prefix = status.get('last_completed', '')
    prefix = prefix[:-3] if prefix.endswith('...') else prefix
    require(len(prefix) > 20 and command.startswith(prefix), 'Different last completed MCP command')
    return command, truncated


def audit(bundle, name, status_path, history_path):
    plan, job = validate_bundle(bundle, name)
    work = Path(job['work'])
    state = json.loads((work/'state.json').read_text())
    require(state['status'] == 'complete' and state['stage'] == 'ooc_complete_pending_independent_audit',
            'Physical flow incomplete; no acceptance from prepared/running artifacts')
    guard = json.loads((work/'guard/state.json').read_text())
    control = json.loads((work/'guard/plan.json').read_text())
    require(guard['status'] == 'complete' and guard['stage'] == 'flow_terminal' and
            guard['flow_status'] == 'complete' and guard['resource_abort'] is False and
            guard['flow_state_sha256'] == digest(work/'state.json'), 'No successful protected physical run')
    require(control['bundle_plan_sha256'] == digest(bundle/'plan.json') and
            control['script_sha256'] == digest(ROOT/'scripts/collision_safe_physical_entry_v1.py'), 'Changed runtime protection')
    require(control['resource_policy']==guard['resource_policy']==POLICY and control['physical_as_bytes']==PHYSICAL_AS_BYTES and control['actual_address_space']==[PHYSICAL_AS_BYTES]*2 and control['actual_core']==[0,0],'Different actual physical limits/policy')
    require(abort_reason(control['entry_memory'],guard['end_memory']) is None,'New OOM during physical flow')
    functional = validate_functional()
    accepted_sources=validate_accepted_sources(plan,functional)
    require(control['accepted_source_bindings']==accepted_sources,'Changed accepted DUT mapping')
    require(control['functional_files'] == functional, 'Changed actual functional prerequisites')
    chain_path=ROOT/'data/derived/snapshot_read_serial_supervision_20261031_v2/state.json'
    require(control['functional_chain_state_sha256']==digest(chain_path),'Changed terminal functional chain')
    chain=json.loads(chain_path.read_text())
    require(chain['status']=='complete' and chain['stage']=='full30_snapshot_and_read_control_independently_audited','Incomplete terminal functional chain')
    observation = json.loads(status_path.read_text())
    history = json.loads(history_path.read_text())
    session = json.loads((work/'session.json').read_text())
    require(observation['session_id'] == session['session_id'] and session['pid'] == control['owner']['pid'],
            'Different dedicated MCP session')
    command, truncated = terminal_receipts(observation, history, state, control['owner'], work)
    files = {**plan['files'], **functional}
    files[str(chain_path)]=digest(chain_path)

    def bind(path):
        files[str(path)] = digest(path)

    log = Path(observation['status']['log_file'])
    text = log.read_text(errors='replace')
    require(command in text and len(re.findall(r'^SEARCH_PHYSICAL_FLOW_COMPLETE\s*$', text, re.M)) == 1,
            'Missing/duplicate exact completion in full log')
    require('PHYSICAL_PROTECTION_ARMED' in text, 'Runtime protection was not armed before flow')
    marker = 'SEARCH_PHYSICAL_STAGE '+work.name+' running prepare'
    require(marker in text, 'Actual physical start missing')
    segment = text[text.index(marker):]
    require(not re.search(r'^ERROR:', segment, re.M), 'Physical flow contains an error')
    require('Got license for feature' in segment and "device 'xcu280'" in segment, 'Missing synthesis license checkout')
    require(not (work/'error.txt').exists(), 'Physical error receipt exists')
    for path in [bundle/'plan.json', work/'state.json', work/'session.json', work/'guard/state.json',
                 work/'guard/plan.json', work/'guard/watch.log', log, status_path, history_path,
                 Path(__file__).resolve(), ROOT/'scripts/check_search_kernel_physical_mode.py',
                 ROOT/'scripts/check_search_kernel_physical.py', ROOT/'scripts/check_netlist_quality.py',
                 ROOT/'scripts/check_vitis_kernel.py']:
        bind(path)
    for name in ['synthesized.dcp', 'placed.dcp', 'routed.dcp']:
        path = work/name
        require(path.is_file() and path.stat().st_size > 0, 'Missing checkpoint: '+name)
        with zipfile.ZipFile(path) as archive:
            require(archive.testzip() is None, 'Corrupt checkpoint: '+name)
        bind(path)
    stages = {}
    for stage in ['synthesis', 'routed']:
        paths = {name: work/'reports'/(stage+'_'+name) for name in ['timing.rpt', 'check_timing.rpt',
            'utilization.rpt', 'drc.rpt', 'methodology.rpt', 'timing.xdc', 'summary.tcllist', 'methodology_properties.tcllist']}
        texts = {name: path.read_text() for name, path in paths.items()}
        for path in paths.values():
            bind(path)
        for name in ['timing.rpt', 'utilization.rpt', 'drc.rpt', 'methodology.rpt']:
            require(re.search(r'\| Design\s*:\s*'+re.escape(job['top'])+r'\s*$', texts[name], re.M), 'Different report design')
            require('Vivado v.2022.2' in texts[name] and 'xcu280-fsvh2892' in texts[name], 'Different tool/device')
        t = timing(texts['timing.rpt'])
        require(t['coverage'] == coverage(texts['check_timing.rpt']), 'Timing coverage disagrees')
        constraints(texts['timing.xdc'])
        stages[stage] = dict(timing=t, resources=utilization(texts['utilization.rpt'], top=job['top']),
                             summary=summary(texts['summary.tcllist'], t), drc=drc_status(paths['drc.rpt']),
                             methodology=drc_status(paths['methodology.rpt']))
    require(re.search(r'\| Design State\s*:\s*(?:Fully )?Routed\s*$', texts['utilization.rpt'], re.M), 'Not post-route resources')
    route_path = work/'reports/route_status.rpt'
    bind(route_path)
    route = route_status(route_path)
    routed = stages['routed']
    gates = quality_gates(routed['timing'], route, routed['drc'], routed['methodology'])
    return dict(status='collision_safe_or_staged_ooc_measurement_complete', job=job['name'], stages=stages,
                route=route, quality_gates=gates, all_quality_gates_pass=all(gates.values()), files=files,
                mcp_history_output_truncated=truncated, created_utc=datetime.now(timezone.utc).isoformat(),
                platform_timing_verified=False, board_verified=False,resource_policy=POLICY,accepted_source_bindings=accepted_sources,
                limitations=['Complete source-specific OOC measurement, not platform shell/AXI IO timing or device execution.',
                             'All DRC and methodology violations retained; a negative quality result is not timing closure.',
                             'Naming-corrected mapped resources are measured independently; HLS estimates are not substituted.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--job', choices=['csr', 'compact', 'read_control'], required=True)
    parser.add_argument('--status', type=Path, required=True)
    parser.add_argument('--history', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'Refuse overwrite')
    report = audit(args.bundle.resolve(), args.job, args.status.resolve(), args.history.resolve())
    with args.output.open('x') as stream:
        json.dump(report, stream, indent=2); stream.write('\n')
    print(report['status'], 'all_quality_gates_pass='+str(report['all_quality_gates_pass']))
    return 0 if report['all_quality_gates_pass'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
