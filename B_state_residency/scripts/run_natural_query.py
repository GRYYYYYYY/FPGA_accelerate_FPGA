from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time,importlib.util
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();build=ROOT/'build/real_trace';bm=json.loads((build/'build.json').read_text());config=json.loads((ROOT/'configs/real_trace.json').read_text());original=build/'original.cpp';assert sha(original)==bm['original']['source_sha256']and sha(build/'router_original')==bm['original']['binary_sha256']
 inp=ROOT/config['input'];assert sha(inp)==config['input_sha256'];reference=ROOT/'results/real_trace_20261022T165136Z/original_0.result';ref_log=reference.with_suffix('.log');assert reference.exists()
 shutil.copyfile(original,src/'original.cpp');include=ROOT.parent/'_shared/assets/gpu_router_original/rewrite/cpp_router/include';shutil.copytree(include,src/'include')
 dp=ROOT/'adapters/natural_query_v1/derive.py';spec=importlib.util.spec_from_file_location('derive_census',dp);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);code,changes=mod.derive(original.read_text());(src/'router.cpp').write_text(code);(src/'changes.json').write_text(json.dumps(changes,indent=2)+'\n')
 for p in [dp,ROOT/'adapters/natural_query_v1/natural_query.hpp',Path(__file__)]:shutil.copyfile(p,src/p.name)
 m={'status':'running','sources':{str(p.relative_to(src)):sha(p)for p in src.rglob('*')if p.is_file()},'base_build_sha256':sha(build/'build.json'),'input':str(inp),'input_sha256':sha(inp),'reference_result':str(reference),'reference_result_sha256':sha(reference),'reference_log_sha256':sha(ref_log),'commands':[],'scope':'First prepared natural query full node-state snapshot and actual candidate/push/poll observation. Original full route hash gate. No RTL replay or speed claim.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save();env={k:v for k,v in os.environ.items()if not k.startswith(('RW_','B_'))};env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None);env.update(config['environment']);env['B_NATURAL_QUERY']=str(out);m['environment']={k:v for k,v in env.items()if k.startswith(('RW_','B_'))};save()
 flags=['-std=c++17','-O3','-g','-fno-fast-math','-fno-omit-frame-pointer','-no-pie','-pthread']
 try:
  for stage,argv in [('compile',['g++',*flags,'-I',str(src/'include'),'-I',str(src),str(src/'router.cpp'),'-o',str(out/'router')]),('execute',['taskset','-c',str(config['cpu']),str(out/'router'),str(inp),str(out/'router.result')])]:
   start=time.monotonic()
   with(out/(stage+'.log')).open('w')as f:r=subprocess.run(argv,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=600)
   m['commands'].append({'stage':stage,'argv':argv,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0,stage
  assert sha(out/'router.result')==m['reference_result_sha256'],'routing changed'
  sys.path.insert(0,str(ROOT/'scripts'));from profile_real import parse_log
  observed=parse_log((out/'execute.log').read_text());expected=parse_log(ref_log.read_text());assert observed['convergence']==expected['convergence'] and all(observed[k]==expected[k]for k in ['iterations','overused','pushes','used_nodes','wire_length'])
  m.update(status='passed',metrics=observed)
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'};save()
 print('NATURAL_QUERY_ROUTE_EQUIVALENT',flush=True)
if __name__=='__main__':main()
