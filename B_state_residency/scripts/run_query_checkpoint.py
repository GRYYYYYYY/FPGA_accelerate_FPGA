from pathlib import Path
import json,sys,subprocess,shutil,time
from run_checkpoint_authority import ROOT,BIN,sha

def main():
 p=Path(sys.argv[1]).resolve();p.mkdir();src=p/'sources';src.mkdir();bench=ROOT/'hardware/variants/query_checkpoint_v1';m={'status':'running','sources':{},'commands':[],'scope':'Native query lifecycle sequence checkpoint with registered mock service/search/route backends. Not unified cold recovery or full-query AXI integration.'}
 for q in [bench/'query_lifecycle.sv',bench/'tb_query_checkpoint.sv',bench/'build.py',Path(__file__)]:shutil.copyfile(q,src/q.name);m['sources'][q.name]=sha(src/q.name)
 (p/'run.tcl').write_text('run 1ms\nquit\n')
 def save():(p/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 try:
  for stage,args in [('compile',[BIN/'xvlog','--sv',src/'query_lifecycle.sv',src/'tb_query_checkpoint.sv']),('elaborate',[BIN/'xelab','tb_query_checkpoint','-s','qcp','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','qcp','--tclbatch','run.tcl','--log','simulate.log','--testplusarg','events='+str(p/'events.txt')])]:
   args=list(map(str,args));start=time.monotonic()
   with(p/(stage+'.stdout.log')).open('w')as fp:r=subprocess.run(args,cwd=p,stdout=fp,stderr=subprocess.STDOUT,timeout=180)
   m['commands'].append({'stage':stage,'argv':args,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0,stage
  log=(p/'simulate.log').read_text();assert 'QUERY_CHECKPOINT_PASS'in log and 'Fatal:'not in log and '$finish called'in log,log[-1200:];m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={q.name:sha(q)for q in p.iterdir()if q.is_file()and q.name!='manifest.json'};save()
if __name__=='__main__':main()
