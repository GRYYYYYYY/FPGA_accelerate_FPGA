"""Compare identical clocked fake models with negedge/posedge NBA inputs.

Use the clock-lead copy; all comparisons and fake models unchanged. A mismatch is evidence about the replay
driver, not about the FPGA RTL or synthesis tool.
"""
from pathlib import Path
import json
import os
import shutil
import subprocess
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity
from config_native_publication_synth_common_v1 import BIN,wait_preserving
from run_stage_static_cp_shadow_stateful_controls_v1 import stub


def main():
    p=BASE/'shadow_transport_nba_control_v2';assert not p.exists()
    assert not os.environ.get('LD_PRELOAD')
    ports=read(ROOT/'results/stage_static_cp_port_schema_20261030.json')['ports']
    ref=stub(ports,'checker_stub_rtl');gate=stub(ports,'checker_stub_gate')
    assert gate.replace('checker_stub_gate','checker_stub_rtl')==ref
    shadow=ROOT/'hardware/variants/stage_static_cp_shadow_clock_v2/shadow.sv'
    assert sha(shadow)==read(ROOT/'results/stage_static_cp_shadow_clock_v2_preparation_20261030.json')['files']['shadow.sv']
    p.mkdir();m=dict(status='running',runner_pid=os.getpid(),runner_start_ticks=identity(os.getpid()),
                    runner_sha256=sha(__file__),stub_generator_sha256=sha(ROOT/'scripts/run_stage_static_cp_shadow_stateful_controls_v1.py'),
                    shadow_sha256=sha(shadow),identical_models_except_names=True,cases={},
                    scope='Bounded replay-driver control with identical fake clocked models. No FPGA DUT, checker alteration, masking or physical timing claim.')
    def save():(p/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
    save()
    try:
        for edge in ['negedge','posedge']:
            d=p/(edge+'_nba');d.mkdir()
            harness=['`timescale 1ns/1ps',ref,gate,'module tb_candidate_offer;',
                     'reg clk=0;always #5 clk=~clk;',
                     'reg cold=1;reg[31:0]stream=0;initial begin #50;cold=0;end',
                     f'always @({edge} clk)if(cold)stream<=0;else stream<=stream+1;',
                     'checker_stub_rtl system (']
            inputs=[q for q in ports if q['direction']=='input']
            for i,q in enumerate(inputs):
                value={'clk':'clk','k_cold_rst':'cold','qc_cp_s_data':'stream'}.get(q['name'],"'0")
                harness.append(f" .{q['name']}({value})"+(',' if i<len(inputs)-1 else ''))
            harness += [');','initial begin #1000;stage_static_cp_shadow.finish_and_check;$finish;end','endmodule']
            (d/'control.sv').write_text('\n'.join(harness)+'\n');shutil.copyfile(shadow,d/'shadow.sv')
            (d/'run.tcl').write_text('run 2us\nquit\n')
            c=dict(status='running',commands=[],inputs={n:sha(d/n) for n in ['control.sv','shadow.sv','run.tcl']});m['cases'][edge+'_nba']=c;save()
            phases=[('compile',[str(BIN.parent/'xvlog'),'--sv','-d','SHADOW_NETLIST_TOP=checker_stub_gate','shadow.sv','control.sv']),
                    ('elaborate',[str(BIN.parent/'xelab'),'tb_candidate_offer','stage_static_cp_shadow','-s','control','--O0','--mt','2']),
                    ('simulate',[str(BIN.parent/'xsim'),'control','-tclbatch','run.tcl'])]
            for stage,argv in phases:
                for name,h in c['inputs'].items():assert sha(d/name)==h
                m['stage']=edge+'_'+stage;save()
                with (d/(stage+'.stdout.log')).open('w') as log:
                    child=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT)
                    m['active_process']=dict(pid=child.pid,start_ticks=identity(child.pid));save()
                    code=wait_preserving(child,600,m,save)
                m.pop('active_process',None);c['commands'].append(dict(stage=stage,argv=argv,exit_code=code,stdout_sha256=sha(d/(stage+'.stdout.log'))));save()
                assert code==0,(edge,stage)
            text=(d/'simulate.stdout.log').read_text()
            passed='FULL_SHADOW_PASS' in text;failed='Fatal: FULL_SHADOW_MISMATCH' in text
            assert passed!=failed and 'FULL_SHADOW_WATCHDOG' not in text
            c.update(status='observed',checker_reported_match=passed);save()
            print('IDENTICAL_MODEL_NBA_CONTROL',edge,'match',passed,flush=True)
        assert all(c['checker_reported_match'] for c in m['cases'].values())
        m.update(status='observed',stage='complete',full_system_functional_netlist_validated=False)
    except Exception as error:
        m.update(status='failed',error=repr(error));raise
    finally:save()


if __name__=='__main__':main()
