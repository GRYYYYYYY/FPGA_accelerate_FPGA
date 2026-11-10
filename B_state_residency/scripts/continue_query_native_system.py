"""Observe the existing full-system runner and preserve its result without retry."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import time
from run_checkpoint_authority import ROOT,sha

p=Path(sys.argv[1]).resolve();pid=int(sys.argv[2]);target=p.parent/'query_native_system_crc_pressure_v1'
proc=Path('/proc')/str(pid);cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode()
assert 'run_query_native_system.py' in cmd and str(target) in cmd
ticks=(proc/'stat').read_text().split(') ',1)[1].split()[19]
p.mkdir();shutil.copyfile(Path(__file__),p/'runner.py')
paths=[ROOT/'scripts'/n for n in ['run_query_native_system.py','audit_query_native_system.py','freeze_query_native_system.py',
    'archive_offer_result.py','verify_search_retire_restore.py','run_checkpoint_authority.py']]
v=ROOT/'hardware/variants/query_native_system_v1'
paths += [v/n for n in ['build.py','tb_query_fault.sv','CONTRACT.md']]
paths += [v/mode/n for mode in ['baseline','fixed']for n in ['query_lifecycle.sv','query_residency_system.sv']]
bound={}
for src in paths:
    rel=src.relative_to(ROOT);dst=p/'bound'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    bound[str(rel)]=sha(src);assert sha(dst)==bound[str(rel)]
m=dict(status='running',stage='wait_existing',target=str(target),existing_pid=pid,existing_start_ticks=ticks,
    existing_cmdline=cmd,bound=bound,runner_sha256=sha(p/'runner.py'),commands=[],
    scope='Observe existing full-system runner, then independent exact audit, archive, actual restoration, freeze. No restart, repair, new synthesis or simulation submission. Failure stops chain.')
def save():(p/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
def run(stage,args,timeout):
    for rel,h in bound.items():assert sha(ROOT/rel)==h==sha(p/'bound'/rel),('source drift',rel)
    m['stage']=stage;save();argv=[sys.executable,*map(str,args)];start=time.monotonic()
    print('START',stage,flush=True)
    with(p/(stage+'.log')).open('w')as f:r=subprocess.run(argv,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
    m['commands'].append(dict(stage=stage,argv=argv,exit_code=r.returncode,elapsed_s=time.monotonic()-start,log_sha256=sha(p/(stage+'.log'))));save()
    assert r.returncode==0,stage
    print('DONE',stage,flush=True)
save()
try:
    deadline=time.monotonic()+5400;last_live=time.monotonic()
    print('WAIT_EXISTING_QUERY_SYSTEM',pid,flush=True)
    while True:
        try:tm=json.loads((target/'manifest.json').read_text())
        except json.JSONDecodeError:
            assert time.monotonic()<deadline;time.sleep(1);continue
        if tm['status']=='observed':break
        assert tm['status']=='running',tm.get('error',tm['status'])
        if proc.exists():
            assert (proc/'stat').read_text().split(') ',1)[1].split()[19]==ticks,'PID identity changed'
            last_live=time.monotonic()
        else:assert time.monotonic()-last_live<30,'runner exited without terminal manifest; inspect without restart'
        assert time.monotonic()<deadline,'observation timeout only; original runner is not stopped'
        time.sleep(5)
    run('audit',['scripts/audit_query_native_system.py',target],240)
    run('archive',['scripts/archive_offer_result.py',target],600)
    run('restore',['scripts/verify_search_retire_restore.py',target.name,'audit_query_native_system.py'],600)
    run('freeze',['scripts/freeze_query_native_system.py'],180)
    m.update(status='observed',stage='complete')
except Exception as e:
    m.update(status='failed',error=repr(e));raise
finally:save()
print('QUERY_NATIVE_SYSTEM_FOLLOWUP_COMPLETED',flush=True)
