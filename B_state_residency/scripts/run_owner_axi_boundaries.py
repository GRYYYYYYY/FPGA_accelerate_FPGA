from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();dep=ROOT/'results/owner_axi_v2_20261024'
 gate=json.loads((dep/'source_bound_audit.json').read_text());assert gate['status']=='passed' and gate['manifest_sha256']==sha(dep/'manifest.json')
 m={'status':'running','functional_gate_sha256':sha(dep/'source_bound_audit.json'),'sources':{},'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 for p in [dep/'sources/owner_state_store.sv',dep/'sources/axi_file_memory.sv',ROOT/'hardware/variants/owner_axi_boundaries_v1/tb_owner_boundaries.sv',ROOT/'hardware/variants/owner_axi_boundaries_v1/boundary_body.inc',Path(__file__)]:
  shutil.copyfile(p,src/p.name);m['sources'][p.name]={'path':str(p),'sha256':sha(p)}
 (out/'actual.bin').write_bytes(bytes(16384));(out/'run.tcl').write_text('run 20ms\nquit\n');save()
 commands=[('compile',[BIN/'xvlog','--sv',src/'owner_state_store.sv',src/'axi_file_memory.sv',src/'tb_owner_boundaries.sv']),('elaborate',[BIN/'xelab','tb_owner','-s','test','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','test','--tclbatch','run.tcl','--log','simulate.log','--testplusarg','owner0='+str(out/'actual.bin'),'--testplusarg','ownerlog='+str(out/'axi.txt')])]
 try:
  for stage,argv in commands:
   c={'stage':stage,'argv':list(map(str,argv))};m['commands'].append(c);save();t=time.monotonic()
   with (out/(stage+'.stdout.log')).open('w')as f:c['exit_code']=subprocess.call(c['argv'],cwd=out,stdout=f,stderr=subprocess.STDOUT)
   c['elapsed_s']=time.monotonic()-t;save();assert c['exit_code']==0,stage
  log=(out/'simulate.log').read_text();hits=[s for s in log.splitlines()if s.startswith('OWNER_BOUNDARIES_PASS ')];assert len(hits)==1 and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log,log[-3000:]
  m.update(status='passed',result=hits[0]);save();print(hits[0])
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
