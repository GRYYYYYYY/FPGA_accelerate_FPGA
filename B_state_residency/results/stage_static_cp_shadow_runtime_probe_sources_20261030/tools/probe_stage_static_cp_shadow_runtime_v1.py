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
    ref=BASE/'stage_static_cp_shadow_system_v5';old=read(ref/'manifest.json')
    assert old['status'] in ['running','observation_timeout'] and old['stage']=='simulate' and old.get('active_process')
    assert identity(old['runner_pid'])==str(old['runner_start_ticks'])
    p=BASE/'stage_static_cp_shadow_runtime_probe_v1';assert not p.exists()
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
    objects=['armed','reset_edges','checks','cp_transfer_checks','ka_transfer_checks','pw_transfer_checks']
    tcl="puts RUNTIME_PROBE_BEGIN\nset previous_time {}\n"
    tcl+="for {set step 1} {$step<=100} {incr step} {\n"
    tcl+=" set code [catch {run 10ns} message]\n"
    tcl+=" if {[llength [info commands current_time]]} {set now_time [current_time]} else {set now_time unavailable}\n"
    tcl+=" puts [list RUNTIME_PROBE_STEP $step actual_time $now_time catch_code $code message $message]\n"
    tcl+=" puts [list RUNTIME_PROBE_CYCLES [get_value -radix hex /tb_candidate_offer/cycles]]\n"
    for name in objects:
        tcl+=' puts [list RUNTIME_PROBE_VALUE '+name+' [get_value -radix hex /stage_static_cp_shadow/'+name+']]\n'
    tcl+=" if {$code || ($now_time ne {unavailable} && $now_time eq $previous_time)} {break}\n set previous_time $now_time\n}\nquit\n"
    (d/'run.tcl').write_text(tcl)
    argv=[a.replace(str(ref),str(p)) for a in old['active_process']['argv']]
    assert argv[0]==str(BIN.parent/'xsim')
    argv += ['--maxdeltaid','10000']
    shutil.copyfile(ref/'manifest.json',p/'parent_manifest_at_start.json')
    record=dict(status='running',runner_pid=os.getpid(),runner_start_ticks=identity(os.getpid()),
                runner_sha256=sha(__file__),reference_manifest_sha256=sha(ref/'manifest.json'),
                snapshot_sha256=snapshot,tcl_sha256=sha(d/'run.tcl'),command=argv,
                objects=objects,parent_snapshot_sha256=sha(p/'parent_manifest_at_start.json'),max_requested_time_ns=1000,max_delta_iterations=10000,
                scope='Short bounded diagnostic copy of the existing v5 snapshot, not a full duplicate regression. Original job preserved. Fresh initial images, no source/force edits. Only official maxdeltaid limit and10ns read-only queries; no functional acceptance.')
    def save():(p/'manifest.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    save()
    try:
        memory_admission(record,save)
        with (d/'stdout.log').open('w') as log:
            child=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT)
            record['active_process']=dict(pid=child.pid,start_ticks=identity(child.pid));save()
            code=wait_preserving(child,600,record,save)
        record.pop('active_process',None);record['exit_code']=code
        log=(d/'simulate.log').read_text()
        assert 'RUNTIME_PROBE_BEGIN' in log
        assert code in [0,1]
        for name,h in snapshot.items():assert sha(original/'iter2'/name)==sha(d/'xsim.dir/iter2'/name)==h
        record.update(status='observed',stage='complete',log_sha256=sha(d/'simulate.log'),stdout_sha256=sha(d/'stdout.log'),full_system_functional_netlist_validated=False)
    except Exception as error:
        record.update(status='failed',error=repr(error));raise
    finally:save()
    print('SHADOW_V5_RUNTIME_BOUNDED_PROBE_OBSERVED')


if __name__=='__main__':main()
