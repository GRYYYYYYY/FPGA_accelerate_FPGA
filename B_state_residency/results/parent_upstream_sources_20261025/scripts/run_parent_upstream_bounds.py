from pathlib import Path
import json,shutil,subprocess,sys,time,hashlib
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();base=ROOT/'results/natural_query_rtl_v1';bm=json.loads((base/'manifest.json').read_text());assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
 m=dict(status='running',sources={},commands=[],base_audit_sha256=sha(base/'source_bound_audit.json'))
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 rtl=[]
 for name in bm['rtl']:
  if Path(name).name.startswith('tb_'):continue
  p=base/'sources'/name
  if p.name=='postprev_inputs.sv':p=ROOT/'hardware/variants/parent_upstream_v1/postprev_inputs.sv'
  q=src/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);m['sources'][name]=sha(q);rtl.append(q)
 tb=ROOT/'hardware/variants/parent_upstream_v1/tb_parent_bounds.sv';shutil.copyfile(tb,src/tb.name);rtl.append(src/tb.name);m['sources'][tb.name]=sha(tb)
 for name in bm['sources']:
  if name.endswith('.dat'):
   p=base/'sources'/name;shutil.copyfile(p,out/p.name)
 shutil.copyfile(__file__,src/'runner.py');m['sources']['runner.py']=sha(src/'runner.py');(out/'run.tcl').write_text('run 10ms\nquit\n');save()
 try:
  for stage,args in [('compile',[BIN/'xvlog','--sv',*rtl]),('elaborate',[BIN/'xelab','tb_parent_bounds','-s','bounds','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','bounds','--tclbatch','run.tcl','--log','simulate.log'])]:
   t=time.monotonic();args=list(map(str,args))
   with(out/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(args,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=180)
   m['commands'].append(dict(stage=stage,argv=args,exit_code=r.returncode,elapsed_s=time.monotonic()-t));save();assert r.returncode==0,stage
  log=(out/'simulate.log').read_text();assert 'PARENT_UPSTREAM_BOUNDS_PASS checks=21'in log and 'Fatal:'not in log and '$finish called'in log;m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'};save()
 print('PARENT_UPSTREAM_BOUNDARIES_PASSED')
if __name__=='__main__':main()
