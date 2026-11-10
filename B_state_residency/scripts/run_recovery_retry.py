"""Retry a failed recovery with a fresh identity and preserved journal."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys, time
ROOT = Path(__file__).resolve().parents[1]
BIN = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1<<20), b''): h.update(b)
    return h.hexdigest()
def main():
    out = Path(sys.argv[1]).resolve(); out.mkdir(); src = out/'sources'; src.mkdir()
    base = ROOT/'results/recovery_fault_matrix_v2'
    bm = json.loads((base/'manifest.json').read_text())
    ba = json.loads((base/'source_bound_audit.json').read_text())
    assert bm['status']=='observed' and ba['status']=='passed' and ba['manifest_sha256'] == sha(base/'manifest.json')
    normal=ROOT/'results/query_lifecycle_join_v2';nm=json.loads((normal/'manifest.json').read_text());inp=Path(nm['input'])
    modes=[('full',None),('pressure','PRESSURE')]
    if '--pilot' in sys.argv[2:]:modes=modes[:1]
    if '--pressure-only' in sys.argv[2:]:modes=[('pressure','PRESSURE')]
    plan=[(mode,define,[1,2,3,4,5]) for mode,define in modes]
    m={'status':'running','base':str(base.resolve()),'base_manifest_sha256':sha(base/'manifest.json'),'base_audit_sha256':sha(base/'source_bound_audit.json'),'sources':{},'cases':{},'builds':{},'expected_cases':[f'{mode}_{fc}'for mode,_,cases in plan for fc in cases],'scope':'Real AXI recovery-phase error after normal owner B error. Three production components implement explicit caller-initiated retry after complete retirement; journal/config descriptor preserved. No autonomous retry policy. Known q1 journal/328-label snapshot only.'}
    def save(): (out/'manifest.json').write_text(json.dumps(m, indent=2)+'\n')
    for n, v in bm['sources'].items():
        p = base/'sources'/n; assert sha(p) == v['sha256']
        if n in ['runner.py','tb_recovery_fault.sv','build_tb.py','build_variant.py']: continue
        q=src/n; q.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(p,q)
        m['sources'][n]={'path':str(p.resolve()),'sha256':sha(q)}
    bench=ROOT/'hardware/variants/recovery_retry_v1'
    extras=[(bench/n,n) for n in ['recovery_coordinator.sv','config_restore_controller.sv','residency_system.sv','build.py']]+[(bench/'tb_recovery_retry.sv','tb_recovery_retry.sv'),(bench/'build_tb.py','build_tb.py'),(Path(__file__),'runner.py')]
    for p,n in extras:
        shutil.copyfile(p,src/n);m['sources'][n]={'path':str(p),'sha256':sha(src/n)}
    rtl=[src/n for n in bm['rtl'] if not Path(n).name.startswith('tb_')]+[src/'tb_recovery_retry.sv']
    m['rtl']=[str(p.relative_to(src)) for p in rtl];save()
    def run(d,stage,argv,record):
        argv=list(map(str,argv));start=time.monotonic()
        with (d/(stage+'.stdout.log')).open('w') as f:
            r=subprocess.run(argv,cwd=d,stdout=f,stderr=subprocess.STDOUT,timeout=600)
        record.append({'stage':stage,'argv':argv,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save()
        assert r.returncode==0,(d.name,stage)
    try:
        for mode,define,cases in plan:
            build=out/('build_'+mode);build.mkdir(); br=m['builds'][mode]={'commands':[]};save()
            run(build,'compile',[BIN/'xvlog','--sv']+(['--define',define] if define else [])+rtl,br['commands'])
            run(build,'elaborate',[BIN/'xelab','tb_candidate_offer','-s','joined','--debug','typical','--mt','2'],br['commands'])
            for faultcase in cases:
                name=f'{mode}_{faultcase}';d=out/name;d.mkdir();(d/'xsim.dir').symlink_to(build/'xsim.dir',target_is_directory=True)
                cm=m['cases'][name]={'status':'running','faultcase':5,'recovery_fault':faultcase,'mode':mode,'commands':[]};save()
                for n in ['design.bin','owners.bin','cost.bin']:shutil.copyfile(inp/n,d/n)
                with (d/'owners.bin').open('ab') as f:f.write((inp/'owner_allocator.bin').read_bytes())
                with (d/'labels.bin').open('wb') as f:f.truncate(3145728)
                for p in src.rglob('*.dat'):shutil.copyfile(p,d/p.name)
                (d/'run.tcl').write_text('run 30ms\nquit\n')
                old=nm['cases'][mode]['commands'][-1]['argv'];args=[BIN/'xsim','joined','--tclbatch','run.tcl','--log','simulate.log']
                for i,x in enumerate(old):
                    if x!='--testplusarg':continue
                    k,v=old[i+1].split('=',1)
                    if k in ['design0','owners0','cost0','labels0']:v=str(d/Path(v).name)
                    elif k.endswith('log'):v=str(d/Path(v).name)
                    args+=['--testplusarg',k+'='+v]
                args+=['--testplusarg','faultcase=5','--testplusarg',f'recoveryfault={faultcase}']
                run(d,'simulate',args,cm['commands'])
                # Per-case launch link is temporary; archives retain build snapshots
                # once, and contain no absolute directory symlink to scratch.
                (d/'xsim.dir').unlink()
                log=(d/'simulate.log').read_text()
                hits=[l for l in log.splitlines() if l.startswith('RECOVERY_RETRY_OBSERVED ')]
                if len(hits)!=1 or 'Fatal:' in log:
                    cm.update(status='test_failed',tail=log[-2200:]);save();print(name,'test_failed',flush=True);continue
                cm.update(status='observed',result=hits[0],outcome=hits[0].split('outcome=')[1].split()[0])
                cm['artifacts']={p.name:sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ['.bin','.log','.txt','.tcl']}
                save();print(name,hits[0],flush=True)
        m['status']='observed' if all(v['status']=='observed' for v in m['cases'].values()) else 'test_failed'
    except Exception as e:m.update(status='failed',error=repr(e));raise
    finally:save()
if __name__=='__main__':main()
