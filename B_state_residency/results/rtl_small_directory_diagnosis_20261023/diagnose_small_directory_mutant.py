"""Same-input simulator-option differential for unexpectedly early mutation failure."""
from pathlib import Path
import subprocess,json,hashlib,os
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/rtl_small_directory_diagnosis_20261023';out.mkdir()
 base=ROOT/'hardware/rtl/backing_frame_directory_small.sv'
 mutant=ROOT/'results/rtl_small_directory_mutants_20261023/drop_checkpoint_backing/backing_frame_directory_small.sv'
 tb=ROOT/'hardware/tb/tb_small_directory.sv'
 m={'status':'running','pid':os.getpid(),'runs':[],'sources':{str(p):sha(p) for p in [base,mutant,tb,Path(__file__)]}}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes());save()
 try:
  for name,rtl,debug in [('baseline_no_debug',base,False),('mutant_typical',mutant,True),('mutant_no_debug',mutant,False)]:
   d=out/name;d.mkdir();(d/base.name).write_bytes(rtl.read_bytes());(d/tb.name).write_bytes(tb.read_bytes());(d/'simulate.tcl').write_text('run 2ms\nquit\n')
   row={'name':name,'commands':[]};m['runs'].append(row);save()
   cmds=[('compile',[BIN/'xvlog','--sv',base.name,tb.name]),('elaborate',[BIN/'xelab','tb_small_directory','-s','diagnosis','--mt','2']+(['--debug','typical'] if debug else [])),('simulate',[BIN/'xsim','diagnosis','--tclbatch','simulate.tcl','--log','simulate.log'])]
   for stage,args in cmds:
    with (d/(stage+'.stdout.log')).open('w') as f:r=subprocess.run(list(map(str,args)),cwd=d,stdout=f,stderr=subprocess.STDOUT)
    row['commands'].append({'stage':stage,'argv':list(map(str,args)),'exit_code':r.returncode});save()
    if stage!='simulate':assert r.returncode==0
   log=(d/'simulate.log').read_text();row['verdict_lines']=[s for s in log.splitlines() if 'Fatal:' in s or s.startswith('SMALL_DIRECTORY_PASS')];save();print(name,row['verdict_lines'],flush=True)
  for p,h in m['sources'].items():assert sha(Path(p))==h
  m['status']='observations_complete';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
