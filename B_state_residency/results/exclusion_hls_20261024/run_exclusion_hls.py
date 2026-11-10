"""Frozen 32-bit protocol and reduced-width exhaustion C++/HLS verification; no retry."""
from pathlib import Path
import json,os,re,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2')
def main():
 out=ROOT/'results/exclusion_hls_20261024';out.mkdir();design=ROOT/'hardware/hls/exclusion'
 real=ROOT/'results/exclusion_real_20261024/source_bound_audit.json';unit=ROOT/'results/exclusion_unit_20261024/manifest.json'
 rg=json.loads(real.read_text());ug=json.loads(unit.read_text());assert rg['status']==ug['status']=='passed'
 assert sha(design/'rearchitect/v1/src/exclusion_machine.hpp')==rg['helper_sha256']==ug['helper_sha256']
 assert (design/'rearchitect/v1/tb/original_functions.inc').read_bytes()==(unit.parent/'original_functions.inc').read_bytes()
 shutil.copytree(design/'rearchitect',out/'rearchitect');src=out/'rearchitect/v1/src';tb=out/'rearchitect/v1/tb'
 (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
 m={'status':'prepared','pid':os.getpid(),'runner_sha256':sha(Path(__file__)),'gates':{'real':sha(real),'unit':sha(unit)},'sources':{str(p.relative_to(out)):sha(p) for p in (out/'rearchitect').rglob('*') if p.is_file()},'part':'xcu280-fsvh2892-2L-e','clock_ns':10.0,'top':'exclusion_step','cases':{},'scope':'Standalone edge exclusion command protocol; generation32 branch cases plus real generation3 exhaustion; not native label integration or full FPGA search.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 def run(row,stage,argv,cwd,log):
  with log.open('w') as f:
   proc=subprocess.Popen(argv,cwd=cwd,stdout=f,stderr=subprocess.STDOUT);step={'stage':stage,'argv':argv,'pid':proc.pid};row['commands'].append(step);save();code=proc.wait();step['exit_code']=code;save();assert code==0,(stage,code)
 save()
 try:
  for bits in [32,3]:
   case=out/f'gen{bits}';case.mkdir();row={'status':'cpp','generation_bits':bits,'commands':[]};m['cases'][str(bits)]=row;save()
   flags=['-std=c++14','-fno-fast-math',f'-DEXCLUSION_GENERATION_BITS={bits}','-I'+str(src),'-I'+str(tb)]
   run(row,'cpp_build',['g++','-O2',*flags,'-I'+str(HLS/'include'),str(src/'kernel_hls.cpp'),str(tb/'testbench.cpp'),'-o',str(case/'cpp_test')],case,case/'cpp_build.log')
   run(row,'cpp_test',[str(case/'cpp_test')],case,case/'cpp_test.log')
   match=re.search(r'EXCLUSION_PORT_PASS generation_bits=(\d+) contexts=(\d+) checks=(\d+)',(case/'cpp_test.log').read_text());assert match
   assert int(match[1])==bits and int(match[2])==(27648 if bits==32 else 7)
   row['expected_pass_line']=match[0];row['checks']=int(match[3]);row['cpp_binary_sha256']=sha(case/'cpp_test')
   tcl=f'''set exclusion_out [file normalize [file dirname [info script]]]
cd $exclusion_out
puts "EXCLUSION_HLS_BEGIN generation_bits={bits} version=[version -short]"
open_project -reset exclusion_step
set_top exclusion_step
add_files {{{src/'kernel_hls.cpp'}}} -cflags {{{' '.join(flags)}}}
add_files -tb {{{tb/'testbench.cpp'}}} -cflags {{{' '.join(flags)}}}
open_solution -reset solution1 -flow_target vivado
set_part {{xcu280-fsvh2892-2L-e}}
create_clock -period 10.000 -name default
csim_design -clean
set f [open [file join $exclusion_out csim_completed.txt] w]; puts $f CSIM_DONE; close $f
csynth_design
set f [open [file join $exclusion_out csynth_completed.txt] w]; puts $f CSYNTH_DONE; close $f
if {{![file isdirectory [file join $exclusion_out exclusion_step solution1 syn]]}} {{error "Missing synthesis before cosim"}}
cosim_design -rtl verilog -tool xsim -trace_level none
set f [open [file join $exclusion_out cosim_completed.txt] w]; puts $f COSIM_DONE; close $f
close_project
puts "EXCLUSION_HLS_DONE generation_bits={bits}"
exit
'''
   (case/'run_hls.tcl').write_text(tcl);row['tcl_sha256']=sha(case/'run_hls.tcl');row['argv_preflight']={'csim':'','cosim':'','both_empty_allowed':True};row['status']='hls';m['status']='running';save()
   run(row,'hls',[str(HLS/'bin/vitis_hls'),'-f',str(case/'run_hls.tcl')],case,case/'flow.stdout.log')
   log=(case/'flow.stdout.log').read_text();assert f'EXCLUSION_HLS_DONE generation_bits={bits}' in log and not re.search(r'^ERROR:',log,re.M)
   assert log.count(row['expected_pass_line'])>=2
   report=case/'exclusion_step/solution1/sim/report/exclusion_step_cosim.rpt';assert re.search(r'Verilog\s*\|\s*Pass',report.read_text(),re.I)
   for stage in ['csim','csynth','cosim']:assert (case/(stage+'_completed.txt')).read_text()==stage.upper()+'_DONE\n'
   row.update(status='passed',flow_log_sha256=sha(case/'flow.stdout.log'),cosim_report_sha256=sha(report));save()
  m['status']='passed';save();print('EXCLUSION_HLS_ALL_PASS',flush=True)
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
