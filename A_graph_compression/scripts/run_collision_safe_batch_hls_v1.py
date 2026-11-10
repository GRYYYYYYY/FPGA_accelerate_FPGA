#!/usr/bin/env python3
"""Versioned C-equivalent naming workaround, full44 C replay, then HLS.

All production/frozen inputs remain unchanged. Three helper function names are
changed in an isolated source copy to avoid the experimentally reproduced
2022.2 module/argument name collision. No algorithm, pragma, capacity or oracle
change is allowed by this preparer.
"""
import json
import os
from pathlib import Path
import re
import resource
import signal
import subprocess
import time

from check_vitis_kernel import digest, require
from owned_sim_resource_policy_v1 import observe, abort_reason, POLICY
from run_compact_native_stack_recovery_v3 import atomic

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
OLD=BASE/'compressed_batch_compact_cosim_setup'
OUT=BASE/'collision_safe_batch_hls_v1'
POINTER=ROOT/'data/derived/collision_safe_batch_hls_20261030_v1'
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')
RENAMES={'roots':'a_collect_tree_roots','query':'a_validate_snapshot_query','net':'a_write_net_trace_record'}


def stop(child):
    try:os.killpg(child.pid,signal.SIGTERM)
    except ProcessLookupError:pass
    try:child.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:os.killpg(child.pid,signal.SIGKILL)
        except ProcessLookupError:pass
        child.wait()


