from pathlib import Path
import hashlib,json,os,subprocess,sys,shutil,time,importlib.util
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 base=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed';out.mkdir();src=out/'sources';shutil.copytree(base/'sources',src)
 dp=ROOT/'adapters/natural_query_v1/make_replay.py';sp=importlib.util.spec_from_file_location('maker',dp);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);driver=m.make((src/'router.cpp').read_text());shutil.copyfile(dp,src/dp.name)
 cp=ROOT/'adapters/natural_query_v1/derive_cost_inputs.py';spec=importlib.util.spec_from_file_location('cost_inputs',cp);cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);router,driver,observer=cm.derive((src/'router.cpp').read_text(),driver)
 (src/'router.cpp').write_text(router);(src/'replay.cpp').write_text(driver);(src/'cost_observer.txt').write_text(observer)
 for path in [cp,ROOT/'adapters/natural_query_v1/export_inputs.hpp',Path(__file__)]:shutil.copyfile(path,src/path.name)
 bm=json.loads((base/'manifest.json').read_text());env={k:v for k,v in os.environ.items()if not k.startswith(('RW_','B_'))};env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None);env.update(bm['environment']);env['B_NATURAL_QUERY']=str(out)
 rec=dict(status='running',base=str(base),base_audit_sha256=sha(base/'source_bound_audit.json'),sources={str(p.relative_to(src)):sha(p)for p in src.rglob('*')if p.is_file()},commands=[],environment={k:v for k,v in env.items()if k.startswith(('RW_','B_'))})
 def save():(out/'manifest.json').write_text(json.dumps(rec,indent=2)+'\n')
 save()
 try:
  for stage,argv in [('compile',['g++','-std=c++17','-O3','-g','-fno-fast-math','-fno-omit-frame-pointer','-no-pie','-pthread','-I',str(src/'include'),str(src/'replay.cpp'),'-o',str(out/'replay')]),('execute',['taskset','-c','8',str(out/'replay'),bm['input'],str(base)])]:
   t=time.monotonic()
   with(out/(stage+'.log')).open('w')as f:r=subprocess.run(argv,env=env,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=600)
   rec['commands'].append(dict(stage=stage,argv=argv,exit_code=r.returncode,elapsed_s=time.monotonic()-t));save();assert r.returncode==0,stage
  names=['initial_nodes.u32','initial_overflow.u32','initial_caches.u32','prices.u32','state.txt','initial_heap.u32','events.txt','search_final_nodes.u32','search_final_heap.u32']
  rec['compared']={n:sha(out/n)for n in names}
  for n,v in rec['compared'].items():assert sha(base/n)==v,n
  rec['status']='passed'
 except Exception as e:rec.update(status='failed',error=repr(e));raise
 finally:rec['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'};save()
 print('NATURAL_QUERY_COST_INPUTS_PASSED')
if __name__=='__main__':main()
