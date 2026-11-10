"""Run verified scalar geometry through actual HLS 2022.2 Csim/synthesis/RTL."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 unit=ROOT/'results/search_geometry_unit_v3_20261024';gate=json.loads((unit/'source_bound_audit.json').read_text())
 assert gate['status']=='passed' and gate['manifest_sha256']==sha(unit/'manifest.json')
 out=ROOT/'results/search_geometry_hls_20261024';out.mkdir();src=out/'sources';shutil.copytree(unit/'sources',src)
 for p in (ROOT/'hardware/hls/search_geometry/v1').iterdir():assert sha(p)==sha(src/p.name)
 (out/'vectors.txt').write_bytes((unit/'vectors.txt').read_bytes());(out/'runner.py').write_bytes(Path(__file__).read_bytes())
 m={'status':'running','pid':os.getpid(),'unit_gate_sha256':sha(unit/'source_bound_audit.json'),'sources':{p.name:sha(p)for p in src.iterdir()},'vectors_sha256':sha(out/'vectors.txt'),'runner_sha256':sha(Path(__file__)),'commands':[],'part':'xcu280-fsvh2892-2L-e','clock_ns':10,'cosim_argv_preflight':{'csim_argv':'','cosim_argv':'','both_empty_allowed':True}}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 tcl='''set geo_out [file normalize [file dirname [info script]]]
set geo_src [file join $geo_out sources]
cd $geo_out
puts "GEOMETRY_HLS_BEGIN version=[version -short]"
open_project -reset geometry_step
set_top geometry_step
add_files [file join $geo_src kernel.cpp] -cflags "-std=c++14 -I$geo_src"
add_files -tb [file join $geo_src testbench.cpp] -cflags "-std=c++14 -I$geo_src"
add_files -tb [file join $geo_out vectors.txt]
open_solution -reset solution1 -flow_target vivado
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 10.000 -name default
csim_design -clean
file copy [file join $geo_out geometry_step solution1 csim build observed.txt] [file join $geo_out csim_observed.txt]
csynth_design
if {![file isdirectory [file join $geo_out geometry_step solution1 syn]]} {error "Missing synthesis before cosim"}
cosim_design -rtl verilog -tool xsim -trace_level none
close_project
puts "GEOMETRY_HLS_DONE"
exit
'''
 (out/'run_hls.tcl').write_text(tcl);m['tcl_sha256']=sha(out/'run_hls.tcl');save()
 try:
  start=time.monotonic();cmd=[str(HLS),'-f',str(out/'run_hls.tcl')]
  with (out/'hls.log').open('w') as log:
   proc=subprocess.Popen(cmd,cwd=out,stdout=log,stderr=subprocess.STDOUT);m['commands'].append({'argv':cmd,'pid':proc.pid});save();code=proc.wait(timeout=1200)
  m['commands'][-1].update(exit_code=code,elapsed_s=time.monotonic()-start);assert code==0
  log=(out/'hls.log').read_text();assert 'GEOMETRY_HLS_DONE' in log and not re.search(r'^ERROR:',log,re.M)
  rpt=out/'geometry_step/solution1/sim/report/geometry_step_cosim.rpt';assert re.search(r'Verilog\s*\|\s*Pass',rpt.read_text())
  m.update(status='completed',cosim_report_sha256=sha(rpt),flow_log_sha256=sha(out/'hls.log'),observations={str(p.relative_to(out)):sha(p)for p in out.rglob('*observed.txt')},generated_rtl_artifacts={str(p.relative_to(out)):sha(p)for p in (out/'geometry_step/solution1/syn').rglob('*')if p.is_file()})
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:save()
 print('GEOMETRY_HLS_COMPLETE')
if __name__=='__main__':main()
