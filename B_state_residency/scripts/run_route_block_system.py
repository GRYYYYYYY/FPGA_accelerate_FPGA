"""Replay an audited full-system case with the two-file route idle blocking candidate on the audited combined baseline."""
from pathlib import Path
import copy,importlib.util,json,shutil,subprocess,sys,time
from run_checkpoint_authority import ROOT,sha

p=Path(sys.argv[1]).resolve();ref=Path(sys.argv[2]).resolve()
assert p.parent==ref.parent
rm=json.loads((ref/'manifest.json').read_text());ra=json.loads((ref/'source_bound_audit.json').read_text())
assert ra['status']=='passed'and ra['manifest_sha256']==sha(ref/'manifest.json')and rm['status']=='observed'
assert len(rm['cases'])==1;case=next(iter(rm['cases']))
variant=ROOT/'hardware/variants/route_block_loops_v1';builder=variant/'build.py'
spec=importlib.util.spec_from_file_location('route_block_builder',builder);b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
baseline,fixed=b.sources(False),b.sources(True)
proof_path=ROOT/'results/route_block_identity_20261027.json';proof=json.loads(proof_path.read_text())
assert proof['status']=='local_boolean_identity_verified_not_rtl_validation'and proof['valuations']==262144
assert proof['analyzer_sha256']==sha(ROOT/'scripts/analyze_route_block_identity.py')
receipt=ROOT/'results'/f'{ref.name}_restore_20261025.json';rr=json.loads(receipt.read_text())
assert rr['status']=='passed'and rr['audit_byte_identical']and rr['audit_sha256']==sha(ref/'source_bound_audit.json')
evidence=dict(builder_sha256=sha(builder),identity_sha256=sha(proof_path),reference_restore_sha256=sha(receipt),
              candidate_sha256={n:sha(variant/'fixed'/n)for n in fixed})
p.mkdir();src=p/'sources';src.mkdir();d=p/case;d.mkdir()
m=copy.deepcopy(rm);m.update(status='running',cases={case:dict(status='running',commands=[])},
    route_block_reference=str(ref),route_block_reference_audit_sha256=sha(ref/'source_bound_audit.json'),
    route_block_evidence=evidence,
    scope='Full-system replay of an audited real four-query case with two route idle blocking changes on the restored combined baseline. Exact native/AXI/final-memory comparison required. Does not prove full-root absence of other loops or timing closure.')
for n,e in rm['sources'].items():
    assert sha(ref/'sources'/n)==e['sha256'],n
    q=src/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ref/'sources'/n,q)
for n,text in fixed.items():
    replacement=variant/'fixed'/n
    assert (src/n).read_text()==baseline[n]
    assert replacement.read_text()==text
    shutil.copyfile(replacement,src/n);m['sources'][n]=dict(path=str(replacement),sha256=sha(src/n))
shutil.copyfile(Path(__file__),src/'runner.py');m['sources']['runner.py']=dict(path=str(Path(__file__)),sha256=sha(src/'runner.py'))
for key in ['scoreboards','next_scoreboards','third_scoreboards','fourth_scoreboards']:
    for n,h in rm[key].items():assert sha(ref/n)==h;shutil.copyfile(ref/n,p/n)
assert sha(Path(m['binding']))==m['binding_sha256']
regions=json.loads(Path(m['binding']).read_text())['regions']
for name,key in [('design.bin','design'),('cost.bin','cost_history_prices_nets')]:shutil.copyfile(Path(regions[key]['path']),d/name)
with(d/'owners.bin').open('wb')as f:
    for key in ['owners','owner_pool','owner_allocator']:
        with Path(regions[key]['path']).open('rb')as source:shutil.copyfileobj(source,f)
for name in ['g3.bin','snapshot.bin','pool.bin']:shutil.copyfile(d/'owners.bin',d/name)
shutil.copyfile(Path(regions['owner_allocator']['path']),d/'allocator.bin')
with(d/'labels.bin').open('wb')as f:f.truncate(3145728)
for f in src.rglob('*.dat'):shutil.copyfile(f,d/f.name)
shutil.copyfile(ref/case/'run.tcl',d/'run.tcl')
def save():(p/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
save()
try:
    for old in rm['cases'][case]['commands']:
        stage=old['stage'];argv=[a.replace(str(ref),str(p))for a in old['argv']];start=time.monotonic()
        with(d/(stage+'.stdout.log')).open('w')as f:
            r=subprocess.run(argv,cwd=d,stdout=f,stderr=subprocess.STDOUT,timeout=2400)
        m['cases'][case]['commands'].append(dict(stage=stage,argv=argv,exit_code=r.returncode,elapsed_s=time.monotonic()-start));save()
        assert r.returncode==0,stage
        print(stage,'completed',flush=True)
    log=(d/'simulate.log').read_text();assert 'Fatal:'not in log and '$finish called'in log
    for marker in ['THIRD_WARM_PASS','G4_PUBLISH_PASS','FOURTH_WARM_PASS polls=83 expands=82 candidates=402 costs=231']:assert marker in log,marker
    m['status']=m['cases'][case]['status']='observed'
except Exception as e:
    m.update(status='failed',error=repr(e));raise
finally:save()
print('ROUTE_BLOCK_SYSTEM_OBSERVED',p.name)
