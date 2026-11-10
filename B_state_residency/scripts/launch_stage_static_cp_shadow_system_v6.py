"""Launch one fresh run and its sole followup; record host evidence without retries."""
from pathlib import Path
import datetime
import json
import os
import signal
import subprocess
import sys
import time

from host_edit_system_common_v1 import ROOT, BASE, read, sha, identity

TARGET = BASE/'stage_static_cp_shadow_system_v6'
FOLLOWUP = BASE/'stage_static_cp_shadow_system_v6_followup_v1'
OWNER = BASE/'stage_static_cp_shadow_system_v6_lifecycle_v1'


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def process_rows(owner_pid, remembered):
    rows = {}
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():
            continue
        try:
            fields = (p/'stat').read_text().rsplit(')', 1)[1].split()
            rows[int(p.name)] = dict(pid=int(p.name), ppid=int(fields[1]), state=fields[0],
                                    start_ticks=fields[19], cpu_ticks=int(fields[11])+int(fields[12]),
                                    rss_bytes=int(fields[21])*os.sysconf('SC_PAGE_SIZE'))
        except (OSError, IndexError, ValueError):
            continue
    selected = {owner_pid}
    selected.update(pid for pid, ticks in remembered.items() if pid in rows and rows[pid]['start_ticks'] == ticks)
    while True:
        children = {pid for pid, row in rows.items() if row['ppid'] in selected}
        if children <= selected:
            break
        selected |= children
    result = []
    for pid in sorted(selected):
        if pid not in rows:
            continue
        row = rows[pid]
        remembered[pid] = row['start_ticks']
        try:
            row['cmdline'] = Path('/proc', str(pid), 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
        except OSError:
            row['cmdline'] = None
        result.append(row)
    return result


def resource_sample(owner_pid, remembered):
    cg = Path('/sys/fs/cgroup')
    def pairs(name):
        return {k: int(v) for k, v in (line.split() for line in (cg/name).read_text().splitlines())}
    stats = pairs('memory.stat')
    disks = {}
    for path in [str(ROOT), '/tmp']:
        fs = os.statvfs(path)
        disks[path] = dict(available_bytes=fs.f_bavail*fs.f_frsize, free_inodes=fs.f_favail)
    return dict(utc=utc(), memory_current_bytes=int((cg/'memory.current').read_text()),
                memory_max=(cg/'memory.max').read_text().strip(), memory_events=pairs('memory.events'),
                memory_stat={k: stats[k] for k in ['anon', 'file', 'file_dirty', 'file_writeback', 'slab']},
                disk=disks, processes=process_rows(owner_pid, remembered))


def main():
    assert not TARGET.exists() and not FOLLOWUP.exists() and not OWNER.exists()
    preparation = ROOT/'results/stage_static_cp_shadow_system_v6_tools_preparation_20261030.json'
    prep = read(preparation)
    assert prep['status'] == 'full_capacity_shadow_v6_tools_prepared_not_executed'
    for name, digest in prep['tools'].items():
        assert sha(name) == digest
    preflight = ROOT/'results/stage_static_cp_shadow_system_v6_positive_preflight_20261030.json'
    pf = read(preflight)
    assert pf['status'] == 'preserved_interruption_unchanged_full_fixture_positive_gate_passed'
    assert pf['preparation_sha256'] == sha(preparation)
    OWNER.mkdir()
    (OWNER/'tools_binding.json').write_text(json.dumps(dict(tools=prep['tools'], preparation_sha256=sha(preparation),
        preflight_sha256=sha(preflight)), indent=2, sort_keys=True)+'\n')
    m = dict(status='running', stage='starting', runner_pid=os.getpid(), runner_start_ticks=identity(os.getpid()),
             started_utc=utc(), children={}, tool_sha256=sha(__file__),
             scope='One fresh full v6 run; sole followup owns audit/archive/restore/freeze. Read-only host sampling. No retries or child termination. Not a functional verdict.')
    children = {}
    logs = []
    remembered = {}
    def save():
        m['updated_utc'] = utc()
        p = OWNER/'manifest.pending.json'
        p.write_text(json.dumps(m, indent=2, sort_keys=True)+'\n')
        p.replace(OWNER/'manifest.json')
    def sample():
        row = resource_sample(os.getpid(), remembered)
        with (OWNER/'resources.jsonl').open('a') as f:
            f.write(json.dumps(row, sort_keys=True)+'\n')
            f.flush()
            os.fsync(f.fileno())
        m['last_resource_utc'] = row['utc']
        return row
    def start(name, script, destination):
        argv = [sys.executable, str(ROOT/'scripts'/script), str(destination)]
        f = (OWNER/(name+'.log')).open('w')
        logs.append(f)
        child = subprocess.Popen(argv, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=f,
                                 stderr=subprocess.STDOUT, start_new_session=True)
        children[name] = child
        m['children'][name] = dict(pid=child.pid, start_ticks=identity(child.pid), argv=argv, exit_code=None)
        save()
        print('START', name, child.pid, flush=True)
        return child
    def interrupted(signum, frame):
        m.update(status='interrupted', stage='owner_signal_children_preserved', signal=signum)
        save()
        raise SystemExit(128+signum)
    for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP]:
        signal.signal(sig, interrupted)
    save()
    try:
        initial = sample()
        m['initial_memory_events'] = initial['memory_events']
        m['stage'] = 'waiting_runner_manifest'
        runner = start('simulation', 'run_stage_static_cp_shadow_system_v6.py', TARGET)
        next_sample = time.monotonic()+30
        while not (TARGET/'manifest.json').exists():
            code = runner.poll()
            assert code is None, f'Runner exited {code} before manifest; no retry'
            if time.monotonic() >= next_sample:
                sample(); save(); next_sample = time.monotonic()+30
            time.sleep(2)
        # After followup launch the lifecycle owner never reads the target root:
        # its sole followup may be archiving/restoring it.
        start('followup', 'continue_stage_static_cp_shadow_system_v6.py', FOLLOWUP)
        m['stage'] = 'observing_children'
        while True:
            for name, child in children.items():
                m['children'][name]['exit_code'] = child.poll()
            if all(child.poll() is not None for child in children.values()):
                break
            if time.monotonic() >= next_sample:
                sample(); next_sample = time.monotonic()+30
            save()
            time.sleep(5)
        final = sample()
        m['memory_events_delta'] = {k: v-initial['memory_events'][k] for k, v in final['memory_events'].items()}
        m['followup_terminal_status'] = read(FOLLOWUP/'manifest.json')['status']
        assert all(child.returncode == 0 for child in children.values()), m['children']
        assert m['followup_terminal_status'] == 'observed'
        m.update(status='observed', stage='chain_complete_requires_main_review')
    except Exception as exc:
        m.update(status='failed', error=repr(exc))
        raise
    finally:
        for name, child in children.items():
            m['children'][name]['exit_code'] = child.poll()
        save()
        for f in logs:
            f.close()


if __name__ == '__main__':
    main()
