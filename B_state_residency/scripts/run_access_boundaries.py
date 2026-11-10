from pathlib import Path
import hashlib,json,subprocess,shutil,sys,time
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();dep=ROOT/'results/access_service_20261024';dm=json.loads((dep/'manifest.json').read_text());g=json.loads((dep/'source_bound_audit.json').read_text());assert g['status']=='passed'and g['manifest_sha256']==sha(dep/'manifest.json')
 m={'status':'running','functional_manifest_sha256':sha(dep/'manifest.json'),'sources':{},'cases':{}}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 paths=[]
 for name,s in dm['sources'].items():
  if Path(name).suffix not in ['.v','.sv','.dat']or name.startswith('tb_'):continue
  p=dep/'sources'/name;assert sha(p)==s['sha256'];paths.append(p)
 paths+=list(p for p in (ROOT/'hardware/variants/access_boundaries_v1').iterdir()if p.is_file())+[Path(__file__)]
 for p in paths:
  shutil.copyfile(p,src/p.name);m['sources'][p.name]={'path':str(p),'sha256':sha(p)}
  if p.suffix=='.dat':shutil.copyfile(p,out/p.name)
 save()
 try:
  for top,marker in [('tb_access_memory_call','ACCESS_MEMORY_CALL_PASS'),('tb_access_boundaries','ACCESS_BOUNDARIES_PASS')]:
   d=out/top;d.mkdir();(d/'run.tcl').write_text('run 2ms\nquit\n');cm=m['cases'][top]={'status':'running','commands':[]};save()
   for stage,args in [('compile',[BIN/'xvlog','--sv']+[src/p.name for p in paths if p.suffix in ['.v','.sv']]),('elaborate',[BIN/'xelab',top,'-s','test','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','test','--tclbatch','run.tcl','--log','simulate.log'])]:
    c={'stage':stage,'argv':list(map(str,args))};cm['commands'].append(c);save();t=time.monotonic()
    with (d/(stage+'.stdout.log')).open('w')as log:c['exit_code']=subprocess.call(c['argv'],cwd=d,stdout=log,stderr=subprocess.STDOUT)
    c['elapsed_s']=time.monotonic()-t;save();assert c['exit_code']==0,(top,stage)
   log=(d/'simulate.log').read_text();hits=[s for s in log.splitlines()if s.startswith(marker)];assert len(hits)==1 and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log,log[-2000:]
   cm.update(status='passed',result=hits[0],artifacts={p.name:sha(p)for p in d.iterdir()if p.is_file()and p.suffix in ['.log','.tcl','.txt']});save();print(hits[0],flush=True)
  m['status']='passed';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
