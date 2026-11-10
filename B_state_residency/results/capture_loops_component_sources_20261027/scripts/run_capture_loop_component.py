"""Bounded paired synthesis and XSim regressions of native capture components."""
from pathlib import Path
import json,subprocess,shutil,sys,time
from run_checkpoint_authority import ROOT,sha

BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
variant=ROOT/'hardware/variants/capture_loops_v1'
p=Path(sys.argv[1]).resolve();p.mkdir();src=p/'sources';src.mkdir()
ref=p.parent/'restore_seed_synth_on_v1';ra=json.loads((ref/'source_bound_audit.json').read_text())
assert ra['status']=='passed'and ra['manifest_sha256']==sha(ref/'manifest.json')
m=dict(status='running',sources={},commands=[],reference=str(ref),reference_audit_sha256=sha(ref/'source_bound_audit.json'),
    scope='Native recursive controller, expansion_capture and children_frames; depth16/capacity4 OOC slice with external physical graph/metadata/access ports. Paired mock-producer protocol simulations and valid-dependent receiver test. Not the full query/recovery system, no timing closure or board claim.',
    execution='local Vivado2022.2 batch and XSim; existing MCP sessions still return version recursion errors')
def copy(origin,name):
    q=src/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(origin,q)
    m['sources'][name]=dict(path=str(origin),sha256=sha(q))
for f in sorted(variant.rglob('*')):
    if f.is_file()and f.suffix in ['.sv','.py','.md','.log']:copy(f,str(f.relative_to(variant)))
for name,origin in [('tb_recursive_candidate_controller.sv','recursive_controller_v1/tb_recursive_candidate_controller.sv'),
                    ('tb_expansion_capture_unit.sv','search_fault_retire_v1/tb_expansion_capture_unit.sv')]:
    copy(ROOT/'hardware/variants'/origin,name)
for n,rel in [('recursive_candidate_controller.sv','recursive/recursive_candidate_controller.sv'),('expansion_capture.sv','capture/expansion_capture.sv'),('children_frames.sv','capture/children_frames.sv')]:
    assert sha(src/'baseline'/n)==sha(ref/'sources'/rel)
shutil.copyfile(Path(__file__),p/'runner.py');m['runner_sha256']=sha(p/'runner.py')
def save():(p/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
save()
def run(stage,argv,work,timeout):
    argv=list(map(str,argv));start=time.monotonic()
    with(work/(stage+'.stdout.log')).open('w')as f:
        r=subprocess.run(argv,cwd=work,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
    m['commands'].append(dict(stage=str(work.relative_to(p))+'/'+stage,argv=argv,exit_code=r.returncode,elapsed_s=time.monotonic()-start))
    save();assert r.returncode==0,(stage,r.returncode)
try:
    for mode in ['baseline','fixed']:
        rtl=[src/mode/n for n in ['children_frames.sv','expansion_capture.sv','recursive_candidate_controller.sv']]
        work=p/mode/'synth';work.mkdir(parents=True)
        tcl='set_param general.maxThreads 2\nputs [list VIVADO_VERSION [version -short]]\n'
        tcl+=''.join('read_verilog -sv {'+str(f)+'}\n'for f in rtl+[src/'capture_loop_slice.sv'])
        tcl+='synth_design -mode out_of_context -top capture_loop_slice -part xcu280-fsvh2892-2L-e\n'
        tcl+='create_clock -period 10.000 -name core_clk [get_ports clk]\n'
        tcl+='report_drc -no_waivers -checks [get_drc_checks LUTLP-1] -file loops.rpt\n'
        tcl+='check_timing -verbose -file check_timing.rpt\nreport_utilization -file utilization.rpt\n'
        tcl+='set f [open facts.txt w]\nputs $f [list loops [llength [get_drc_violations]] latches [llength [get_cells -hier -filter {REF_NAME =~ LD*}]] blackboxes [llength [get_cells -hier -filter {IS_BLACKBOX == 1}]] port_bits [llength [get_ports]]]\nclose $f\n'
        tcl+='write_checkpoint -force synth.dcp\nwrite_verilog -force synth.v\nputs CAPTURE_LOOP_SYNTH_DONE\n'
        (work/'synth.tcl').write_text(tcl)
        run('synth',[BIN/'vivado','-mode','batch','-source','synth.tcl','-log','vivado.log','-journal','vivado.jou'],work,600)
        assert 'CAPTURE_LOOP_SYNTH_DONE'in(work/'vivado.log').read_text()
        for test,top,marker in [('controller','tb_recursive_candidate_controller','RECURSIVE_CONTROLLER_PASS cases=7'),
                                ('retire','tb_expansion_capture_unit','SEARCH_CAPTURE_RETIRE_PASS normal_nested=1 failures=9'),
                                ('offer','tb_root_offer','ROOT_OFFER_BASELINE_BLOCKED cycles=16'if mode=='baseline'else'ROOT_OFFER_FIXED_PASS checks=18 accepted=1')]:
            work=p/mode/test;work.mkdir();(work/'run.tcl').write_text('run 2ms\nquit\n')
            run('compile',[BIN/'xvlog','--sv',*rtl,src/(top+'.sv')],work,120)
            run('elaborate',[BIN/'xelab',top,'-s','capture_test','--debug','typical','--mt','2'],work,120)
            args=[BIN/'xsim','capture_test','--tclbatch','run.tcl','--log','simulate.log']
            if test=='offer':args+=['--testplusarg','expected_stall='+str(int(mode=='baseline'))]
            run('simulate',args,work,120)
            log=(work/'simulate.log').read_text()
            assert marker in log and '$finish called'in log and 'Fatal:'not in log,(mode,test)
    m['status']='observed'
except Exception as e:
    m.update(status='failed',error=repr(e));raise
finally:
    m['artifacts']={str(f.relative_to(p)):sha(f)for f in sorted(p.rglob('*'))if f.is_file()and f.suffix in ['.log','.rpt','.tcl','.dcp','.v','.txt']and 'sources'not in f.relative_to(p).parts}
    save()
print('CAPTURE_COMPONENT_OBSERVED',p)
