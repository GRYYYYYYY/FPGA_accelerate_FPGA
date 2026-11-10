"""Freeze and verify real AXI-backed design lifecycle storage (independent of query labels)."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time,shutil
ROOT=Path(__file__).resolve().parents[1]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();graph=ROOT/'results/graph_image_20261024'
 gm=read(graph/'manifest.json');gate=read(graph/'source_bound_audit.json');assert gate['status']=='passed'and gate['manifest_sha256']==sha(graph/'manifest.json')
 m={'status':'running','pid':os.getpid(),'sources':{},'graph':str(graph),'graph_manifest_sha256':sha(graph/'manifest.json'),'graph_gate_sha256':sha(graph/'source_bound_audit.json'),'graph_artifacts':{},'commands':[],'cases':{},'scope':'Actual RTL persistent design records and claim/keep-mask/publish service over file-backed AXI. Real graph node IDs/counts/children drive most store commands; keep decisions are synthetic, not complete getChildren or graph/pager integration.'}
 def save():
  q=out/'manifest.tmp';q.write_text(json.dumps(m,indent=2)+'\n');q.replace(out/'manifest.json')
 for name in ['offsets.u32le','edges.u32le']:
  digest=sha(graph/name);assert digest==gm['artifacts'][name];m['graph_artifacts'][name]=digest
 for p in sorted((ROOT/'hardware/variants/design_store_v1').iterdir())+[Path(__file__)]:
  if p.is_file():shutil.copyfile(p,src/p.name);m['sources'][p.name]={'path':str(p),'sha256':sha(p)}
 save()
 def run(stage,args,d,rows):
  row={'stage':stage,'argv':list(map(str,args))};rows.append(row);save();t=time.monotonic()
  with (d/(stage+'.stdout.log')).open('w')as log:
   proc=subprocess.Popen(row['argv'],cwd=d,stdout=log,stderr=subprocess.STDOUT);row['pid']=proc.pid;save();row['exit_code']=proc.wait();row['elapsed_s']=time.monotonic()-t;save()
  assert row['exit_code']==0,(d,stage)
 try:
  run('oracle',[sys.executable,src/'make_vectors.py',graph,out],out,m['commands'])
  m['oracle']={name:sha(out/name)for name in ['vectors.txt','coverage.json','expected_memory.bin']};save()
  size=read(out/'coverage.json')['backing_bytes']
  for case,limit,faults in [('pilot',200,0),('full',0,0),('faults',0,1)]:
   d=out/case;d.mkdir();cm=m['cases'][case]={'status':'running','commands':[]};save()
   with (d/'memory.bin').open('wb')as f:f.truncate(size)
   cm['initial_memory_sha256']=sha(d/'memory.bin');save()
   (d/'run.tcl').write_text('run 1000ms\nquit\n')
   run('compile',[BIN/'xvlog','--sv',src/'design_state_store.sv',src/'tb_design_state_store.sv'],d,cm['commands'])
   run('elaborate',[BIN/'xelab','tb_design_state_store','-s','design_store','--debug','typical','--mt','2'],d,cm['commands'])
   run('simulate',[BIN/'xsim','design_store','--tclbatch','run.tcl','--log','simulate.log','--testplusarg','memory='+str(d/'memory.bin'),'--testplusarg','vectors='+str(out/'vectors.txt'),'--testplusarg','trace='+str(d/'axi_trace.txt'),'--testplusarg','limit='+str(limit),'--testplusarg','faults='+str(faults)],d,cm['commands'])
   log=(d/'simulate.log').read_text();hits=[s for s in log.splitlines()if s.startswith('DESIGN_STORE_PASS ')]
   assert len(hits)==1 and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log,(case,log[-2200:])
   if case=='full':assert sha(d/'memory.bin')==m['oracle']['expected_memory.bin']
   cm.update(status='passed',result=hits[0],artifacts={p.name:sha(p)for p in d.iterdir()if p.is_file()and p.suffix in('.log','.tcl','.txt','.bin')});save();print(case,hits[0],flush=True)
  for name,spec in m['sources'].items():assert sha(src/name)==spec['sha256']==sha(Path(spec['path']))
  for name,digest in m['graph_artifacts'].items():assert sha(graph/name)==digest
  m['status']='passed';save()
 except Exception as exc:m.update(status='failed',error=repr(exc));save();raise
if __name__=='__main__':main()
