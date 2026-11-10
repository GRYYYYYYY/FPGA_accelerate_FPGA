"""Run the complete host RTL plus delayed structural-netlist shadow after accepted OOC."""
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
from stage_static_cp_shadow_common_v1 import TARGET,REFERENCE,SYNTH,VARIANT,evidence
from namespace_functional_netlist_v1 import namespace


def main():
    p=Path(sys.argv[1]).resolve();assert p==TARGET and not p.exists()
    rm,proof=evidence();ref=REFERENCE;fixed={}
    tb=(VARIANT/'tb_query_fault.sv').read_text()
    preparation=ROOT/'results/stage_static_cp_shadow_system_tools_preparation_20261030.json'
    pr=read(preparation);assert pr['status']=='full_shadow_system_tools_prepared_not_executed'
    for name,digest in pr['tools'].items():assert sha(name)==digest
    proof.update(pr['tools']);proof[str(preparation)]=sha(preparation)
    rm=read(ref/'manifest.json');assert rm['status']=='observed' and list(rm['cases'])==['pressure']
    assert not os.environ.get('LD_PRELOAD'),'Preserve the working XSim runtime'
    p.mkdir();src=p/'sources';src.mkdir();d=p/'pressure';d.mkdir();(p/'bound').mkdir()
    m=copy.deepcopy(rm);m.pop('active_process',None)
    m.update(status='running',stage='wait_memory',mode='full_netlist_shadow',runner_pid=os.getpid(),
        runner_start_ticks=identity(os.getpid()),runner_sha256=sha(__file__),stage_reference=str(ref),
        stage_reference_audit_sha256=sha(ref/'source_bound_audit.json'),predecessors=proof,
        cases={'pressure':dict(status='running',commands=[])},bound={},
        scope='Complete host behavioral RTL plus 200ns transport-delayed structural shadow; all217 input pins, all346 output pins strict four-state. All original host/CP/query/backend/capture/path/stage assertions retained. Not physical timing or arbitrary formal proof.')
    for i,(source,digest) in enumerate(proof.items()):
        source=Path(source);assert sha(source)==digest;name=f'{i:02d}_{source.name}'
        shutil.copyfile(source,p/'bound'/name);m['bound'][name]=dict(source=str(source),sha256=digest)
    for n,e in rm['sources'].items():
        assert sha(ref/'sources'/n)==e['sha256'];q=src/n;q.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ref/'sources'/n,q)
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

    # Namespacing changes only module definition/type tokens; preserve its exact inverse receipt.
    raw=(SYNTH/'synth.v').read_text();shadow_net,ns=namespace(raw)
    (src/'shadow_netlist.v').write_text(shadow_net)
    ns.update(source_sha256=sha(SYNTH/'synth.v'),output_sha256=sha(src/'shadow_netlist.v'))
    (p/'namespace.json').write_text(json.dumps(ns,indent=2,sort_keys=True)+'\n')
    shutil.copyfile(VARIANT/'shadow.sv',src/'shadow.sv')
    glbl=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/data/verilog/src/glbl.v')
    shutil.copyfile(glbl,src/'glbl.v')
    m['shadow_inputs']={n:sha(src/n) for n in ['shadow_netlist.v','shadow.sv','glbl.v']}
    m['namespace_sha256']=sha(p/'namespace.json');m['synthesis_netlist_sha256']=sha(SYNTH/'synth.v')
    m['original_vendor_glbl_sha256']=sha(glbl)

    def save():
        temp=p/'manifest.pending.json';temp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');temp.replace(p/'manifest.json')

    def validate():
        for name,e in m['bound'].items():assert sha(e['source'])==e['sha256']==sha(p/'bound'/name)
        for name,e in m['sources'].items():assert sha(src/name)==e['sha256']
        assert sha(d/'run.tcl')==m['run_tcl_sha256']
        for n,h in m['shadow_inputs'].items():assert sha(src/n)==h
        assert sha(p/'namespace.json')==m['namespace_sha256']

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
            if stage=='compile':
                argv += ['--define','SHADOW_NETLIST_TOP='+ns['shadow_top']]+[str(src/n) for n in ['shadow_netlist.v','shadow.sv','glbl.v']]
            elif stage=='elaborate':
                argv += ['stage_static_cp_shadow','glbl','-L','unisims_ver','--O0']
            start=time.monotonic();m['stage']=stage;save()
            with (d/(stage+'.stdout.log')).open('w') as log:
                child=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT);ticks=identity(child.pid)
                m['active_process']=dict(stage=stage,pid=child.pid,start_ticks=ticks,argv=argv);save()
                code=wait_preserving(child,7200,m,save)
            m.pop('active_process',None)
            m['cases']['pressure']['commands'].append(dict(stage=stage,argv=argv,pid=child.pid,start_ticks=ticks,
                exit_code=code,elapsed_s=time.monotonic()-start,stdout_sha256=sha(d/(stage+'.stdout.log'))));save()
            assert code==0,stage
            print('FULL_NETLIST_SHADOW_SYSTEM',stage,'exit0',flush=True)
        log=(d/'simulate.log').read_text()
        for marker in ['FULL_SHADOW_PASS outputs=346 bits=14384','ROUTE_PATH_BANK_PASS','ROUTE_STAGE_BANK_PASS','HOST_EDIT_NATIVE_PASS','FOURTH_WARM_PASS polls=83 expands=82 candidates=402 costs=231','$finish called']:
            assert marker in log
        assert 'Fatal:' not in log and 'ERROR:' not in log
        m.update(status='observed',stage='complete');m['cases']['pressure']['status']='observed'
    except Exception as exc:
        if m['status']!='observation_timeout':m.update(status='failed',error=repr(exc))
        raise
    finally:save()
    print('FULL_NETLIST_SHADOW_SYSTEM_OBSERVED',p)


if __name__=='__main__':main()
