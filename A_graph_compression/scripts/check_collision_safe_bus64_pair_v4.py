#!/usr/bin/env python3
"""Independent paired HLS/full C audit; no RTL or physical acceptance."""
import json
import argparse
from pathlib import Path
import re
import shlex
import xml.etree.ElementTree as ET
from check_vitis_kernel import digest, require
from check_collision_safe_batch_hls_v1 import instances
from owned_sim_resource_policy_v1 import abort_reason, POLICY
from prepare_collision_safe_bus64_pair_v1 import ROOT, BASE, OUT, REPORT as PREP

REPORT = ROOT/'results/collision_safe_bus64_pair_hls_audit_20261030_v3.json'


def audit(execution_root=OUT):
    OUT = Path(execution_root)
    state = json.loads((OUT/'state.json').read_text())
    require(state['status'] == 'complete' and state['stage'] == 'paired_hls_complete_independent_audit_pending' and
            state['completed_modes'] == [0, 1], 'Paired HLS not complete')
    plan = json.loads((OUT/'execution_plan.json').read_text()); prep = json.loads(PREP.read_text())
    require(plan['jobs'] == prep['jobs'] and plan['resource_policy'] == POLICY, 'Changed execution plan')
    files = dict(plan['files'])
    for name, checksum in files.items(): require(digest(name) == checksum, 'Changed bound input '+name)
    def bind(p):
        checksum = digest(p)
        require(str(p) not in files or files[str(p)] == checksum, 'Conflicting binding')
        files[str(p)] = checksum
        return checksum
    if 'independent_compiler_gate' in plan:
        gate_receipt = json.loads((OUT/'compiler_gate.json').read_text())
        gate_path = Path(plan['independent_compiler_gate'])
        require(gate_receipt['path'] == str(gate_path) and bind(gate_path) == gate_receipt['sha256'], 'Changed recovery gate')
        gate = json.loads(gate_path.read_text())
        require(gate['status'] == 'surviving_original_native_compiler_exit0_snapshot_and_full_inputs_independently_verified_RTL_pending', 'Wrong recovery compiler gate')
        for name, checksum in gate['files'].items(): require(bind(name) == checksum, 'Changed recovery evidence')
        require(bind(gate_receipt['receipt']) == gate_receipt['receipt_sha256'], 'Changed independent compiler receipt')
        receipt = json.loads(Path(gate_receipt['receipt']).read_text())
        require(receipt['exit_code'] == 0, 'Independent compiler audit failed')
        bind(OUT/'compiler_gate.json')
    initial = json.loads((OUT/'initial_memory.json').read_text())
    inventory_path = ROOT/'results/hls_collided_port_inventory_20261030_v1.json'
    inventory = json.loads(inventory_path.read_text())
    require(len(inventory['connections']) == 9, 'Wrong collision inventory')
    for name, checksum in inventory['files'].items():
        require(bind(name) == checksum, 'Changed original collision evidence')
    top = 'search_batch_trace_top_v2'; summaries = []; interfaces = []
    for job in plan['jobs']:
        mode = job['mode']; work = Path(job['cwd']); solution = Path(job['project'])/'solution'
        receipt = json.loads((work/'receipt.json').read_text()); actual = json.loads((work/'actual_limits.json').read_text())
        text = (work/'hls.log').read_text()
        require(receipt['exit_code'] == 0 and receipt['abort_reason'] is None and receipt['command'] == job['command'] and
                receipt['cwd'] == str(work) and receipt['actual_limits'] == actual and receipt['elapsed_seconds'] > 0 and
                receipt['log_sha256'] == bind(work/'hls.log'), 'Failed or changed HLS execution')
        require(abort_reason(initial, receipt['final_memory']) is None, 'OOM/reset during paired HLS')
        require(actual['address_space'] == [64*1024**3]*2 and actual['stack'] == [64*1024**2]*2 and
                actual['core'] == [0,0] and actual['pid'] > 0 and int(actual['start_ticks']) > 0, 'Missing finite actual limits')
        argv = shlex.split(actual['command'])
        require(Path(argv[0]).name == 'vitis_hls' and '-f' in argv and
                argv[argv.index('-f')+1] == job['flow'], 'Different actual HLS program/flow')
        require(not any(s in text for s in ['ERROR:', 'Fatal:', 'LLVM ERROR', 'runtime error:']), 'HLS error')
        require(not any('RTL name' in line and 'due to conflict' in line for line in text.splitlines()), 'Naming conflict remains')
        for marker in ['COLLISION_SAFE_BUS64_CSIM_COMPLETE', 'COLLISION_SAFE_BUS64_CSYNTH_COMPLETE']:
            require(text.splitlines().count(marker) == 1, 'Missing actual completion marker')
        require(f'FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode={mode} ports=44 transactions=4' in text and
                f'SEARCH_BATCH_PASS mode={mode}' in text and 'CSim done with 0 errors.' in text, 'Original C checks missing')
        for tx in range(4):
            snapshot = work/f'csim_{mode}_{tx}.bin'; original = BASE/'compressed_batch_rtl_tb_cpu_v2'/f'cpu_{mode}_{tx}.bin'
            require(snapshot.stat().st_size == original.stat().st_size == 946498280 and bind(snapshot) == bind(original), 'Full44 mismatch')
            trace = solution/'csim/build'/f'trace_mode_{mode}_case_{tx}.bin'
            require(bind(trace) == bind(BASE/'compressed_batch_rtl_tb_cpu_v2'/trace.name), 'Exact trace mismatch')
        xml = solution/'syn/report'/f'{top}_csynth.xml'; tree = ET.parse(xml).getroot()
        assignments = {p.tag:p.text for p in tree.find('UserAssignments')}
        require(tree.findtext('ReportVersion/Version') == '2022.2' and assignments['TopModelName'] == top and
                assignments['Part'] == 'xcu280-fsvh2892-2L-e' and float(assignments['TargetClockPeriod']) == 5 and
                float(assignments['ClockUncertainty']) == 1.35, 'Wrong tool/top/constraints')
        sources = ET.parse(Path(job['project'])/'hls.app').getroot().findall('files/file')
        require(len(sources) == 2 and {Path(p.attrib['name']).name for p in sources} ==
                {top+'.cpp', 'test_compressed_batch_rtl_full_depth.cpp'}, 'Different project source/testbench set')
        for source in sources:
            flags = shlex.split(source.attrib.get('cflags', ''))
            require([f for f in flags if f.startswith('-D')] == [f'-DSEARCH_GRAPH_MODE={mode}'] and
                    '-std=c++14' in flags, 'Different synthesized mode/diagnostic definitions')
        resources = {p.tag:int(p.text) for p in tree.find('AreaEstimates/Resources')}
        require(set(resources) == {'BRAM_18K','DSP','FF','LUT','URAM'} and resources['LUT'] > 0, 'Incomplete resource estimates')
        ports = {p.findtext('name'):{c.tag:c.text for c in p} for p in tree.findall('InterfaceSummary/RtlPorts')}
        widths = {name:int(row['Bits']) for name,row in ports.items() if name.startswith('m_axi_') and name.endswith('_RDATA')}
        baseline_path = ROOT/'results/compressed_batch_synthesis_review_20261025_v1.json'
        baseline = json.loads(baseline_path.read_text())
        expected_widths = {name:min(width,64) for name,width in baseline['read_data_port_widths'].items()}
        require(len(widths) == 30 and widths == expected_widths, 'Incomplete/unrealized global64 interfaces')
        bind(baseline_path)
        interfaces.append(ports)
        rtl = solution/'syn/verilog'; restored = []
        for row in inventory['connections']:
            parent = rtl/Path(row['parent']).name
            module = top+'_a_write_net_trace_record' if row['module'] == top+'_net' else row['module']
            # Both actual bus64 modes specialize this sink-loop helper as update.
            # Restrict the mapping to the known parent/mode; retain exact callee and pin checks.
            if mode in (0, 1) and parent.name == top+'_sink_loop_worker.v' and module == top+'_update_3':
                module = top+'_update'
            entries = [entry for entry in instances(parent.read_text()) if entry[0] == module]
            require(len(entries) == 1, 'Ambiguous restored callee '+module)
            _, instance, pins, _ = entries[0]; port = row['port'][:-2]
            require(port in pins and row['port'] not in pins, 'Unrestored port')
            value = pins[port].strip()
            require(re.fullmatch(r'[A-Za-z_]\w*', value) is not None and
                    re.search(r'^(?:input|wire|reg)\s+(?:signed\s+)?(?:\[[^\]]+\]\s*)?'+re.escape(value)+r'\s*;', parent.read_text(), re.M), 'Non-signal connection')
            require(re.search(r'^input\s+(?:signed\s+)?\[(?:63|31):0\]\s+'+port+r'\s*;', (rtl/(module+'.v')).read_text(), re.M), 'Wrong child input type')
            restored.append(dict(parent=str(parent), instance=instance, port=port, connection=value))
        for p in rtl.glob('*.v'): require(not re.search(r'\.(?:roots_x|query_x|net_x)\(', p.read_text()), 'Old collided port remains')
        for directory in [rtl, solution/'syn/report']:
            for p in directory.rglob('*'):
                if p.is_file(): bind(p)
        for p in [work/'receipt.json', work/'actual_limits.json', work/'comparison.json', Path(job['project'])/'hls.app']: bind(p)
        summaries.append(dict(mode=mode, resources=resources,
                              estimated_clock_ns=float(tree.findtext('PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod')),
                              restored_connections=restored, read_data_port_widths=widths))
    require(interfaces[0] == interfaces[1], 'Paired top interfaces differ')
    for p in [OUT/'state.json', OUT/'execution_plan.json', OUT/'initial_memory.json', inventory_path, Path(__file__).resolve()]: bind(p)
    return dict(status='collision_safe_bus64_pair_full8_C_and_HLS_independently_verified_RTL_pending', files=files,
                modes=summaries, full44_transactions_per_mode=4, rtl_verified=False, physical_verified=False, board_verified=False,
                limits=['HLS estimates and C/structural verification only; fresh paired RTL is required.',
                        'No routed capacity, clock closure, throughput, power or full routing acceptance.'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execution-root',type=Path,default=OUT)
    parser.add_argument('--output',type=Path,default=REPORT)
    args = parser.parse_args()
    require(args.execution_root == OUT or args.output not in {ROOT/'results/collision_safe_bus64_pair_hls_audit_20261030_v1.json', ROOT/'results/collision_safe_bus64_pair_hls_audit_20261030_v2.json'}, 'Recovered execution must preserve original report paths')
    require(not args.output.exists(), 'Refuse overwrite')
    result = audit(args.execution_root)
    with args.output.open('x') as stream: json.dump(result, stream, indent=2); stream.write('\n')
    print(result['status'])
