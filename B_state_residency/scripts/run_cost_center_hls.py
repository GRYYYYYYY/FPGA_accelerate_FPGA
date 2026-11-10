from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();unit=ROOT/'results/cost_center_cpu_20261025';gate=json.loads((unit/'source_bound_audit.json').read_text());um=json.loads((unit/'manifest.json').read_text());assert gate['status']=='passed'and gate['manifest_sha256']==sha(unit/'manifest.json')
 src=out/'sources';shutil.copytree(unit/'sources',src);base=src/'hls/cost_center/v1'
 for n in ['cost_center.hpp','kernel.cpp']:
  spec=um['sources']['hls/cost_center/v1/'+n];assert sha(base/n)==spec['sha256']==sha(Path(spec['path']))
 assert sha(src/'hls/search_cost/exact_v2/softfloat32.hpp')==um['sources']['hls/search_cost/exact_v2/softfloat32.hpp']['sha256']
 bench=ROOT/'hardware/hls/cost_center/v1/rtl_testbench.cpp';shutil.copyfile(bench,base/'rtl_testbench.cpp');shutil.copyfile(unit/'vectors.txt',out/'vectors.txt');assert sha(out/'vectors.txt')==um['vectors_sha256'];shutil.copyfile(__file__,out/'runner.py')
 m={'status':'running','pid':os.getpid(),'unit_audit_sha256':sha(unit/'source_bound_audit.json'),'unit_manifest_sha256':sha(unit/'manifest.json'),'sources':{str(p.relative_to(src)):sha(p)for p in src.rglob('*')if p.is_file()},'vectors_sha256':sha(out/'vectors.txt'),'commands':[],'part':'xcu280-fsvh2892-2L-e','clock_ns':10,'cosim_argv_preflight':{'csim_argv':'','cosim_argv':'','both_empty_allowed':True},'scope':'Actual HLS frozen-vector Csim/csynth/Verilog cosim of finite-center scalar, not joined packet or search'}
 tcl='''set center_out [file normalize [file dirname [info script]]]
set center_src [file join $center_out sources hls cost_center v1]
cd $center_out
puts "COST_CENTER_HLS_BEGIN version=[version -short]"
open_project -reset cost_center_step
set_top cost_center_step
add_files [file join $center_src kernel.cpp] -cflags "-std=c++14 -I$center_src"
add_files -tb [file join $center_src rtl_testbench.cpp] -cflags "-std=c++14 -I$center_src"
add_files -tb [file join $center_out vectors.txt]
open_solution -reset solution1 -flow_target vivado
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 10.000 -name default
csim_design -clean
file copy [file join $center_out cost_center_step solution1 csim build observed.txt] [file join $center_out csim_observed.txt]
csynth_design
if {![file isdirectory [file join $center_out cost_center_step solution1 syn]]} {error "Missing synthesis before cosim"}
cosim_design -rtl verilog -tool xsim -trace_level none
close_project
puts "COST_CENTER_HLS_DONE"
exit
'''
 (out/'run_hls.tcl').write_text(tcl);(out/'hls_config.cfg').write_text('[hls]\nsyn.top=cost_center_step\nsyn.file=sources/hls/cost_center/v1/kernel.cpp\ntb.file=sources/hls/cost_center/v1/rtl_testbench.cpp\ncsim.argv=\ncosim.argv=\npart=xcu280-fsvh2892-2L-e\nclock=10ns\n')
 m['tcl_sha256']=sha(out/'run_hls.tcl');m['config_sha256']=sha(out/'hls_config.cfg')
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  cmd=[str(HLS),'-f',str(out/'run_hls.tcl')];start=time.monotonic()
  with (out/'hls.log').open('w')as log:
   proc=subprocess.Popen(cmd,cwd=out,stdout=log,stderr=subprocess.STDOUT);m['commands'].append({'argv':cmd,'pid':proc.pid});save();code=proc.wait()
  m['commands'][-1].update(exit_code=code,elapsed_s=time.monotonic()-start);save();assert code==0
  log=(out/'hls.log').read_text();assert 'COST_CENTER_HLS_DONE'in log and not re.search(r'^ERROR:',log,re.M)
  rpt=out/'cost_center_step/solution1/sim/report/cost_center_step_cosim.rpt';assert re.search(r'Verilog\s*\|\s*Pass',rpt.read_text())
  assert sha(unit/'vectors.txt')==m['vectors_sha256']==sha(out/'vectors.txt')
  m.update(status='completed',flow_log_sha256=sha(out/'hls.log'),cosim_report_sha256=sha(rpt),observations={str(p.relative_to(out)):sha(p)for p in out.rglob('*observed.txt')},generated_rtl_artifacts={str(p.relative_to(out)):sha(p)for p in(out/'cost_center_step/solution1/syn').rglob('*')if p.is_file()});save();print('COST_CENTER_HLS_COMPLETE',flush=True)
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
