"""Paired native REARM/label-service structural and lifecycle experiment."""
from pathlib import Path
import json,shutil,subprocess,sys,time
from run_checkpoint_authority import ROOT,sha
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
variant=ROOT/'hardware/variants/rearm_loops_v1'
p=Path(sys.argv[1]).resolve();p.mkdir();src=p/'sources';src.mkdir()
ref=p.parent/'restore_seed_synth_on_v1';ra=json.loads((ref/'source_bound_audit.json').read_text())
assert ra['status']=='passed'and ra['manifest_sha256']==sha(ref/'manifest.json')
m=dict(status='running',sources={},commands=[],reference=str(ref),reference_audit_sha256=sha(ref/'source_bound_audit.json'),
    scope='Actual recovery_coordinator and label_restore_controller, J0 failed CRC/held receipts/unsafe rearm/late unexpected response/attempt-floor rejection/noncold retry. Native five-field restore and readback against a RAM model. External reconfiguration, physical retirement and authority/owner interfaces are modeled; no AXI, full warm join or full-root zero-loop claim.')
for f in sorted(variant.rglob('*')):
    if f.is_file()and f.suffix in ['.sv','.py','.md','.log']:
        name=str(f.relative_to(variant));q=src/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q)
        m['sources'][name]=dict(path=str(f),sha256=sha(q))
for n in ['recovery_coordinator.sv','label_restore_controller.sv','residency_system.sv']:assert sha(src/'baseline'/n)==sha(ref/'sources'/n)
shutil.copyfile(Path(__file__),p/'runner.py');m['runner_sha256']=sha(p/'runner.py')
def save():(p/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
def run(stage,argv,d):
    argv=list(map(str,argv));start=time.monotonic()
    with(d/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(argv,cwd=d,stdout=f,stderr=subprocess.STDOUT,timeout=600 if stage=='synth'else 120)
    m['commands'].append(dict(stage=str(d.relative_to(p))+'/'+stage,argv=argv,exit_code=r.returncode,elapsed_s=time.monotonic()-start));save()
    assert r.returncode==0,stage
save()
try:
    for mode in ['baseline','fixed']:
        rtl=[src/mode/n for n in ['recovery_coordinator.sv','label_restore_controller.sv','rearm_loop_slice.sv']]
        d=p/mode/'synth';d.mkdir(parents=True)
        tcl='set_param general.maxThreads 2\nputs [list VIVADO_VERSION [version -short]]\n'
        tcl+=''.join('read_verilog -sv {'+str(f)+'}\n'for f in rtl)
        tcl+='synth_design -mode out_of_context -top rearm_loop_slice -part xcu280-fsvh2892-2L-e\ncreate_clock -period 10.000 -name core_clk [get_ports clk]\n'
        tcl+='report_drc -no_waivers -checks [get_drc_checks LUTLP-1] -file loops.rpt\ncheck_timing -verbose -file check_timing.rpt\nreport_utilization -file utilization.rpt\n'
        tcl+='set f [open facts.txt w]\nputs $f [list loops [llength [get_drc_violations]] latches [llength [get_cells -hier -filter {REF_NAME =~ LD*}]] blackboxes [llength [get_cells -hier -filter {IS_BLACKBOX == 1}]] port_bits [llength [get_ports]]]\nclose $f\n'
        tcl+='write_checkpoint -force synth.dcp\nwrite_verilog -force synth.v\nputs REARM_LOOP_SYNTH_DONE\n'
        (d/'synth.tcl').write_text(tcl);run('synth',[BIN/'vivado','-mode','batch','-source','synth.tcl','-log','vivado.log','-journal','vivado.jou'],d)
        assert 'REARM_LOOP_SYNTH_DONE'in(d/'vivado.log').read_text()
        d=p/mode/'simulate';d.mkdir();(d/'run.tcl').write_text('run 2ms\nquit\n')
        run('compile',[BIN/'xvlog','--sv',*rtl,src/'tb_rearm_loop.sv'],d)
        run('elaborate',[BIN/'xelab','tb_rearm_loop','-s','rearm_test','--debug','typical','--mt','2'],d)
        run('simulate',[BIN/'xsim','rearm_test','--tclbatch','run.tcl','--log','simulate.log'],d)
        log=(d/'simulate.log').read_text()
        assert 'REARM_LOOP_PASS scenarios=3 successes=3 failures=10 checks=179'in log and '$finish called'in log and 'Fatal:'not in log
    m['status']='observed'
except Exception as e:
    m.update(status='failed',error=repr(e));raise
finally:
    m['artifacts']={str(f.relative_to(p)):sha(f)for f in sorted(p.rglob('*'))if f.is_file()and f.suffix in ['.rpt','.log','.tcl','.dcp','.v','.txt']and 'sources'not in f.relative_to(p).parts}
    save()
print('REARM_COMPONENT_OBSERVED',p)
