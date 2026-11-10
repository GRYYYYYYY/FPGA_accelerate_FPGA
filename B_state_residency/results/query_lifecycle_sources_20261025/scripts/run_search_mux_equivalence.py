from pathlib import Path
import json,hashlib,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();m=dict(status='running',sources={},commands=[],scope='Side-by-side dynamic/static selection, all4096 response bits for all16 known lanes plus256 gate combinations/lane, all outputs compared; two-state lane inputs, not formal equivalence.')
 for p in [ROOT/'hardware/variants/search_static_v2/search_host_fence.sv',ROOT/'hardware/variants/search_static_v2/tb_search_mux_equivalence.sv',Path(__file__)]:shutil.copyfile(p,src/p.name)
 original=(ROOT/'hardware/variants/search_scheduler_v1/search_host_fence.sv').read_text();(src/'reference.sv').write_text(original.replace('module search_host_fence(', 'module search_host_fence_reference('))
 m['sources']={p.name:sha(p)for p in src.iterdir()};(out/'run.tcl').write_text('run 1ms\nquit\n')
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  for stage,argv in [('compile',[BIN/'xvlog','--sv',src/'reference.sv',src/'search_host_fence.sv',src/'tb_search_mux_equivalence.sv']),('elaborate',[BIN/'xelab','tb_search_mux_equivalence','-s','miter','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','miter','--tclbatch','run.tcl','--log','simulate.log'])]:
   argv=list(map(str,argv));t=time.monotonic()
   with(out/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=180)
   m['commands'].append(dict(stage=stage,argv=argv,exit_code=r.returncode,elapsed_s=time.monotonic()-t));save();assert r.returncode==0
  log=(out/'simulate.log').read_text();assert 'SEARCH_MUX_EQUIVALENCE_PASS checks=69632'in log and 'Fatal:'not in log and '$finish called'in log;m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'};save()
 print('SEARCH_MUX_EQUIVALENCE_PASSED')
if __name__=='__main__':main()
