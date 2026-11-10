"""Bounded legal five-word producer controls for the CP export observer."""
from pathlib import Path
import json
import os
import shutil
import subprocess
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity
from config_native_publication_synth_common_v1 import BIN,wait_preserving

CASES=[('matching',None,'FULL_SHADOW_PROTOCOL_PASS'),
       ('ready_nba','READY_NBA','FULL_SHADOW_PROTOCOL_PASS'),
       ('stall_data_flip','DATA_FLIP_STALL','CP_DATA_MISMATCH phase=0 ready=0'),
       ('active_data_flip','DATA_FLIP_ACTIVE','CP_DATA_MISMATCH'),
       ('edge_only_data_flip','EDGE_ONLY_FLIP','CP_DATA_MISMATCH phase=1 ready=1'),
       ('active_unknown_both','DATA_X_BOTH','CP_DATA_UNKNOWN'),
       ('valid_unknown_both','VALID_X_BOTH','CP_VALID_UNKNOWN'),
       ('idle_valid_unknown_both','IDLE_VALID_X_BOTH','CP_VALID_UNKNOWN'),
       ('valid_drop','VALID_DROP','CP_VALID_MISMATCH'),
       ('metadata_flip','META_FLIP','CP_META_MISMATCH'),
       ('other_control_flip','OTHER_FLIP','FULL_SHADOW_MISMATCH port=boot_pending'),
       ('other_control_x','OTHER_X','FULL_SHADOW_MISMATCH port=boot_pending'),
       ('other_control_z','OTHER_Z','FULL_SHADOW_MISMATCH port=boot_pending'),
       ('short_reset','SHORT_RESET','FULL_SHADOW_INCOMPLETE'),
       ('no_stream','NO_STREAM','CP_PROTOCOL_COVERAGE_MISSING'),
       ('no_transfers','NO_TRANSFERS','CP_PROTOCOL_COVERAGE_MISSING'),
       ('no_stalls','NO_STALLS','CP_PROTOCOL_COVERAGE_MISSING')]


