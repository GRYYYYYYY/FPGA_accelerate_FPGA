from pathlib import Path
import json,hashlib,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();inp=ROOT/'results/cost_state_inputs_20261025';im=json.loads((inp/'manifest.json').read_text());assert im['status']=='passed'
 m={'status':'running','input_manifest_sha256':sha(inp/'manifest.json'),'sources':{},'cases':{},'scope':'Actual AXI design history, price and net state with host edit/publish fence; CPU initial import and scripted edits; not yet joined candidate/cost or full route'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 rtl=[]
 for p in [ROOT/'hardware/variants/cost_state_v1/cost_state_store.sv',ROOT/'hardware/variants/cost_state_v1/tb_cost_state.sv',ROOT/'results/access_owner_v3_20261024/sources/coordinate/axi_file_memory.sv']:
  q=src/p.name;shutil.copyfile(p,q);m['sources'][p.name]={'path':str(p),'sha256':sha(q)};rtl.append(q)
 shutil.copyfile(__file__,src/'runner.py');save()
 try:
  for case,ic in im['cases'].items():
   d=out/case;d.mkdir();layout=ic['layout'];cm=m['cases'][case]={'status':'running','commands':[]};save()
   for n,digest in ic['artifacts'].items():assert sha(inp/case/n)==digest
   shutil.copyfile(inp/case/'initial.bin',d/'state.bin');(d/'run.tcl').write_text('run 10ms\nquit\n')
   args=[BIN/'xsim','state','--tclbatch','run.tcl','--log','simulate.log'];params={'state0':d/'state.bin','statelog':d/'axi.txt','commands':inp/case/'commands.txt','observed':d/'observed.txt','nodes':layout['nodes'],'nets':layout['net_count'],'bytes':layout['total_bytes'],'prices_offset':layout['prices_offset'],'nets_offset':layout['nets_offset']}
   for k,v in params.items():args+=['--testplusarg',k+'='+str(v)]
   for stage,argv in [('compile',[BIN/'xvlog','--sv']+rtl),('elaborate',[BIN/'xelab','tb_cost_state','-s','state','--debug','typical','--mt','2']),('simulate',args)]:
    start=time.monotonic();row={'stage':stage,'argv':list(map(str,argv))};cm['commands'].append(row);save()
    with (d/(stage+'.stdout.log')).open('w')as f:row['exit_code']=subprocess.call(row['argv'],cwd=d,stdout=f,stderr=subprocess.STDOUT)
    row['elapsed_s']=time.monotonic()-start;save();assert row['exit_code']==0,(case,stage)
   log=(d/'simulate.log').read_text();hits=[s for s in log.splitlines()if s.startswith('COST_STATE_PASS ')];assert len(hits)==1 and 'Fatal:'not in log and '$finish called'in log,log[-2500:]
   assert sha(d/'state.bin')==ic['artifacts']['expected.bin']and(d/'observed.txt').read_bytes()==(inp/case/'expected.txt').read_bytes()
   cm.update(status='passed',result=hits[0],artifacts={p.name:sha(p)for p in d.iterdir()if p.is_file()and p.suffix in ['.bin','.txt','.log','.tcl']});save();print(hits[0],flush=True)
  m['status']='passed';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
