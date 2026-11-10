"""Replay an immutable failed snapshot with read-only Tcl value observations.

Fresh input images and copied runtime snapshot; no RTL/checker edits or forces.
"""
from pathlib import Path
import json
import os
import shutil
import subprocess
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity
from config_native_publication_synth_common_v1 import wait_preserving,BIN,memory_admission


def main():
    ref=BASE/'stage_static_cp_shadow_system_v4';old=read(ref/'manifest.json')
    assert old['status']=='failed' and old['stage']=='simulate' and not old.get('active_process')
    assert identity(old['runner_pid'])!=str(old['runner_start_ticks'])
    p=BASE/'stage_static_cp_shadow_failure_probe_v2';assert not p.exists()
    assert not os.environ.get('LD_PRELOAD')
    p.mkdir();d=p/'full';d.mkdir()
    original=ref/'full/xsim.dir';shutil.copytree(original,d/'xsim.dir')
    snapshot={n:sha(original/'iter2'/n) for n in ['xsimk','xsim.mem','xsim.reloc','xsim.dbg','xsim.xdbg']}
    for name,h in snapshot.items():assert sha(d/'xsim.dir/iter2'/name)==h
    for key in ['scoreboards','next_scoreboards','third_scoreboards','fourth_scoreboards']:
        for name,h in old[key].items():assert sha(ref/name)==h;shutil.copyfile(ref/name,p/name)
    assert sha(old['binding'])==old['binding_sha256'];regions=read(old['binding'])['regions']
    for name,key in [('design.bin','design'),('cost.bin','cost_history_prices_nets')]:shutil.copyfile(regions[key]['path'],d/name)
    with (d/'owners.bin').open('wb') as out:
        for key in ['owners','owner_pool','owner_allocator']:
            with Path(regions[key]['path']).open('rb') as source:shutil.copyfileobj(source,out)
    for name in ['g3.bin','snapshot.bin','pool.bin']:shutil.copyfile(d/'owners.bin',d/name)
    shutil.copyfile(regions['owner_allocator']['path'],d/'allocator.bin')
    with (d/'labels.bin').open('wb') as out:out.truncate(3145728)
    for file in (ref/'sources').rglob('*.dat'):shutil.copyfile(file,d/file.name)
    schema_path=ROOT/'results/stage_static_cp_port_schema_20261030.json'
    schema=read(schema_path)
    outputs=[e['name'] for e in schema['ports'] if e['direction']=='output']
    inputs=[e['name'] for e in schema['ports'] if e['direction']=='input']
    assert len(outputs)==346 and len(inputs)==217
    objects=[prefix+name for name in outputs for prefix in ['actual_','expected_']]
    objects += ['drive_'+name for name in inputs]
    objects += ['armed','reset_edges','checks','cp_active_checks','cp_stall_checks','cp_transfer_checks','cp_edge_checks','cp_idle_observations','cp_idle_differences']
    assert len(objects)==918 and len(set(objects))==918
    def observe(label):
        return ''.join('puts [list SHADOW_PROBE '+label+' '+name+' [get_value -radix hex /stage_static_cp_shadow/'+name+']]\n' for name in objects)
    tcl='run 255ns\n'+observe('before_255ns')+'run 1ns\n'+observe('after_256ns')+'quit\n'
    (d/'run.tcl').write_text(tcl)
    argv=[a.replace(str(ref),str(p)) for a in old['cases']['full']['commands'][-1]['argv']]
    assert argv[0]==str(BIN.parent/'xsim')
    record=dict(status='running',runner_pid=os.getpid(),runner_start_ticks=identity(os.getpid()),
                runner_sha256=sha(__file__),reference_manifest_sha256=sha(ref/'manifest.json'),
                snapshot_sha256=snapshot,tcl_sha256=sha(d/'run.tcl'),command=argv,
                schema_sha256=sha(schema_path),objects=objects,
                scope='Copied exact compiled snapshot and fresh original input images; original v4 checker unchanged. Read-only Tcl before/after failure, no force/deposit or source edits; not functional acceptance.')
    def save():(p/'manifest.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    save()
    try:
        memory_admission(record,save)
        with (d/'stdout.log').open('w') as log:
            child=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT)
            record['active_process']=dict(pid=child.pid,start_ticks=identity(child.pid));save()
            code=wait_preserving(child,600,record,save)
        record.pop('active_process',None);record['exit_code']=code
        assert code==0
        log=(d/'simulate.log').read_text()
        assert 'FULL_SHADOW_MISMATCH port=k_a_net time=256000 actual=00000000 expected=xxxxxxxx' in log
        assert 'SHADOW_PROBE before_255ns actual_cp_m_valid 0' in log
        assert 'SHADOW_PROBE before_255ns expected_cp_m_valid 0' in log
        assert 'SHADOW_PROBE after_256ns actual_cp_m_valid 0' in log
        assert 'SHADOW_PROBE after_256ns expected_cp_m_valid 0' in log
        assert 'SHADOW_PROBE before_255ns actual_k_a_valid 0' in log
        assert 'SHADOW_PROBE before_255ns expected_k_a_valid 0' in log
        assert 'SHADOW_PROBE after_256ns actual_k_a_valid 0' in log
        assert 'SHADOW_PROBE after_256ns expected_k_a_valid 0' in log
        for name,h in snapshot.items():assert sha(original/'iter2'/name)==sha(d/'xsim.dir/iter2'/name)==h
        record.update(status='observed',stage='complete',log_sha256=sha(d/'simulate.log'),full_system_functional_netlist_validated=False)
    except Exception as error:
        record.update(status='failed',error=repr(error));raise
    finally:save()
    print('SHADOW_V4_FAILURE_ALL_PORT_PROBE_OBSERVED')


if __name__=='__main__':main()
