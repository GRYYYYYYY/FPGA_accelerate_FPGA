"""Single successor: finish stage observations, then measure the fixed CP physical anchor."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import time
from run_checkpoint_authority import ROOT, sha

p = Path(sys.argv[1]).resolve()
assert p.name == 'checkpoint_edit_physical_queue_v1'
base = p.parent
gate = base/'route_stage_synth_followup_v1'
target = base/'checkpoint_edit_physical_v1'
reference = base/'checkpoint_edit_synth_v1'
gm = json.loads((gate/'manifest.json').read_text())
assert gm['status'] in ['running','observed']
if gm['status'] == 'observed':
    assert gm['stage'] == 'complete'
parent_pid = gm['runner_pid']
parent_ticks = gm['runner_start_ticks']
proc = Path('/proc')/str(parent_pid)
if gm['status'] == 'running':
    assert proc.exists()
    assert (proc/'stat').read_text().split(') ',1)[1].split()[19] == parent_ticks
    assert b'run_route_stage_synth_queue.py' in (proc/'cmdline').read_bytes()
assert not target.exists()
for name in ['route_stage_timing_path_20261029.json','route_stage_tradeoff_20261029.json',
             'route_stage_timing_sources_20261029','checkpoint_edit_physical_20261029.json',
             'checkpoint_edit_physical_sources_20261029']:
    assert not (ROOT/'results'/name).exists(), name
p.mkdir()
shutil.copyfile(Path(__file__),p/'runner.py')
names = ['scripts/analyze_route_stage_timing.py','scripts/analyze_route_stage_tradeoff.py',
         'scripts/freeze_route_stage_analysis.py','scripts/prepare_state_ooc_physical.py',
         'scripts/run_state_ooc_physical.py','scripts/audit_state_ooc_physical_v2.py',
         'scripts/freeze_state_ooc_physical_v2.py','scripts/archive_offer_result.py',
         'scripts/verify_search_retire_restore.py','scripts/release_experiment_cache.py',
         'scripts/run_checkpoint_authority.py','hardware/scripts/implement_state_ooc.tcl',
         'results/state_full_physical_readiness_20261029.json',
         'results/state_ooc_physical_tools_preparation_20261029.json',
         'results/checkpoint_edit_synth_v1_restore_20261025.json']
bound = {}
items = [(name,ROOT/name) for name in names]
items += [('reference/'+name,reference/name) for name in ['manifest.json','source_bound_audit.json']]
for label,source in items:
    dest = p/'bound'/label
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,dest)
    bound[label] = dict(source=str(source),sha256=sha(source))
    assert sha(dest) == bound[label]['sha256']
m = dict(status='running',stage='wait_stage_chain',gate=str(gate),target=str(target),reference=str(reference),
         gate_pid=parent_pid,gate_start_ticks=parent_ticks,runner_pid=os.getpid(),
         runner_start_ticks=Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19],
         runner_sha256=sha(p/'runner.py'),bound=bound,commands=[],
         memory_admission_fraction=0.75,memory_stable_seconds=60,
         scope='Wait for the existing stage owner without restart. Own stage timing/tradeoff observation '
               'and their freeze, then one full-system physical measurement of the fixed, restored CP anchor. '
               'Never select/promote a candidate, change constraints, retry, repair, or stop unrelated jobs. '
               'Memory admission is not a hard cap on external jobs.')


def save():
    tmp = p/'manifest.pending.json'
    tmp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
    tmp.replace(p/'manifest.json')


def check_bound():
    for name,entry in bound.items():
        assert sha(Path(entry['source'])) == entry['sha256'] == sha(p/'bound'/name), name


def memory():
    c = Path('/sys/fs/cgroup')
    return int((c/'memory.current').read_text()),int((c/'memory.max').read_text())


def admit_memory(stage):
    m['stage'] = stage
    deadline = time.monotonic()+10800
    stable_since = None
    print('WAIT_MEMORY',stage,flush=True)
    while True:
        now = time.monotonic()
        current,limit = memory()
        if current*4 <= limit*3:
            if stable_since is None:
                stable_since = now
        else:
            stable_since = None
        stable = 0 if stable_since is None else now-stable_since
        m['memory_observation'] = dict(current_bytes=current,limit_bytes=limit,
                                       stable_seconds=stable,checked_unix_s=time.time())
        save()
        if stable>=60:
            check_bound()
            return
        assert now<deadline,'Memory admission expired; no next stage submitted'
        time.sleep(10)


def run(stage,args,timeout=None):
    check_bound()
    m['stage'] = stage
    argv = [sys.executable,'-B',*map(str,args)]
    print('START',stage,flush=True)
    start = time.monotonic()
    with (p/(stage+'.log')).open('w') as handle:
        child = subprocess.Popen(argv,cwd=ROOT,stdout=handle,stderr=subprocess.STDOUT)
        m['active_process'] = dict(pid=child.pid,argv=argv)
        save()
        code = child.wait(timeout=timeout)
    m['commands'].append(dict(stage=stage,argv=argv,pid=child.pid,exit_code=code,
                              elapsed_s=time.monotonic()-start,log_sha256=sha(p/(stage+'.log'))))
    m.pop('active_process',None)
    save()
    assert code==0,stage
    print('DONE',stage,flush=True)


save()
try:
    print('WAIT_EXISTING_STAGE_OWNER',parent_pid,flush=True)
    deadline = time.monotonic()+14400
    last_live = time.monotonic()
    while True:
        gm = json.loads((gate/'manifest.json').read_text())
        if gm['status']=='observed':
            assert gm['stage']=='complete'
            break
        assert gm['status']=='running',gm.get('error',gm['status'])
        if proc.exists():
            assert (proc/'stat').read_text().split(') ',1)[1].split()[19]==parent_ticks
            last_live = time.monotonic()
        else:
            assert time.monotonic()-last_live<30,'Stage owner missing without terminal manifest; never restart'
        assert time.monotonic()<deadline,'Observation timeout only; original owner is untouched'
        time.sleep(10)
    run('stage_timing',['scripts/analyze_route_stage_timing.py'],180)
    run('stage_tradeoff',['scripts/analyze_route_stage_tradeoff.py'],180)
    run('stage_analysis_freeze',['scripts/freeze_route_stage_analysis.py'],180)
    admit_memory('wait_memory_before_physical_prepare')
    assert not target.exists(),'Target appeared while waiting; do not resubmit'
    run('physical_prepare',['scripts/prepare_state_ooc_physical.py',target,reference],180)
    current,limit = memory()
    if current*4>limit*3:
        admit_memory('wait_memory_before_physical_run')
    run('physical_run',['scripts/run_state_ooc_physical.py',target])
    run('physical_audit',['scripts/audit_state_ooc_physical_v2.py',target],300)
    run('physical_archive',['scripts/archive_offer_result.py',target],900)
    run('physical_restore',['scripts/verify_search_retire_restore.py',target.name,
                            'audit_state_ooc_physical_v2.py'],900)
    run('physical_freeze',['scripts/freeze_state_ooc_physical_v2.py',target],300)
    run('physical_cache',['scripts/release_experiment_cache.py',target,base/'.preserved'/target.name,'--apply'],180)
    m.update(status='observed',stage='complete')
except Exception as error:
    m.update(status='failed',error=repr(error))
    raise
finally:
    save()
print('CHECKPOINT_EDIT_PHYSICAL_QUEUE_COMPLETED',flush=True)
