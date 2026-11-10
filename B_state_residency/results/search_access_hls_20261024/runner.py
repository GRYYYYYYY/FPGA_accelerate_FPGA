"""Run verified scalar geometry through actual HLS 2022.2 Csim/synthesis/RTL."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 unit=ROOT/'results/search_access_unit_v3_20261024';gate=json.loads((unit/'source_bound_audit.json').read_text())
 assert gate['status']=='passed' and gate['manifest_sha256']==sha(unit/'manifest.json')
 out=ROOT/'results/search_access_hls_20261024';out.mkdir();src=out/'sources';shutil.copytree(unit/'sources',src)
 for name in ['access_machine.hpp','kernel.cpp']:
  assert sha(ROOT/'hardware/hls/search_access/v2'/name)==sha(src/name)
 for name in ['testbench.cpp','hls_config.cfg']:(src/name).write_bytes((ROOT/'hardware/hls/search_access/v2'/name).read_bytes())
 (out/'vectors.txt').write_bytes((unit/'vectors.txt').read_bytes());
 # Explicitly test malformed op/state/config; each failure has an all-zero body.
 valid=[0,0,0,0,0,0,17,0,12,12,1,0,0,0,0,0,-1,1,-1,1]
 invalid=[]
 for field,value in [(0,2),(1,0),(1,19),(2,16),(4,3),(7,512),(8,256),(9,256),(10,256)]:
  x=valid[:];x[0]=1;x[1]=1;x[field]=value;invalid.append(x)
 with (out/'vectors.txt').open('a')as f:
  for i,x in enumerate(invalid):f.write(f'{195175+i} {46656+i} '+' '.join(f'{v&0xffffffff:08x}'for v in x+[1,0,0,0,0,0])+'\n')
 (out/'runner.py').write_bytes(Path(__file__).read_bytes())
 m={'status':'running','pid':os.getpid(),'unit_gate_sha256':sha(unit/'source_bound_audit.json'),'sources':{p.name:sha(p)for p in src.iterdir()},'vectors_sha256':sha(out/'vectors.txt'),'runner_sha256':sha(Path(__file__)),'commands':[],'part':'xcu280-fsvh2892-2L-e','clock_ns':10,'cosim_argv_preflight':{'csim_argv':'','cosim_argv':'','both_empty_allowed':True}}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 tcl='''set acc_out [file normalize [file dirname [info script]]]
set acc_src [file join $acc_out sources]
cd $acc_out
puts "ACCESS_HLS_BEGIN version=[version -short]"
open_project -reset access_step
set_top access_step
add_files [file join $acc_src kernel.cpp] -cflags "-std=c++14 -I$acc_src"
add_files -tb [file join $acc_src testbench.cpp] -cflags "-std=c++14 -I$acc_src"
add_files -tb [file join $acc_out vectors.txt]
open_solution -reset solution1 -flow_target vivado
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 10.000 -name default
csim_design -clean
file copy [file join $acc_out access_step solution1 csim build observed.txt] [file join $acc_out csim_observed.txt]
csynth_design
if {![file isdirectory [file join $acc_out access_step solution1 syn]]} {error "Missing synthesis before cosim"}
cosim_design -rtl verilog -tool xsim -trace_level none
close_project
puts "ACCESS_HLS_DONE"
exit
'''
 (out/'run_hls.tcl').write_text(tcl);m['tcl_sha256']=sha(out/'run_hls.tcl');save()
 try:
  start=time.monotonic();cmd=[str(HLS),'-f',str(out/'run_hls.tcl')]
  with (out/'hls.log').open('w') as log:
   proc=subprocess.Popen(cmd,cwd=out,stdout=log,stderr=subprocess.STDOUT);m['commands'].append({'argv':cmd,'pid':proc.pid});save();code=proc.wait(timeout=1200)
  m['commands'][-1].update(exit_code=code,elapsed_s=time.monotonic()-start);assert code==0
  log=(out/'hls.log').read_text();assert 'ACCESS_HLS_DONE' in log and not re.search(r'^ERROR:',log,re.M)
  rpt=out/'access_step/solution1/sim/report/access_step_cosim.rpt';assert re.search(r'Verilog\s*\|\s*Pass',rpt.read_text())
  m.update(status='completed',cosim_report_sha256=sha(rpt),flow_log_sha256=sha(out/'hls.log'),observations={str(p.relative_to(out)):sha(p)for p in out.rglob('*observed.txt')},generated_rtl_artifacts={str(p.relative_to(out)):sha(p)for p in (out/'access_step/solution1/syn').rglob('*')if p.is_file()})
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:save()
 print('ACCESS_HLS_COMPLETE')
if __name__=='__main__':main()
