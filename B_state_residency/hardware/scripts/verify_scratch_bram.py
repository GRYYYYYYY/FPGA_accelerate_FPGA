"""Local batch fallback after the MCP parent exited; explicit pure-SV source list."""
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha


def main():
    tool=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
    source=ROOT/'hardware/rtl/scratch_frame_store_bram.sv'
    tb=ROOT/'hardware/tb/tb_scratch_frame_store.sv'
    xdc=ROOT/'hardware/rtl/scratch_frame_store.xdc'
    vectors=ROOT/'results/rtl_scratch_20261023/actual_vectors.txt'
    vector_manifest=vectors.parent/'vectors_manifest.json'
    expected=json.loads(vector_manifest.read_text())
    for path,digest in expected['files'].items():
        if sha(path)!=digest:raise ValueError('Frozen vector evidence changed')
    out=ROOT/'results'/('rtl_scratch_bram_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'));out.mkdir()
    inputs=[Path(__file__).resolve(),source,tb,xdc,vectors,vector_manifest]
    record=dict(status='running',performance=None,toolchain='Vivado/XSim 2022.2',part='xcu280-fsvh2892-2L-e',
                clock_constraint_ns=10.0,commands=[],files={str(path):sha(path) for path in inputs},
                scope='Single-owner scratch frame storage primitive, trusted external CLEAN and binding quarantine. Cold reset only. Behavioral simulation and out-of-context synthesis, no DMA controller, timing closure, board execution or speed claim.')
    for path in (source,tb,xdc,Path(__file__).resolve()):(out/path.name).write_bytes(path.read_bytes())
    def save():(out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
    def run(name,command):
        record['commands'].append(dict(stage=name,command=list(map(str,command))));save()
        with (out/(name+'.console.log')).open('w') as log:
            result=subprocess.run(command,cwd=out,stdout=log,stderr=subprocess.STDOUT)
        record['commands'][-1]['exit_code']=result.returncode;save()
        if result.returncode:raise RuntimeError('Stage failed: '+name)
    save();print(out,flush=True)
    try:
        run('compile',[tool/'xvlog','--sv','--work','xil_defaultlib',source,tb])
        run('elaborate',[tool/'xelab','xil_defaultlib.tb_scratch_frame_store','--snapshot','scratch_bram_tb','--debug','typical','--mt','2'])
        (out/'simulate.tcl').write_text('run 120ms\nquit\n')
        run('simulate',[tool/'xsim','scratch_bram_tb','--tclbatch','simulate.tcl','--testplusarg','VECTORS='+str(vectors),'--log','simulate.log'])
        logs='\n'.join((out/name).read_text() for name in ('compile.console.log','elaborate.console.log','simulate.console.log','simulate.log'))
        if re.search(r'(?im)^\s*(ERROR|FATAL|Fatal):',logs):raise ValueError('Unexpected simulation error')
        matches=re.findall(r'TEST_PASS scratch_frame_store checks=(\d+) actual_commands=(\d+) stalled_cycles=(\d+)',logs)
        if not matches or len(set(matches))!=1:raise ValueError('Missing or conflicting terminal PASS')
        checks,actual,stalls=map(int,matches[0])
        if actual!=expected['commands'] or checks!=actual+29 or not stalls:raise ValueError('Incomplete RTL stimulus')
        record['simulation']=dict(status='passed',checks=checks,actual_commands=actual,stalled_cycles=stalls,
                                  actual_queries=expected['queries'],actual_field_accesses=expected['actual_field_accesses']);save()
        print('Behavioral RTL passed; starting out-of-context synthesis',flush=True)
        tcl=f'''set_param general.maxThreads 2
read_verilog -sv {{{source}}}
read_xdc {{{xdc}}}
synth_design -top scratch_frame_store -part xcu280-fsvh2892-2L-e -mode out_of_context
report_utilization -file utilization.rpt
write_checkpoint scratch_frame_store.dcp
set b_rams [get_cells -hier -filter {{REF_NAME =~ RAMB*}}]
if {{[llength $b_rams] == 0}} {{error "No block RAM inferred"}}
set b_file [open ram_cells.txt w]
foreach b_cell $b_rams {{puts $b_file "$b_cell [get_property REF_NAME $b_cell]"}}
close $b_file
puts "B_SYNTH_PASS ram_cells=[llength $b_rams]"
exit
'''
        (out/'synthesize.tcl').write_text(tcl)
        run('synthesize',[tool/'vivado','-mode','batch','-source','synthesize.tcl','-log','synthesize.log','-journal','synthesize.jou'])
        synthesis=(out/'synthesize.log').read_text()
        if not re.search(r'B_SYNTH_PASS ram_cells=[1-9]\d*',synthesis) or 'RAM "data_reg" dissolved' in synthesis:
            raise ValueError('Block RAM implementation gate failed')
        record['synthesis']=dict(status='passed',ram_cells=(out/'ram_cells.txt').read_text().splitlines())
        for path,digest in record['files'].items():
            if sha(path)!=digest:raise ValueError('Bound RTL/test/vector changed during flow')
        artifacts=[out/name for name in ('simulate.tcl','simulate.log','synthesize.tcl','synthesize.log','utilization.rpt','ram_cells.txt','scratch_frame_store.dcp')]
        artifacts += [out/(stage['stage']+'.console.log') for stage in record['commands']]
        record['artifacts']={str(path):sha(path) for path in artifacts}
        record['status']='passed';print(json.dumps(record['synthesis']),flush=True)
    except Exception as error:
        record.update(status='failed',error=repr(error));raise
    finally:save()


if __name__=='__main__':main()
