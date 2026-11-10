"""Single owner: admit memory, prepare one stage OOC, inspect and actually restore it."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import time
from run_checkpoint_authority import ROOT, sha

p = Path(sys.argv[1]).resolve()
assert p.name == 'route_stage_synth_followup_v1'
base = p.parent
target = base/'route_stage_synth_v1'
full = base/'route_stage_system_crc_pressure_v1'
gate = json.loads((base/'route_stage_system_followup_v1/manifest.json').read_text())
assert gate['status'] == 'observed' and gate['stage'] == 'complete'
a = json.loads((full/'source_bound_audit.json').read_text())
rp = ROOT/'results/route_stage_system_crc_pressure_v1_restore_20261025.json'
r = json.loads(rp.read_text())
assert a['status'] == r['status'] == 'passed' and r['audit_byte_identical']
assert r['audit_sha256'] == sha(full/'source_bound_audit.json')
assert a['manifest_sha256'] == sha(full/'manifest.json')
assert len(a['exact_comparisons']) == 27
assert all(a['route_stage_bank'][k] > 0 for k in ['captures', 'imports', 'checked_cycles'])
freeze = ROOT/'results/route_stage_system_crc_sources_20261029'
fm = json.loads((freeze/'manifest.json').read_text())
assert fm['status'] == 'frozen'
for name, entry in fm['files'].items():
    assert sha(freeze/name) == entry['sha256'], name
assert not target.exists(), 'Do not resubmit an existing experiment'
assert not (ROOT/'results/route_stage_synth_20261029.json').exists()
assert not (ROOT/'results/route_stage_synth_sources_20261029').exists()
p.mkdir()
shutil.copyfile(Path(__file__), p/'runner.py')
names = [
    'scripts/prepare_route_stage_synth.py', 'scripts/audit_route_stage_synth.py',
    'scripts/freeze_route_stage_synth.py', 'scripts/run_restore_seed_synth.py',
    'scripts/inspect_restore_seed_synth.py', 'scripts/analyze_restore_seed_loops.py',
    'scripts/audit_restore_seed_diagnostics.py', 'scripts/archive_offer_result.py',
    'scripts/verify_search_retire_restore.py', 'scripts/run_checkpoint_authority.py',
    'scripts/prepare_checkpoint_edit_monitor.py',
    'scripts/analyze_route_stage_write_factoring_v2.py',
    'scripts/audit_route_stage_system.py', 'scripts/freeze_route_stage_system.py',
    'hardware/variants/route_stage_system_v1/build.py',
    'hardware/variants/route_stage_write_v1/build.py',
    'hardware/variants/route_stage_write_v1/manifest.json',
    'hardware/variants/route_stage_write_v1/baseline/route_commit_controller.sv',
    'hardware/variants/route_stage_write_v1/baseline/route_commit_host_adapter.sv',
    'hardware/variants/route_stage_write_v1/fixed/route_commit_controller.sv',
    'hardware/variants/route_stage_write_v1/fixed/route_commit_host_adapter.sv',
    'results/route_stage_write_factoring_20261029.json',
    'results/route_stage_system_crc_20261029.json',
    'results/route_stage_system_crc_sources_20261029/manifest.json',
    'results/route_stage_system_crc_pressure_v1_restore_20261025.json',
]
bound = {}
for name in names:
    dest = p/'bound'/name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT/name, dest)
    bound[name] = sha(ROOT/name)
    assert sha(dest) == bound[name]
m = dict(status='running', stage='wait_memory_before_prepare', target=str(target),
         runner_pid=os.getpid(),
         runner_start_ticks=Path('/proc/self/stat').read_text().split(') ', 1)[1].split()[19],
         runner_sha256=sha(p/'runner.py'), bound=bound, commands=[],
         full_system_audit_sha256=sha(full/'source_bound_audit.json'),
         memory_admission_fraction=0.75, memory_stable_seconds=60,
         scope='One new stage OOC after completed full-system actual restoration. '
               'Wait for 60 seconds below 75% shared memory, then prepare/run once; '
               'independent DCP inspection, audit, archive, actual restore, freeze. '
               'No automatic retry, repair, or interference with unrelated processes. '
               'Memory admission is not a hard cap on concurrent external jobs.')


def save():
    tmp = p/'manifest.pending.json'
    tmp.write_text(json.dumps(m, indent=2, sort_keys=True)+'\n')
    tmp.replace(p/'manifest.json')


def check_bound():
    for name, digest in bound.items():
        assert sha(ROOT/name) == digest == sha(p/'bound'/name), name


def memory():
    c = Path('/sys/fs/cgroup')
    return int((c/'memory.current').read_text()), int((c/'memory.max').read_text())


def admit_memory(stage):
    m['stage'] = stage
    deadline = time.monotonic()+10800
    stable_since = None
    print('WAIT_MEMORY', stage, flush=True)
    while True:
        now = time.monotonic()
        current, limit = memory()
        if current*4 <= limit*3:
            if stable_since is None:
                stable_since = now
        else:
            stable_since = None
        stable = 0 if stable_since is None else now-stable_since
        m['memory_observation'] = dict(current_bytes=current, limit_bytes=limit,
                                       stable_seconds=stable, checked_unix_s=time.time())
        save()
        if stable >= 60:
            check_bound()
            return
        assert now < deadline, 'Memory admission wait expired; no next stage submitted'
        time.sleep(10)


def run(stage, args, timeout=None):
    check_bound()
    m['stage'] = stage
    argv = [sys.executable, '-B', *map(str, args)]
    print('START', stage, flush=True)
    start = time.monotonic()
    with (p/(stage+'.log')).open('w') as f:
        child = subprocess.Popen(argv, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT)
        m['active_process'] = dict(pid=child.pid, argv=argv)
        save()
        code = child.wait(timeout=timeout)
    m['commands'].append(dict(stage=stage, argv=argv, pid=child.pid, exit_code=code,
                              elapsed_s=time.monotonic()-start,
                              log_sha256=sha(p/(stage+'.log'))))
    m.pop('active_process', None)
    save()
    assert code == 0, stage
    print('DONE', stage, flush=True)


save()
try:
    admit_memory('wait_memory_before_prepare')
    assert not target.exists(), 'Target appeared while waiting; do not resubmit'
    run('prepare', ['scripts/prepare_route_stage_synth.py', target], 180)
    current, limit = memory()
    if current*4 > limit*3:
        admit_memory('wait_memory_before_synth')
    run('synth', ['scripts/run_restore_seed_synth.py', target])
    admit_memory('wait_memory_before_inspect')
    run('inspect', ['scripts/inspect_restore_seed_synth.py', target])
    run('walks', ['scripts/analyze_restore_seed_loops.py', target], 180)
    run('audit', ['scripts/audit_route_stage_synth.py', target], 180)
    run('archive', ['scripts/archive_offer_result.py', target], 600)
    run('restore', ['scripts/verify_search_retire_restore.py', target.name,
                    'audit_route_stage_synth.py'], 600)
    run('freeze', ['scripts/freeze_route_stage_synth.py'], 180)
    m.update(status='observed', stage='complete')
except Exception as error:
    m.update(status='failed', error=repr(error))
    raise
finally:
    save()
print('ROUTE_STAGE_SYNTH_QUEUE_COMPLETED', flush=True)
