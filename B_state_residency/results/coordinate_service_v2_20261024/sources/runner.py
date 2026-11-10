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
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();graph=ROOT/'results/graph_image_20261024';oracle=ROOT/'results/coordinate_inputs_20261024'
 m={'status':'running','pid':os.getpid(),'sources':{},'gates':{},'cases':{},'oracle':str(oracle),'graph':str(graph),'scope':'Actual graph reader + row/column table reader + paged labels + coordinate controller. resident_zero defaults; selected real nodes and synthetic Laguna; not dense routing equivalence or board.'}
 def save():
  q=out/'manifest.tmp';q.write_text(json.dumps(m,indent=2)+'\n');q.replace(out/'manifest.json')
 def freeze(p,name):
  q=src/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);m['sources'][name]={'path':str(p),'sha256':sha(p)};return q
 rtl=[]
 for result,pre in [('auto_pager_20261024','pager'),('graph_reader_20261024','graph')]:
  dep=ROOT/'results'/result;gate=read(dep/'source_bound_audit.json');dm=read(dep/'manifest.json');assert dm['status']==gate['status']=='passed'and gate['manifest_sha256']==sha(dep/'manifest.json')
  m['gates'][str(dep/'manifest.json')]=sha(dep/'manifest.json');m['gates'][str(dep/'source_bound_audit.json')]=sha(dep/'source_bound_audit.json')
  for name,spec in dm['sources'].items():
   if not name.endswith(('.sv','.v'))or Path(name).name.startswith('tb_')or name.startswith('hls3/'):continue
   p=dep/'sources'/name;assert sha(p)==spec['sha256'];rtl.append(freeze(p,pre+'/'+name))
 for dep in [oracle,ROOT/'results/coordinate_inputs_verify_20261024',graph]:
  dm=read(dep/'manifest.json');assert dm['status'] in ['prepared','passed']
  for name,digest in dm['artifacts'].items():assert sha(dep/name)==digest
  m['gates'][str(dep/'manifest.json')]=sha(dep/'manifest.json')
 q=freeze(ROOT/'hardware/variants/expansion_v1/axi_file_memory.sv','axi_file_memory.sv');rtl.append(q)
 for p in sorted((ROOT/'hardware/variants/coordinate_v1').iterdir()):
  if p.is_file():
   q=freeze(p,'coordinate/'+p.name)
   if q.suffix=='.sv':rtl.append(q)
 freeze(Path(__file__),'runner.py');m['rtl']=[str(p.relative_to(src))for p in rtl];save()
 def run(stage,args,d,rows):
  row={'stage':stage,'argv':list(map(str,args))};rows.append(row);save();t=time.monotonic()
  with (d/(stage+'.stdout.log')).open('w')as log:
   proc=subprocess.Popen(row['argv'],cwd=d,stdout=log,stderr=subprocess.STDOUT);row['pid']=proc.pid;save();row['exit_code']=proc.wait();row['elapsed_s']=time.monotonic()-t;save()
  assert row['exit_code']==0,(d,stage)
 try:
  run('vectors',[sys.executable,'-I',src/'coordinate/make_vectors.py',oracle,graph,out],out,m.setdefault('preparation',[]))
  for case,fixture,define in [('synthetic','synthetic',None),('real','real',None),('pressure','synthetic','PRESSURE')]:
   d=out/case;d.mkdir(exist_ok=True);meta=read(out/fixture/'metadata.json');gp=oracle/'synthetic' if fixture=='synthetic' else graph
   cm=m['cases'][case]={'status':'running','commands':[],'fixture':fixture,'define':define};save()
   with (d/'labels.bin').open('wb')as f:f.truncate(3145728)
   (d/'run.tcl').write_text('run 1000ms\nquit\n');save()
   run('compile',[BIN/'xvlog','--sv']+(['--define',define]if define else [])+rtl,d,cm['commands'])
   run('elaborate',[BIN/'xelab','tb_coordinate_service','-s','coordinate','--debug','typical','--mt','2'],d,cm['commands'])
   args=[BIN/'xsim','coordinate','--tclbatch','run.tcl','--log','simulate.log']
   params={'graph0':gp/'offsets.u32le','graph1':gp/'edges.u32le','graph2':gp/'nodes.rrt32','graphlog':d/'graph_axi.txt','tables0':oracle/fixture/'rows.bin','tables1':oracle/fixture/'columns.bin','tableslog':d/'table_axi.txt','labels0':d/'labels.bin','labelslog':d/'label_axi.txt','vectors':out/fixture/'vectors.txt','output':d/'output.txt',**{k:meta[k] for k in ['nodes','edges','rows','columns']}}
   for key,value in params.items():args+=['--testplusarg',key+'='+str(value)]
   run('simulate',args,d,cm['commands']);log=(d/'simulate.log').read_text();hits=[s for s in log.splitlines()if s.startswith('COORDINATE_PASS ')]
   assert len(hits)==1 and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log,(case,log[-3000:])
   cm.update(status='passed',result=hits[0],artifacts={p.name:sha(p)for p in d.iterdir()if p.is_file()and p.suffix in('.log','.tcl','.txt','.bin')});save();print(case,hits[0],flush=True)
  for name,spec in m['sources'].items():assert sha(src/name)==spec['sha256']==sha(Path(spec['path']))
  for path,digest in m['gates'].items():assert sha(Path(path))==digest
  m['status']='passed';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
