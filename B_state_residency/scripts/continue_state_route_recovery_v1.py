"""Single read-only waiter, then audit/archive/actual restore/freeze of one recovery."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import time
from run_checkpoint_authority import ROOT, sha

p=Path(sys.argv[1]).resolve(); target=p.parent/'checkpoint_edit_route_recovery_v1'
assert p.name=='checkpoint_edit_route_recovery_followup_v1' and not p.exists()
tm=json.loads((target/'manifest.json').read_text())
assert tm['status'] in ['running','observed']
pid=tm['runner_pid']; ticks=tm['runner_start_ticks']
def live():
    stat=Path('/proc',str(pid),'stat')
    return stat.exists() and stat.read_text().split(') ',1)[1].split()[19]==ticks
if tm['status']=='running': assert live()
else: assert tm['stage']=='complete'
p.mkdir(); shutil.copyfile(Path(__file__),p/'runner.py')
names=['scripts/prepare_state_route_recovery_v2.py','scripts/run_state_route_recovery_v2.py',
       'scripts/audit_state_route_recovery_v2.py','scripts/freeze_state_route_recovery_v2.py',
       'scripts/audit_state_ooc_physical_v2.py','scripts/parse_state_timing_paths.py','scripts/run_checkpoint_authority.py',
       'scripts/archive_offer_result.py','scripts/verify_search_retire_restore.py','scripts/restore_offer_result.py',
       'hardware/scripts/resume_state_route_v1.tcl','hardware/scripts/inspect_state_route_v1.tcl',
       'results/udev_runtime_recovery_20261030.json','results/udev_runtime_recovery_sources_20261030/manifest.json',
       'results/udev_route_probe_v2_restore_20261025.json']
bound={}
for name in names:
    source=ROOT/name; dest=p/'bound'/name; dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,dest); bound[name]=dict(source=str(source),sha256=sha(dest))
    assert sha(source)==bound[name]['sha256']
m=dict(status='running',stage='wait_existing',target=str(target),solver_pid=pid,solver_start_ticks=ticks,
       runner_pid=os.getpid(),runner_start_ticks=Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19],
       runner_sha256=sha(p/'runner.py'),bound=bound,commands=[],
       scope='Own postprocessing only after this exact recovery runner finishes. Never restart, repair, retry, '
             'change constraints or stop any compute process. Observation timeout leaves the original process untouched.')
def save():
    temp=p/'manifest.pending.json';temp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');temp.replace(p/'manifest.json')
def check_bound():
    for name,entry in bound.items(): assert sha(Path(entry['source']))==entry['sha256']==sha(p/'bound'/name),name
def run(stage,args,timeout):
    check_bound(); m['stage']=stage; start=time.monotonic(); argv=[sys.executable,'-B',*map(str,args)]
    print('START',stage,flush=True)
    with (p/(stage+'.log')).open('w') as handle:
        child=subprocess.Popen(argv,cwd=ROOT,stdout=handle,stderr=subprocess.STDOUT)
        m['active_process']=dict(pid=child.pid,argv=argv); save()
        try: code=child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            m.update(status='observation_timeout',error='Postprocess child may still be alive; inspect it before any mutation');save();raise
    m['commands'].append(dict(stage=stage,pid=child.pid,argv=argv,exit_code=code,elapsed_s=time.monotonic()-start,
                              log_sha256=sha(p/(stage+'.log'))))
    m.pop('active_process',None);save();assert code==0,stage
    print('DONE',stage,flush=True)
save()
try:
    deadline=time.monotonic()+21600; missing_since=None
    print('WAIT_EXISTING',pid,flush=True)
    while True:
        tm=json.loads((target/'manifest.json').read_text())
        assert tm['runner_pid']==pid and tm['runner_start_ticks']==ticks
        if tm['status']=='observed':
            assert tm['stage']=='complete' and tm['exit_code']==0
            if not live(): break
        else: assert tm['status']=='running',tm.get('error',tm['status'])
        now=time.monotonic()
        if live(): missing_since=None
        elif missing_since is None: missing_since=now
        else: assert now-missing_since<30,'Owner absent without an accepted terminal manifest; do not resubmit'
        assert now<deadline,'Observation timeout; original recovery untouched'
        time.sleep(10)
    run('physical_audit',['scripts/audit_state_route_recovery_v2.py',target],600)
    run('physical_archive',['scripts/archive_offer_result.py',target],1800)
    run('physical_restore',['scripts/verify_search_retire_restore.py',target.name,'audit_state_route_recovery_v2.py'],1800)
    run('physical_freeze',['scripts/freeze_state_route_recovery_v2.py',target],600)
    m.update(status='observed',stage='complete')
except Exception as e:
    if m['status']!='observation_timeout': m.update(status='failed',error=repr(e))
    raise
finally: save()
print('STATE_ROUTE_RECOVERY_FOLLOWUP_COMPLETE',flush=True)
