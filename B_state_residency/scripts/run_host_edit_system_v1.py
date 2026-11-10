"""Run one real-port extension after restored matrix and descriptor probes."""
from pathlib import Path
import copy
import os
import shutil
import subprocess
import sys
import time
from host_edit_system_common_v1 import (ROOT, BASE, REFERENCE, TARGETS, CHANGED,
    sha, read, identity, predecessors, sources)


def main():
    p = Path(sys.argv[1]).resolve()
    mode = next((name for name, path in TARGETS.items() if p == path), None)
    assert mode is not None and not p.exists()
    gates = predecessors(mode)  # No directory or process before all predecessors.
    rm, _, tb, original, files = sources()
    assert not os.environ.get('LD_PRELOAD'), 'Keep the working XSim environment'
    files += list(map(Path, gates))
    p.mkdir(); src = p / 'sources'; src.mkdir(); d = p / 'pressure'; d.mkdir(); bound = p / 'bound'; bound.mkdir()
    m = copy.deepcopy(rm)
    m.pop('active_process', None)
    for key in ['checkpoint_edit_reference', 'checkpoint_edit_reference_audit_sha256', 'checkpoint_edit_evidence']:
        m.pop(key, None)
    m.update(status='running', stage='wait_memory', mode=mode, runner_pid=os.getpid(),
        runner_start_ticks=identity(os.getpid()), runner_sha256=sha(__file__), predecessors=gates,
        host_edit_original=str(REFERENCE), cases={'pressure':dict(status='running',commands=[])}, bound={},
        runtime=dict(LD_PRELOAD=None, simulator='XSim 2022.2'),
        scope='Separate real host lane8 edit after four original real queries. Full original trace prefix, exact suffix semantics and source binding required. CP must exactly match all27 outputs/cycles of the actual restored extended baseline. No timing or board claim.')
    for i, source in enumerate(dict.fromkeys(files)):
        name = f'{i:02d}_{source.name}'; shutil.copyfile(source, bound / name)
        m['bound'][name] = dict(source=str(source), sha256=sha(source))
        assert sha(bound / name) == m['bound'][name]['sha256']
    for n, e in rm['sources'].items():
        assert sha(REFERENCE / 'sources' / n) == e['sha256']
        q = src / n; q.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(REFERENCE / 'sources' / n, q)
    if mode == 'baseline':
        for n in CHANGED:
            source = BASE / 'query_native_synth_v1/sources' / n
            shutil.copyfile(source, src / n); m['sources'][n] = dict(path=str(source), sha256=sha(source))
    shutil.copyfile(tb, src / 'tb_query_fault.sv')
    m['sources']['tb_query_fault.sv'] = dict(path=str(tb), sha256=sha(tb))
    shutil.copyfile(Path(__file__), src / 'runner.py')
    m['sources']['runner.py'] = dict(path=str(Path(__file__).resolve()), sha256=sha(__file__))
    for n in original[mode]['rtl']:
        assert sha(src / n) == original[mode]['sources'][n]
    for key in ['scoreboards', 'next_scoreboards', 'third_scoreboards', 'fourth_scoreboards']:
        for n, digest in rm[key].items():
            assert sha(REFERENCE / n) == digest; shutil.copyfile(REFERENCE / n, p / n)
    assert sha(rm['binding']) == rm['binding_sha256']
    regions = read(rm['binding'])['regions']
    for name, key in [('design.bin', 'design'), ('cost.bin', 'cost_history_prices_nets')]:
        shutil.copyfile(regions[key]['path'], d / name)
    with (d / 'owners.bin').open('wb') as dest:
        for key in ['owners', 'owner_pool', 'owner_allocator']:
            with Path(regions[key]['path']).open('rb') as source:
                shutil.copyfileobj(source, dest)
    for name in ['g3.bin', 'snapshot.bin', 'pool.bin']:
        shutil.copyfile(d / 'owners.bin', d / name)
    shutil.copyfile(regions['owner_allocator']['path'], d / 'allocator.bin')
    with (d / 'labels.bin').open('wb') as dest:
        dest.truncate(3145728)
    for f in src.rglob('*.dat'):
        shutil.copyfile(f, d / f.name)
    shutil.copyfile(REFERENCE / 'pressure/run.tcl', d / 'run.tcl'); m['run_tcl_sha256'] = sha(d / 'run.tcl')

    def save():
        temp = p / 'manifest.pending.json'; temp.write_text(__import__('json').dumps(m, indent=2, sort_keys=True)+'\n')
        temp.replace(p / 'manifest.json')

    def validate():
        for name, e in m['bound'].items():
            assert sha(e['source']) == e['sha256'] == sha(bound / name), name
        for n, e in m['sources'].items():
            assert sha(src / n) == e['sha256'], n
        assert sha(d / 'run.tcl') == m['run_tcl_sha256']

    save()
    try:
        stable = None; deadline = time.monotonic() + 10800
        while True:
            now = time.monotonic(); cg = Path('/sys/fs/cgroup')
            current, limit = int((cg/'memory.current').read_text()), int((cg/'memory.max').read_text())
            stable = (now if stable is None else stable) if current*4 <= limit*3 else None
            seconds = 0 if stable is None else now-stable
            m['memory_admission'] = dict(current_bytes=current, limit_bytes=limit, stable_seconds=seconds); save()
            if seconds >= 60:
                break
            assert now < deadline, 'Memory observation expired before launching a solver'
            time.sleep(10)
        for old in rm['cases']['pressure']['commands']:
            validate(); stage = old['stage']; argv = [a.replace(str(REFERENCE), str(p)) for a in old['argv']]
            m['stage'] = stage; save(); start = time.monotonic()
            with (d / (stage+'.stdout.log')).open('w') as log:
                child = subprocess.Popen(argv, cwd=d, stdout=log, stderr=subprocess.STDOUT)
                ticks = identity(child.pid); m['active_process'] = dict(pid=child.pid,start_ticks=ticks,stage=stage,argv=argv); save()
                try:
                    code = child.wait(timeout=7200)
                except subprocess.TimeoutExpired:
                    m.update(status='observation_timeout',error='Keep the original child; inspect its identity, do not restart or kill it'); save(); raise
            m.pop('active_process',None)
            m['cases']['pressure']['commands'].append(dict(stage=stage,argv=argv,pid=child.pid,start_ticks=ticks,
                exit_code=code,elapsed_s=time.monotonic()-start,stdout_sha256=sha(d/(stage+'.stdout.log')))); save()
            assert code == 0, stage
            print('HOST_EDIT_SYSTEM',mode,stage,'exit0',flush=True)
        log = (d/'simulate.log').read_text()
        for marker in ['HOST_EDIT_NATIVE_PASS','FOURTH_WARM_PASS polls=83 expands=82 candidates=402 costs=231',
                       'CHECKPOINT_EDIT_EXCLUSION_PASS','ITER2_CONTINUOUS_PREP_PASS','$finish called']:
            assert marker in log, marker
        assert 'Fatal:' not in log and 'ERROR:' not in log
        m.update(status='observed',stage='complete'); m['cases']['pressure']['status']='observed'
    except Exception as exc:
        if m['status'] != 'observation_timeout':
            m.update(status='failed',error=repr(exc))
        raise
    finally:
        save()
    print('HOST_EDIT_SYSTEM_OBSERVED',p)


if __name__ == '__main__':
    main()
