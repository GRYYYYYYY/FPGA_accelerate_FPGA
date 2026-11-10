"""Freeze unchanged production RTL; classify real fault/recovery/retry outcomes."""
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
    base = ROOT/'results/query_lifecycle_join_v2'
    bm = json.loads((base/'manifest.json').read_text())
    ba = json.loads((base/'source_bound_audit.json').read_text())
    assert bm['status'] == ba['status'] == 'passed' and ba['manifest_sha256'] == sha(base/'manifest.json')
    inp = Path(bm['input'])
    route_fix='--route-fix' in sys.argv[2:]
    m = {'status':'running', 'base':str(base.resolve()), 'base_manifest_sha256':sha(base/'manifest.json'),
         'base_audit_sha256':sha(base/'source_bound_audit.json'), 'sources':{}, 'cases':{}, 'builds':{},
         'scope':'Behavioral real-service AXI fault diagnostics, original production RTL unchanged. A stalled outcome is NOT successful recovery. Retry uses trusted initial 328-label snapshot and q1 owner authority only; no complete design checkpoint or board claim.'}
    m['route_fix']=route_fix
    m['expected_cases']=['full_5','pressure_5'] if route_fix else ['full_1','full_3','full_4','full_5','full_6','pressure_1','pressure_2','pressure_3','pressure_4','pressure_5','pressure_6']
    if route_fix:m['scope']=m['scope'].replace('original production RTL unchanged','only query top retirement predicate changed (query_recovery_v2)')
    def save(): (out/'manifest.json').write_text(json.dumps(m, indent=2)+'\n')
    for n, v in bm['sources'].items():
        p = base/'sources'/n; assert sha(p) == v['sha256']
        if n in ['runner.py','tb_query_lifecycle_join.sv']: continue
        if route_fix and n=='query_residency_system.sv':p=ROOT/'hardware/variants/query_recovery_v2/query_residency_system.sv'
        q=src/n; q.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(p,q)
        m['sources'][n]={'path':str(p.resolve()),'sha256':sha(q)}
    for p,n in [(ROOT/'hardware/variants/query_fault_v1/tb_query_fault.sv','tb_query_fault.sv'),
                (ROOT/'hardware/variants/query_fault_v1/build_tb.py','build_tb.py'),(Path(__file__),'runner.py')]:
        shutil.copyfile(p,src/n);m['sources'][n]={'path':str(p),'sha256':sha(src/n)}
    rtl=[src/n for n in bm['rtl'] if not Path(n).name.startswith('tb_')]+[src/'tb_query_fault.sv']
    m['rtl']=[str(p.relative_to(src)) for p in rtl];save()
    def run(d,stage,argv,record):
        argv=list(map(str,argv));start=time.monotonic()
        with (d/(stage+'.stdout.log')).open('w') as f:
            r=subprocess.run(argv,cwd=d,stdout=f,stderr=subprocess.STDOUT,timeout=600)
        record.append({'stage':stage,'argv':argv,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save()
        assert r.returncode==0,(d.name,stage)
    try:
        for mode,define in [('full',None),('pressure','PRESSURE')]:
            build=out/('build_'+mode);build.mkdir(); br=m['builds'][mode]={'commands':[]};save()
            run(build,'compile',[BIN/'xvlog','--sv']+(['--define',define] if define else [])+rtl,br['commands'])
            run(build,'elaborate',[BIN/'xelab','tb_candidate_offer','-s','joined','--debug','typical','--mt','2'],br['commands'])
            for faultcase in ([5] if route_fix else [1,3,4,5,6] if mode=='full' else [1,2,3,4,5,6]):
                name=f'{mode}_{faultcase}';d=out/name;d.mkdir();(d/'xsim.dir').symlink_to(build/'xsim.dir',target_is_directory=True)
                cm=m['cases'][name]={'status':'running','faultcase':faultcase,'mode':mode,'commands':[]};save()
                for n in ['design.bin','owners.bin','cost.bin']:shutil.copyfile(inp/n,d/n)
                with (d/'owners.bin').open('ab') as f:f.write((inp/'owner_allocator.bin').read_bytes())
                with (d/'labels.bin').open('wb') as f:f.truncate(3145728)
                for p in src.rglob('*.dat'):shutil.copyfile(p,d/p.name)
                (d/'run.tcl').write_text('run 30ms\nquit\n')
                old=bm['cases'][mode]['commands'][-1]['argv'];args=[BIN/'xsim','joined','--tclbatch','run.tcl','--log','simulate.log']
                for i,x in enumerate(old):
                    if x!='--testplusarg':continue
                    k,v=old[i+1].split('=',1)
                    if k in ['design0','owners0','cost0','labels0']:v=str(d/Path(v).name)
                    elif k.endswith('log'):v=str(d/Path(v).name)
                    args+=['--testplusarg',k+'='+v]
                args+=['--testplusarg',f'faultcase={faultcase}']
                run(d,'simulate',args,cm['commands'])
                # Per-case launch link is temporary; archives retain build snapshots
                # once, and contain no absolute directory symlink to scratch.
                (d/'xsim.dir').unlink()
                log=(d/'simulate.log').read_text()
                hits=[l for l in log.splitlines() if l.startswith('QUERY_FAULT_OBSERVED ')]
                if len(hits)!=1 or 'Fatal:' in log:
                    cm.update(status='test_failed',tail=log[-2200:]);save();print(name,'test_failed',flush=True);continue
                cm.update(status='observed',result=hits[0],outcome=hits[0].split('outcome=')[1].split()[0])
                cm['artifacts']={p.name:sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ['.bin','.log','.txt','.tcl']}
                save();print(name,hits[0],flush=True)
        m['status']='observed' if all(v['status']=='observed' for v in m['cases'].values()) else 'test_failed'
    except Exception as e:m.update(status='failed',error=repr(e));raise
    finally:save()
if __name__=='__main__':main()
