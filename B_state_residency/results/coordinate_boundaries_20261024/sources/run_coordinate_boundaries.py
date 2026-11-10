from pathlib import Path
import hashlib,json,os,shutil,subprocess,time,sys
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();dep=ROOT/'results/coordinate_service_v2_20261024';gate=json.loads((dep/'source_bound_audit.json').read_text());assert gate['status']=='passed'and gate['manifest_sha256']==sha(dep/'manifest.json')
 m={'status':'running','functional_manifest_sha256':sha(dep/'manifest.json'),'sources':{},'cases':{}}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 for p in list((ROOT/'hardware/variants/coordinate_boundaries_v1').glob('*'))+[dep/'sources/coordinate/coordinate_controller.sv',dep/'sources/coordinate/geometry_table_reader.sv',Path(__file__)]:
  if p.is_file():shutil.copyfile(p,src/p.name);m['sources'][p.name]={'path':str(p),'sha256':sha(p)}
 save()
 try:
  for top,marker in [('coordinate_controller','CONTROLLER_BOUNDARIES_PASS'),('geometry_table_reader','TABLE_BOUNDARIES_PASS')]:
   d=out/top;d.mkdir();(d/'run.tcl').write_text('run 1ms\nquit\n');cm=m['cases'][top]={'status':'running','commands':[]};save()
   for name,args in [('compile',[BIN/'xvlog','--sv',src/(top+'.sv'),src/('tb_'+top+'.sv')]),('elaborate',[BIN/'xelab','tb_'+top,'-s','test','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','test','--tclbatch','run.tcl','--log','simulate.log'])]:
    c={'stage':name,'argv':list(map(str,args))};cm['commands'].append(c);save();t=time.monotonic()
    with (d/(name+'.stdout.log')).open('w')as log:c['exit_code']=subprocess.call(c['argv'],cwd=d,stdout=log,stderr=subprocess.STDOUT)
    c['elapsed_s']=time.monotonic()-t;save();assert c['exit_code']==0,(top,name)
   log=(d/'simulate.log').read_text();hits=[s for s in log.splitlines()if s.startswith(marker)];assert len(hits)==1 and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log,log[-2500:]
   cm.update(status='passed',result=hits[0],artifacts={p.name:sha(p)for p in d.iterdir()if p.is_file()and p.suffix in ['.log','.tcl']});save();print(hits[0],flush=True)
  m['status']='passed';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
