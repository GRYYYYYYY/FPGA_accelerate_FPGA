"""Observe the existing synthesis, then serially diagnose and preserve its result."""
from pathlib import Path
import json,shutil,subprocess,sys,time
from run_checkpoint_authority import ROOT,sha

p=Path(sys.argv[1]).resolve();pid=int(sys.argv[2])
target=p.parent/'query_native_synth_v1';proc=Path('/proc')/str(pid)
cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode()
assert 'unwrapped/lnx64.o/vivado' in cmd and str(target/'synth.tcl') in cmd
ticks=(proc/'stat').read_text().split(') ',1)[1].split()[19]
assert not(target/'results/methodology_v1').exists()
p.mkdir();shutil.copyfile(Path(__file__),p/'runner.py')
m=dict(status='running',stage='wait_existing',target=str(target),existing_pid=pid,
    existing_start_ticks=ticks,existing_cmdline=cmd,runner_sha256=sha(p/'runner.py'),commands=[],
    scope='Only observes the already running synthesis; never restarts or stops it. Serial independent DCP inspection, audit, archive, actual restoration and freeze. Artifact audit does not imply hardware acceptance.')
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
    deadline=time.monotonic()+5400;last_live=time.monotonic()
    print('WAIT_EXISTING_SYNTH',pid,flush=True)
    while True:
        tm=json.loads((target/'manifest.json').read_text())
        if tm['status']=='observed':
            assert tm['exit_code']==0;break
        assert tm['status']=='running',tm.get('error',tm['status'])
        if proc.exists():
            assert (proc/'stat').read_text().split(') ',1)[1].split()[19]==ticks,'PID identity changed'
            last_live=time.monotonic()
        else:
            assert time.monotonic()-last_live<30,'synthesis exited without terminal manifest; inspect, never automatically restart'
        assert time.monotonic()<deadline,'observer timeout only; synthesis is not stopped'
        time.sleep(5)
    run('inspect',['scripts/inspect_restore_seed_synth.py',target],2400)
    run('walks',['scripts/analyze_restore_seed_loops.py',target],180)
    run('audit',['scripts/audit_query_native_synth.py',target],180)
    run('archive',['scripts/archive_offer_result.py',target],600)
    run('restore',['scripts/verify_search_retire_restore.py',target.name,'audit_query_native_synth.py'],600)
    run('freeze',['scripts/freeze_query_native_synth.py'],180)
    m.update(status='observed',stage='complete')
except Exception as e:
    m.update(status='failed',error=repr(e));raise
finally:save()
print('QUERY_NATIVE_SYNTH_FOLLOWUP_COMPLETED',flush=True)
