from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir()
 dep=ROOT/'results/owner_store_v2_20261024';gate=json.loads((dep/'source_bound_audit.json').read_text());assert gate['status']=='passed' and gate['manifest_sha256']==sha(dep/'manifest.json')
 m={'status':'preparing','model_gate_sha256':sha(dep/'source_bound_audit.json'),'sources':{},'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 files=list((ROOT/'hardware/variants/owner_axi_v1').glob('*'))+[dep/'sources/owner_store.hpp',ROOT/'results/access_fabric_v3_20261024/sources/coordinate/axi_file_memory.sv',Path(__file__)]
 for p in files:
  if p.is_file():shutil.copyfile(p,src/p.name);m['sources'][p.name]={'path':str(p),'sha256':sha(p)}
 (out/'run.tcl').write_text('run 500ms\nquit\n');save()
 stages=[('vector_build',['g++','-std=c++17','-O2','-fsanitize=undefined','-fno-sanitize-recover=all','-I'+str(src),str(src/'make_vectors.cpp'),'-o',str(out/'make_vectors')]),('vectors',[out/'make_vectors']),('compile',[BIN/'xvlog','--sv',src/'owner_state_store.sv',src/'axi_file_memory.sv',src/'tb_owner.sv']),('elaborate',[BIN/'xelab','tb_owner','-s','test','--debug','typical','--mt','2'])]
 try:
  for stage,argv in stages:
   m['status']=stage;c={'stage':stage,'argv':list(map(str,argv))};m['commands'].append(c);save()
   with (out/(stage+'.stdout.log')).open('w')as f:c['exit_code']=subprocess.call(c['argv'],cwd=out,stdout=f,stderr=subprocess.STDOUT)
   save();assert c['exit_code']==0,stage
  shutil.copyfile(out/'initial.bin',out/'actual.bin')
  argv=[str(BIN/'xsim'),'test','--tclbatch','run.tcl','--log','simulate.log']
  for k,v in {'vectors':out/'commands.txt','observed':out/'observed.txt','owner0':out/'actual.bin','ownerlog':out/'axi.txt'}.items():argv+=['--testplusarg',k+'='+str(v)]
  c={'stage':'simulate','argv':argv};m['commands'].append(c);m['status']='simulate';save();t=time.monotonic()
  with (out/'simulate.stdout.log').open('w')as f:c['exit_code']=subprocess.call(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT)
  c['elapsed_s']=time.monotonic()-t;save();assert c['exit_code']==0
  log=(out/'simulate.log').read_text();hits=[s for s in log.splitlines()if s.startswith('OWNER_AXI_PASS ')]
  assert len(hits)==1 and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log,log[-2000:]
  assert (out/'actual.bin').read_bytes()==(out/'expected.bin').read_bytes()
  m.update(status='passed',result=hits[0]);save();print(hits[0])
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
