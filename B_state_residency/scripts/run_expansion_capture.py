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
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();graph=ROOT/'results/graph_image_20261024';oracle=ROOT/'results/expansion_inputs_20261024'
 m={'status':'running','pid':os.getpid(),'sources':{},'gates':{},'cases':{},'oracle':str(oracle),'graph':str(graph),'scope':'Actual graph reader + persistent design store + children HLS engine + paged exclusion engine, compared with original CPU getChildren under scripted query/label contexts. Not full routing, timing/occupancy update, or board.'}
 def save():
  q=out/'manifest.tmp';q.write_text(json.dumps(m,indent=2)+'\n');q.replace(out/'manifest.json')
 def freeze(p,name):
  q=src/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);m['sources'][name]={'path':str(p),'sha256':sha(p)};return q
 rtl=[]
 for result,pre in [('auto_pager_20261024','pager'),('children_engine_v2_20261024','children'),('graph_reader_20261024','graph'),('design_store_v3_20261024','design')]:
  dep=ROOT/'results'/result;gate=read(dep/'source_bound_audit.json');dm=read(dep/'manifest.json');assert dm['status']==gate['status']=='passed'and gate['manifest_sha256']==sha(dep/'manifest.json')
  m['gates'][str(dep/'manifest.json')]=sha(dep/'manifest.json');m['gates'][str(dep/'source_bound_audit.json')]=sha(dep/'source_bound_audit.json')
  for name,spec in dm['sources'].items():
   if not name.endswith(('.sv','.v'))or Path(name).name.startswith('tb_')or name.startswith('hls3/'):continue
   p=dep/'sources'/name;assert sha(p)==spec['sha256'];rtl.append(freeze(p,pre+'/'+name))
 for dep in [oracle,graph]:
  gate=read(dep/'source_bound_audit.json');assert gate['status']=='passed'and gate['manifest_sha256']==sha(dep/'manifest.json')
  for name in ['manifest.json','source_bound_audit.json']:m['gates'][str(dep/name)]=sha(dep/name)
 for p in sorted((ROOT/'hardware/variants/expansion_v1').iterdir()):
  if p.is_file():
   q=freeze(p,'expansion/'+p.name)
   if q.suffix=='.sv' and not p.name.startswith('tb_'):rtl.append(q)
 
 for name in ['children_frames.sv','expansion_capture.sv','tb_expansion_capture.sv']:
  rtl.append(freeze(ROOT/'hardware/variants/recursive_frames_v1'/name,'capture/'+name))
 freeze(Path(__file__),'runner.py');m['rtl']=[str(p.relative_to(src))for p in rtl];save()
 def run(stage,args,d,rows):
  row={'stage':stage,'argv':list(map(str,args))};rows.append(row);save();t=time.monotonic()
  with (d/(stage+'.stdout.log')).open('w')as log:
   proc=subprocess.Popen(row['argv'],cwd=d,stdout=log,stderr=subprocess.STDOUT);row['pid']=proc.pid;save();row['exit_code']=proc.wait();row['elapsed_s']=time.monotonic()-t;save()
  assert row['exit_code']==0,(d,stage)
 try:
  for case,limit,define in [('pilot',16,None),('full',0,None),('pressure',0,'PRESSURE')]:
   d=out/case;d.mkdir();cm=m['cases'][case]={'status':'running','commands':[],'limit':limit,'define':define};save()
   shutil.copyfile(oracle/'initial_design.bin',d/'design.bin');cm['initial_design_sha256']=sha(d/'design.bin')
   with (d/'labels.bin').open('wb')as f:f.truncate(49152)
   (d/'run.tcl').write_text('run 1000ms\nquit\n');save()
   run('compile',[BIN/'xvlog','--sv']+(['--define',define]if define else [])+rtl,d,cm['commands'])
   run('elaborate',[BIN/'xelab','tb_node_expansion','-s','expansion','--debug','typical','--mt','2'],d,cm['commands'])
   args=[BIN/'xsim','expansion','--tclbatch','run.tcl','--log','simulate.log']
   params={'graph0':graph/'offsets.u32le','graph1':graph/'edges.u32le','graph2':graph/'nodes.rrt32','graphlog':d/'graph_axi.txt','design0':d/'design.bin','designlog':d/'design_axi.txt','labels0':d/'labels.bin','labelslog':d/'label_axi.txt','vectors':oracle/'vectors.txt','output':d/'output.txt','attrs':graph/'nodes.rrt32','limit':limit}
   for key,value in params.items():args+=['--testplusarg',key+'='+str(value)]
   run('simulate',args,d,cm['commands']);log=(d/'simulate.log').read_text();hits=[s for s in log.splitlines()if s.startswith('EXPANSION_CAPTURE_PASS ')]
   assert len(hits)==1 and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log,(case,log[-3000:])
   if limit==0:assert sha(d/'design.bin')==sha(oracle/'expected_design.bin')
   cm.update(status='passed',result=hits[0],artifacts={p.name:sha(p)for p in d.iterdir()if p.is_file()and p.suffix in('.log','.tcl','.txt','.bin')});save();print(case,hits[0],flush=True)
  for name,spec in m['sources'].items():assert sha(src/name)==spec['sha256']==sha(Path(spec['path']))
  for path,digest in m['gates'].items():assert sha(Path(path))==digest
  m['status']='passed';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
