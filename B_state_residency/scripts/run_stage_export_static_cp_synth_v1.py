"""Synthesize the unchanged controller for the accepted narrow port probe."""
from pathlib import Path
import json
import os
import shutil
import subprocess
from host_edit_system_common_v1 import ROOT,BASE,read,sha,restored,identity,verify_freeze
from config_native_publication_synth_common_v1 import BIN,runtime_environment,memory_admission,wait_preserving


def main():
    accepted=ROOT/'results/stage_export_static_cp_rtl_20261030.json'
    assert read(accepted)['status']=='static_stage_rtl_probe_actual_restored'
    verify_freeze(ROOT/'results/stage_export_static_cp_rtl_sources_20261030')
    ref=BASE/'stage_export_static_cp_rtl_v1';rm,ra,_=restored(ref)
    p=BASE/'stage_export_static_cp_synth_v1';assert not p.exists()
    env,runtime=runtime_environment();p.mkdir()
    for name in ['controller.sv','tb.sv']:shutil.copyfile(ref/name,p/name)
    tcl='''set_param general.maxThreads 2
if {[version -short] ne "2022.2"} {error "Expected matched2022.2"}
read_verilog -sv controller.sv
synth_design -mode out_of_context -top route_commit_controller -part xcu280-fsvh2892-2L-e -flatten_hierarchy rebuilt -generic MAX_PATH=8 -generic MAX_CYCLES=256 -generic PATH_SLOTS=2 -generic PATH_SLOT_BITS=1 -generic STATIC_STAGE_WRITES=1
create_clock -name core_clk -period 10.000 [get_ports clk]
write_checkpoint synth.dcp
write_verilog -mode funcsim functional.v
report_utilization -file utilization.rpt
puts STAGE_EXPORT_CONTROLLER_SYNTH_DONE
close_project
'''
    (p/'synth.tcl').write_text(tcl)
    m=dict(status='running',stage='wait_memory',runner_pid=os.getpid(),runner_start_ticks=identity(os.getpid()),
        runner_sha256=sha(Path(__file__)),sources={n:sha(p/n) for n in ['controller.sv','tb.sv','synth.tcl']},
        reference_audit_sha256=sha(ref/'source_bound_audit.json'),runtime=runtime,
        scope='Standalone2-slot/MAX_PATH8 isolated CP static-stage enabled controller only. Matched probe parameters, not full-system133-source OOC or timing comparison.')
    def save():
        tmp=p/'manifest.pending.json';tmp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');tmp.replace(p/'manifest.json')
    save()
    try:
        memory_admission(m,save)
        assert runtime_environment()[1]==runtime
        argv=[str(BIN),'-mode','batch','-source',str(p/'synth.tcl'),'-log',str(p/'vivado.log'),'-journal',str(p/'vivado.jou')]
        m.update(stage='synthesis',command=argv)
        with (p/'stdout.log').open('w') as log:
            child=subprocess.Popen(argv,cwd=p,env=env,stdout=log,stderr=subprocess.STDOUT)
            m['active_process']=dict(pid=child.pid,start_ticks=identity(child.pid));save()
            code=wait_preserving(child,3600,m,save)
        m.pop('active_process',None);m['exit_code']=code;assert code==0
        assert 'STAGE_EXPORT_CONTROLLER_SYNTH_DONE' in (p/'stdout.log').read_text()
        for n,h in m['sources'].items():assert sha(p/n)==h
        names=['synth.dcp','functional.v','utilization.rpt','stdout.log','vivado.log','vivado.jou']
        for n in names:assert (p/n).stat().st_size>0
        m.update(status='observed',stage='complete',artifact_sha256={n:sha(p/n) for n in names})
    except Exception as error:
        m.update(status='failed',error=repr(error));raise
    finally:save()
    print('STAGE_EXPORT_CONTROLLER_SYNTH_OBSERVED')


if __name__=='__main__':main()
