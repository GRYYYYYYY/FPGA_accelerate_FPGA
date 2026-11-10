from pathlib import Path
import hashlib,json,shutil,subprocess,time,sys
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();dep=ROOT/'results/coordinate_service_v2_20261024';dm=json.loads((dep/'manifest.json').read_text());dg=json.loads((dep/'source_bound_audit.json').read_text());assert dg['status']=='passed'and dg['manifest_sha256']==sha(dep/'manifest.json')
 m={'status':'running','functional_manifest_sha256':sha(dep/'manifest.json'),'sources':{},'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 rtl=[]
 for n in dm['rtl']:
  if Path(n).name.startswith('tb_'):continue
  p=dep/'sources'/n;q=src/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);m['sources'][n]={'path':str(p),'sha256':sha(p)};rtl.append(q)
 for p in [ROOT/'hardware/variants/coordinate_boundaries_v1/tb_coordinate_integration.sv',ROOT/'hardware/variants/coordinate_boundaries_v1/integration_body.inc',Path(__file__)]:
  shutil.copyfile(p,src/p.name);m['sources'][p.name]={'path':str(p),'sha256':sha(p)}
 rtl.append(src/'tb_coordinate_integration.sv');(out/'labels.bin').write_bytes(bytes(3145728));(out/'run.tcl').write_text('run 20ms\nquit\n');save()
 inp=ROOT/'results/coordinate_inputs_20261024/synthetic';params={'graph0':inp/'offsets.u32le','graph1':inp/'edges.u32le','graph2':inp/'nodes.rrt32','graphlog':out/'graph_axi.txt','tables0':inp/'rows.bin','tables1':inp/'columns.bin','tableslog':out/'table_axi.txt','labels0':out/'labels.bin','labelslog':out/'label_axi.txt'}
 args=[BIN/'xsim','test','--tclbatch','run.tcl','--log','simulate.log']
 for k,v in params.items():args+=['--testplusarg',k+'='+str(v)]
 try:
  for stage,argv in [('compile',[BIN/'xvlog','--sv','--define','PRESSURE']+rtl),('elaborate',[BIN/'xelab','tb_coordinate_service','-s','test','--debug','typical','--mt','2']),('simulate',args)]:
   c={'stage':stage,'argv':list(map(str,argv))};m['commands'].append(c);save();t=time.monotonic()
   with (out/(stage+'.stdout.log')).open('w')as log:c['exit_code']=subprocess.call(c['argv'],cwd=out,stdout=log,stderr=subprocess.STDOUT)
   c['elapsed_s']=time.monotonic()-t;save();assert c['exit_code']==0,stage
  log=(out/'simulate.log').read_text();hits=[s for s in log.splitlines()if s.startswith('INTEGRATED_BOUNDARIES_PASS ')];assert len(hits)==1 and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log,log[-2000:]
  m.update(status='passed',result=hits[0],artifacts={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.suffix in ['.log','.tcl','.txt','.bin']});save();print(hits[0])
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
