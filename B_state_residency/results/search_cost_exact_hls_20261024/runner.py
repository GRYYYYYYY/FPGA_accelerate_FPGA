"""Characterize native HLS float behavior; completion does not imply exact CPU agreement."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/search_cost_exact_hls_20261024';out.mkdir();src=out/'sources'
 shutil.copytree(ROOT/'hardware/hls/search_cost/exact_v2',src)
 assert sha(src/'search_cost.hpp')==sha(ROOT/'hardware/search/search_cost.hpp')
 cpp=ROOT/'results/search_cost_exact_cpp_v2_20261024'
 assert json.loads((cpp/'source_bound_audit.json').read_text())['status']=='passed'
 assert sha(src/'kernel.cpp')==sha(cpp/'sources/kernel.cpp') and sha(src/'softfloat32.hpp')==sha(cpp/'sources/softfloat32.hpp')
 (src/'vector_count.hpp').write_text('#pragma once\n#define COST_CASES 21576\n')
 gates={}
 for name in ['search_cost_unit_20261024','search_cost_real_20261024','search_cost_exact_cpp_v2_20261024','cost_capture_real_20261024']:
  p=ROOT/'results'/name/'source_bound_audit.json';assert json.loads(p.read_text())['status']=='passed';gates[name]=sha(p)
 m={'status':'preparing','pid':os.getpid(),'gates':gates,'sources':{p.name:sha(p)for p in src.iterdir()if p.is_file()},'runner_sha256':sha(Path(__file__)),'commands':[],'part':'xcu280-fsvh2892-2L-e','clock_ns':10,'cosim_argv_preflight':{'csim_argv':'','cosim_argv':'','both_empty_allowed':True},'scope':'Numerical characterization only. Cosim completion may contain exact-bit differences; independent audit decides compatibility.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 def run(stage,cmd,cwd):
  start=time.monotonic();m['status']=stage;m['commands'].append({'stage':stage,'argv':list(map(str,cmd))});save()
  with (out/(stage+'.log')).open('w') as log:
   p=subprocess.Popen(list(map(str,cmd)),cwd=cwd,stdout=log,stderr=subprocess.STDOUT);m['commands'][-1]['pid']=p.pid;save();code=p.wait(timeout=2400)
  m['commands'][-1].update(exit_code=code,elapsed_s=time.monotonic()-start);save();assert code==0,stage
 (out/'runner.py').write_bytes(Path(__file__).read_bytes());save()
 try:
  run('vector_build',['g++','-std=c++14','-O2','-fno-fast-math','-ffp-contract=off',src/'make_vectors_extended.cpp','-o',out/'make_vectors'],out)
  run('vectors',[out/'make_vectors',out/'synthetic_vectors.txt'],out)
  lines=(out/'synthetic_vectors.txt').read_text().splitlines()
  native=ROOT/'results/search_cost_native_hls_20261024'
  assert lines[:4776]==(native/'vectors.txt').read_text().splitlines() and len(lines)==5352
  for line in (ROOT/'results/cost_capture_real_20261024/cost_packets.txt').read_text().splitlines():
   v=line.split()
   if v[0]=='V':lines.append('4 '+' '.join(v[6:]))
  assert len(lines)==21576;(out/'vectors.txt').write_text('\n'.join(lines)+'\n')
  run('host_build',['g++','-std=c++14','-O2','-fno-fast-math','-ffp-contract=off',src/'kernel.cpp',src/'testbench.cpp','-o',out/'host_check'],out)
  run('host_check',[out/'host_check'],out)
  assert 'COST_CHARACTERIZED cases=21576 mismatched_cases=0 mismatched_words=0 normal_mismatches=0' in (out/'host_check.log').read_text()
  m['vectors_sha256']=sha(out/'vectors.txt');save()
  tcl='''set cost_out [file normalize [file dirname [info script]]]
set cost_src [file join $cost_out sources]
cd $cost_out
puts "COST_HLS_BEGIN version=[version -short]"
open_project -reset cost_step
set_top cost_step
add_files [file join $cost_src kernel.cpp] -cflags "-std=c++14 -fno-fast-math -ffp-contract=off -I$cost_src"
add_files -tb [file join $cost_src testbench.cpp] -cflags "-std=c++14 -fno-fast-math -ffp-contract=off -I$cost_src"
add_files -tb [file join $cost_out vectors.txt]
open_solution -reset solution1 -flow_target vivado
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 10.000 -name default
csim_design -clean
file copy [file join $cost_out cost_step solution1 csim build observed.txt] [file join $cost_out csim_observed.txt]
puts "COST_CSIM_DONE"
csynth_design
if {![file isdirectory [file join $cost_out cost_step solution1 syn]]} {error "Missing synthesis before cosim"}
puts "COST_CSYNTH_DONE"
cosim_design -rtl verilog -tool xsim -trace_level none
puts "COST_COSIM_DONE"
close_project
puts "COST_HLS_DONE"
exit
'''
  (out/'run_hls.tcl').write_text(tcl);m['tcl_sha256']=sha(out/'run_hls.tcl');save()
  run('hls',[HLS,'-f',out/'run_hls.tcl'],out)
  log=(out/'hls.log').read_text();assert 'COST_HLS_DONE' in log and not re.search(r'^ERROR:',log,re.M)
  rpt=out/'cost_step/solution1/sim/report/cost_step_cosim.rpt';assert re.search(r'Verilog\s*\|\s*Pass',rpt.read_text())
  m.update(status='characterized',flow_log_sha256=sha(out/'hls.log'),cosim_report_sha256=sha(rpt),observations={str(p.relative_to(out)):sha(p)for p in out.rglob('*observed.txt')},generated_rtl_artifacts={str(p.relative_to(out)):sha(p)for p in (out/'cost_step/solution1/syn').rglob('*')if p.is_file()});save();print('COST_EXACT_CHARACTERIZATION_COMPLETE',flush=True)
 except Exception as exc:m.update(status='failed',error=repr(exc));save();raise
if __name__=='__main__':main()
