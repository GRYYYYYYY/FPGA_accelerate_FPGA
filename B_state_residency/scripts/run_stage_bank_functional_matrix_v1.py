"""Observe three standalone synthesis/functional cases, retaining design failures."""
from pathlib import Path
import json
import os
import re
import shutil
import subprocess
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity,verify_freeze,restored
from config_native_publication_synth_common_v1 import BIN,runtime_environment,memory_admission,wait_preserving


def main():
    assert read(ROOT/'results/stage_bank_matrix_rtl_20261030.json')['status']=='four_slot_full_path_three_mode_rtl_actual_restored'
    verify_freeze(ROOT/'results/stage_bank_matrix_rtl_sources_20261030')
    reference=BASE/'stage_bank_matrix_rtl_v2';rm,ra,_=restored(reference)
    variant=ROOT/'hardware/variants/stage_static_cp_v1';vm=read(variant/'manifest.json')
    tb=ROOT/'hardware/tests/tb_stage_bank_matrix_v1.sv'
    assert sha(tb)==rm['tb_sha256']
    glbl=BIN.parent.parent/'data/verilog/src/glbl.v';assert glbl.exists()
    prep=ROOT/'results/stage_bank_functional_matrix_preparation_20261030.json'
    pr=read(prep)
    for n,h in pr['bound'].items():assert sha(n)==h
    p=BASE/'stage_bank_functional_matrix_v1';assert not p.exists() and not os.environ.get('LD_PRELOAD')
    env,runtime=runtime_environment();p.mkdir()
    m=dict(status='running',stage='prepare',runner_pid=os.getpid(),runner_start_ticks=identity(os.getpid()),
        runner_sha256=sha(Path(__file__)),preparation_sha256=sha(prep),runtime=runtime,cases={},
        reference_audit_sha256=sha(reference/'source_bound_audit.json'),
        scope='Standalone4-slot/MAX_PATH32 original/default/static functional matrix. Observed run completion includes preserved design failures; no full-system or timing acceptance.')
    def save():
        tmp=p/'manifest.pending.json';tmp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');tmp.replace(p/'manifest.json')
    def run(mode,stage,argv,d,child_env,timeout):
        m['stage']=mode+'_'+stage;save()
        with (d/(stage+'.stdout.log')).open('w') as log:
            child=subprocess.Popen(argv,cwd=d,env=child_env,stdout=log,stderr=subprocess.STDOUT)
            m['active_process']=dict(pid=child.pid,start_ticks=identity(child.pid),argv=argv);save()
            code=wait_preserving(child,timeout,m,save)
        m.pop('active_process',None)
        m['cases'][mode]['commands'].append(dict(stage=stage,argv=argv,exit_code=code));save()
        assert code==0,(mode,stage,'Infrastructure/tool failure: preserve attempt')
    save()
    try:
        for mode,source,extra in [('original','baseline.sv',''),('default','fixed.sv',' -generic STATIC_STAGE_WRITES=0'),('static','fixed.sv',' -generic STATIC_STAGE_WRITES=1')]:
            d=p/mode;d.mkdir();shutil.copyfile(variant/source,d/'controller.sv');shutil.copyfile(tb,d/'tb.sv');shutil.copyfile(glbl,d/'glbl.v')
            assert sha(d/'controller.sv')==vm['baseline_sha256' if mode=='original' else 'fixed_sha256']
            tcl='''set_param general.maxThreads 2
if {[version -short] ne "2022.2"} {error "Expected2022.2"}
read_verilog -sv controller.sv
synth_design -mode out_of_context -top route_commit_controller -part xcu280-fsvh2892-2L-e -flatten_hierarchy rebuilt -generic MAX_PATH=32 -generic MAX_CYCLES=256 -generic PATH_SLOTS=4 -generic PATH_SLOT_BITS=2@EXTRA@
create_clock -name core_clk -period 10.000 [get_ports clk]
write_checkpoint synth.dcp
write_verilog -mode funcsim functional.v
report_utilization -file utilization.rpt
puts STAGE_MATRIX_SYNTH_DONE
close_project
'''.replace('@EXTRA@',extra)
            (d/'synth.tcl').write_text(tcl);(d/'run.tcl').write_text('run all\nquit\n')
            c=dict(status='running',inputs={n:sha(d/n) for n in ['controller.sv','tb.sv','glbl.v','synth.tcl','run.tcl']},commands=[]);m['cases'][mode]=c
            m['stage']=mode+'_synth_wait_memory';save();memory_admission(m,save)
            assert runtime_environment()[1]==runtime
            run(mode,'synthesis',[str(BIN),'-mode','batch','-source',str(d/'synth.tcl'),'-log',str(d/'vivado.log'),'-journal',str(d/'vivado.jou')],d,env,3600)
            assert 'STAGE_MATRIX_SYNTH_DONE' in (d/'synthesis.stdout.log').read_text()
            for n in ['synth.dcp','functional.v','utilization.rpt']:assert (d/n).stat().st_size>0
            c['functional_netlist_sha256']=sha(d/'functional.v');c['dcp_sha256']=sha(d/'synth.dcp')
            m['stage']=mode+'_functional_wait_memory';save();memory_admission(m,save)
            run(mode,'compile',[str(BIN.parent/'xvlog'),'--sv','-d','NETLIST','functional.v','tb.sv','glbl.v'],d,None,900)
            run(mode,'elaborate',[str(BIN.parent/'xelab'),'--O0','-L','unisims_ver','tb_stage_bank_matrix','glbl','-s','probe','--mt','2'],d,None,900)
            run(mode,'simulate',[str(BIN.parent/'xsim'),'probe','-tclbatch','run.tcl'],d,None,900)
            log=(d/'simulate.stdout.log').read_text()
            passed='STAGE_BANK_MATRIX_PASS commands=12 responses=12 imports=477 exports=1092 checks=12' in log
            fatals=re.findall(r'^Fatal:.*$',log,re.M)
            assert (passed and not fatals) or (not passed and len(fatals)==1), 'Unclassified test termination'
            if fatals:assert fatals[0].startswith(('Fatal: export mismatch','Fatal: CP status','Fatal: failed import changed slots','Fatal: export CRC','Fatal: reset slots','Fatal: watchdog','Fatal: backpressure','Fatal: coverage counts'))
            trace='\n'.join(re.findall(r'^(?:EVT |CASE |STAGE_BANK_MATRIX_PASS).*$',log,re.M))+'\n';(d/'events.txt').write_text(trace)
            for n,h in c['inputs'].items():assert sha(d/n)==h
            assert sha(d/'functional.v')==c['functional_netlist_sha256']
            c.update(status='observed',functional_passed=passed,fatal_messages=fatals,
                finish_records=re.findall(r'(?:\$finish called at time :|Time:)\s*(\d+) ns',log),
                artifact_sha256={n:sha(d/n) for n in ['functional.v','synth.dcp','utilization.rpt','synthesis.stdout.log','vivado.log','vivado.jou','compile.stdout.log','elaborate.stdout.log','simulate.stdout.log','events.txt']})
            save();print('STAGE_FUNCTIONAL_MATRIX_CASE',mode,'passed' if passed else 'design_failed',flush=True)
        m.update(status='observed',stage='complete',exit_code=0,
            all_functional_cases_passed=all(c['functional_passed'] for c in m['cases'].values()))
    except Exception as error:
        m.update(status='failed',error=repr(error));raise
    finally:save()
    print('STAGE_BANK_FUNCTIONAL_MATRIX_OBSERVED')


if __name__=='__main__':main()
