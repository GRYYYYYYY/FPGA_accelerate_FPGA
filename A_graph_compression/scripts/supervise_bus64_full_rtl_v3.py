#!/usr/bin/env python3
"""Wait for full native/input acceptance, then serial CSR and compact RTL plus audits."""
import json,os,signal,subprocess,sys,time
from pathlib import Path
from check_vitis_kernel import digest,require
from experiment_status_v6 import process
from owned_sim_resource_policy_v1 import observe,abort_reason
from run_compact_native_stack_recovery_v3 import atomic
from run_collision_safe_batch_hls_v1 import stop
from run_collision_safe_bus64_full_rtl_v1 import ROOT,BASE,NATIVE_GATE,paths
OUT=ROOT/'data/derived/bus64_full_rtl_supervision_20261030_v3'
NATIVE=ROOT/'data/derived/native_directory_recovery_supervision_20261030_v2'
INPUTS=ROOT/'data/derived/bus64_audit_recovery_supervision_20261030_v3'
def read(p):return json.loads(p.read_text())
def matches(owner):
    live=process(owner['pid'])
    return bool(live and live['state']!='Z' and live['start_ticks']==owner['start_ticks'] and live['command']==owner['command'])
def main():
    def interrupted(signum,frame):raise SystemExit(128+signum)
    signal.signal(signal.SIGTERM,interrupted)
    require(not OUT.exists(),'Refuse duplicate full RTL supervisor')
    owners={}
    for folder,script in [(NATIVE,'supervise_native_directory_recovery_v2.py'),(INPUTS,'supervise_bus64_audit_recovery_v3.py')]:
        state=read(folder/'state.json');owner=process(state['owner_pid'])
        require(owner and owner['state']!='Z' and script in owner['command'],'Existing prerequisite owner not verified')
        owners[str(folder)]=owner
    steps=[]
    for mode in [0,1]:
        _,trial,_=paths(mode);report=ROOT/f'results/collision_safe_bus64_full_rtl_mode_{mode}_audit_20261030_v1.json'
        require(not trial.exists() and not report.exists(),'Existing trial/report; no restart')
        steps += [dict(phase=f'mode_{mode}_full_RTL_C',mode=mode,script='run_collision_safe_bus64_full_rtl_v1.py',audit=False),
                  dict(phase=f'mode_{mode}_independent_RTL_audit',mode=mode,script='check_collision_safe_bus64_full_rtl_v1.py',audit=True,report=str(report))]
    names={'run_collision_safe_bus64_full_rtl_v1.py','check_collision_safe_bus64_full_rtl_v1.py','check_vitis_kernel.py','experiment_status_v6.py','owned_sim_resource_policy_v1.py','run_compact_native_stack_recovery_v3.py','run_collision_safe_batch_hls_v1.py','run_compact_nonzero_native_rtl_v2.py','compact_nonzero_native_contract_v2.py','check_collision_safe_batch_hls_v1.py',Path(__file__).name}
    files={str(ROOT/'scripts'/n):digest(ROOT/'scripts'/n) for n in names}
    OUT.mkdir();atomic(OUT/'plan.json',dict(files=files,owners=owners,steps=steps,no_physical_or_board_launch=True,serial_modes=[0,1]))
    state=dict(owner_pid=os.getpid(),status='running',stage='waiting_native_and_nonzero_independent_acceptance',completed=[]);atomic(OUT/'state.json',state);child=None
    try:
        while True:
            states={n:read(Path(n)/'state.json') for n in owners};live={n:matches(o) for n,o in owners.items()}
            for n,o in owners.items():
                require(states[n]['owner_pid']==o['pid'] and states[n]['status']!='failed','Prerequisite changed/failed')
                require(live[n] or states[n]['status']=='complete','Prerequisite disappeared without success')
            if all(not value for value in live.values()):
                native=states[str(NATIVE)];inputs=states[str(INPUTS)]
                require(native['status']=='complete' and native['stage']=='native_full_RTL_independent_audit_complete','Wrong native terminal')
                require(inputs['status']=='complete' and inputs['stage']=='both_modes_full_nonzero_inputs_independently_audited_RTL_pending','Wrong input terminal')
                require(native['report_sha256']==digest(NATIVE_GATE),'Changed native acceptance')
                gates={str(NATIVE_GATE):digest(NATIVE_GATE)}
                for folder,phase,report,status in [(NATIVE,'independent_final_audit',NATIVE_GATE,'recovered_collision_safe_native_full4tx_full44_original_C_independently_verified')]+[
                    (INPUTS,f'mode_{mode}_nonzero_audit',paths(mode)[2],'collision_safe_bus64_full44_inputs_all30_guards_all44_relocations_independently_verified') for mode in [0,1]]:
                    receipt=folder/(phase+'.receipt.json');r=read(receipt);log=folder/(phase+'.log')
                    require(r['exit_code']==0 and r.get('abort_reason') is None and r['log_sha256']==digest(log),'Failed predecessor audit')
                    result=read(report);require(result['status']==status,'Wrong typed predecessor acceptance')
                    if folder==INPUTS:
                        record=read(folder/(phase+'.result.json'))
                        require(record['report']==str(report) and record['sha256']==digest(report),'Changed input acceptance')
                    for name,h in result['files'].items():require(digest(name)==h,'Changed predecessor evidence '+name)
                    for p in [report,receipt,log,folder/'state.json']:gates[str(p)]=digest(p)
                atomic(OUT/'gates.json',dict(files=gates));break
            atomic(OUT/'observation.json',dict(owners_verified=live,stages={n:s['stage'] for n,s in states.items()},monotonic_seconds=time.monotonic()))
            time.sleep(10)
        initial=observe()
        for step in steps:
            for name,h in files.items():require(digest(name)==h,'Frozen RTL code changed '+name)
            require(abort_reason(initial,observe()) is None,'New OOM/reset before phase')
            # Runner must be able to lower its child limits to the original 192/96 GiB contract.
            cap=(16 if step['audit'] else 192)*1024**3;stack=(64 if step['audit'] else 256)*1024**2
            command=['prlimit',f'--as={cap}:{cap}',f'--stack={stack}:{stack}','--core=0:0','--',sys.executable,str(ROOT/'scripts'/step['script']),'--mode',str(step['mode'])]
            state['stage']=step['phase'];atomic(OUT/'state.json',state);started=time.monotonic();reason=None;log=OUT/(step['phase']+'.log')
            with log.open('x') as output:
                child=subprocess.Popen(command,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
                state['child_pid']=child.pid;atomic(OUT/'state.json',state)
                while child.poll() is None:
                    reason=abort_reason(initial,observe())
                    if reason:stop(child);break
                    time.sleep(1)
                code=child.wait();child=None
            final=observe();reason=reason or abort_reason(initial,final)
            atomic(OUT/(step['phase']+'.receipt.json'),dict(command=command,exit_code=code,abort_reason=reason,elapsed_seconds=time.monotonic()-started,log_sha256=digest(log),initial_memory=initial,final_memory=final))
            require(code==0 and reason is None,'Failed full RTL stage '+step['phase'])
            if step['audit']:
                report=read(Path(step['report']))
                require(report['status']=='collision_safe_bus64_full4tx_full44_original_C_oracle_independently_verified' and report['graph_mode']==step['mode'] and report['rtl_verified'] is True,'Wrong full RTL acceptance')
                atomic(OUT/(step['phase']+'.result.json'),dict(report=step['report'],sha256=digest(step['report'])))
            else:
                trial=read(paths(step['mode'])[1]/'state.json')
                require(trial['status']=='complete' and trial['stage']=='independent_final_rtl_audit_pending','Incomplete trial')
            state['completed'].append(step['phase']);atomic(OUT/'state.json',state)
        state.update(status='complete',stage='both_bus64_modes_full4_RTL_original_C_independently_audited_physical_pending');atomic(OUT/'state.json',state)
    except BaseException as exc:
        if child is not None and child.poll() is None:stop(child)
        state.update(status='failed',error=str(exc));atomic(OUT/'state.json',state);raise
if __name__=='__main__':main()
