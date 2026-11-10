from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();hls=ROOT/'results/search_access_hls_20261024';unit=ROOT/'results/search_access_unit_v3_20261024'
 m={'status':'running','sources':{},'gates':{},'commands':[],'scope':'Actual HLS with resident per-child decision controller; scripted source-verified dynamic responses. No host step loop. Physical service fabric and complete search not integrated.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 for dep in [hls,unit]:
  gate=json.loads((dep/'source_bound_audit.json').read_text());assert gate['status']=='passed'and gate['manifest_sha256']==sha(dep/'manifest.json')
  for name in ['manifest.json','source_bound_audit.json']:m['gates'][str(dep/name)]=sha(dep/name)
 hm=json.loads((hls/'manifest.json').read_text());paths=[]
 for name,h in hm['generated_rtl_artifacts'].items():
  if '/syn/verilog/'in name and Path(name).suffix in ['.v','.dat']:
   p=hls/name;assert sha(p)==h;paths.append(p)
 paths+=sorted(p for p in (ROOT/'hardware/variants/access_service_v1').iterdir()if p.is_file())
 for p in paths:
  shutil.copyfile(p,src/p.name);m['sources'][p.name]={'path':str(p),'sha256':sha(p)}
  if p.suffix=='.dat':shutil.copyfile(p,out/p.name)
 shutil.copyfile(unit/'vectors.txt',out/'vectors.txt');m['vectors_sha256']=sha(out/'vectors.txt');shutil.copyfile(Path(__file__),out/'runner.py');m['runner_sha256']=sha(Path(__file__));(out/'run.tcl').write_text('run 100ms\nquit\n');save()
 try:
  for stage,args in [('compile',[BIN/'xvlog','--sv']+[src/p.name for p in paths if p.suffix in ['.v','.sv']]),('elaborate',[BIN/'xelab','tb_access_service','-s','access','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','access','--tclbatch','run.tcl','--log','simulate.log'])]:
   c={'stage':stage,'argv':list(map(str,args))};m['commands'].append(c);save();t=time.monotonic()
   with (out/(stage+'.stdout.log')).open('w')as log:c['exit_code']=subprocess.call(c['argv'],cwd=out,stdout=log,stderr=subprocess.STDOUT)
   c['elapsed_s']=time.monotonic()-t;save();assert c['exit_code']==0,stage
  log=(out/'simulate.log').read_text();hits=[s for s in log.splitlines()if s.startswith('ACCESS_SERVICE_PASS ')];assert len(hits)==1 and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log,log[-2000:]
  m.update(status='passed',result=hits[0]);print(hits[0])
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.suffix in ['.log','.tcl','.txt']};save()
if __name__=='__main__':main()