def run(state,initial,phase,args,as_gib,env):
    command=['prlimit',f'--as={as_gib*1024**3}:{as_gib*1024**3}',
             '--stack=67108864:67108864','--core=0:0','--',*args]
    state.update(stage=phase);atomic(OUT/'state.json',state)
    started=time.monotonic();child=None;reason=None;last=0
    try:
        require(abort_reason(initial,observe()) is None,'New OOM before '+phase)
        with (OUT/(phase+'.log')).open('x') as log:
            child=subprocess.Popen(command,cwd=OUT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            state['child_pid']=child.pid;atomic(OUT/'state.json',state)
            while child.poll() is None:
                current=observe();reason=abort_reason(initial,current)
                if time.monotonic()-last>=30:
                    atomic(OUT/'resource_observation.json',dict(phase=phase,observation=current));last=time.monotonic()
                if reason:stop(child);break
                time.sleep(1)
            code=child.wait();child=None
        receipt=dict(command=command,exit_code=code,elapsed_seconds=time.monotonic()-started,
                     abort_reason=reason,final_memory=observe(),log_sha256=digest(OUT/(phase+'.log')))
        atomic(OUT/(phase+'.receipt.json'),receipt)
        require(reason is None and code==0,'Failed '+phase)
        text=(OUT/(phase+'.log')).read_text(errors='replace')
        require(not any(x in text for x in ['ERROR:','Fatal:','runtime error:','AddressSanitizer:','LLVM ERROR']),'Error in '+phase)
        return text
    finally:
        if child is not None and child.poll() is None:stop(child)


def main():
    require(not OUT.exists() and not POINTER.exists(),'Refuse overwrite or duplicate build')
    proof=ROOT/'results/hls_root_name_reproducer_20261030_v1.json'
    repro=json.loads(proof.read_text());require(repro['naming_hypothesis_reproduced'] is True,'Missing controlled reproduction')
    for n,h in repro['files'].items():require(digest(n)==h,'Changed reproducer evidence '+n)
    setup=json.loads((OLD/'setup.json').read_text())
    oldcpu=ROOT/'results/compressed_batch_rtl_full_depth_cpu_20261025_v1.json'
    cpu=json.loads(oldcpu.read_text())
    require(cpu['status']=='compressed_batch_full44_declared_depth_cpu_snapshots_verified_rtl_pending','Wrong original full44 reference')
    OUT.mkdir();POINTER.mkdir()
    atomic(POINTER/'location.json',dict(bundle=str(OUT),owner_pid=os.getpid(),local_storage_ephemeral=True))
    state=dict(owner_pid=os.getpid(),status='running',stage='prepare',completed=[],full_kernel_accepted=False)
    atomic(OUT/'state.json',state);initial=observe()
    try:
        source=OUT/'source';source.mkdir();files={};changes=[]
        for p in (OLD/'source').iterdir():
            require(p.is_file(),'Unexpected source directory')
            sha=digest(p);require(setup['files'].get(str(p))==sha,'Changed original source '+str(p))
            original=p.read_text();candidate=original
            if p.suffix in ('.cpp','.hpp','.h'):
                # Only method definitions and method calls. In particular,
                # vector declarations named roots are not function calls.
                candidate=re.sub(r'::roots(?=\s*\()', '::'+RENAMES['roots'],candidate)
                candidate=re.sub(r'::net(?=\s*\()', '::'+RENAMES['net'],candidate)
                if p.name=='search_route_tree.hpp':
                    candidate=candidate.replace('static Status roots(', 'static Status '+RENAMES['roots']+'(')
                if p.name=='search_resident_snapshot.hpp':
                    candidate=re.sub(r'\bquery(?=\s*\()',RENAMES['query'],candidate)
                if p.name=='search_trace_records.hpp':
                    candidate=candidate.replace('static unsigned net(', 'static unsigned '+RENAMES['net']+'(')
            restored=candidate
            for old,new in RENAMES.items():
                require(new not in original,'Rename already existed')
                restored=re.sub(r'\b'+new+r'\b',old,restored)
            require(restored==original,'Change beyond helper identifiers')
            target=source/p.name;target.write_text(candidate)
            files[str(p)]=sha;files[str(target)]=digest(target)
            if candidate!=original:
                changes.append(dict(original=str(p),candidate=str(target),
                                    replacements={old:len(re.findall(r'\b'+new+r'\b',candidate)) for old,new in RENAMES.items()}))
        require({Path(r['candidate']).name for r in changes}=={'search_route_tree.hpp','search_resident_snapshot.hpp',
                'search_trace_records.hpp','search_batch_trace_top_v2.cpp','search_batch_top.cpp','search_net_top.cpp'},
                'Unexpected source change set')
        flow=OUT/'flow.tcl';flow.write_text('''open_project project
set_top search_batch_trace_top_v2
add_files source/search_batch_trace_top_v2.cpp -cflags "-std=c++14 -DSEARCH_GRAPH_MODE=1"
add_files -tb source/test_compressed_batch_rtl_full_depth.cpp -cflags "-std=c++14 -DSEARCH_GRAPH_MODE=1"
open_solution solution -flow_target vitis
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 5 -name default
set_clock_uncertainty 1.35
config_compile -pipeline_loops 0
csynth_design
puts COLLISION_SAFE_FULL_BATCH_CSYNTH_COMPLETE
exit
''')
        for p in [proof,oldcpu,OLD/'setup.json',Path(__file__).resolve(),flow,
                  ROOT/'scripts/owned_sim_resource_policy_v1.py']:
            files[str(p)]=digest(p)
        plan=dict(status='isolated_three_helper_function_identifier_renames',files=files,changes=changes,
                  renames=RENAMES,identifiers_only_inverse_verified=True,transactions_per_mode=4,ports=44,
                  c_modes=[0,1],hls_mode=1,part='xcu280-fsvh2892-2L-e',clock_ns=5,uncertainty_ns=1.35,
                  hls_max_widen_bitwidth='original_native_default_unchanged',cpu_as_gib=16,hls_as_gib=64,
                  resource_policy=POLICY,initial_memory=initial,full_kernel_accepted=False,
                  limitations=['C validation is against all8 original complete full44 snapshots; it does not replace RTL validation.',
                               'This native compact synthesis is a new candidate, not acceptance of any failed/encoded/physical result.',
                               'No frozen downstream prerequisite is rebound by this script.'])
        atomic(OUT/'plan.json',plan)
        env={k:v for k,v in os.environ.items() if k!='LD_PRELOAD'}
        env['A_BATCH_RTL_SNAPSHOT_PREFIX']=str(OUT/'candidate')
        comparisons=[]
        for mode in [0,1]:
            exe=OUT/f'mode_{mode}'
            run(state,initial,f'compile_{mode}',['g++','-std=c++14','-O2','-Wno-unknown-pragmas',
                f'-DSEARCH_GRAPH_MODE={mode}',str(source/'test_compressed_batch_rtl_full_depth.cpp'),
                str(source/'search_batch_trace_top_v2.cpp'),'-o',str(exe)],16,env)
            text=run(state,initial,f'cpu_{mode}',[str(exe)],16,env)
            require(f'FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode={mode} ports=44 transactions=4' in text and
                    f'SEARCH_BATCH_PASS mode={mode}' in text,'Missing full CPU markers')
            for tx in range(4):
                target=OUT/f'candidate_{mode}_{tx}.bin'
                reference=BASE/f'compressed_batch_rtl_tb_cpu_v2/cpu_{mode}_{tx}.bin'
                expected=cpu['files'].get(str(reference))
                require(expected is not None and digest(reference)==expected,'Changed original full44 oracle')
                require(target.stat().st_size==reference.stat().st_size==946498280,'Full snapshot size changed')
                actual=digest(target);require(actual==expected,'Complete snapshot differs')
                comparisons.append(dict(mode=mode,transaction=tx,candidate=str(target),reference=str(reference),
                                        bytes=946498280,sha256=actual))
                files[str(target)]=actual;files[str(reference)]=expected
            state['completed'].append(f'full44_cpu_mode_{mode}');atomic(OUT/'state.json',state)
        for p in OUT.glob('*.receipt.json'):files[str(p)]=digest(p)
        for p in OUT.glob('*.log'):files[str(p)]=digest(p)
        c_report=ROOT/'results/collision_safe_batch_full44_cpu_20261030_v1.json'
        require(not c_report.exists(),'CPU report exists')
        atomic(c_report,dict(status='identifier_only_candidate_matches_all8_original_full44_C_snapshots',files=files,
                            comparisons=comparisons,changes=changes,ports=44,transactions_per_mode=4,
                            modes=[0,1],full_kernel_accepted=False))
        hls_env={**env,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1'}
        text=run(state,initial,'hls',[str(HLS),'-f',str(flow)],64,hls_env)
        require('COLLISION_SAFE_FULL_BATCH_CSYNTH_COMPLETE' in text,'HLS incomplete')
        conflicts=[line for line in text.splitlines() if 'RTL name' in line and 'due to conflict' in line]
        require(not conflicts,'Remaining naming conflicts; inspect before RTL execution')
        rtl=OUT/'project/solution/syn/verilog';bad=[]
        for p in rtl.glob('*.v'):
            for number,line in enumerate(p.read_text().splitlines(),1):
                if re.search(r'\.(?:roots_x|query_x|net_x)\(',line):bad.append((str(p),number,line.strip()))
        require(not bad,'Old collided ports remain')
        state.update(status='synthesized_pending_independent_audit',stage='full_cpu_equal_and_new_compact_hls_complete',
                     cpu_report=str(c_report),remaining_naming_conflicts=conflicts,old_collided_connections=bad)
        atomic(OUT/'state.json',state)
        print(state['status'])
    except BaseException as exc:
        state.update(status='failed',error=str(exc));atomic(OUT/'state.json',state);raise


if __name__=='__main__':main()
