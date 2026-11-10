"""Wait for the existing backend run, audit/restore it, then run the combined case."""
from pathlib import Path
import json,shutil,subprocess,sys,time
from run_checkpoint_authority import ROOT,sha

p=Path(sys.argv[1]).resolve();pid=int(sys.argv[2])
base=p.parent
existing=base/'recovery_backend_system_crc_pressure_v2'
target=base/'native_retirement_system_crc_pressure_v1'
ref=base/'route_block_system_crc_pressure_v1'
proc=Path('/proc')/str(pid)
cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode()
assert 'run_recovery_backend_system_v2.py' in cmd and str(existing) in cmd
ticks=(proc/'stat').read_text().split(') ',1)[1].split()[19]
assert not target.exists()
p.mkdir();shutil.copyfile(Path(__file__),p/'runner.py')
m=dict(status='running',stage='wait_existing',existing=str(existing),target=str(target),
    existing_pid=pid,existing_start_ticks=ticks,existing_cmdline=cmd,
    runner_sha256=sha(p/'runner.py'),commands=[],
    scope='Existing-process observation only; never restarts prior jobs. Serial behavioral simulations. Any failed prerequisite stops the chain.')
def save():(p/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
def run(stage,args,timeout):
    m['stage']=stage;save();argv=[sys.executable,*map(str,args)]
    print('START',stage,flush=True);start=time.monotonic()
    with(p/(stage+'.log')).open('w')as f:
        r=subprocess.run(argv,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
    m['commands'].append(dict(stage=stage,argv=argv,exit_code=r.returncode,elapsed_s=time.monotonic()-start,log_sha256=sha(p/(stage+'.log'))));save()
    assert r.returncode==0,stage
    print('DONE',stage,flush=True)
save()
try:
    deadline=time.monotonic()+1800
    print('WAIT_EXISTING_BACKEND_RUN',pid,flush=True)
    while True:
        em=json.loads((existing/'manifest.json').read_text())
        if em['status']=='observed':break
        assert em['status']=='running',em.get('error',em['status'])
        assert proc.exists(),'existing runner disappeared without terminal manifest; inspect before any retry'
        assert (proc/'stat').read_text().split(') ',1)[1].split()[19]==ticks,'PID identity changed'
        assert time.monotonic()<deadline,'observer timeout only; existing job is not stopped'
        time.sleep(5)
    run('audit_backend',['scripts/audit_recovery_backend_system_v2.py',existing],180)
    run('archive_backend',['scripts/archive_offer_result.py',existing],600)
    run('restore_backend',['scripts/verify_search_retire_restore.py',existing.name,'audit_recovery_backend_system_v2.py'],600)
    run('run_combined',['scripts/run_native_retirement_system.py',target,ref],7500)
    run('audit_combined',['scripts/audit_native_retirement_system.py',target],180)
    run('archive_combined',['scripts/archive_offer_result.py',target],600)
    run('restore_combined',['scripts/verify_search_retire_restore.py',target.name,'audit_native_retirement_system.py'],600)
    m.update(status='observed',stage='complete')
except Exception as e:
    m.update(status='failed',error=repr(e));raise
finally:save()
print('NATIVE_RETIREMENT_FOLLOWUP_COMPLETED',flush=True)
