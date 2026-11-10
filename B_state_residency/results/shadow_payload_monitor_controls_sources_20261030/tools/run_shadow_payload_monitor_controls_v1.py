"""Calibrate read-only three-stream transfer loggers using two legal fake producers."""
from pathlib import Path
import json,os,re,shutil,subprocess
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity,restored,verify_freeze
from config_native_publication_synth_common_v1 import BIN,memory_admission,wait_preserving
from run_shadow_payload_contract_controls_v1 import harness as payload_harness


def harness(ports):
    s=payload_harness(ports)
    needle='reg[31:0]ka_index,pw_index;';assert s.count(needle)==2
    s=s.replace(needle,needle+'\nreg aw_done;\nalways @(posedge clk)if(k_cold_rst)aw_done<=0;else if(p_m_awvalid&&p_m_awready)aw_done<=1;')
    for n,expr in dict(p_m_awvalid='(counter>=5&&!aw_done)',p_m_awaddr="32'h00001000",p_m_awlen="8'd4",p_m_awsize="3'd6",p_m_awburst="2'd1",p_m_awid="4'd0").items():
        s,count=re.subn(r'^assign '+n+r'=.*;$',lambda _:f'assign {n}={expr};',s,flags=re.M);assert count==2,n
    assert s.count(".p_m_awready('0)")==1;s=s.replace(".p_m_awready('0)",'.p_m_awready(p_ready)')
    return s


def main():
    report=ROOT/'results/shadow_payload_contract_controls_20261030.json'
    assert report.exists(),'Wait for actual-restored59 observer controls'
    accepted=read(report);assert accepted['status']=='three_payload_contract_controls59_actual_restored'
    cf=verify_freeze(ROOT/'results/shadow_payload_contract_controls_sources_20261030')
    _,ca,_=restored(BASE/'shadow_payload_contract_controls_v1');assert ca==accepted['audit']
    p=BASE/'shadow_payload_monitor_controls_v1';assert not p.exists() and not os.environ.get('LD_PRELOAD')
    checker=ROOT/'hardware/variants/stage_static_cp_shadow_protocol_v5/shadow.sv';assert sha(checker)==ca['checker_sha256']
    cp=ROOT/'hardware/tests/tb_shadow_cp_transfer_monitor_v1.sv';payload=ROOT/'hardware/tests/tb_shadow_payload_transfer_monitor_v1.sv'
    source=harness(read(ROOT/'results/stage_static_cp_port_schema_20261030.json')['ports'])
    p.mkdir();m=dict(status='running',stage='wait_memory',runner_pid=os.getpid(),runner_start_ticks=identity(os.getpid()),runner_sha256=sha(__file__),checker_sha256=sha(checker),cp_monitor_sha256=sha(cp),payload_monitor_sha256=sha(payload),parent_control_report_sha256=sha(report),parent_control_freeze_sha256=sha(cf),cases={},scope='Two bounded fake-model logger controls only, no actual FPGA DUT.')
    def save():
        t=p/'manifest.pending.json';t.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');t.replace(p/'manifest.json')
    save()
    try:
        memory_admission(m,save)
        for name,define in [('matching',None),('ready_nba','READY_NBA')]:
            d=p/name;d.mkdir();(d/'control.sv').write_text(source)
            for src,out in [(checker,'shadow.sv'),(cp,'cp_monitor.sv'),(payload,'payload_monitor.sv')]:shutil.copyfile(src,d/out)
            (d/'run.tcl').write_text('run 2us\nquit\n')
            c=dict(status='running',commands=[],inputs={n:sha(d/n) for n in ['control.sv','shadow.sv','cp_monitor.sv','payload_monitor.sv','run.tcl']});m['cases'][name]=c;save()
            compiler=[str(BIN.parent/'xvlog'),'--sv','-d','SHADOW_NETLIST_TOP=protocol_gate']
            if define:compiler+=['-d',define]
            stages=[('compile',compiler+['control.sv','shadow.sv','cp_monitor.sv','payload_monitor.sv']),('elaborate',[str(BIN.parent/'xelab'),'tb_candidate_offer','stage_static_cp_shadow','shadow_cp_transfer_monitor','shadow_payload_transfer_monitor','-s','control','--O0','--mt','2']),('simulate',[str(BIN.parent/'xsim'),'control','-tclbatch','run.tcl'])]
            for stage,argv in stages:
                for n,h in c['inputs'].items():assert sha(d/n)==h
                m['stage']=name+'_'+stage;save()
                with (d/(stage+'.stdout.log')).open('w') as log:
                    child=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT);m['active_process']=dict(pid=child.pid,start_ticks=identity(child.pid));save();code=wait_preserving(child,600,m,save)
                m.pop('active_process',None);c['commands'].append(dict(stage=stage,argv=argv,exit_code=code,stdout_sha256=sha(d/(stage+'.stdout.log'))));save();assert code==0,(name,stage)
            log=(d/'simulate.stdout.log').read_text();assert 'Fatal:' not in log and 'FULL_SHADOW_PROTOCOL_PASS' in log
            assert 'CP_TRANSFER_MONITOR_END words=5' in log and 'PAYLOAD_TRANSFER_MONITOR_END ka=5 pw=5 aw=1' in log
            c.update(status='observed',transfer_log_sha256={n:sha(d/n) for n in ['shadow_cp_export.log','shadow_ka_requests.log','shadow_pw_beats.log']});save();print('THREE_STREAM_MONITOR_CONTROL_OBSERVED',name,flush=True)
        m.update(status='observed',stage='complete',full_system_functional_netlist_validated=False)
    except Exception as error:m.update(status='failed',error=repr(error));raise
    finally:save()


if __name__=='__main__':main()
