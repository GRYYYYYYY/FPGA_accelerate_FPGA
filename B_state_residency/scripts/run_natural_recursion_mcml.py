from pathlib import Path
import hashlib,json,shutil,subprocess,os,sys,time
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();base=Path(sys.argv[2]).resolve();bm=json.loads((base/'manifest.json').read_text());bg=json.loads((base/'source_bound_audit.json').read_text());assert bm['status']==bg['status']=='passed'and bg['manifest_sha256']==sha(base/'manifest.json')
 for n,h in bm['sources'].items():assert sha(base/'sources'/n)==h
 assert sha(base/'router')==bm['artifacts']['router']
 matrix=ROOT/'results/research_chain_20261022T183749Z/matrix';mm=json.loads((matrix/'manifest.json').read_text());assert mm['status']=='passed';row=next(r for r in mm['runs']if r['dataset']=='vtr_mcml'and r['mode']=='serial'and r['variant']=='original'and r['repetition']==0);assert row['verified']and row['exit_code']==0
 ds=next(d for d in mm['config']['datasets']if d['id']=='vtr_mcml');inp=ROOT/ds['input'];reference=matrix/(row['name']+'.result');assert sha(inp)==ds['input_sha256']and sha(reference)==row['result_sha256']
 shutil.copytree(base/'sources',out/'sources');shutil.copy2(base/'router',out/'router');shutil.copyfile(__file__,out/'sources'/Path(__file__).name)
 env={k:v for k,v in os.environ.items()if not k.startswith(('RW_','B_'))};env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None);env.update(row['environment']);env['B_RECURSION_CENSUS']=str(out/'attempts.txt')
 m={'status':'running','sources':{str(p.relative_to(out/'sources')):sha(p)for p in(out/'sources').rglob('*')if p.is_file()},'base_build_sha256':bm['base_build_sha256'],'observer_base_manifest_sha256':sha(base/'manifest.json'),'observer_base_audit_sha256':sha(base/'source_bound_audit.json'),'binary_reused_sha256':sha(out/'router'),'matrix_manifest_sha256':sha(matrix/'manifest.json'),'input':str(inp),'input_sha256':sha(inp),'reference_result':str(reference),'reference_result_sha256':sha(reference),'reference_log_sha256':sha(reference.with_suffix('.log')),'environment':{k:v for k,v in env.items()if k.startswith(('RW_','B_'))},'commands':[],'scope':'Full original serial MCML routing census with exactly the same observer source and binary as logicnets. No selected snapshots or RTL replay; timings are instrumented receipts.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  argv=['taskset','-c',mm['config']['serial_cpu'],str(out/'router'),str(inp),str(out/'router.result')];start=time.monotonic()
  with(out/'execute.log').open('w')as f:r=subprocess.run(argv,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=600)
  m['commands'].append({'stage':'execute','argv':argv,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0
  assert sha(out/'router.result')==m['reference_result_sha256']
  sys.path.insert(0,str(ROOT/'scripts'));from profile_real import parse_log
  observed=parse_log((out/'execute.log').read_text());assert all(observed[k]==row['metrics'][k]for k in ['iterations','overused','pushes','used_nodes','wire_length','convergence']);m.update(status='passed',metrics=observed)
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'};save()
 print('NATURAL_MCML_CENSUS_ROUTE_EQUIVALENT',flush=True)
if __name__=='__main__':main()
