"""Persist and actually restore the v7 main-review evidence bundle."""
from pathlib import Path
import datetime
import json
import shutil
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from shadow_recovered_evidence_v7 import sha, read

BASE = Path('/tmp/B_state_residency_recovery_20261102')
P = BASE / 'stage_static_cp_shadow_system_v7'
S = BASE / 'stage_static_cp_shadow_system_v7_supervision_v1'
FREEZE = ROOT / 'results/stage_static_cp_shadow_system_v7_sources_20261103'
RESTORE = BASE / 'stage_static_cp_shadow_v7_review_actual_restore_20261103'
ARCHIVE = ROOT / 'results/recovery_archives_20261102/stage_static_cp_shadow_v7_review_20261103.tar.gz'
OUT = ROOT / 'results/stage_static_cp_shadow_system_v7_20261103.json'


def main():
    review_path = ROOT / 'results/stage_static_cp_shadow_system_v7_main_review_20261103.json'
    review = read(review_path)
    assert review['status'] == 'full_shadow_v7_actual_restore_main_reviewed'
    assert review['full_system_functional_netlist_validated'] and not review['physical_gate_open']
    assert review['audit'] == read(P / 'source_bound_audit.json')
    reviewer = ROOT / 'scripts/research_checks/review_full_shadow_v7_terminal_v1.py'
    assert sha(reviewer) == review['reviewer_sha256']
    for source, digest in review['evidence_sha256'].items():
        assert sha(source) == digest
    assert sha(review['archive']) == review['archive_sha256']
    assert all(not path.exists() for path in [FREEZE, RESTORE, ARCHIVE, OUT])
    FREEZE.mkdir()
    files = {}

    def copy(source, relative):
        source, relative = Path(source), Path(relative)
        assert not source.is_symlink() and not (FREEZE / relative).exists()
        dest = FREEZE / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
        digest = sha(source)
        assert sha(dest) == digest
        files[str(relative)] = dict(source=str(source), sha256=digest)

    for directory in ['sources', 'bound']:
        for source in sorted((P / directory).rglob('*')):
            assert not source.is_symlink()
            if source.is_file():
                copy(source, source.relative_to(P))
    for name in ['manifest.json', 'preparation.json', 'namespace.json', 'input_plan.json', 'source_bound_audit.json']:
        copy(P / name, Path('run') / name)
    for name in ['run.tcl', 'compile.stdout.log', 'elaborate.stdout.log', 'simulate.stdout.log', 'simulate.log',
                 'shadow_cp_export.log', 'shadow_ka_requests.log', 'shadow_pw_beats.log']:
        copy(P / 'full' / name, Path('run/full') / name)
    for source in sorted(S.iterdir()):
        assert source.is_file() and not source.is_symlink()
        copy(source, Path('supervision') / source.name)
    for source in [Path(s) for s in review['evidence_sha256']] + [review_path]:
        if source.is_relative_to(ROOT / 'results'):
            copy(source, Path('reports') / source.name)
    tools = {ROOT / 'scripts' / name for name in read(P / 'preparation.json')['tools']}
    tools.update([reviewer, Path(__file__), ROOT / 'scripts/research_checks/supervise_full_shadow_v7_v1.py',
                  ROOT / 'scripts/audit_stage_static_cp_shadow_system_v7.py',
                  ROOT / 'scripts/check_shadow_payload_transfer_logs_v1.py'])
    for source in sorted(tools):
        copy(source, Path('tools') / source.relative_to(ROOT / 'scripts'))
    for source, digest in review['diagnostics']['vendor_models'].items():
        assert sha(source) == digest
        copy(source, Path('vendor_model_port_review') / Path(source).name)
    frozen_manifest = dict(status='frozen', files=files, main_review_sha256=sha(review_path),
                           full_system_functional_netlist_validated=True, physical_gate_open=False,
                           timing_qualified=False, board_acceptance=False, all_pin_strict_equivalence=False)
    (FREEZE / 'manifest.json').write_text(json.dumps(frozen_manifest, indent=2, sort_keys=True) + '\n')
    expected = {n: e['sha256'] for n, e in files.items()}
    expected['manifest.json'] = sha(FREEZE / 'manifest.json')
    with tarfile.open(ARCHIVE, 'w:gz') as tf:
        for name in sorted(expected):
            tf.add(FREEZE / name, arcname=name, recursive=False)
    RESTORE.mkdir()
    seen = set()
    with tarfile.open(ARCHIVE, 'r|gz') as tf:
        for member in tf:
            path = Path(member.name)
            assert member.isfile() and not path.is_absolute() and '..' not in path.parts
            assert member.name in expected and member.name not in seen
            seen.add(member.name)
            dest = RESTORE / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            with tf.extractfile(member) as inp, dest.open('xb') as out:
                shutil.copyfileobj(inp, out, 1 << 20)
            assert sha(dest) == expected[member.name] == sha(FREEZE / path)
    assert seen == set(expected)
    assert read(RESTORE / 'manifest.json') == frozen_manifest
    assert read(RESTORE / 'reports' / review_path.name) == review
    result = dict(status='full_capacity_fixture_ready_shadow_main_reviewed_frozen_actual_restored',
                  time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  freezer_sha256=sha(Path(__file__)), main_review=str(review_path), main_review_sha256=sha(review_path),
                  audit=review['audit'], terminal_archive=review['archive'], terminal_archive_sha256=review['archive_sha256'],
                  freeze_root=str(FREEZE), freeze_manifest_sha256=sha(FREEZE / 'manifest.json'),
                  review_archive=str(ARCHIVE), review_archive_sha256=sha(ARCHIVE), review_archive_bytes=ARCHIVE.stat().st_size,
                  review_actual_restore=str(RESTORE), frozen_files=len(files), archived_files=len(expected),
                  all_review_files_actual_restored_sha_identical=True, full_system_functional_netlist_validated=True,
                  physical_gate_open=False, timing_qualified=False, board_acceptance=False, all_pin_strict_equivalence=False,
                  production_rtl_modified=False, simulation_rerun=False, controls_rerun=False,
                  scope=review['scope'], retained_limitations=review['retained_limitations'])
    with OUT.open('x') as f:
        f.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('FULL_SHADOW_V7_REVIEW_FROZEN_ACTUAL_RESTORED', len(expected), sha(ARCHIVE), flush=True)


if __name__ == '__main__':
    main()
