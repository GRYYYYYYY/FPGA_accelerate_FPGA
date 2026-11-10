"""Run default-off or G4-only full-record restore seed bypass ablation."""
from pathlib import Path
import copy,json,runpy,shutil,subprocess,sys,time
from run_checkpoint_authority import ROOT,sha

out=Path(sys.argv[1]).resolve()
case=sys.argv[2]
enabled=int(sys.argv[3])
assert case in ['full','pressure'] and enabled in [0,1]
base=out.parent/'fourth_warm_full_v2'
bm=json.loads((base/'manifest.json').read_text())
ba=json.loads((base/'source_bound_audit.json').read_text())
assert ba['status']=='passed' and ba['manifest_sha256']==sha(base/'manifest.json')
variant=ROOT/'hardware/variants/restore_seed_bypass_v1'
candidate=runpy.run_path(str(variant/'build.py'))['make']()
tb=runpy.run_path(str(variant/'build_tb.py'))['make']()
assert tb==(variant/'tb_restore_seed.sv').read_text()
out.mkdir();src=out/'sources';src.mkdir();d=out/case;d.mkdir()
m=copy.deepcopy(bm)
m.update(status='running',cases={case:dict(status='running',commands=[])},
         parent_run=str(base),parent_audit_sha256=sha(base/'source_bound_audit.json'),
         restore_seed_bypass=enabled,
         scope='Experimental default-off / G4-only native full-record restore seed bypass; source provenance and start-pin drop checked. Not yet an audited correctness or performance claim.')
for n,e in bm['sources'].items():
    assert sha(base/'sources'/n)==e['sha256'],n
    target=src/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(base/'sources'/n,target)
for n,text in candidate.items():
    assert text==(variant/'sources'/n).read_text()
    (src/n).write_text(text)
    m['sources'][n]=dict(path=str(variant/'sources'/n),sha256=sha(src/n))
for n,p in {'runner.py':Path(__file__),'tb_query_fault.sv':variant/'tb_restore_seed.sv',
            'restore_seed_build.py':variant/'build.py','restore_seed_tb_build.py':variant/'build_tb.py'}.items():
    shutil.copyfile(p,src/n);m['sources'][n]=dict(path=str(p),sha256=sha(src/n))
for key in ['scoreboards','next_scoreboards','third_scoreboards','fourth_scoreboards']:
    for n,h in bm[key].items():
        assert sha(base/n)==h;shutil.copyfile(base/n,out/n)
reg=json.loads(Path(m['binding']).read_text())['regions']
assert sha(Path(m['binding']))==m['binding_sha256']
for n,k in [('design.bin','design'),('cost.bin','cost_history_prices_nets')]:shutil.copyfile(Path(reg[k]['path']),d/n)
with(d/'owners.bin').open('wb')as f:
    for k in ['owners','owner_pool','owner_allocator']:
        with Path(reg[k]['path']).open('rb')as source:shutil.copyfileobj(source,f)
for n in ['g3.bin','snapshot.bin','pool.bin']:shutil.copyfile(d/'owners.bin',d/n)
shutil.copyfile(Path(reg['owner_allocator']['path']),d/'allocator.bin')
with(d/'labels.bin').open('wb')as f:f.truncate(3145728)
for f in src.rglob('*.dat'):shutil.copyfile(f,d/f.name)
(d/'run.tcl').write_text('run 100ms\nquit\n')
def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
save()
try:
    for old in bm['cases']['full']['commands']:
        stage=old['stage'];argv=[a.replace(str(base/'full'),str(d)).replace(str(base),str(out))for a in old['argv']]
        if stage=='compile':
            if case=='pressure':argv[1:1]=['--define','PRESSURE']
            if enabled:argv[1:1]=['--define','RESTORE_SEED_BYPASS']
        start=time.monotonic()
        with(d/(stage+'.stdout.log')).open('w')as log:
            r=subprocess.run(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT,timeout=2400)
        m['cases'][case]['commands'].append(dict(stage=stage,argv=argv,exit_code=r.returncode,elapsed_s=time.monotonic()-start));save()
        assert r.returncode==0,stage
        print(stage,'completed',flush=True)
    log=(d/'simulate.log').read_text()
    assert 'Fatal:'not in log and '$finish called'in log
    for marker in ['THIRD_WARM_PASS','G4_PUBLISH_PASS','FOURTH_WARM_PASS polls=83 expands=82 candidates=402 costs=231']:assert marker in log,marker
    if enabled:assert '\nPASS 'in(d/'restore_seed_trace.txt').read_text()
    else:assert(d/'restore_seed_trace.txt').stat().st_size==0
    m['status']=m['cases'][case]['status']='observed'
except Exception as e:
    m.update(status='failed',error=repr(e));raise
finally:save()
print('RESTORE_SEED_OBSERVED',case,enabled)
