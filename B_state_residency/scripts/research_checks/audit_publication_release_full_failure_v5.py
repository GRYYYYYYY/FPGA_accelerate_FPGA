"""Audit a retained full-RTL invariant counterexample, never turn it into a PASS."""
from pathlib import Path
import datetime
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
BASE = Path('/tmp/B_state_residency_recovery_20261102')
RUN = BASE / 'ka_publication_release_full_rtl_v5'


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def read(p):
    return json.loads(p.read_text())


def main():
    m = read(RUN / 'manifest.json')
    pr = read(RUN / 'preparation.json')
    assert m['status'] == 'failed' and 'active_process' not in m
    assert sha(RUN / 'preparation.json') == m['preparation_sha256']
    assert m['attempt_kind'] == 'independent_new_host_attempt'
    assert m['memory_observation']['stable_seconds'] >= 60
    assert m['memory_observation']['current_bytes'] <= 225 * 1024**3
    assert sha(ROOT / 'scripts/research_checks/run_publication_release_full_rtl_v5.py') == m['runner_sha256']
    assert len(m['commands']) == 3
    for c, argv in zip(m['commands'], pr['commands']):
        assert c['exit_code'] == 0 and c['argv'] == argv
        assert sha(RUN / 'full' / (c['stage'] + '.stdout.log')) == c['stdout_sha256']
    for n, h in pr['sources'].items():
        assert sha(RUN / 'sources' / n) == h
    ref = Path(pr['reference'])
    assert sha(ref / 'source_bound_audit.json') == pr['reference_audit_sha256']
    rm = read(ref / 'manifest.json')
    assert pr['parameters'] == rm['parameters'] and len(pr['parameters']) == 13
    assert len(pr['production_sha256']) == 133
    for n, h in pr['production_sha256'].items():
        assert sha(RUN / 'sources' / n) == sha(ref / 'sources' / n) == h
    tb = (RUN / 'sources/tb_query_fault.sv').read_text()
    parent = (ref / 'sources/tb_query_fault.sv').read_text()
    assert tb.replace(pr['verification_call'], '', 1).replace(pr['verification_task'], '', 1) == parent
    assertion = 'if(jp_owned&&(!pc_owned||pc_release_ready))$fatal(1,"unexpected publication or lost lease in cancel case");'
    assert tb.count(assertion) == parent.count(assertion) == 1
    log = (RUN / 'full/simulate.log').read_text()
    fatal = 'Fatal: unexpected publication or lost lease in cancel case'
    assert log.count('Fatal:') == log.count(fatal) == 1 and 'ERROR:' not in log
    assert 'FULL_RTL_RELEASE_OVERLAP_OBSERVED' not in log
    assert 'Time: 327975 ns' in log and '$finish called at time : 327975 ns' in log
    patterns = [r'^FULL_PROBE_READY cycle=(\d+) time=(\d+) generation=([0-9a-f]+) checkpoint=(\d+) version=(\d+)$',
                r'^FULL_SIMULTANEOUS_ACCEPT cycle=(\d+) time=(\d+) start=1 release=1$',
                r'^FULL_OWNERSHIP_SPLIT cycle=(\d+) time=(\d+) publication=1 lease=0$']
    matches = [re.findall(pat, log, re.M) for pat in patterns]
    assert all(len(x) == 1 for x in matches)
    ready, accepted, split = [x[0] for x in matches]
    assert ready == ('32796', '327960000', '0000000100000001', '17', '3')
    assert accepted == ('32796', '327965000') and split == ('32797', '327966000')
    natural = (RUN / 'full/natural_trace.txt').read_text()
    assert 'BASELINE_NO_PRELOAD 73\n' in natural and 'JS 32796 17 0 3 3 1\n' in natural
    assert 'NR 32782 0 0 ' in natural
    vcd = (RUN / 'full/probe.vcd').read_text()
    assert '1ps' in vcd
    scopes, names, values, rows = [], {}, {}, {}
    time_ps = 0
    for line in vcd.splitlines():
        z = line.split()
        if not z:
            continue
        if z[0] == '$scope':
            scopes.append(z[2])
        elif z[0] == '$upscope':
            scopes.pop()
        elif z[0] == '$var':
            names[z[3]] = '.'.join(scopes[1:] + [z[4]])
        elif line.startswith('#'):
            rows[time_ps] = dict(values)
            time_ps = int(line[1:])
        elif line.startswith('b'):
            bits, code = line[1:].split()
            if code in names:
                values[names[code]] = int(bits, 2) if all(c in '01' for c in bits) else bits
        elif line[0] in '01xz' and line[1:] in names:
            values[names[line[1:]]] = int(line[0]) if line[0] in '01' else line[0]
    rows[time_ps] = dict(values)
    expected = {'clk', 'bench_rst', 'k_cold_rst', 'pc_acquire_valid', 'pc_acquire_ready',
                'pc_release_valid', 'pc_release_ready', 'pc_owned', 'jp_start', 'jp_start_ready',
                'jp_owned', 'jp_done', 'jp_result', 'system.publication.start_ok'}
    assert set(names.values()) == expected
    at = lambda t: rows[max(k for k in rows if k <= t)]
    before = at(327965000 - 1)
    after = at(327966000)
    assert before['clk'] == 0 and at(327965000)['clk'] == 1
    assert all(before[n] == 1 for n in ['jp_start', 'jp_start_ready', 'pc_release_valid', 'pc_release_ready', 'pc_owned', 'system.publication.start_ok'])
    assert before['jp_owned'] == before['bench_rst'] == before['k_cold_rst'] == 0
    assert after['jp_owned'] == 1 and after['pc_owned'] == 0
    prior = {}
    leases = []
    for t, val in sorted(rows.items()):
        if prior.get('clk') == 0 and val.get('clk') == 1 and prior.get('pc_acquire_valid') == prior.get('pc_acquire_ready') == 1:
            leases.append(t)
        prior = val
    assert len(leases) == 1 and leases[0] < 327960000
    plan = read(RUN / 'input_plan.json')
    assert sha(RUN / 'input_plan.json') == pr['input_plan_sha256']
    assert sha(Path(plan['binding'])) == plan['binding_sha256']
    for e in plan['regions'].values():
        assert sha(Path(e['path'])) == e['sha256']
    concat = hashlib.sha256()
    for key in ['owners', 'owner_pool', 'owner_allocator']:
        with Path(plan['regions'][key]['path']).open('rb') as stream:
            for block in iter(lambda: stream.read(1 << 20), b''):
                concat.update(block)
    regions = plan['regions']
    fresh = {n: concat.hexdigest() for n in ['owners.bin', 'snapshot.bin', 'pool.bin', 'g3.bin']}
    fresh.update({'design.bin': regions['design']['sha256'], 'cost.bin': regions['cost_history_prices_nets']['sha256'],
                  'allocator.bin': regions['owner_allocator']['sha256'], 'labels.bin': hashlib.sha256(bytes(3145728)).hexdigest()})
    assert fresh == m['fresh_input_sha256']
    preserved = read(ROOT / 'results/ka_publication_release_full_rtl_v5_terminal_preservation_20261102.json')
    assert preserved['run_status'] == 'failed'
    restored = Path(preserved['actual_restore'])
    for n, h in preserved['file_sha256'].items():
        assert sha(restored / n) == h
    report = {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'status': 'initialized_full_RTL_overlap_counterexample_audited',
              'run_status_preserved': 'failed', 'first_fatal': fatal, 'reviewer_sha256': sha(Path(__file__)),
              'lease_acquisition_ps': leases[0], 'ready_ps': 327960000, 'accept_ps': 327965000,
              'ownership_split_ps': 327966000, 'original_monitor_fatal_ps': 327975000,
              'pre_accept_values': before, 'post_accept_values': after,
              'terminal_archive_sha256': preserved['archive_sha256'],
              'evidence_sha256': {n: sha(RUN / n) for n in ['manifest.json', 'preparation.json', 'full/simulate.log', 'full/natural_trace.txt', 'full/probe.vcd']},
              'scope': 'Actual original initialized 133-source full RTL accepts both interface requests and loses lease while publication owns. Unmodified parent monitor terminates before the planned HALT marker. No HALT-result acceptance or full-regression PASS. External caller-protocol permissibility remains separate.',
              'full_system_functional_netlist_validated': False, 'physical_gate_open': False}
    output = ROOT / 'results/ka_publication_release_full_rtl_v5_counterexample_review_20261102.json'
    assert not output.exists()
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['status', 'accept_ps', 'ownership_split_ps', 'original_monitor_fatal_ps']}))


if __name__ == '__main__':
    main()
