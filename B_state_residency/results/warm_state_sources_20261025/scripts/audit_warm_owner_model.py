from pathlib import Path
import json,hashlib,subprocess,os,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=Path(sys.argv[1]).resolve();base=Path('/tmp/B_state_residency_offer_20261025/warm_iter2_codec_v1');a=json.loads((base/'source_bound_audit.json').read_text());layout=json.loads((base/'layout.json').read_text());assert a['status']=='passed'
for n,f in [('check_owner_image.cpp','adapters/warm_state_v1/check_owner_image.cpp'),('owner_store.hpp','hardware/search/owner_state_v1/owner_store.hpp')]:assert sha(p/'sources'/n)==sha(ROOT/f)
env=dict(os.environ);env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None)
compile=['g++','-O2','-std=c++17','-UNDEBUG','-I',str(p/'sources'),str(p/'sources/check_owner_image.cpp'),'-o',str(p/'check')];execute=[str(p/'check'),str(base),str(layout['nodes']),str(layout['owner_pool_capacity'])]
with(p/'compile.log').open('w')as f:subprocess.run(compile,stdout=f,stderr=subprocess.STDOUT,check=True,env=env,timeout=60)
r=subprocess.run(execute,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=True,env=env,timeout=60);v=json.loads(r.stdout);assert v['nodes']==a['rows_verified'] and v['overflow_gets']==a['overflow_entries_verified'] and v['transitions']>0
(p/'execute.log').write_text(r.stdout)
(p/'sources/audit_warm_owner_model.py').write_bytes(Path(__file__).read_bytes())
result=dict(status='passed',auditor_sha256=sha(Path(__file__)),base_audit_sha256=sha(base/'source_bound_audit.json'),commands=[compile,execute],metrics=v,files={str(f.relative_to(p)):sha(f)for f in p.rglob('*')if f.is_file()and f.name!='source_bound_audit.json'},scope='Existing executable owner layout specification, all real primary/overflow GETs; one actual multiowner primary-removal/promotion/free-list-reuse sequence. Not RTL or all mutation permutations.')
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(v))
