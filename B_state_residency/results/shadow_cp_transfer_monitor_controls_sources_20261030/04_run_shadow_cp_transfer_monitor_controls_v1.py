"""Calibrate read-only transfer logging on two actual-restored5-word controls."""
from pathlib import Path
import json
import os
import shutil
import subprocess
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity,restored
from config_native_publication_synth_common_v1 import BIN,wait_preserving


def main():
    ref=BASE/'shadow_cp_protocol_controls_v5';_,a,_=restored(ref)
    assert a['complete_contract_controls_passed']
    p=BASE/'shadow_cp_transfer_monitor_controls_v1';assert not p.exists() and not os.environ.get('LD_PRELOAD')
    monitor=ROOT/'hardware/tests/tb_shadow_cp_transfer_monitor_v1.sv'
    p.mkdir();m=dict(status='running',runner_pid=os.getpid(),runner_start_ticks=identity(os.getpid()),
                    runner_sha256=sha(__file__),monitor_sha256=sha(monitor),cases={},
                    scope='Read-only pre-edge transfer logger calibration on two finite fake producer controls; no FPGA netlist acceptance.')
    def save():(p/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
    save()
    try:
        for mode in ['matching','ready_nba']:
            d=p/mode;d.mkdir()
            for name in ['control.sv','shadow.sv','run.tcl']:shutil.copyfile(ref/mode/name,d/name)
            shutil.copyfile(monitor,d/'monitor.sv')
            c=dict(status='running',inputs={n:sha(d/n) for n in ['control.sv','shadow.sv','run.tcl','monitor.sv']},commands=[]);m['cases'][mode]=c;save()
            compile=[str(BIN.parent/'xvlog'),'--sv','-d','SHADOW_NETLIST_TOP=protocol_gate']
            if mode=='ready_nba':compile+=['-d','READY_NBA']
            phases=[('compile',compile+['shadow.sv','control.sv','monitor.sv']),
                    ('elaborate',[str(BIN.parent/'xelab'),'tb_candidate_offer','stage_static_cp_shadow','shadow_cp_transfer_monitor','-s','control','--O0','--mt','2']),
                    ('simulate',[str(BIN.parent/'xsim'),'control','-tclbatch','run.tcl'])]
            for stage,argv in phases:
                m['stage']=mode+'_'+stage;save()
                for name,h in c['inputs'].items():assert sha(d/name)==h
                with (d/(stage+'.stdout.log')).open('w') as log:
                    child=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT)
                    m['active_process']=dict(pid=child.pid,start_ticks=identity(child.pid));save()
                    code=wait_preserving(child,600,m,save)
                m.pop('active_process',None);c['commands'].append(dict(stage=stage,argv=argv,exit_code=code,stdout_sha256=sha(d/(stage+'.stdout.log'))));save();assert code==0
            log=(d/'simulate.stdout.log').read_text()
            assert 'FULL_SHADOW_PROTOCOL_PASS' in log and 'CP_TRANSFER_MONITOR_END words=5' in log and 'Fatal:' not in log
            assert len((d/'shadow_cp_export.log').read_text().splitlines())==5
            c['status']='observed';save();print('CP_TRANSFER_MONITOR_CONTROL',mode,flush=True)
        m.update(status='observed',stage='complete',full_system_functional_netlist_validated=False)
    except Exception as error:
        m.update(status='failed',error=repr(error));raise
    finally:save()


if __name__=='__main__':main()
