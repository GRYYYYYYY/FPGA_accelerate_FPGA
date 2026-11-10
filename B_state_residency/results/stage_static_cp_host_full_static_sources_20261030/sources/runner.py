"""Run one explicit full-capacity host RTL mode; never reuse pressure timing as oracle."""
from pathlib import Path
import copy
import json
import os
import shutil
import subprocess
import sys
import time
from host_edit_system_common_v1 import ROOT,BASE,sha,read,identity,load
from config_native_publication_synth_common_v1 import wait_preserving
from check_stage_static_cp_fixture_parameters_v1 import defines,fixture_parameters

TARGETS={'baseline':BASE/'stage_static_cp_host_full_baseline_v1','static':BASE/'stage_static_cp_host_full_static_v1'}
BUILDER=ROOT/'hardware/variants/stage_static_cp_system_v1/build.py'


def main():
    mode=sys.argv[2];assert mode in TARGETS
    p=Path(sys.argv[1]).resolve();assert p==TARGETS[mode] and not p.exists()
    # Serialize against the active OOC and its restore owner before any mutation.
    accepted=ROOT/'results/stage_static_cp_synth_20261030.json'
    assert accepted.exists(),'Wait for OOC actual restore/freeze and main review'
    if mode=='static':
        paired=ROOT/'results/stage_static_cp_host_full_baseline_20261030.json'
        assert paired.exists(),'Wait for independent full-capacity baseline actual restore/freeze'
        assert read(paired)['status']=='full_capacity_host_baseline_actual_restored'
    from host_edit_system_common_v1 import verify_freeze,restored
    sf=verify_freeze(ROOT/'results/stage_static_cp_synth_sources_20261030')
    sm,sa,se=restored(BASE/'stage_static_cp_synth_v1')
    assert read(accepted)['audit']==sa and sm['stage']=='complete'
    follow=read(BASE/'stage_static_cp_synth_followup_v1/manifest.json')
    assert follow['status']=='observed' and follow['stage']=='complete'
    assert identity(follow['runner_pid'])!=str(follow['runner_start_ticks'])
    b=load('isolated_stage_full_system_builder',BUILDER);ref=b.REFERENCE
    fixed,proof=b.sources(ref)  # Actual twelve-unit acceptance before any directory creation.
    if mode=='baseline':fixed={}
    tb=b.monitored_tb((ref/'sources/tb_query_fault.sv').read_text())
    proof.update({str(q):sha(q) for q in se+[accepted,sf]})
    rm=read(ref/'manifest.json')
    oldcompile=rm['cases']['pressure']['commands'][0]['argv']
    macros=defines(oldcompile);assert 'PRESSURE' in macros
    full_parameters=fixture_parameters(tb,(BASE/'stage_static_cp_synth_v1/sources/query_residency_system.sv').read_text(),macros-{'PRESSURE'})
    assert full_parameters==sm['parameters'] and full_parameters['SLOTS']==32
    if mode=='static':
        bm,ba,be=restored(TARGETS['baseline'])
        assert read(paired)['audit']==ba and bm['stage']=='complete'
        bf=verify_freeze(ROOT/'results/stage_static_cp_host_full_baseline_sources_20261030')
        proof.update({str(q):sha(q) for q in be+[paired,bf]})
    preparation=ROOT/'results/stage_static_cp_host_full_tools_preparation_20261030.json'
    pr=read(preparation);assert pr['status']=='full_capacity_host_tools_prepared_not_executed'
    for name,digest in pr['tools'].items():assert sha(name)==digest
    proof.update(pr['tools']);proof[str(preparation)]=sha(preparation)
    rm=read(ref/'manifest.json');assert rm['status']=='observed' and list(rm['cases'])==['pressure']
    assert not os.environ.get('LD_PRELOAD'),'Preserve the working XSim runtime'
    p.mkdir();src=p/'sources';src.mkdir();d=p/'full';d.mkdir();(p/'bound').mkdir()
    m=copy.deepcopy(rm);m.pop('active_process',None)
    m.update(status='running',stage='wait_memory',mode=mode+'_full_capacity',parameters=full_parameters,compile_defines=sorted(macros-{'PRESSURE'}),runner_pid=os.getpid(),
        runner_start_ticks=identity(os.getpid()),runner_sha256=sha(__file__),stage_reference=str(ref),
        stage_reference_audit_sha256=sha(ref/'source_bound_audit.json'),predecessors=proof,
        cases={'full':dict(status='running',commands=[])},bound={},
        scope='Explicit SLOTS32 host RTL fixture with unchanged host/CP/query/backend/capture/path/stage stimuli and checks. Only PRESSURE compile define removed. Baseline and static candidate require independent complete run and paired outputs. No pressure-cycle oracle, netlist, timing or board claim.')
    for i,(source,digest) in enumerate(proof.items()):
        source=Path(source);assert sha(source)==digest;name=f'{i:02d}_{source.name}'
        shutil.copyfile(source,p/'bound'/name);m['bound'][name]=dict(source=str(source),sha256=digest)
    for n,e in rm['sources'].items():
        assert sha(ref/'sources'/n)==e['sha256'];q=src/n;q.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ref/'sources'/n,q)
    for n,text in fixed.items():
        (src/n).write_text(text);m['sources'][n]=dict(path=str(b.CANDIDATE/'fixed'/n),sha256=sha(src/n))
    m['rtl']=rm['rtl']
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
            validate();stage=old['stage'];argv=[a.replace(str(ref/'pressure'),str(d)).replace(str(ref),str(p)) for a in old['argv']]
            if stage=='compile':
                at=argv.index('PRESSURE');assert argv[at-1]=='--define';del argv[at-1:at+1]
                assert 'PRESSURE' not in defines(argv)
            start=time.monotonic();m['stage']=stage;save()
            with (d/(stage+'.stdout.log')).open('w') as log:
                child=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT);ticks=identity(child.pid)
                m['active_process']=dict(stage=stage,pid=child.pid,start_ticks=ticks,argv=argv);save()
                code=wait_preserving(child,7200,m,save)
            m.pop('active_process',None)
            m['cases']['full']['commands'].append(dict(stage=stage,argv=argv,pid=child.pid,start_ticks=ticks,
                exit_code=code,elapsed_s=time.monotonic()-start,stdout_sha256=sha(d/(stage+'.stdout.log'))));save()
            assert code==0,stage
            print('FULL_CAPACITY_HOST_SYSTEM',stage,'exit0',flush=True)
        log=(d/'simulate.log').read_text()
        for marker in ['ROUTE_PATH_BANK_PASS','ROUTE_STAGE_BANK_PASS','HOST_EDIT_NATIVE_PASS','FOURTH_WARM_PASS polls=83 expands=82 candidates=402 costs=231','$finish called']:
            assert marker in log
        assert 'Fatal:' not in log and 'ERROR:' not in log
        m.update(status='observed',stage='complete');m['cases']['full']['status']='observed'
    except Exception as exc:
        if m['status']!='observation_timeout':m.update(status='failed',error=repr(exc))
        raise
    finally:save()
    print('FULL_CAPACITY_HOST_SYSTEM_OBSERVED',p)


if __name__=='__main__':main()
