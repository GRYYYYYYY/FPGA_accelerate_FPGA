from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();inputs=ROOT/'results/metadata_inputs_20261024';im=read(inputs/'manifest.json');assert im['status']=='passed'
 m={'status':'running','input_manifest_sha256':sha(inputs/'manifest.json'),'sources':{},'gates':{},'cases':{}}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 def freeze(p,name):
  q=src/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);m['sources'][name]={'path':str(p),'sha256':sha(p)};return q
 rtl=[]
 for depname,name in [('graph_reader_20261024','graph_static_reader.sv'),('design_store_v3_20261024','design_state_store.sv')]:
  dep=ROOT/'results'/depname;g=read(dep/'source_bound_audit.json');assert g['status']=='passed'and g['manifest_sha256']==sha(dep/'manifest.json')
  m['gates'][str(dep/'source_bound_audit.json')]=sha(dep/'source_bound_audit.json');rtl.append(freeze(dep/'sources'/name,name))
 for p in (ROOT/'hardware/variants/metadata_v1').iterdir():
  if p.is_file():
   q=freeze(p,'metadata/'+p.name)
   if q.suffix in ['.sv','.v']:rtl.append(q)
 rtl.append(freeze(ROOT/'results/access_owner_v3_20261024/sources/coordinate/axi_file_memory.sv','axi_file_memory.sv'));freeze(Path(__file__),'runner.py');m['rtl']=[str(p.relative_to(src))for p in rtl];save()
 try:
  for case,cm in im['cases'].items():
   d=out/case;d.mkdir();gp=Path(cm['graph']);assert sha(gp/'nodes.rrt32')==cm['attrs_sha256']
   shutil.copyfile(inputs/case/'commands.txt',d/'commands.txt');assert sha(d/'commands.txt')==cm['commands_sha256']
   size=(cm['nodes']*16+63)&~63
   with (d/'design.bin').open('wb')as f:f.truncate(size)
   (d/'run.tcl').write_text('run 100ms\nquit\n');entry=m['cases'][case]={'status':'running','commands':[]};save()
   args=[BIN/'xsim','test','--tclbatch','run.tcl','--log','simulate.log']
   for k,v in {'graph0':gp/'offsets.u32le','graph1':gp/'edges.u32le','graph2':gp/'nodes.rrt32','graphlog':d/'graph_axi.txt','design0':d/'design.bin','designlog':d/'design_axi.txt','commands':d/'commands.txt','observed':d/'observed.txt','nodes':cm['nodes'],'edges':cm['edges']}.items():args+=['--testplusarg',k+'='+str(v)]
   for stage,argv in [('compile',[BIN/'xvlog','--sv']+rtl),('elaborate',[BIN/'xelab','tb_metadata','-s','test','--debug','typical','--mt','2']),('simulate',args)]:
    c={'stage':stage,'argv':list(map(str,argv))};entry['commands'].append(c);save();t=time.monotonic()
    with (d/(stage+'.stdout.log')).open('w')as f:c['exit_code']=subprocess.call(c['argv'],cwd=d,stdout=f,stderr=subprocess.STDOUT)
    c['elapsed_s']=time.monotonic()-t;save();assert c['exit_code']==0,(case,stage)
   log=(d/'simulate.log').read_text();hits=[s for s in log.splitlines()if s.startswith('METADATA_PASS ')];assert len(hits)==1 and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log,log[-2000:]
   assert f'cases={cm["count"]} 'in hits[0]
   entry.update(status='passed',result=hits[0],artifacts={p.name:sha(p)for p in d.iterdir()if p.is_file()and p.suffix in ['.bin','.txt','.log','.tcl']});save();print(case,hits[0],flush=True)
  m['status']='passed';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
