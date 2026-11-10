"""Bind actual Vivado OOC resources to the independently tested v2 bridge."""
from pathlib import Path
import hashlib
import json
import re
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    out = ROOT / 'results/exclusion_label_adapter_v2_synthesis_20261024'
    sim = ROOT / 'results/exclusion_label_adapter_v2_20261024'
    gate = json.loads((sim / 'source_bound_audit.json').read_text())
    assert gate['status'] == 'passed' and gate['manifest_sha256'] == sha(sim / 'manifest.json')
    assert sha(out / 'simulation_audit.json') == sha(sim / 'source_bound_audit.json')
    assert sha(out / 'exclusion_label_adapter.sv') == sha(sim / 'sources/exclusion_label_adapter.sv')
    script = ROOT / 'hardware/scripts/synthesize_exclusion_label_adapter_v2.tcl'
    assert sha(script) == sha(out / script.name)
    receipt = json.loads((out / 'completion_receipt.json').read_text())
    assert receipt['exit_code'] == 0
    log = receipt['output']
    assert 'LABEL_ADAPTER_SYNTH_DONE' in log and 'Synth Design complete, checksum: 5684f693' in log
    assert 'Synthesis finished with 0 errors, 0 critical warnings' in log
    assert not re.search(r'^(ERROR:|CRITICAL WARNING:)', log, re.M)
    warnings = [line for line in log.splitlines() if line.startswith('WARNING:')]
    for line in warnings:
        if '[Synth 8-3917]' in line:
            assert re.search(r'port native_cmd_(op|value|field)\[\d+\] driven by constant [01]$', line)
        elif '[Synth 8-7129]' in line:
            bit = int(re.search(r'Port native_rsp_payload\[(\d+)\]', line)[1])
            assert bit < 64 or bit >= 128, line
        else:
            assert line == 'WARNING: [Synth 8-7080] Parallel synthesis criteria is not met', line
    rpt = (out / 'utilization.rpt').read_text()
    assert 'Design State : Synthesized' in rpt and 'xcu280-fsvh2892-2L-e' in rpt
    def value(label):
        return int(re.search(r'^\|\s*' + re.escape(label) + r'\s*\|\s*(\d+)\s*\|', rpt, re.M)[1])
    metrics = {label: value(label) for label in ('CLB LUTs*', 'CLB Registers', 'Register as Latch', 'Block RAM Tile', 'URAM', 'DSPs')}
    assert metrics == {'CLB LUTs*': 163, 'CLB Registers': 191, 'Register as Latch': 0, 'Block RAM Tile': 0, 'URAM': 0, 'DSPs': 0}
    cells = dict((name, int(count)) for name, count in (line.split() for line in (out / 'primitive_counts.tsv').read_text().splitlines()))
    assert cells['FDRE'] == metrics['CLB Registers']
    assert sum(count for name, count in cells.items() if name.startswith('LUT')) == 171
    assert not any(name.startswith(('RAM', 'URAM', 'DSP', 'LD')) for name in cells)
    assert (out / 'exclusion_label_adapter.dcp').stat().st_size > 1000
    (out / 'auditor.py').write_bytes(Path(__file__).read_bytes())
    artifacts = [p for p in out.iterdir() if p.is_file() and p.name not in ('final_audit.json', 'audit.stdout.log')]
    result = {'status': 'passed', 'script_sha256': sha(script), 'auditor_sha256': sha(Path(__file__)),
              'artifacts': {p.name: sha(p) for p in sorted(artifacts)},
              'resources': metrics, 'raw_lut_primitives': 171,
              'lut_note': 'report_utilization adjusts CLB LUTs for LUT combining; raw primitive sum is separate.',
              'warnings': dict(Counter(re.search(r'\[([^]]+)\]', line)[1] for line in warnings)),
              'elapsed_s': receipt['elapsed_seconds'], 'scope': 'Standalone OOC synthesis only; no routed timing or integrated resource claim.'}
    (out / 'final_audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'resources': metrics, 'elapsed_s': result['elapsed_s']}, indent=2))

if __name__ == '__main__':
    main()
