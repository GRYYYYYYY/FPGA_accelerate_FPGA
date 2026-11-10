from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();base=ROOT/'results/candidate_cost23_pilot_20261025';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 m={'status':'running','sources':{},'commands':[],'scope':'Mock coordinate replies for branch control, actual geometry/cost HLS and collectors; explicit unsupported-landmark rejection and full version drift. Not real crossSLR graph routing.'};rtl=[]
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 for name,item in bm['sources'].items():
  if Path(name).suffix not in ['.sv','.v'] or name.split('/')[0]not in ['geometry','exact','geometry_service_v1','cost_service_v2','cost23']:continue
  p=base/'sources'/name;assert sha(p)==item['sha256'];q=src/Path(name).name;shutil.copyfile(p,q);m['sources'][q.name]=sha(q);rtl.append(q)
 p=ROOT/'hardware/variants/candidate_cost23_v1/tb_cost23_branches.sv';q=src/p.name;shutil.copyfile(p,q);m['sources'][q.name]=sha(q);rtl.append(q);shutil.copyfile(__file__,out/'runner.py');m['runner_sha256']=sha(out/'runner.py');(out/'run.tcl').write_text('run 2ms\nquit\n');save()
 try:
  for stage,args in [('compile',[BIN/'xvlog','--sv']+rtl),('elaborate',[BIN/'xelab','tb_cost23_branches','-s','branches','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','branches','--tclbatch','run.tcl','--log','simulate.log'])]:
   start=time.monotonic()
   with(out/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(list(map(str,args)),cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=180)
   m['commands'].append({'stage':stage,'argv':list(map(str,args)),'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0,stage
  log=(out/'simulate.log').read_text();assert 'COST23_BRANCHES_PASS cases=5'in log and 'Fatal:'not in log and '$finish called'in log;m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.suffix in ['.tcl','.log']};save()
 print(m['status'])
if __name__=='__main__':main()
