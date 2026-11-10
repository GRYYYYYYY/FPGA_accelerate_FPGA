"""Execute isolated candidate controls after existing memory admission; never run a full DUT."""
from pathlib import Path
import json,os,shutil,subprocess,socket
from host_edit_system_common_v1 import ROOT,sha,read,identity
from config_native_publication_synth_common_v1 import BIN,wait_preserving
from shadow_fixture_ready_recovery_v2 import BASE,predecessor,memory_admission

def main():
    p=BASE/'shadow_fixture_ready_controls_v2';assert not p.exists() and not os.environ.get('LD_PRELOAD')
    prior=predecessor()
    variant=ROOT/'hardware/variants/stage_static_cp_shadow_fixture_ready_v1';vm=read(variant/'manifest.json')
    assert vm['status']=='prepared_candidate_not_compiled_or_validated' and vm['inverse_exact'] and vm['cp_pw_tasks_unchanged']
    proof=ROOT/'results/ka_as_ready_temporal_composition_review_20261101.json';assert sha(proof)==vm['proof_report_sha256']
    cases=read(variant/'cases.json')
    shadow=variant/'shadow.sv';assert sha(shadow)==vm['files']['shadow.sv']
    source=(variant/'control.sv').read_text();assert sha(variant/'control.sv')==vm['files']['control.sv'] and sha(variant/'cases.json')==vm['files']['cases.json']
    p.mkdir();m=dict(status='running',stage='wait_memory',runner_pid=os.getpid(),runner_start_ticks=identity(os.getpid()),runner_sha256=sha(__file__),checker_sha256=sha(shadow),checker_manifest_sha256=sha(variant/'manifest.json'),cases={},planned_cases=len(cases),scope='58 bounded fixture-ready fake controls only; no real FPGA netlist or full acceptance.')
    m.update(predecessor=prior,hostname=socket.gethostname(),boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),pid_namespace=os.readlink('/proc/self/ns/pid'),helper_sha256=sha(ROOT/'scripts/shadow_fixture_ready_recovery_v2.py'))
    def save():
        q=p/'manifest.pending.json';q.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');q.replace(p/'manifest.json')
    save()
    try:
        memory_admission(m,save)
        for case in cases:
            mode,define,expected=case['name'],case['define'],case['expected']
            d=p/mode;d.mkdir();(d/'control.sv').write_text(source);shutil.copyfile(shadow,d/'shadow.sv');(d/'run.tcl').write_text('run 2us\nquit\n')
            c=dict(status='running',expected=expected,commands=[],inputs={n:sha(d/n) for n in ['control.sv','shadow.sv','run.tcl']});m['cases'][mode]=c;save()
            compiler=[str(BIN.parent/'xvlog'),'--sv','-d','SHADOW_NETLIST_TOP=protocol_gate']
            if define:compiler+=['-d',define]
            phases=[('compile',compiler+['shadow.sv','control.sv']),('elaborate',[str(BIN.parent/'xelab'),'tb_candidate_offer','stage_static_cp_shadow','-s','control','--O0','--mt','2']),('simulate',[str(BIN.parent/'xsim'),'control','-tclbatch','run.tcl'])]
            for stage,argv in phases:
                for n,h in c['inputs'].items():assert sha(d/n)==h
                m['stage']=mode+'_'+stage;save()
                with (d/(stage+'.stdout.log')).open('w') as log:
                    child=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT);m['active_process']=dict(pid=child.pid,start_ticks=identity(child.pid));save();code=wait_preserving(child,600,m,save)
                m.pop('active_process',None);c['commands'].append(dict(stage=stage,argv=argv,exit_code=code,stdout_sha256=sha(d/(stage+'.stdout.log'))));save();assert code==0,(mode,stage)
            log=(d/'simulate.stdout.log').read_text();assert expected in log,(mode,log[-1800:])
            if mode in ['matching','ready_nba']:assert 'Fatal:' not in log and 'PAYLOAD_GROUP_PASS group=KA' in log and 'PAYLOAD_GROUP_PASS group=PW' in log
            else:assert 'Fatal:' in log and 'FULL_SHADOW_PROTOCOL_PASS' not in log and 'FULL_SHADOW_FIXTURE_READY_CANDIDATE_PASS' not in log
            c['status']='observed';save();print('PAYLOAD_CONTROL_OBSERVED',mode,flush=True)
        m.update(status='observed',stage='complete',full_system_functional_netlist_validated=False)
    except Exception as error:m.update(status='failed',error=repr(error));raise
    finally:save()


if __name__=='__main__':main()
