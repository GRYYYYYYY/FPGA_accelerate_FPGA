from pathlib import Path
import json,hashlib,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();rtl=[]
 base=ROOT/'results/candidate_compile_v2_20261024';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 m={'status':'running','scope':'Actual candidate integration with real CSR and initial owner image; scripted query labels; no cost/push/full routing or board','sources':{},'cases':{},'gates':{}}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 def freeze(p,name):
  q=src/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);m['sources'][name]={'path':str(p),'sha256':sha(q)};return q
 for pstr in bm['rtl']:
  p=Path(pstr)
  if p.name.startswith('tb_'):continue
  rel=str(p.relative_to(base/'sources'));assert sha(p)==bm['sources'][rel]['sha256']
  if p.name=='candidate_controller.sv':p=ROOT/'hardware/variants/candidate_pipeline_v1/candidate_controller.sv'
  rtl.append(freeze(p,rel))
 for name,p in [('tb_candidate.sv',ROOT/'hardware/variants/candidate_pipeline_v1/tb_candidate.sv'),('axi_file_memory.sv',ROOT/'results/access_owner_v3_20261024/sources/coordinate/axi_file_memory.sv')]:rtl.append(freeze(p,name))
 freeze(Path(__file__),'runner.py');m['rtl']=[str(p.relative_to(src))for p in rtl]
 inp=ROOT/'results/candidate_decisions_20261024';own=ROOT/'results/candidate_initial_owner_20261024';graph=ROOT/'results/graph_image_20261024';tables=ROOT/'results/coordinate_inputs_20261024/real'
 for dep in [base,inp,own]:assert json.loads((dep/'manifest.json').read_text())['status']=='passed';m['gates'][str(dep/'manifest.json')]=sha(dep/'manifest.json')
 save()
 try:
  cases=[('pilot',16,None)]if len(sys.argv)<3 else [('full',0,None),('pressure',0,'PRESSURE'),('default',0,'DEFAULT_DIRECTORY')]
  for case,limit,define in cases:
   d=out/case;d.mkdir();cm=m['cases'][case]={'status':'running','limit':limit,'commands':[]};save()
   shutil.copyfile(inp/'initial_design.bin',d/'design.bin');shutil.copyfile(own/'owners.bin',d/'owners.bin');(d/'labels.bin').write_bytes(bytes(31457280 if define=='DEFAULT_DIRECTORY'else 3145728));(d/'run.tcl').write_text('run 1000ms\nquit\n')
   args=[BIN/'xsim','candidate','--tclbatch','run.tcl','--log','simulate.log']
   params={'graph0':graph/'offsets.u32le','graph1':graph/'edges.u32le','graph2':graph/'nodes.rrt32','graphlog':d/'graph_axi.txt','design0':d/'design.bin','designlog':d/'design_axi.txt','tables0':tables/'rows.bin','tables1':tables/'columns.bin','tableslog':d/'table_axi.txt','labels0':d/'labels.bin','labelslog':d/'label_axi.txt','owners0':d/'owners.bin','ownerslog':d/'owner_axi.txt','vectors':inp/'vectors.txt','output':d/'observed.txt','limit':limit}
   for k,v in params.items():args+=['--testplusarg',k+'='+str(v)]
   for stage,argv in [('compile',[BIN/'xvlog','--sv']+(['--define',define]if define else [])+rtl),('elaborate',[BIN/'xelab','tb_candidate','-s','candidate','--debug','typical','--mt','2']),('simulate',args)]:
    start=time.monotonic();row={'stage':stage,'argv':list(map(str,argv))};cm['commands'].append(row);save()
    with (d/(stage+'.stdout.log')).open('w')as f:row['exit_code']=subprocess.call(row['argv'],cwd=d,stdout=f,stderr=subprocess.STDOUT)
    row['elapsed_s']=time.monotonic()-start;save();assert row['exit_code']==0,(case,stage)
   log=(d/'simulate.log').read_text();hits=[s for s in log.splitlines()if s.startswith('CANDIDATE_PASS ')];assert len(hits)==1 and 'Fatal:'not in log and '$finish called'in log,log[-3000:]
   assert sha(d/'owners.bin')==sha(own/'owners.bin')
   if not limit:assert sha(d/'design.bin')==sha(inp/'expected_design.bin')
   cm.update(status='passed',result=hits[0],artifacts={p.name:sha(p)for p in d.iterdir()if p.is_file()and p.suffix in ['.bin','.txt','.log','.tcl']});save();print(hits[0],flush=True)
  m['status']='passed';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
