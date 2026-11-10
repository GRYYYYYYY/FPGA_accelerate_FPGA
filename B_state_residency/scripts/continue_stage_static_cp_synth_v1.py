"""Own the deterministic postprocessing of the existing static-stage OOC only.

No synthesis submission, retries, repairs or signals. Wait timeouts preserve
all subprocesses and ownership. Scientific interpretation remains with caller.
"""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import time
from stage_static_cp_synth_common_v1 import ROOT,BASE,TARGET,TOOLS,PREPARATION,sha,read,identity,wait_preserving


def main():
    p=Path(sys.argv[1]).resolve()
    assert p==BASE/'stage_static_cp_synth_followup_v1' and not p.exists()
    target=TARGET;tm=read(target/'manifest.json')
    assert tm['status'] in ['running','observation_timeout']
    pid,ticks=tm['runner_pid'],str(tm['runner_start_ticks'])
    assert identity(pid)==ticks
    cmd=Path('/proc',str(pid),'cmdline').read_bytes().replace(b'\0',b' ').decode()
    assert 'run_stage_static_cp_synth_v1.py' in cmd and str(target) in cmd
    assert not (target/'results/methodology_v1').exists()
    assert not (target/'source_bound_audit.json').exists()
    assert not (ROOT/'results/offer_archives_20261025'/f'{target.name}.json').exists()
    assert not (ROOT/'results/stage_static_cp_synth_20261030.json').exists()
    p.mkdir();(p/'tools').mkdir()
    snapshot=p/'parent_manifest_at_start.json';shutil.copyfile(target/'manifest.json',snapshot)
    bound_sources=[ROOT/'scripts'/name for name in TOOLS]+[PREPARATION,Path(__file__).resolve()]
    bound={}
    for i,source in enumerate(bound_sources):
        name=f'{i:02d}_{source.name}';shutil.copyfile(source,p/'tools'/name)
        bound[name]=dict(source=str(source),sha256=sha(source))
    m=dict(status='running',stage='wait_existing',runner_pid=os.getpid(),
           runner_start_ticks=identity(os.getpid()),target=str(target),
           existing_runner_pid=pid,existing_runner_start_ticks=ticks,
           parent_snapshot_sha256=sha(snapshot),bound=bound,commands=[],
           scope='Wait existing synthesis only; serial inspect/walks/audit/archive/actual restore/freeze. No retries, repairs, new experiments or design acceptance decisions.')
    def save():
        temp=p/'manifest.pending.json';temp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');temp.replace(p/'manifest.json')
    def validate():
        for name,e in bound.items():assert sha(e['source'])==sha(p/'tools'/name)==e['sha256']
        assert sha(snapshot)==m['parent_snapshot_sha256']
    def run(stage,args,timeout):
        validate();m.update(status='running',stage=stage);save()
        argv=[sys.executable,*map(str,args)]
        print('START',stage,flush=True)
        start=time.monotonic()
        with (p/(stage+'.log')).open('w') as log:
            child=subprocess.Popen(argv,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            m['active_process']=dict(pid=child.pid,start_ticks=identity(child.pid),argv=argv);save()
            code=wait_preserving(child,timeout,m,save)
        m.pop('active_process',None);m['status']='running'
        m['commands'].append(dict(stage=stage,argv=argv,exit_code=code,
                                 elapsed_s=time.monotonic()-start,log_sha256=sha(p/(stage+'.log'))));save()
        assert code==0,stage
        print('DONE',stage,flush=True)
    save()
    try:
        deadline=time.monotonic()+7800;missing_since=None
        print('WAIT_EXISTING_STATIC_STAGE_SYNTH',pid,flush=True)
        while True:
            validate();tm=read(target/'manifest.json')
            live=identity(pid)
            if live is not None:assert live==ticks,'Runner PID identity changed'
            if tm['status']=='observed':
                assert tm['stage']=='complete' and tm['exit_code']==0
                if live is None:break
            else:
                assert tm['status'] in ['running','observation_timeout'],tm.get('error',tm['status'])
                if live is None:
                    missing_since=missing_since or time.monotonic()
                    assert time.monotonic()-missing_since<60,'Runner gone without terminal receipt; inspect, do not restart'
            if time.monotonic()>deadline:
                m['status']='observation_timeout';save()
                print('WAIT_OBSERVATION_TIMEOUT_ORIGINAL_PRESERVED',pid,flush=True)
                deadline=time.monotonic()+7800
            time.sleep(10)
        run('inspect',[ROOT/'scripts/inspect_stage_static_cp_synth_v1.py',target],2400)
        run('walks',[ROOT/'scripts/analyze_restore_seed_loops.py',target],180)
        run('audit',[ROOT/'scripts/audit_stage_static_cp_synth_v1.py',target],600)
        run('archive',[ROOT/'scripts/archive_offer_result.py',target],1200)
        run('restore',[ROOT/'scripts/verify_search_retire_restore.py',target.name,'audit_stage_static_cp_synth_v1.py'],1200)
        run('freeze',[ROOT/'scripts/freeze_stage_static_cp_synth_v1.py'],600)
        m.update(status='observed',stage='complete');save()
    except Exception as error:
        m.update(status='failed',error=repr(error));save();raise
    print('STATIC_STAGE_SYNTH_FOLLOWUP_COMPLETE',flush=True)


if __name__=='__main__':main()
