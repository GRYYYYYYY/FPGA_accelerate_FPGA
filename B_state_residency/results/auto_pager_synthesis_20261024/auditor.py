"""Bind full pager OOC synthesis to simulation and enforce no-loop structure."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def main():
    out = ROOT / 'results/auto_pager_synthesis_20261024'
    sim = ROOT / 'results/auto_pager_20261024'
    gate = read(sim / 'source_bound_audit.json')
    assert gate['status'] == 'passed' and gate['manifest_sha256'] == sha(sim / 'manifest.json')
    assert sha(out / 'simulation_audit.json') == sha(sim / 'source_bound_audit.json')
    for name, spec in read(sim / 'manifest.json')['sources'].items():
        assert sha(out / 'sources' / name) == spec['sha256'] == sha(sim / 'sources' / name)
    script = ROOT / 'hardware/scripts/synthesize_auto_pager.tcl'
    assert sha(script) == sha(out / script.name)
    tcl = script.read_text()
    assert 'synth_design -top paged_exclusion_engine -part xcu280-fsvh2892-2L-e -mode out_of_context' in tcl
    assert '-generic' not in tcl
    assert 'ALLOW_COMBINATORIAL_LOOPS' not in tcl + (out / 'research_clock.xdc').read_text()
    top = (out / 'sources/pager/paged_exclusion_engine.sv').read_text()
    assert 'SLOTS=32,TX_BITS=16,GEN_BITS=16' in top
    assert 'FRAMES=163840,INDEX_BITS=18,HASH_BITS=18,PROBE_LIMIT=64,EPOCH_BITS=16' in top
    receipt = read(out / 'completion_receipt.json')
    assert receipt['exit_code'] == 0
    log = receipt['output']
    assert 'AUTO_PAGER_SYNTH_DONE' in log and '0 Critical Warnings and 0 Errors encountered.' in log
    assert not re.search(r'^(ERROR:|CRITICAL WARNING:)', log, re.M)
    checksum = re.search(r'Synth Design complete, checksum: (\w+)', log)[1]
    drc = (out / 'combinational_loops.rpt').read_text()
    assert re.search(r'Violations found:\s*0\b', drc)
    timing = (out / 'check_timing.rpt').read_text()
    for label in ['no_clock', 'unconstrained_internal_endpoints', 'loops', 'latch_loops']:
        assert f'checking {label} (0)' in timing
    io = {label: int(re.search(r'checking no_' + label + r'_delay \((\d+)\)', timing)[1]) for label in ('input', 'output')}
    rpt = (out / 'utilization.rpt').read_text()
    def number(label):
        return float(re.search(r'^\|\s*' + re.escape(label) + r'\s*\|\s*([\d.]+)\s*\|', rpt, re.M)[1])
    resources = {k: number(k) for k in ['CLB LUTs*', 'CLB Registers', 'Register as Latch', 'Block RAM Tile', 'URAM', 'DSPs']}
    assert resources['Register as Latch'] == 0 and resources['Block RAM Tile'] > 0
    assert (out / 'paged_exclusion_engine.dcp').stat().st_size > 0
    (out / 'auditor.py').write_bytes(Path(__file__).read_bytes())
    artifacts = {str(p.relative_to(out)): sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name not in ['final_audit.json', 'audit.stdout.log']}
    result = {'status': 'passed', 'resources': resources, 'combinational_loop_violations': 0,
              'checksum': checksum, 'elapsed_s': receipt['elapsed_seconds'], 'io_without_delay': io,
              'warnings': dict(Counter(re.findall(r'^WARNING: \[([^]]+)\]', log, re.M))),
              'artifacts': artifacts, 'auditor_sha256': sha(Path(__file__)),
              'scope': 'Full pager + state-reset exclusion HLS + native sparse endpoint OOC synthesis, default 32 slots/163840 frames/TX16/binding16/epoch16. No routed timing, platform, board or whole-router performance proof.'}
    (out / 'final_audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'artifacts'}, indent=2))


if __name__ == '__main__':
    main()
