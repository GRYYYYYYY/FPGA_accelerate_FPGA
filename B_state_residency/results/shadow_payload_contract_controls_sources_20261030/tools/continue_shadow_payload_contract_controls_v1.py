"""Own deterministic postprocessing of one existing 59-case payload observer controls.

No simulation submission, retries, repairs or signals. Wait timeouts preserve
all subprocesses and ownership. Scientific interpretation remains with caller.
"""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import time
from host_edit_system_common_v1 import ROOT,BASE,sha,read,identity
from config_native_publication_synth_common_v1 import wait_preserving


def main():
    p=Path(sys.argv[1]).resolve()
    assert p==BASE/'shadow_payload_contract_controls_v1_followup_v1' and not p.exists()
    target=BASE/'shadow_payload_contract_controls_v1';tm=read(target/'manifest.json')
    preparation=ROOT/'results/shadow_payload_contract_controls_v1_preparation_20261030.json'
    prepared=read(preparation)
    assert prepared['status']=='59_controls_prepared_not_executed'
    for source,h in prepared['tools'].items():assert sha(source)==h
    assert tm['status'] in ['running','observation_timeout']
    pid,ticks=tm['runner_pid'],str(tm['runner_start_ticks'])
    assert identity(pid)==ticks
    cmd=Path('/proc',str(pid),'cmdline').read_bytes().replace(b'\0',b' ').decode()
    assert 'run_shadow_payload_contract_controls_v1.py' in cmd and str(target) in cmd
    assert not (target/'source_bound_audit.json').exists()
    assert not (ROOT/'results/offer_archives_20261025'/f'{target.name}.json').exists()
    assert not (ROOT/'results/shadow_payload_contract_controls_20261030.json').exists()
    p.mkdir();(p/'tools').mkdir()
    snapshot=p/'parent_manifest_at_start.json';shutil.copyfile(target/'manifest.json',snapshot)
    bound_sources=[Path(name) for name in prepared['tools']]+[preparation,Path(__file__).resolve(),ROOT/'scripts/audit_shadow_payload_contract_controls_v1.py',ROOT/'scripts/freeze_shadow_payload_contract_controls_v1.py',ROOT/'scripts/audit_shadow_cp_protocol_controls_v3.py',ROOT/'scripts/archive_offer_result.py',ROOT/'scripts/restore_offer_result.py',ROOT/'scripts/verify_search_retire_restore.py']
    bound={}
    for i,source in enumerate(bound_sources):
        name=f'{i:02d}_{source.name}';shutil.copyfile(source,p/'tools'/name)
        bound[name]=dict(source=str(source),sha256=sha(source))
    m=dict(status='running',stage='wait_existing',runner_pid=os.getpid(),
           runner_start_ticks=identity(os.getpid()),target=str(target),
           existing_runner_pid=pid,existing_runner_start_ticks=ticks,
           parent_snapshot_sha256=sha(snapshot),bound=bound,commands=[],
           scope='Wait existing 59-case observer controls only; serial audit/archive/actual restore/freeze. No retries, repairs, new experiments or design acceptance decisions.')
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
        print('WAIT_EXISTING_THREE_PAYLOAD_CONTROLS59',pid,flush=True)
        while True:
            validate();tm=read(target/'manifest.json')
            live=identity(pid)
            if live is not None:assert live==ticks,'Runner PID identity changed'
            if tm['status']=='observed':
                assert tm['stage']=='complete' and len(tm['cases'])==59 and all(c['status']=='observed' for c in tm['cases'].values())
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
        run('audit',[ROOT/'scripts/audit_shadow_payload_contract_controls_v1.py',target],600)
        run('archive',[ROOT/'scripts/archive_offer_result.py',target],1200)
        run('restore',[ROOT/'scripts/verify_search_retire_restore.py',target.name,'audit_shadow_payload_contract_controls_v1.py'],1200)
        run('freeze',[ROOT/'scripts/freeze_shadow_payload_contract_controls_v1.py'],600)
        m.update(status='observed',stage='complete');save()
    except Exception as error:
        m.update(status='failed',error=repr(error));save();raise
    print('THREE_PAYLOAD_CONTROLS59_FOLLOWUP_COMPLETE',flush=True)


if __name__=='__main__':main()