def model(ports,gate):
    name='protocol_gate' if gate else 'protocol_rtl'
    lines=[f'module {name} (']
    for i,p in enumerate(ports):
        packed='' if p['width']==1 else f"[{p['width']-1}:0] "
        lines.append(f" {p['direction']} wire {packed}{p['name']}"+(',' if i<len(ports)-1 else ''))
    lines += [');','reg[31:0]counter,sampled,word_index;',
              '`ifdef NO_STREAM',"wire stream_valid=1'b0;",'`else',
              'wire stream_valid=(counter>=10&&word_index<5);','`endif',
              'always @(posedge clk)begin',
              ' if(k_cold_rst)begin counter<=0;sampled<=0;word_index<=0;end',
              ' else begin counter<=counter+1;sampled<=qc_cp_s_data;',
              '  if(stream_valid&&cp_m_ready)word_index<=word_index+1;',
              ' end','end',
              'reg edge_fault=0;',
              'always @(negedge clk)begin if(stream_valid&&cp_m_ready)begin #4.999;edge_fault=1;end else edge_fault<=0;end',
              "always @(posedge clk)edge_fault<=1'b0;"]
    for p in ports:
        if p['direction']!='output':continue
        n,w=p['name'],p['width']
        if n=='cp_m_valid':
            drop="(stream_valid&&word_index!=2)" if gate else 'stream_valid'
            lines += ['`ifdef VALID_X_BOTH',f"assign {n}=(counter>=12)?1'bx:stream_valid;",
                      '`elsif IDLE_VALID_X_BOTH',f"assign {n}=(counter==1)?1'bx:stream_valid;",
                      '`elsif VALID_DROP',f'assign {n}={drop};','`else',f'assign {n}=stream_valid;','`endif']
        elif n=='cp_m_data':
            idle="32'h00000000" if gate else "32'hxxxxxxxx"
            base="(32'hd00d0000+word_index)"
            stall=f"({base}^(!cp_m_ready?32'h1:32'h0))" if gate else base
            active=f"({base}^((word_index==2)?32'h1:32'h0))" if gate else base
            edge=f"({base}^(edge_fault?32'h1:32'h0))" if gate else base
            lines += ['`ifdef DATA_X_BOTH',f"assign {n}=stream_valid?32'hxxxxxxxx:{idle};",
                      '`elsif DATA_FLIP_STALL',f'assign {n}=stream_valid?{stall}:{idle};',
                      '`elsif DATA_FLIP_ACTIVE',f'assign {n}=stream_valid?{active}:{idle};',
                      '`elsif EDGE_ONLY_FLIP',f'assign {n}=stream_valid?{edge}:{idle};',
                      '`else',f'assign {n}=stream_valid?{base}:{idle};','`endif']
        elif n=='cp_m_index':
            expr="(word_index^((stream_valid&&word_index==2)?32'h1:32'h0))" if gate else 'word_index'
            lines += ['`ifdef META_FLIP',f'assign {n}={expr};','`else',f'assign {n}=word_index;','`endif']
        elif n=='cp_m_last':lines.append('assign cp_m_last=(word_index==4);')
        elif n=='boot_pending' and gate:
            lines += ['`ifdef OTHER_FLIP',"assign boot_pending=(counter>=12)?~counter[0]:counter[0];",
                      '`elsif OTHER_X',"assign boot_pending=(counter>=12)?1'bx:counter[0];",
                      '`elsif OTHER_Z',"assign boot_pending=(counter>=12)?1'bz:counter[0];",
                      '`else','assign boot_pending=counter[0];','`endif']
        else:
            value="'x" if n=='boot_status' else "'z" if n=='boot_verified_count' else ('sampled' if n=='qc_cp_crc' else '{'+str((w+31)//32)+'{counter}}')
            lines.append(f'assign {n}={value};')
    lines.append('endmodule')
    return '\n'.join(lines)


def harness(ports):
    lines=['`timescale 1ns/1ps',model(ports,False),model(ports,True),
           'module tb_candidate_offer;',
           'reg clk=0;always #5 clk=~clk;',
           'reg cold=1;reg[31:0]stream=0;reg ready=0;',
           '`ifdef SHORT_RESET','initial begin #20;cold=0;end','`else','initial begin #50;cold=0;end','`endif',
           'always @(posedge clk)if(cold)stream<=0;else stream<=stream+1;',
           '`ifdef READY_NBA','always @(posedge clk)if($time>=205)ready<=1;',
           '`elsif NO_TRANSFERS','initial ready=0;',
           '`elsif NO_STALLS','initial ready=1;',
           '`else','initial begin #200;ready=1;end','`endif',
           'protocol_rtl system (']
    inputs=[p for p in ports if p['direction']=='input']
    for i,p in enumerate(inputs):
        value={'clk':'clk','k_cold_rst':'cold','qc_cp_s_data':'stream','cp_m_ready':'ready'}.get(p['name'],"'0")
        lines.append(f" .{p['name']}({value})"+(',' if i<len(inputs)-1 else ''))
    lines += [');','initial begin #1000;stage_static_cp_shadow.finish_and_check;$finish;end','endmodule']
    return '\n'.join(lines)+'\n'


def main():
    p=BASE/'shadow_cp_protocol_controls_v5';assert not p.exists() and not os.environ.get('LD_PRELOAD')
    variant=ROOT/'hardware/variants/stage_static_cp_shadow_protocol_v4'
    vm=read(variant/'manifest.json');assert vm['unconditional_outputs']==345
    shadow=variant/'shadow.sv';assert sha(shadow)==vm['files']['shadow.sv']
    ports=read(ROOT/'results/stage_static_cp_port_schema_20261030.json')['ports'];source=harness(ports)
    p.mkdir();m=dict(status='running',runner_pid=os.getpid(),runner_start_ticks=identity(os.getpid()),runner_sha256=sha(__file__),
                    checker_sha256=sha(shadow),checker_manifest_sha256=sha(variant/'manifest.json'),cases={},
                    scope='17 bounded five-word producer controls only. Idle data deliberately X versus0; valid data/index/last hold under ready0; posedge NBA stimulus/ready exercised. No actual FPGA netlist validation.')
    def save():(p/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
    save()
    try:
        for mode,define,expected in CASES:
            d=p/mode;d.mkdir();(d/'control.sv').write_text(source);shutil.copyfile(shadow,d/'shadow.sv');(d/'run.tcl').write_text('run 2us\nquit\n')
            c=dict(status='running',expected=expected,commands=[],inputs={n:sha(d/n) for n in ['control.sv','shadow.sv','run.tcl']});m['cases'][mode]=c;save()
            compile=[str(BIN.parent/'xvlog'),'--sv','-d','SHADOW_NETLIST_TOP=protocol_gate']
            if define:compile+=['-d',define]
            phases=[('compile',compile+['shadow.sv','control.sv']),
                    ('elaborate',[str(BIN.parent/'xelab'),'tb_candidate_offer','stage_static_cp_shadow','-s','control','--O0','--mt','2']),
                    ('simulate',[str(BIN.parent/'xsim'),'control','-tclbatch','run.tcl'])]
            for stage,argv in phases:
                for n,h in c['inputs'].items():assert sha(d/n)==h
                m['stage']=mode+'_'+stage;save()
                with (d/(stage+'.stdout.log')).open('w') as log:
                    child=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT)
                    m['active_process']=dict(pid=child.pid,start_ticks=identity(child.pid));save()
                    code=wait_preserving(child,600,m,save)
                m.pop('active_process',None);c['commands'].append(dict(stage=stage,argv=argv,exit_code=code,stdout_sha256=sha(d/(stage+'.stdout.log'))));save()
                assert code==0,(mode,stage)
            log=(d/'simulate.stdout.log').read_text();assert expected in log,(mode,log[-1600:])
            if mode in ['matching','ready_nba']:assert 'Fatal:' not in log
            else:assert 'Fatal:' in log and 'FULL_SHADOW_PROTOCOL_PASS' not in log
            c['status']='observed';save();print('CP_PROTOCOL_CONTROL_OBSERVED',mode,flush=True)
        m.update(status='observed',stage='complete',full_system_functional_netlist_validated=False)
    except Exception as error:
        m.update(status='failed',error=repr(error));raise
    finally:save()


if __name__=='__main__':main()
