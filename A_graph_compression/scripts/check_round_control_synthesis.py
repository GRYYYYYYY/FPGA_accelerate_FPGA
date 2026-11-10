#!/usr/bin/env python3
"""Verify completed 2022.2 occupancy Csim/synthesis, preserving scheduling warnings."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from check_vitis_kernel import digest, require


def main():
    parser = argparse.ArgumentParser(description=__doc__);parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True);a = parser.parse_args()
    out = a.bundle.resolve();require(not a.output.exists(), 'Existing synthesis review')
    plan_path = out / 'plan.json';plan = json.loads(plan_path.read_text())
    state_path = out / 'state.json';state = json.loads(state_path.read_text())
    require(state['status'] == 'complete' and state['stage'] == 'synthesized_pending_independent_audit_and_rtl', 'Synthesis not complete')
    for p, sha in {**plan['files'], **plan['generated']}.items():require(digest(p) == sha, 'HLS input changed: ' + p)
    receipt_path = out / 'receipt.json';receipt = json.loads(receipt_path.read_text());log_path = out / 'flow.log'
    require(receipt['exit_code'] == 0 and receipt['command'] == plan['command'] and receipt['log_sha256'] == digest(log_path), 'Bad flow receipt')
    log = log_path.read_text()
    for marker in ['ROUND_CONTROL_CPU_PASS random=3000 nodes=1048576 nets=65536 rejected=13 final_conflict_advances=1 input_immutable=1', 'ROUND_CONTROL_CSIM_COMPLETE', 'ROUND_CONTROL_SYNTHESIS_COMPLETE']:
        require(len(re.findall(r'^' + marker + r'$', log, re.M)) == 1, 'Missing/duplicate completion: ' + marker)
    require('ERROR:' not in log and 'INFO: [SIM 211-1] CSim done with 0 errors.' in log, 'HLS C simulation failed')
    require('ROUND_CONTROL_CPU_PASS random=3000 nodes=1048576 nets=65536 rejected=13 final_conflict_advances=1 input_immutable=1' in log,'Different round control coverage')
    project = Path(plan['project']);solution = project / 'solution'
    xml_path = solution / 'syn/report/search_round_control_top_csynth.xml';xml = ET.parse(xml_path).getroot()
    user = {c.tag: c.text for c in xml.find('UserAssignments')}
    require(user['Part'] == plan['part'] == 'xcu280-fsvh2892-2L-e' and user['TopModelName'] == 'search_round_control_top'
            and float(user['TargetClockPeriod']) == plan['clock_ns'] == 5
            and float(user['ClockUncertainty']) == plan['setup_uncertainty_ns'] == 1.35
            and xml.findtext('ReportVersion/Version') == '2022.2', 'Wrong synthesis target')
    resources = {c.tag: int(c.text) for c in xml.find('AreaEstimates/Resources')}
    require({'BRAM_18K', 'LUT', 'FF', 'DSP', 'URAM'} <= resources.keys() and resources['LUT'] > 0 and resources['FF'] > 0, 'Missing resources')
    estimated = float(xml.findtext('PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod'))
    require(estimated > 0, 'Missing clock estimate')
    latency = {c.tag: c.text for c in xml.find('PerformanceEstimates/SummaryOfOverallLatency')}
    ports = {p.findtext('name'): int(p.findtext('Bits')) for p in xml.findall('InterfaceSummary/RtlPorts')
             if p.findtext('name', '').endswith('_RDATA') and p.findtext('name', '').startswith('m_axi_')}
    require(len(ports) == 3, 'Missing external memory bundle')
    pipelines = [dict(target=target, achieved_ii=int(ii), depth=int(depth), loop=loop)
                 for target, ii, depth, loop in re.findall(r"Pipelining result : Target II = (\S+), Final II = (\d+), Depth = (\d+), loop '([^']+)'", log)]
    warnings = Counter(re.findall(r'^WARNING: \[([^]]+)\]', log, re.M))
    rtl = list((solution / 'syn/verilog').glob('*.v'))
    require(any(p.name == 'search_round_control_top.v' for p in rtl), 'Missing actual generated top')
    bound = [plan_path, state_path, receipt_path, log_path, xml_path, Path(__file__).resolve(),
             Path(__file__).resolve().parent / 'check_vitis_kernel.py']
    bound += list((solution / 'syn/report').glob('*.rpt')) + rtl
    report = dict(status='round_control_csim_and_synthesis_verified_rtl_pending',
        files={str(p): digest(p) for p in bound}, source_bindings={**plan['files'], **plan['generated']},
        target=user, estimated_clock_ns=estimated, resources=resources, static_latency_estimates=latency,
        read_data_port_widths=ports, pipeline_schedules=pipelines, warning_counts=dict(warnings),
        loop_constraints_all_satisfied=(False if 'All loop constraints were NOT satisfied' in log else True if 'All loop constraints were satisfied' in log else None),
        rtl_verified=False, physical_timing_verified=False, board_verified=False,
        limitations=['Synthesis estimates only; no complete-operation measured RTL latency or board throughput.',
                    'Automatic pipelines have scheduling/flattening warnings; all warnings retained in original log.',
                    'Static loop-bound latency estimates are not measured workload latency.',
                    'Csim uses the same C++14 set/literal-state oracle already checked under sanitizers. No RTL run/setup performed by this flow.',
                    'End-of-round decision only; host executes component commands and retains observations/traces. No autonomous PL scheduler or device execution is established.'])
    with a.output.open('x') as stream:json.dump(report, stream, indent=2);stream.write('\n')
    print(json.dumps(dict(status=report['status'], resources=resources, estimated_clock_ns=estimated, warnings=dict(warnings))))


if __name__ == '__main__':main()
