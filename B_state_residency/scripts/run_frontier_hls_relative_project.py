"""Frozen Vitis HLS2022.2 Csim->Csynth->full-capacity RTL cosim, no retry."""
from pathlib import Path
import json,os,subprocess,shutil,sys,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')
def main():
 out=ROOT/'results/frontier_hls_relative_project_20261024';out.mkdir();design=ROOT/'hardware/hls/frontier'
 gates={}
 for label,p in [('cpp',ROOT/'results/frontier_cpp_verified_20261024/source_bound_audit.json'),('real_route',ROOT/'results/bounded_frontier_real_20261024/source_bound_audit.json')]:
  g=json.loads(p.read_text());assert g['status']=='passed';gates[label]=sha(p)
 assert json.loads((ROOT/'results/frontier_cpp_verified_20261024/source_bound_audit.json').read_text())['helper_sha256']==json.loads((ROOT/'results/bounded_frontier_real_20261024/source_bound_audit.json').read_text())['helper_sha256']
 shutil.copytree(design/'rearchitect',out/'rearchitect')
 src=out/'rearchitect/v1/src';tb=out/'rearchitect/v1/tb';cpp=ROOT/'results/frontier_cpp_verified_20261024'
 for folder in [src,tb]:
  for p in folder.iterdir():assert sha(p)==sha(cpp/p.relative_to(out))
 m={'status':'prepared','pid':os.getpid(),'gates':gates,'runner_sha256':sha(Path(__file__)),'sources':{str(p.relative_to(out)):sha(p) for p in (out/'rearchitect').rglob('*') if p.is_file()},'part':'xcu280-fsvh2892-2L-e','clock_ns':10.0,'top':'frontier_step','capacity':65536,'cosim_argv_preflight':{'csim_argv':'','cosim_argv':'','both_empty_allowed':True},'commands':[],'scope':'Standalone single-context frontier component, not native-state integration, full FPGA routing or physical timing closure.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  script='''set frontier_out [file normalize [file dirname [info script]]]
set frontier_src [file join $frontier_out rearchitect v1 src]
set frontier_tb [file join $frontier_out rearchitect v1 tb]
puts "FRONTIER_HLS_BEGIN version=[version -short]"
cd $frontier_out
open_project -reset frontier_step
set_top frontier_step
add_files [file join $frontier_src kernel_hls.cpp] -cflags "-std=c++14 -fno-fast-math -I$frontier_src"
add_files -tb [file join $frontier_tb testbench.cpp] -cflags "-std=c++14 -fno-fast-math -I$frontier_src -I$frontier_tb"
open_solution -reset solution1 -flow_target vivado
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 10.000 -name default
puts "FRONTIER_CSIM_BEGIN"
csim_design -clean
set frontier_fd [open [file join $frontier_out csim_completed.txt] w]
puts $frontier_fd "FRONTIER_CSIM_DONE"
close $frontier_fd
puts "FRONTIER_CSYNTH_BEGIN"
csynth_design
set frontier_fd [open [file join $frontier_out csynth_completed.txt] w]
puts $frontier_fd "FRONTIER_CSYNTH_DONE"
close $frontier_fd
if {![file isdirectory [file join $frontier_out frontier_step solution1 syn]]} {error "Missing synthesis output before cosim"}
puts "FRONTIER_COSIM_BEGIN argv_empty_allowed=1"
cosim_design -rtl verilog -tool xsim -trace_level none
set frontier_fd [open [file join $frontier_out cosim_completed.txt] w]
puts $frontier_fd "FRONTIER_COSIM_DONE"
close $frontier_fd
close_project
puts "FRONTIER_HLS_DONE"
exit
'''
  (out/'run_hls.tcl').write_text(script);m['tcl_sha256']=sha(out/'run_hls.tcl')
  (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
  argv=[str(HLS),'-f',str(out/'run_hls.tcl')]
  with (out/'flow.stdout.log').open('w') as log:
   proc=subprocess.Popen(argv,cwd=out,stdout=log,stderr=subprocess.STDOUT);m['status']='running';m['commands'].append({'stage':'hls','argv':argv,'pid':proc.pid});save();code=proc.wait();m['commands'][-1]['exit_code']=code;save();assert code==0
  text=(out/'flow.stdout.log').read_text();assert 'FRONTIER_HLS_DONE' in text and not re.search(r'^ERROR:',text,re.M)
  for stage in ['csim','csynth','cosim']:assert (out/(stage+'_completed.txt')).read_text()=='FRONTIER_'+stage.upper()+'_DONE\n'
  cosim=out/'frontier_step/solution1/sim/report/frontier_step_cosim.rpt';assert cosim.exists() and re.search(r'Verilog\s*\|\s*Pass',cosim.read_text(),re.I)
  assert 'FRONTIER_TEST_PASS capacity=65536 checks=135228 comparisons=1000169' in text
  m.update(status='passed',flow_log_sha256=sha(out/'flow.stdout.log'),cosim_report_sha256=sha(cosim));save();print('FRONTIER_HLS_FLOW_PASS',flush=True)
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
