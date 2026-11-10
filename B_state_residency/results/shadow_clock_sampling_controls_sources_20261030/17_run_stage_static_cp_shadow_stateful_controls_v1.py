"""Bounded fake-DUT controls for the full-port checker, not FPGA acceptance."""
from pathlib import Path
import json
import os
import shutil
import subprocess
from host_edit_system_common_v1 import ROOT, BASE, read, sha, identity
from config_native_publication_synth_common_v1 import BIN, wait_preserving


def stub(ports, module, gate=False):
    lines = [f'module {module} (']
    for i,p in enumerate(ports):
        width = '' if p['width']==1 else f"[{p['width']-1}:0] "
        lines.append(f" {p['direction']} wire {width}{p['name']}" + (',' if i<len(ports)-1 else ''))
    lines.append(');')
    lines += ['reg[31:0]counter;', 'reg[31:0]sampled;',
              'always @(posedge clk)begin',
              ' if(k_cold_rst)begin counter<=0;sampled<=0;end',
              ' else begin counter<=counter+1;sampled<=qc_cp_s_data;end', 'end']
    if gate:
        lines += ['reg inject=0;', 'initial begin #300;inject=1;end']
    for p in ports:
        if p['direction']!='output':continue
        n,w=p['name'],p['width']
        expression = "'x" if n=='boot_status' else "'z" if n=='boot_verified_count' else ('sampled' if n=='qc_cp_crc' else '{'+str((w+31)//32)+'{counter}}')
        if gate and n=='boot_pending':
            lines += ['`ifdef INJECT_KNOWN',f'assign {n}=inject?~counter[0]:counter[0];',
                      '`elsif INJECT_X',f"assign {n}=inject?1'bx:counter[0];",
                      '`elsif INJECT_Z',f"assign {n}=inject?1'bz:counter[0];",'`else',f'assign {n}={expression};','`endif']
        else:lines.append(f'assign {n}={expression};')
    lines.append('endmodule')
    return '\n'.join(lines)


def main():
    p=BASE/'stage_static_cp_shadow_stateful_controls_v1'
    assert not p.exists() and not os.environ.get('LD_PRELOAD')
    schema=read(ROOT/'results/stage_static_cp_port_schema_20261030.json');ports=schema['ports']
    shadow=ROOT/'hardware/variants/stage_static_cp_shadow_v1/shadow.sv'
    accepted=read(ROOT/'results/stage_static_cp_shadow_preparation_20261030.json')
    assert sha(shadow)==accepted['files']['shadow.sv']
    harness=['`timescale 1ns/1ps',stub(ports,'checker_stub_rtl'),stub(ports,'checker_stub_gate',True),
             'module tb_candidate_offer;', 'reg clk=0;always #5 clk=~clk;',
             'reg cold=1;reg[31:0]stream=0;',
             '`ifdef SHORT_RESET','initial begin #20;cold=0;end','`else',
             'initial begin #50;cold=0;end','`endif',
             "initial begin #260;stream=32'h12345678;#1;stream=32'h87654321;#1;stream=32'habcdef01;end",
             'checker_stub_rtl system (']
    inputs=[q for q in ports if q['direction']=='input']
    for i,q in enumerate(inputs):
        expression={'clk':'clk','k_cold_rst':'cold','qc_cp_s_data':'stream'}.get(q['name'],"'0")
        harness.append(f" .{q['name']}({expression})"+(',' if i<len(inputs)-1 else ''))
    harness += [');',
                "initial begin #460.5;if(stage_static_cp_shadow.drive_qc_cp_s_data!==32'h12345678)$fatal(1,\"transport first transition lost\");",
                " #1;if(stage_static_cp_shadow.drive_qc_cp_s_data!==32'h87654321)$fatal(1,\"transport second transition lost\");",
                " #1;if(stage_static_cp_shadow.drive_qc_cp_s_data!==32'habcdef01)$fatal(1,\"transport third transition lost\");end",
                'initial begin #1000;stage_static_cp_shadow.finish_and_check;$finish;end','endmodule']
    p.mkdir();m=dict(status='running',runner_pid=os.getpid(),runner_start_ticks=identity(os.getpid()),
                    runner_sha256=sha(__file__),shadow_sha256=sha(shadow),cases={},
                    scope='Five stateful fake-DUT checker controls with clocked counter and sampled stream on every output; not real RTL/netlist validation.')
    def save():(p/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
    save()
    try:
        for mode,define,expected in [('matching',None,'FULL_SHADOW_PASS'),
             ('known_mismatch','INJECT_KNOWN','FULL_SHADOW_MISMATCH port=boot_pending'),
             ('x_mismatch','INJECT_X','FULL_SHADOW_MISMATCH port=boot_pending'),
             ('z_mismatch','INJECT_Z','FULL_SHADOW_MISMATCH port=boot_pending'),
             ('short_reset','SHORT_RESET','FULL_SHADOW_INCOMPLETE')]:
            d=p/mode;d.mkdir();shutil.copyfile(shadow,d/'shadow.sv')
            (d/'control.sv').write_text('\n'.join(harness)+'\n');(d/'run.tcl').write_text('run 2us\nquit\n')
            c=dict(status='running',expected=expected,commands=[],inputs={n:sha(d/n) for n in ['shadow.sv','control.sv','run.tcl']});m['cases'][mode]=c;save()
            compile=[str(BIN.parent/'xvlog'),'--sv','-d','SHADOW_NETLIST_TOP=checker_stub_gate']
            if define:compile+=['-d',define]
            phases=[('compile',compile+['shadow.sv','control.sv']),
                    ('elaborate',[str(BIN.parent/'xelab'),'tb_candidate_offer','stage_static_cp_shadow','-s','control','--O0','--mt','2']),
                    ('simulate',[str(BIN.parent/'xsim'),'control','-tclbatch','run.tcl'])]
            for stage,argv in phases:
                m['stage']=mode+'_'+stage;save()
                for n,h in c['inputs'].items():assert sha(d/n)==h
                with (d/(stage+'.stdout.log')).open('w') as log:
                    child=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT)
                    m['active_process']=dict(pid=child.pid,start_ticks=identity(child.pid));save()
                    code=wait_preserving(child,600,m,save)
                m.pop('active_process',None);c['commands'].append(dict(stage=stage,argv=argv,exit_code=code,stdout_sha256=sha(d/(stage+'.stdout.log'))));save()
                assert code==0,(mode,stage)
            log=(d/'simulate.stdout.log').read_text();assert expected in log
            if mode=='matching':assert 'Fatal:' not in log and 'reset_edges=5' in log
            else:assert 'Fatal:' in log and 'FULL_SHADOW_PASS' not in log
            c['status']='observed';save();print('STATEFUL_SHADOW_CONTROL_OBSERVED',mode,flush=True)
        m.update(status='observed',stage='complete',full_system_functional_netlist_validated=False)
    except Exception as error:
        m.update(status='failed',error=repr(error));raise
    finally:save()


if __name__=='__main__':main()
