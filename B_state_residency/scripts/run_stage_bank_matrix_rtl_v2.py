"""Run original/default/static CP RTL on identical four-slot full-path stimuli."""
from pathlib import Path
import json
import os
import re
import shutil
import subprocess
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity,verify_freeze
from config_native_publication_synth_common_v1 import BIN,memory_admission,wait_preserving


def main():
    accepted=ROOT/'results/stage_static_functional_pair_20261030.json'
    assert read(accepted)['status']=='isolated_static_stage_narrow_functional_pair_actual_restored'
    verify_freeze(ROOT/'results/stage_static_functional_pair_sources_20261030')
    variant=ROOT/'hardware/variants/stage_static_cp_v1';vm=read(variant/'manifest.json')
    assert sha(variant/'baseline.sv')==vm['baseline_sha256']
    assert sha(variant/'fixed.sv')==vm['fixed_sha256']
    tb=ROOT/'hardware/tests/tb_stage_bank_matrix_v1.sv'
    p=BASE/'stage_bank_matrix_rtl_v2';assert not p.exists() and not os.environ.get('LD_PRELOAD')
    p.mkdir()
    m=dict(status='running',stage='prepare',runner_pid=os.getpid(),runner_start_ticks=identity(os.getpid()),
        runner_sha256=sha(Path(__file__)),tb_sha256=sha(tb),variant_manifest_sha256=sha(variant/'manifest.json'),cases={},
        scope='Original/default/static RTL,4 slots/MAX_PATH32; full image exports, CRC/duplicate/index failure, partial safe-withdraw cancellation, reset and atomic retention. Not functional netlist or full system.')
    def save():
        tmp=p/'manifest.pending.json';tmp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');tmp.replace(p/'manifest.json')
    save()
    try:
        for mode,source,defines in [('original','baseline.sv',['ORIGINAL']),('default','fixed.sv',[]),('static','fixed.sv',['STAGE_ON'])]:
            d=p/mode;d.mkdir();shutil.copyfile(variant/source,d/'controller.sv');shutil.copyfile(tb,d/'tb.sv')
            (d/'run.tcl').write_text('run all\nquit\n')
            c=dict(status='running',inputs={n:sha(d/n) for n in ['controller.sv','tb.sv','run.tcl']},commands=[]);m['cases'][mode]=c
            m['stage']=mode+'_wait_memory';save();memory_admission(m,save)
            compile=[str(BIN.parent/'xvlog'),'--sv']
            for flag in defines:compile+=['-d',flag]
            compile+=['controller.sv','tb.sv']
            phases=[('compile',compile),('elaborate',[str(BIN.parent/'xelab'),'--O0','tb_stage_bank_matrix','-s','probe','--mt','2']),
                    ('simulate',[str(BIN.parent/'xsim'),'probe','-tclbatch','run.tcl'])]
            for stage,argv in phases:
                for n,h in c['inputs'].items():assert sha(d/n)==h
                m['stage']=mode+'_'+stage;save()
                with (d/(stage+'.stdout.log')).open('w') as log:
                    child=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT)
                    m['active_process']=dict(pid=child.pid,start_ticks=identity(child.pid));save()
                    code=wait_preserving(child,900,m,save)
                m.pop('active_process',None);c['commands'].append(dict(stage=stage,argv=argv,exit_code=code));save();assert code==0,(mode,stage)
            log=(d/'simulate.stdout.log').read_text()
            assert 'STAGE_BANK_MATRIX_PASS commands=12 responses=12 imports=477 exports=1092 checks=12' in log
            assert 'Fatal:' not in log
            trace='\n'.join(re.findall(r'^(?:EVT |CASE |STAGE_BANK_MATRIX_PASS).*$',log,re.M))+'\n'
            (d/'events.txt').write_text(trace);c.update(status='observed',events_sha256=sha(d/'events.txt'));save()
            print('STAGE_MATRIX_RTL_CASE_OBSERVED',mode,flush=True)
        traces=[(p/mode/'events.txt').read_bytes() for mode in ['original','default','static']]
        assert traces[0]==traces[1]==traces[2], 'Full cycle/event/data trace mismatch'
        m.update(status='observed',stage='complete',exit_code=0)
    except Exception as error:
        m.update(status='failed',error=repr(error));raise
    finally:save()
    print('STAGE_BANK_MATRIX_RTL_OBSERVED')


if __name__=='__main__':main()
