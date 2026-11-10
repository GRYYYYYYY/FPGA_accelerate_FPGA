#!/usr/bin/env python3
"""Bind the observed worst routed path; do not infer closure from HLS estimates."""
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    base = ROOT / 'data/derived/search_packet64_physopt_20261025_v1'
    rtl_base=ROOT/'data/derived/search_packet_width64_physical_20261025_v1/csr'
    report = base / 'reports/routed_timing.rpt'
    text = report.read_text()
    section = text.split('Max Delay Paths', 1)[1]
    slack = float(re.search(r'Slack \(VIOLATED\)\s*:\s*([-\d.]+)ns', section)[1])
    source = re.search(r'Source:\s*(\S+)', section)[1]
    destination = re.search(r'Destination:\s*(\S+)', section)[1]
    delays = re.search(r'Data Path Delay:\s*([\d.]+)ns\s*\(logic ([\d.]+)ns \(([\d.]+)%\)\s*route ([\d.]+)ns \(([\d.]+)%\)\)', section)
    assert delays and 'validate_path' in source and destination.endswith('/CE')
    delay, logic, logic_pct, route, route_pct = map(float, delays.groups())
    assert abs(delay-logic-route) < .002 and slack < 0
    evidence = [report, rtl_base/'source/search_kernel_top_validate_path.v',
                rtl_base/'source/search_kernel_top_read_r.v',
                ROOT/'results/search_packet_width64_physical_audit_20261025_v2.json',
                ROOT/'results/search_packet64_physopt_audit_20261025_v1.json',
                ROOT/'hardware/vitis/search_label_records.hpp',
                Path(__file__).resolve()]
    result = dict(status='observed_worst_routed_path_diagnosed_no_fix_or_closure_claim',
                  source=source, destination=destination, setup_slack_ns=slack,
                  logic_levels=12,carry8_cells=5,observed_control_net_fanout=231,
                  candidate_is_unimplemented=True,
                  data_delay_ns=delay, logic_delay_ns=logic, route_delay_ns=route,
                  route_fraction_percent=route_pct,
                  evidence_based_next_action='Evaluate a separate read_r validity/control staging candidate while preserving every invalid-record, parent-chain and full-capacity check; require new CPU/HLS/RTL/postroute evidence rather than infer timing closure.',
                  limits=['Observed path names identify generated modules; exact C++ operation mapping needs HLS debug provenance.',
                          'Route delay dominates this path but that does not prove a physical optimization will close timing.',
                          'No DUT, constraints, completed Vivado session or existing report modified.'],
                  files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in evidence})
    baseline=json.loads((ROOT/'results/search_packet_width64_physical_audit_20261025_v2.json').read_text())
    for p in [rtl_base/'source/search_kernel_top_validate_path.v',rtl_base/'source/search_kernel_top_read_r.v']:
        assert baseline['files'][str(p)]==hashlib.sha256(p.read_bytes()).hexdigest()
    target = ROOT/'results/search_packet64_physopt_path_diagnosis_20261025_v1.json'
    assert not target.exists()
    temporary = target.with_suffix('.json.tmp')
    with temporary.open('x') as stream:
        json.dump(result, stream, indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, target)
    print(json.dumps({k:result[k] for k in ['status','setup_slack_ns','route_fraction_percent']}))

if __name__ == '__main__':
    main()
