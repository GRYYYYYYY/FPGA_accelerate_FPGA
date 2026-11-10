"""Read-only terminal review; never rerun simulation or alter accepted run files."""
from pathlib import Path
import ast
import bisect
import collections
import datetime
import hashlib
import itertools
import json
import re
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from shadow_recovered_evidence_v7 import sha, read, identity

BASE = Path('/tmp/B_state_residency_recovery_20261102')
P = BASE / 'stage_static_cp_shadow_system_v7'
O = BASE / 'stage_static_cp_shadow_v7_preserved_terminal'
S = BASE / 'stage_static_cp_shadow_system_v7_supervision_v1'
REF = BASE / 'stage_static_cp_host_full_static_v1'
OUT = ROOT / 'results/stage_static_cp_shadow_system_v7_main_review_20261103.json'
UNISIMS = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/data/verilog/src/unisims')


def stream_sha(stream):
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1 << 20), b''):
        h.update(chunk)
    return h.hexdigest()


def inventory(root):
    entries = {}
    for f in root.rglob('*'):
        assert not f.is_symlink(), f
        if f.is_file():
            entries[str(f.relative_to(root))] = sha(f)
    return entries


def diagnostics():
    logs = {}
    warnings = []
    for name in ['compile.stdout.log', 'elaborate.stdout.log', 'simulate.stdout.log', 'simulate.log']:
        text = (P / 'full' / name).read_text()
        assert not re.search(r'Fatal:|FATAL_ERROR:|ERROR:|CRITICAL WARNING:', text), name
        rows = [line for line in text.splitlines() if 'WARNING:' in line]
        logs[name] = dict(sha256=sha(P / 'full' / name), warnings=len(rows), errors=0, fatal=0, critical_warnings=0)
        if name.endswith('.stdout.log'):
            warnings.extend(rows)
    assert [logs[n]['warnings'] for n in logs] == [1, 4887, 0, 0]
    normalize = lambda s: re.sub(r'\[/[^\]]*/([^/]+:\d+)\]', r'[\1]', s)
    reference_warnings = []
    for stage in ['compile', 'elaborate']:
        reference_warnings.extend(normalize(s) for s in (REF / 'full' / (stage + '.stdout.log')).read_text().splitlines() if 'WARNING:' in s)
    inherited = [normalize(s) for s in warnings if '/shadow_netlist.v:' not in s]
    assert inherited == reference_warnings and len(inherited) == 13
    tb = (P / 'sources/tb_query_fault.sv').read_text()
    assert tb.count('stage_static_cp_shadow.finish_and_check;$finish;') == 1
    assert tb.replace('stage_static_cp_shadow.finish_and_check;$finish;', '$finish;') == (REF / 'sources/tb_query_fault.sv').read_text()
    assert sha(P / 'sources/axi_file_memory.sv') == sha(REF / 'sources/axi_file_memory.sv')
    assert "hold_r===1'b1" in (P / 'sources/axi_file_memory.sv').read_text().replace(' ', '')
    lines = (P / 'sources/shadow_netlist.v').read_text().splitlines()
    starts, types = [], []
    for number, line in enumerate(lines, 1):
        match = re.match(r'^  ([A-Z][A-Z0-9_]*)\s+', line)
        if match and (UNISIMS / (match[1] + '.v')).is_file():
            starts.append(number)
            types.append(match[1])
    models, entries, counts = {}, [], collections.Counter()
    for warning in warnings:
        if '/shadow_netlist.v:' not in warning:
            continue
        number = int(re.search(r':(\d+)\]', warning)[1])
        port = re.search(r"port '([^']+)'", warning)[1]
        # XSim attributes an unconnected-port diagnostic to the preceding
        # instance attribute, whereas width diagnostics point into the port map.
        if lines[number - 1].lstrip().startswith('(*'):
            idx = bisect.bisect_left(starts, number)
            assert all(not s.strip() or s.lstrip().startswith('(*') for s in lines[number - 1:starts[idx] - 1])
        else:
            idx = bisect.bisect_right(starts, number) - 1
        primitive = types[idx]
        model = UNISIMS / (primitive + '.v')
        if primitive not in models:
            models[primitive] = model.read_text()
        direction = re.search(r'\b(output|input|inout)\b[^;\n]*\b' + port + r'\s*[,;]', models[primitive])
        assert direction and direction[1] == 'output', (warning, primitive)
        # Check the actual statement, not just a nearby primitive name.
        block = []
        for line in itertools.islice(lines, starts[idx] - 1, None):
            block.append(line)
            if line.rstrip().endswith(';'):
                break
        statement = '\n'.join(block)
        code = re.search(r'\[VRFC ([0-9-]+)\]', warning)[1]
        assert code in ['10-3091', '10-3645']
        connected = re.search(r'\.' + port + r'\s*\(', statement) is not None
        assert connected == (code == '10-3091'), warning
        if code == '10-3091':
            actual, formal = map(int, re.search(r'actual bit length (\d+) differs from formal bit length (\d+)', warning).groups())
            assert 0 < actual < formal
        counts[(primitive, code)] += 1
        entries.append(dict(log=warning, primitive=primitive, primitive_line=starts[idx], port=port, direction='output'))
    assert len(entries) == 4875
    return dict(logs=logs, inherited_reference_warnings=inherited,
                netlist_output_port_warning_count=len(entries),
                netlist_warning_groups=[dict(primitive=p, code=c, count=n) for (p, c), n in sorted(counts.items())],
                vendor_models={str(UNISIMS / (p + '.v')): sha(UNISIMS / (p + '.v')) for p in models},
                netlist_warning_inventory=entries,
                interpretation='All netlist diagnostics concern narrower or unconnected primitive OUTPUT ports; exact synthesized netlist namespace transformation is checked by the original auditor. The 13 non-netlist warnings are identical to the accepted RTL reference; hold_r uses strict ===1. This is a fixed-fixture functional review, not a waiver of physical or arbitrary-input correctness checks.')


