"""Run the isolated native-publication full system after actual-restored unit proof."""
from pathlib import Path
import copy
import json
import os
import shutil
import subprocess
import sys
import time
from host_edit_system_common_v1 import ROOT,BASE,sha,read,identity,load

TARGET=BASE/'config_native_publication_system_v1'
BUILDER=ROOT/'hardware/variants/config_native_publication_system_v1/build.py'


def main():
    p=Path(sys.argv[1]).resolve();assert p==TARGET and not p.exists()
    b=load('native_publication_full_system_builder',BUILDER);ref=b.REFERENCE
    fixed,model,tb,proof=b.sources(ref)  # All gates precede directory creation.
    rm=read(ref/'manifest.json');assert rm['status']=='observed' and list(rm['cases'])==['pressure']
    assert not os.environ.get('LD_PRELOAD'),'Preserve the working XSim runtime'
    p.mkdir();src=p/'sources';src.mkdir();d=p/'pressure';d.mkdir();(p/'bound').mkdir()
    m=copy.deepcopy(rm);m.pop('active_process',None)
    m.update(status='running',stage='wait_memory',mode='native_publication',runner_pid=os.getpid(),
        runner_start_ticks=identity(os.getpid()),runner_sha256=sha(__file__),native_reference=str(ref),
        native_reference_audit_sha256=sha(ref/'source_bound_audit.json'),predecessors=proof,
        cases={'pressure':dict(status='running',commands=[])},bound={},
        scope='Native descriptor publication candidate on actual restored CP real-host-edit fixture. Retain every stimulus and original monitor; compare original-controller self-feedback observer4810 state/7238 output bits every edge, plus all27 external artifacts/cycles. No OOC, physical or board claim.')
    for i,(source,digest) in enumerate(proof.items()):
        source=Path(source);assert sha(source)==digest;name=f'{i:02d}_{source.name}'
        shutil.copyfile(source,p/'bound'/name);m['bound'][name]=dict(source=str(source),sha256=digest)
    for n,e in rm['sources'].items():
        assert sha(ref/'sources'/n)==e['sha256'];q=src/n;q.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ref/'sources'/n,q)
    for n,text in fixed.items():
        (src/n).write_text(text);m['sources'][n]=dict(path=str(b.CANDIDATE/'fixed'/n),sha256=sha(src/n))
    (src/b.MODEL).write_text(model);m['sources'][b.MODEL]=dict(path=str(src/b.MODEL),sha256=sha(src/b.MODEL),
        original_controller_sha256=sha(b.CANDIDATE/'baseline/config_restore_controller.sv'))
    m['rtl']=rm['rtl']+[b.MODEL]
    (src/'tb_query_fault.sv').write_text(tb);m['sources']['tb_query_fault.sv']=dict(path=str(src/'tb_query_fault.sv'),sha256=sha(src/'tb_query_fault.sv'))
    shutil.copyfile(Path(__file__),src/'runner.py');m['sources']['runner.py']=dict(path=str(Path(__file__).resolve()),sha256=sha(src/'runner.py'))
    for key in ['scoreboards','next_scoreboards','third_scoreboards','fourth_scoreboards']:
        for n,h in rm[key].items():assert sha(ref/n)==h;shutil.copyfile(ref/n,p/n)
    assert sha(rm['binding'])==rm['binding_sha256'];regions=read(rm['binding'])['regions']
    for name,key in [('design.bin','design'),('cost.bin','cost_history_prices_nets')]:shutil.copyfile(regions[key]['path'],d/name)
    with (d/'owners.bin').open('wb') as dest:
        for key in ['owners','owner_pool','owner_allocator']:
            with Path(regions[key]['path']).open('rb') as source:shutil.copyfileobj(source,dest)
    for name in ['g3.bin','snapshot.bin','pool.bin']:shutil.copyfile(d/'owners.bin',d/name)
    shutil.copyfile(regions['owner_allocator']['path'],d/'allocator.bin')
    with (d/'labels.bin').open('wb') as dest:dest.truncate(3145728)
    for file in src.rglob('*.dat'):shutil.copyfile(file,d/file.name)
    shutil.copyfile(ref/'pressure/run.tcl',d/'run.tcl');m['run_tcl_sha256']=sha(d/'run.tcl')

    def save():
        temp=p/'manifest.pending.json';temp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');temp.replace(p/'manifest.json')

    def validate():
        for name,e in m['bound'].items():assert sha(e['source'])==e['sha256']==sha(p/'bound'/name)
        for name,e in m['sources'].items():assert sha(src/name)==e['sha256']
        assert sha(d/'run.tcl')==m['run_tcl_sha256']

    save()
    try:
        stable=None;deadline=time.monotonic()+10800
        while True:
            now=time.monotonic();cg=Path('/sys/fs/cgroup');current,limit=int((cg/'memory.current').read_text()),int((cg/'memory.max').read_text())
            stable=(now if stable is None else stable) if current*4<=limit*3 else None
            seconds=0 if stable is None else now-stable
            m['memory_admission']=dict(current_bytes=current,limit_bytes=limit,stable_seconds=seconds);save()
            if seconds>=60:break
            assert now<deadline,'Memory observation expired before solver launch'
            time.sleep(10)
        for old in rm['cases']['pressure']['commands']:
            validate();stage=old['stage'];argv=[a.replace(str(ref),str(p)) for a in old['argv']]
            if stage=='compile':argv.append(str(src/b.MODEL))
            start=time.monotonic();m['stage']=stage;save()
            with (d/(stage+'.stdout.log')).open('w') as log:
                child=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT);ticks=identity(child.pid)
                m['active_process']=dict(stage=stage,pid=child.pid,start_ticks=ticks,argv=argv);save()
                try:code=child.wait(timeout=7200)
                except subprocess.TimeoutExpired:
                    m.update(status='observation_timeout',error='Keep the original child; inspect its identity, do not restart/kill');save();raise
            m.pop('active_process',None)
            m['cases']['pressure']['commands'].append(dict(stage=stage,argv=argv,pid=child.pid,start_ticks=ticks,
                exit_code=code,elapsed_s=time.monotonic()-start,stdout_sha256=sha(d/(stage+'.stdout.log'))));save()
            assert code==0,stage
            print('NATIVE_PUBLICATION_SYSTEM',stage,'exit0',flush=True)
        log=(d/'simulate.log').read_text()
        for marker in ['CONFIG_NATIVE_SYSTEM_PASS','HOST_EDIT_NATIVE_PASS','FOURTH_WARM_PASS polls=83 expands=82 candidates=402 costs=231','$finish called']:
            assert marker in log
        assert 'Fatal:' not in log and 'ERROR:' not in log
        m.update(status='observed',stage='complete');m['cases']['pressure']['status']='observed'
    except Exception as exc:
        if m['status']!='observation_timeout':m.update(status='failed',error=repr(exc))
        raise
    finally:save()
    print('NATIVE_PUBLICATION_SYSTEM_OBSERVED',p)


if __name__=='__main__':main()
