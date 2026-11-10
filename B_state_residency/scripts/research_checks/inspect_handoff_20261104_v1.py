"""Read-only handoff snapshot and key durable-artifact verification; no experiments."""
from pathlib import Path
import datetime
import json
import os
import shutil
import socket
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from shadow_recovered_evidence_v7 import sha, read, identity

BASE = Path('/tmp/B_state_residency_recovery_20261102')


def main():
    state_path = ROOT / 'results/session_handoff_state_20261104.json'
    artifact_path = ROOT / 'results/session_handoff_artifacts_20261104.json'
    assert not state_path.exists() and not artifact_path.exists()
    accepted_path = ROOT / 'results/stage_static_cp_shadow_system_v7_20261103.json'
    accepted = read(accepted_path)
    assert accepted['full_system_functional_netlist_validated'] and not accepted['physical_gate_open']
    main_review = Path(accepted['main_review'])
    assert sha(main_review) == accepted['main_review_sha256']
    review = read(main_review)
    assert accepted['audit'] == review['audit'] == read(BASE / 'stage_static_cp_shadow_system_v7/source_bound_audit.json')
    paths = [accepted_path, main_review,
             ROOT / 'results/stage_static_cp_shadow_v7_physical_prerequisites_20261103.json',
             ROOT / 'results/stage_static_cp_shadow_v7_review_completion_20261103.json',
             ROOT / 'results/stage_static_cp_shadow_v7_terminal_preservation_20261102.json',
             ROOT / 'results/shadow_fixture_ready_controls_v3_review_20261102.json',
             ROOT / 'results/shadow_ka_dependency_gate_review_20261102.json',
             ROOT / 'results/shadow_synthesis_new_host_recovery_review_20261102.json',
             ROOT / 'results/ka_publication_release_full_rtl_v5_counterexample_review_20261102.json',
             ROOT / 'results/ka_publication_release_contract_lineage_review_20261102.json',
             ROOT / 'results/ka_publication_release_full_rtl_v4_execution_authorization_20261102.json',
             Path(accepted['freeze_root']) / 'manifest.json',
             ROOT / 'scripts/research_checks/review_full_shadow_v7_terminal_v1.py',
             ROOT / 'scripts/research_checks/freeze_full_shadow_v7_review_v1.py',
             ROOT / 'scripts/research_checks/review_shadow_v7_physical_prerequisites_v1.py',
             ROOT / 'scripts/check_stage_static_cp_physical_inputs_v5.py',
             ROOT / 'hardware/scripts/implement_state_ooc.tcl', Path(__file__)]
    assert sha(Path(accepted['freeze_root']) / 'manifest.json') == accepted['freeze_manifest_sha256']
    archives = {}
    for name, expected in [(accepted['terminal_archive'], accepted['terminal_archive_sha256']),
                           (accepted['review_archive'], accepted['review_archive_sha256'])]:
        p = Path(name)
        assert sha(p) == expected
        archives[str(p)] = dict(bytes=p.stat().st_size, sha256=expected)
    runs = []
    for name in ['stage_static_cp_shadow_system_v7', 'stage_static_cp_shadow_system_v7_supervision_v1',
                 'shadow_fixture_ready_controls_v3', 'ka_publication_release_full_rtl_v5']:
        p = BASE / name / 'manifest.json'
        m = read(p)
        actual = identity(m['runner_pid'])
        alive = actual == str(m['runner_start_ticks'])
        assert not alive and not m.get('active_process')
        runs.append(dict(root=str(p.parent), manifest_sha256=sha(p), status=m['status'], stage=m.get('stage'),
                         pid=m['runner_pid'], recorded_start_ticks=m['runner_start_ticks'],
                         current_start_ticks=actual, original_process_alive=alive, active_process=m.get('active_process')))
        paths.append(p)
    excluded = set()
    pid = os.getpid()
    while pid > 0 and pid not in excluded:
        excluded.add(pid)
        try:
            stat = Path('/proc') / str(pid) / 'stat'
            pid = int(stat.read_text().rsplit(')', 1)[1].split()[1])
        except (OSError, ValueError):
            break
    matches = []
    markers = ['B_state_residency_recovery_20261102', 'B_state_residency_offer_20261025',
               'run_stage_static_cp_', 'supervise_full_shadow_', 'run_shadow_fixture_ready_', 'run_publication_release_full_']
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name) in excluded:
            continue
        try:
            cmd = (proc / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace').strip()
            if any(marker in cmd for marker in markers):
                matches.append(dict(pid=int(proc.name), start_ticks=identity(int(proc.name)), command=cmd))
        except (OSError, ValueError):
            continue
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cg = Path('/sys/fs/cgroup')
    state = dict(time_utc=now, hostname=socket.gethostname(), boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                 goal_tool_status=None, runs=runs, matched_local_processes=matches,
                 process_scan_scope='Local /proc command lines matching project scratch roots or named runners; excludes this inspection and ancestors. Does not establish current old-host state.',
                 memory_current_bytes=int((cg / 'memory.current').read_text()), memory_max=(cg / 'memory.max').read_text().strip(),
                 disk_free_bytes={str(p): shutil.disk_usage(p).free for p in [ROOT, Path('/tmp')]},
                 physical_roots_found=[str(p) for p in BASE.glob('stage_static_cp_physical*')],
                 full_system_functional_netlist_validated=True, physical_gate_open=False,
                 timing_qualified=False, board_acceptance=False, experiments_started=False)
    artifacts = dict(time_utc=now, status='handoff_key_reports_and_archives_rechecked',
                     files={str(p): dict(bytes=p.stat().st_size, sha256=sha(p)) for p in paths}, archives=archives,
                     scope='Handoff index, not a new scientific proof or replay. Full terminal and review archive SHA rechecked; previous actual-restore evidence retained. Controls and simulations not rerun.')
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + '\n')
    artifact_path.write_text(json.dumps(artifacts, indent=2, sort_keys=True) + '\n')
    print(json.dumps(state, indent=2))


if __name__ == '__main__':
    main()
