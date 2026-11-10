"""Observe the existing complete-system simulation, then audit and preserve its result."""
from pathlib import Path
import json,shutil,subprocess,sys,time
from run_checkpoint_authority import ROOT,sha

p=Path(sys.argv[1]).resolve();pid=int(sys.argv[2])
target=p.parent/'route_stage_system_crc_pressure_v1';proc=Path('/proc')/str(pid)
cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode()
assert 'scripts/run_route_stage_system.py' in cmd and str(target) in cmd
ticks=(proc/'stat').read_text().split(') ',1)[1].split()[19]
assert not(target/'source_bound_audit.json').exists()
p.mkdir();shutil.copyfile(Path(__file__),p/'runner.py')
m=dict(status='running',stage='wait_existing',target=str(target),existing_pid=pid,
    existing_start_ticks=ticks,existing_cmdline=cmd,runner_sha256=sha(p/'runner.py'),commands=[],
    scope='Only observes the already running full-system simulation; never restarts or stops it. Serial independent audit, archive, actual restoration and freeze. Artifact audit does not imply hardware acceptance.')
bound_names=['scripts/run_route_stage_system.py', 'scripts/audit_route_stage_system.py', 'scripts/freeze_route_stage_system.py', 'scripts/archive_offer_result.py', 'scripts/verify_search_retire_restore.py', 'scripts/run_checkpoint_authority.py', 'hardware/variants/route_stage_system_v1/build.py', 'hardware/variants/route_stage_write_v1/build.py', 'hardware/variants/route_stage_write_v1/manifest.json', 'hardware/variants/route_stage_write_v1/fixed/route_commit_controller.sv', 'hardware/variants/route_stage_write_v1/fixed/route_commit_host_adapter.sv', 'scripts/analyze_route_stage_write_factoring_v2.py', 'results/route_stage_write_factoring_20261029.json', 'scripts/prepare_checkpoint_edit_monitor.py']
m['bound']={name:sha(ROOT/name) for name in bound_names}
for name in bound_names:
    dest=p/'tools'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dest)
def check_bound():
    for name,h in m['bound'].items():assert sha(ROOT/name)==sha(p/'tools'/name)==h,name

def save():(p/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
def run(stage,args,timeout):
    check_bound();m['stage']=stage;save();argv=[sys.executable,*map(str,args)]
    print('START',stage,flush=True);start=time.monotonic()
    with(p/(stage+'.log')).open('w')as f:
        r=subprocess.run(argv,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
    m['commands'].append(dict(stage=stage,argv=argv,exit_code=r.returncode,elapsed_s=time.monotonic()-start,log_sha256=sha(p/(stage+'.log'))));save()
    assert r.returncode==0,stage
    print('DONE',stage,flush=True)
save()
try:
    deadline=time.monotonic()+7800;last_live=time.monotonic()
    print('WAIT_EXISTING_SYSTEM',pid,flush=True)
    while True:
        tm=json.loads((target/'manifest.json').read_text())
        if tm['status']=='observed':
            assert all(c['status']=='observed' and len(c['commands'])==3 and all(x['exit_code']==0 for x in c['commands']) for c in tm['cases'].values());break
        assert tm['status']=='running',tm.get('error',tm['status'])
        if proc.exists():
            assert (proc/'stat').read_text().split(') ',1)[1].split()[19]==ticks,'PID identity changed'
            last_live=time.monotonic()
        else:
            assert time.monotonic()-last_live<30,'simulation runner exited without terminal manifest; inspect, never automatically restart'
        assert time.monotonic()<deadline,'observer timeout only; simulation is not stopped'
        time.sleep(5)
    run('audit',['scripts/audit_route_stage_system.py',target],180)
    run('archive',['scripts/archive_offer_result.py',target],600)
    run('restore',['scripts/verify_search_retire_restore.py',target.name,'audit_route_stage_system.py'],600)
    run('freeze',['scripts/freeze_route_stage_system.py'],180)
    m.update(status='observed',stage='complete')
except Exception as e:
    m.update(status='failed',error=repr(e));raise
finally:save()
print('ROUTE_STAGE_SYSTEM_FOLLOWUP_COMPLETED',flush=True)
