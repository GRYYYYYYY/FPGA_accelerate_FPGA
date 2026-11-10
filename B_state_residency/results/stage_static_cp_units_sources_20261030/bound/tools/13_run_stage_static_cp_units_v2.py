"""Twelve preserved controller fixtures, stage-only CP sources and both observers."""
from pathlib import Path
import importlib.util
import json
import os
import shutil
import subprocess
from host_edit_system_common_v1 import ROOT,BASE,read,sha,restored,identity,verify_freeze
from config_native_publication_synth_common_v1 import BIN,memory_admission,wait_preserving


def main():
    accepted=ROOT/'results/stage_bank_functional_matrix_20261030.json'
    assert read(accepted)['status']=='four_slot_functional_matrix_outcomes_actual_restored'
    verify_freeze(ROOT/'results/stage_bank_functional_matrix_sources_20261030')
    ref=BASE/'route_checkpoint_unit_v8'
    history=read(ref/'manifest.json');audit=read(ref/'source_bound_audit.json')
    receipt=read(ROOT/'results/route_checkpoint_unit_v8_restore_20261025.json')
    assert history['status']=='passed' and audit['status']==receipt['status']=='passed'
    assert audit['manifest_sha256']==sha(ref/'manifest.json')
    assert receipt['audit_byte_identical'] and receipt['audit_sha256']==sha(ref/'source_bound_audit.json')
    assert sha(Path(receipt['preserved_original'])/'source_bound_audit.json')==receipt['audit_sha256']
    variant=ROOT/'hardware/variants/stage_static_cp_v1';vm=read(variant/'manifest.json')
    prep=ROOT/'results/stage_static_cp_units_v2_preparation_20261030.json';pr=read(prep)
    for n,h in pr['bound'].items():assert sha(n)==h
    builder=ROOT/'hardware/variants/stage_static_cp_units_v1/build_tb.py'
    spec=importlib.util.spec_from_file_location('isolated_stage_preserved_tb',builder)
    b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
    p=BASE/'stage_static_cp_units_v2';assert not p.exists() and not os.environ.get('LD_PRELOAD')
    p.mkdir();shutil.copyfile(ref/'labels.txt',p/'labels.txt')
    bound={}
    for i,(src,digest) in enumerate(pr['bound'].items()):
        rel=f'tools/{i:02d}_{Path(src).name}';q=p/rel;q.parent.mkdir(exist_ok=True);shutil.copyfile(src,q)
        bound[rel]=dict(source=src,sha256=digest);assert sha(q)==digest
    m=dict(status='running',stage='prepare',runner_pid=os.getpid(),runner_start_ticks=identity(os.getpid()),
        runner_sha256=sha(Path(__file__)),preparation_sha256=sha(prep),bound=bound,cases=[],
        labels_sha256=sha(p/'labels.txt'),reference_audit_sha256=sha(ref/'source_bound_audit.json'),
        scope='Original CP/default/static-stage only: route,CP8,CP32,generic same-cycle reply; original stimuli, path word changes and old-tree stage bank observer retained. No path factoring, native publication or full system.')
    def save():
        tmp=p/'manifest.pending.json';tmp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');tmp.replace(p/'manifest.json')
    save()
    try:
        for mode in ['baseline','default','factored']:
            for suite in ['route','checkpoint','checkpoint32','generic_overlap']:
                for rel,e in bound.items():assert sha(e['source'])==sha(p/rel)==e['sha256']
                d=p/(mode+'_'+suite);d.mkdir();source=variant/('baseline.sv' if mode=='baseline' else 'fixed.sv')
                assert sha(source)==vm['baseline_sha256' if mode=='baseline' else 'fixed_sha256']
                shutil.copyfile(source,d/'route_commit_controller.sv');tb,marker=b.build(ROOT,mode,suite)
                (d/'tb.sv').write_text(tb);(d/'run.tcl').write_text('run 1ms\nquit\n')
                c=dict(mode=mode,suite=suite,status='running',commands=[],rtl_sha256=sha(source),tb_sha256=sha(d/'tb.sv'));m['cases'].append(c)
                m['stage']=mode+'_'+suite+'_wait_memory';save();memory_admission(m,save)
                phases=[('compile',[str(BIN.parent/'xvlog'),'--sv','route_commit_controller.sv','tb.sv']),
                    ('elaborate',[str(BIN.parent/'xelab'),'--O0','tb_route_commit','-s','route','--debug','typical','--mt','2']),
                    ('simulate',[str(BIN.parent/'xsim'),'route','--tclbatch','run.tcl','--log','simulate.log',
                        '--testplusarg','labels='+str(p/'labels.txt'),'--testplusarg','events='+str(d/'events.txt'),
                        '--testplusarg','bank_events='+str(d/'bank_events.txt'),'--testplusarg','stage_events='+str(d/'stage_events.txt')])]
                for stage,argv in phases:
                    m['stage']=mode+'_'+suite+'_'+stage;save()
                    with (d/(stage+'.stdout.log')).open('w') as log:
                        child=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT)
                        m['active_process']=dict(pid=child.pid,start_ticks=identity(child.pid));save()
                        code=wait_preserving(child,600,m,save)
                    m.pop('active_process',None);c['commands'].append(dict(stage=stage,argv=argv,exit_code=code,log_sha256=sha(d/(stage+'.stdout.log'))));save();assert code==0,(mode,suite,stage)
                log=(d/'simulate.log').read_text()
                assert 'ROUTE_STAGE_BANK_PASS' in log and marker in log and '$finish called' in log and 'Fatal:' not in log and 'ERROR:' not in log
                c.update(status='passed',trace_sha256=sha(d/'events.txt'),simulate_log_sha256=sha(d/'simulate.log'),bank_trace_sha256=sha(d/'bank_events.txt'),stage_trace_sha256=sha(d/'stage_events.txt'));save()
                print('ISOLATED_STAGE_UNITS',mode,suite,'passed',flush=True)
        m.update(status='observed',stage='complete',exit_code=0)
    except Exception as error:
        m.update(status='failed',error=repr(error));raise
    finally:save()
    print('ISOLATED_STAGE_TWELVE_UNITS_OBSERVED')


if __name__=='__main__':main()
