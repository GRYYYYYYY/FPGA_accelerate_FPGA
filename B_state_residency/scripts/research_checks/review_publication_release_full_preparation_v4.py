"""Independent source/input/path review; archive preparation, never accept simulation."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[2]
BASE = Path('/tmp/B_state_residency_recovery_20261102')
OLD = Path('/tmp/B_state_residency_offer_20261025')
RUN = BASE / 'ka_publication_release_full_rtl_v4'


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def read(p):
    return json.loads(p.read_text())


def main():
    pr = read(RUN / 'preparation.json')
    ref = BASE / 'stage_static_cp_host_full_static_v1'
    rm = read(ref / 'manifest.json')
    assert pr['status'] == 'prepared_not_running'
    assert not (RUN / 'manifest.json').exists() and not list((RUN / 'full').glob('*.bin'))
    assert pr['execution_authority_resolved'] is False and pr['old_host_backend_status'] == 'unconfirmed'
    assert sha(ref / 'source_bound_audit.json') == pr['reference_audit_sha256'] == 'f087aaff4c300605867c02d9fadf149b67125ebb6d9e13f6599edc7dbd01c770'
    assert rm['parameters'] == pr['parameters'] == read(ROOT / 'results/ka_publication_release_full_rtl_v2_preparation_review_20261101.json')['parameters']
    assert len(pr['parameters']) == 13 and pr['parameters']['SLOTS'] == 32
    production = [n for n in rm['rtl'] if n not in ['tb_query_fault.sv', 'tb_directory_observer.sv', 'axi_file_memory.sv']]
    assert len(production) == 133 and len(rm['rtl']) == 136
    vf = ROOT / 'results/stage_static_cp_shadow_v6_failure_preservation_20261031.json'
    assert sha(vf) == pr['source_comparison_report_sha256']
    historical = read(vf)['files']['stage_static_cp_shadow_system_v6']
    assert set(pr['production_sha256']) == set(production)
    for n in production:
        assert sha(RUN / 'sources' / n) == sha(ref / 'sources' / n) == historical['sources/' + n] == pr['production_sha256'][n]
    assert set(pr['sources']) == set(rm['sources'])
    for n, digest in pr['sources'].items():
        assert sha(RUN / 'sources' / n) == digest
        if n != 'tb_query_fault.sv':
            assert digest == rm['sources'][n]['sha256']
    # Extract only literal stimulus constants from the frozen predecessor; never execute it.
    parent = ROOT / 'scripts/research_checks/prepare_publication_release_full_rtl_v2.py'
    assert sha(parent) == pr['parent_preparer_sha256']
    literals = {}
    for node in ast.parse(parent.read_text()).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ['call', 'task', 'anchor', 'objects']:
                    literals[target.id] = ast.literal_eval(node.value)
    assert literals['call'] == pr['verification_call'] and literals['task'] == pr['verification_task']
    original = (ref / 'sources/tb_query_fault.sv').read_text()
    assert original.count(literals['anchor']) == original.count('endmodule') == 1
    expected_tb = original.replace(literals['anchor'], literals['call'] + literals['anchor'], 1).replace('endmodule', literals['task'] + 'endmodule', 1)
    tb = RUN / 'sources/tb_query_fault.sv'
    assert tb.read_text() == expected_tb
    assert tb.read_bytes() == (ROOT / 'hardware/variants/ka_publication_release_full_rtl_v2/tb_query_fault.sv').read_bytes()
    expected_tcl = 'open_vcd probe.vcd\nlog_vcd [get_objects {' + ' '.join('/tb_candidate_offer/' + n.replace('.', '/') for n in literals['objects']) + '}]\nrun 200 us\nclose_vcd\nquit\n'
    assert (RUN / 'full/run.tcl').read_text() == expected_tcl and len(literals['objects']) == 14
    expected_commands = []
    for c in rm['cases']['full']['commands']:
        cmd = []
        for token in c['argv']:
            token = token.replace(str(OLD / ref.name), str(RUN))
            token = token.replace(str(OLD) + '/', str(BASE) + '/')
            token = token.replace(str(ROOT / 'results/transaction_fence_static_join_rtl_v1/authority.txt'), str(BASE / 'transaction_fence_static_join_rtl_v1/authority.txt'))
            cmd.append(token)
        if Path(cmd[0]).name == 'xsim':
            cmd += ['-onfinish', 'stop']
        expected_commands.append(cmd)
    assert pr['commands'] == expected_commands and len(expected_commands) == 3
    readonly = {}
    for token in expected_commands[-1]:
        if '=' not in token:
            continue
        _, value = token.split('=', 1)
        path = Path(value)
        if path.is_absolute() and not path.is_relative_to(RUN / 'full'):
            readonly[value] = {'bytes': path.stat().st_size, 'sha256': sha(path)}
    assert readonly == pr['read_only_inputs']
    for group in ['scoreboards', 'next_scoreboards', 'third_scoreboards', 'fourth_scoreboards']:
        for n, h in rm[group].items():
            assert sha(RUN / n) == h
    plan = read(RUN / 'input_plan.json')
    assert sha(RUN / 'input_plan.json') == pr['input_plan_sha256']
    assert sha(Path(plan['binding'])) == plan['binding_sha256'] == rm['binding_sha256']
    original_regions = read(Path(plan['binding']))['regions']
    keys = ['design', 'owners', 'owner_pool', 'owner_allocator', 'cost_history_prices_nets']
    assert plan['original_regions'] == {k: original_regions[k] for k in keys}
    assert plan['regions'] == {k: dict(original_regions[k], path=str(BASE / Path(original_regions[k]['path']).relative_to(OLD))) for k in keys}
    for e in plan['regions'].values():
        assert Path(e['path']).stat().st_size == e['bytes'] and sha(Path(e['path'])) == e['sha256']
    assert pr['memory_policy'] == {'total_current_max_gib': 225, 'stable_seconds': 60, 'poll_seconds': 5}
    scripts = [ROOT / 'scripts/research_checks' / n for n in [
        'prepare_publication_release_full_rtl_v4.py', 'run_publication_release_full_rtl_v4.py',
        'audit_publication_release_full_rtl_v4.py', 'review_publication_release_full_preparation_v4.py']]
    for script in scripts:
        compile(script.read_text(), str(script), 'exec')
    guard = subprocess.run([sys.executable, '-B', str(scripts[1])], capture_output=True, text=True)
    assert guard.returncode == 1 and 'NOT_STARTED: old-host backend status is unconfirmed' in guard.stderr
    assert not (RUN / 'manifest.json').exists() and not list((RUN / 'full').glob('*.bin'))
    files = {RUN.name + '/' + p.relative_to(RUN).as_posix(): p for p in RUN.rglob('*') if p.is_file()}
    for p in scripts + [ROOT / 'scripts/research_checks/check_publication_release_full_probe_v1.py']:
        files['review_tools/' + p.name] = p
    expected = {n: sha(p) for n, p in files.items()}
    archive = ROOT / 'results/recovery_archives_20261102/ka_publication_release_full_rtl_v4_prepared.tar.gz'
    restored = BASE / 'ka_publication_release_full_rtl_v4_preparation_restore'
    assert not archive.exists() and not restored.exists()
    partial = archive.with_name(archive.name + '.partial')
    assert not partial.exists()
    with tarfile.open(partial, 'w:gz', compresslevel=3) as tf:
        for n, p in sorted(files.items()):
            assert not p.is_symlink()
            tf.add(p, arcname=n, recursive=False)
    restored.mkdir()
    with tarfile.open(partial) as tf:
        seen = set()
        for item in tf:
            rel = Path(item.name)
            assert not rel.is_absolute() and '..' not in rel.parts and item.isfile()
            assert item.name in expected and item.name not in seen
            seen.add(item.name)
            p = restored / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            with tf.extractfile(item) as inp, p.open('xb') as out:
                shutil.copyfileobj(inp, out, 1 << 20)
            assert sha(p) == expected[item.name]
        assert seen == set(expected)
    assert {n: sha(p) for n, p in files.items()} == expected
    partial.rename(archive)
    report = {'status': 'new_host_full_RTL_probe_preparation_reviewed_not_executed',
              'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'run': str(RUN), 'production_count': 133, 'compile_files': 136, 'parameters': pr['parameters'],
              'preparation_sha256': sha(RUN / 'preparation.json'), 'readonly_input_count': len(readonly),
              'runner_default_rejection': {'exit_code': guard.returncode, 'message': guard.stderr.strip()},
              'archive': str(archive), 'archive_sha256': sha(archive), 'archive_bytes': archive.stat().st_size,
              'actual_restore': str(restored), 'file_sha256': expected,
              'scope': 'Exact original full RTL and additive cold-prefix probe; path/input recovery only. Prepared runner requires explicit authorization of an independent new-host attempt while old-host backend status is unconfirmed.',
              'full_system_functional_netlist_validated': False, 'physical_gate_open': False}
    output = ROOT / 'results/ka_publication_release_full_rtl_v4_preparation_review_20261102.json'
    assert not output.exists()
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['status', 'production_count', 'readonly_input_count', 'archive_sha256']}))


if __name__ == '__main__':
    main()