def readonly_original_audit():
    source = ROOT / 'scripts/audit_stage_static_cp_shadow_system_v7.py'
    tree = ast.parse(source.read_text(), filename=str(source))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    assert ast.unparse(function.body[-3]) == "assert not (p / 'source_bound_audit.json').exists()"
    assert '.write_text(' in ast.unparse(function.body[-2]) and isinstance(function.body[-1], ast.Expr)
    # Keep every original evidence assertion and result construction; remove
    # only the final absence guard, report write and print. Frozen tool unchanged.
    function.body = function.body[:-3] + [ast.Return(value=ast.Name(id='result', ctx=ast.Load()))]
    ast.fix_missing_locations(tree)
    env = dict(__file__=str(source), __name__='readonly_terminal_review')
    old = sys.argv
    try:
        sys.argv = [str(source), str(P)]
        exec(compile(tree, str(source), 'exec'), env)
        return env['main']()
    finally:
        sys.argv = old


def main():
    assert not OUT.exists()
    receipt_path = ROOT / 'results/stage_static_cp_shadow_v7_terminal_preservation_20261102.json'
    receipt, supervisor, manifest = read(receipt_path), read(S / 'manifest.json'), read(P / 'manifest.json')
    assert receipt['status'] == supervisor['status'] == 'terminal_audited_and_actual_restored_awaiting_main_review'
    assert supervisor['stage'] == 'complete' and not supervisor.get('active_process')
    assert supervisor['terminal_report_sha256'] == sha(receipt_path)
    assert receipt['original_preserved'] == str(O) and receipt['actual_restore'] == str(P)
    assert supervisor['tool_sha256'] == receipt['supervisor_tool_sha256'] == sha(ROOT / 'scripts/research_checks/supervise_full_shadow_v7_v1.py')
    for m in [supervisor, manifest]:
        assert not m.get('active_process') and identity(m['runner_pid']) != str(m['runner_start_ticks'])
    assert supervisor['commands'] == receipt['commands']
    assert [c['stage'] for c in supervisor['commands']] == ['full_run', 'terminal_audit', 'restored_reaudit']
    for c in supervisor['commands']:
        assert c['exit_code'] == 0 and identity(c['pid']) != str(c['start_ticks'])
        assert sha(S / (c['stage'] + '.log')) == c['log_sha256']
    expected = receipt['file_sha256']
    assert len(expected) == 687 and supervisor['files'] == len(expected)
    archive = Path(receipt['archive'])
    assert sha(archive) == receipt['archive_sha256'] == supervisor['archive_sha256']
    archived = {}
    with tarfile.open(archive, 'r|gz') as tf:
        for member in tf:
            path = Path(member.name)
            assert member.isfile() and not path.is_absolute() and '..' not in path.parts
            assert member.name in expected and member.name not in archived
            with tf.extractfile(member) as stream:
                archived[member.name] = stream_sha(stream)
    assert archived == expected == inventory(O) == inventory(P)
    assert (O / 'source_bound_audit.json').read_bytes() == (P / 'source_bound_audit.json').read_bytes() == (S / 'expected_restored_audit.json').read_bytes()
    print('687 archive/original/restored files verified', flush=True)
    warning_review = diagnostics()
    print('4888 warnings source-classified; no errors/fatal/critical', flush=True)
    audit = read(P / 'source_bound_audit.json')
    assert audit['auditor_sha256'] == sha(ROOT / 'scripts/audit_stage_static_cp_shadow_system_v7.py')
    assert readonly_original_audit() == audit
    assert inventory(P) == expected, 'Read-only review must not mutate the run'
    reports = [receipt_path, S / 'manifest.json', P / 'manifest.json', P / 'source_bound_audit.json',
               ROOT / 'results/stage_static_cp_shadow_v7_preparation_review_20261102.json',
               ROOT / 'results/stage_static_cp_shadow_v7_launch_review_20261102.json',
               ROOT / 'results/stage_static_cp_shadow_v7_terminal_auditor_delta_review_20261102.json',
               ROOT / 'results/shadow_ka_dependency_gate_review_20261102.json',
               ROOT / 'results/shadow_fixture_ready_controls_v3_review_20261102.json',
               ROOT / 'results/ka_publication_release_full_rtl_v5_counterexample_review_20261102.json',
               ROOT / 'results/ka_publication_release_contract_lineage_review_20261102.json']
    result = dict(status='full_shadow_v7_actual_restore_main_reviewed',
                  time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  reviewer_sha256=sha(Path(__file__)), evidence_sha256={str(f): sha(f) for f in reports},
                  run_root=str(P), original_preserved=str(O), archive=str(archive), archive_sha256=sha(archive),
                  files=687, archive_original_restored_all_sha_identical=True,
                  readonly_original_auditor_all_assertions_passed=True, deterministic_audit_identical=True,
                  original_and_restored_audits_byte_identical=True, audit=audit, diagnostics=warning_review,
                  full_system_functional_netlist_validated=True, physical_gate_open=False,
                  timing_qualified=False, board_acceptance=False, all_pin_strict_equivalence=False,
                  controls_rerun=False, simulation_rerun=False, production_rtl_modified=False,
                  scope=audit['scope'],
                  retained_limitations=[
                      'Original full shadow v6 remains failed; v7 uses independently validated fixture-ready policy.',
                      'Publication start/release full-RTL v5 counterexample is retained. External caller arbitration and a production fix remain unresolved; this fixed fixture does not cover that race.',
                      'Physical input gate must be newly bound to accepted v7 and recovered synthesis; legacy gate still targets failed v6/old host. No physical job is authorized by this acceptance report itself.',
                      'Supervisor automatic receipt remains historical awaiting_main_review/false. This separately bound report records the completed review without rewriting it.'])
    with OUT.open('x') as f:
        f.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('FULL_SHADOW_V7_MAIN_REVIEW_ACCEPTED', OUT, flush=True)


if __name__ == '__main__':
    main()
