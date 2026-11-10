#!/usr/bin/env python3
"""Preserve old naming-check failure, then audit both modes and prepare full RTL inputs."""
import json,os,signal,subprocess,sys,time
from pathlib import Path
from check_vitis_kernel import digest,require
from experiment_status_v6 import process
from owned_sim_resource_policy_v1 import observe,abort_reason
from run_compact_native_stack_recovery_v3 import atomic
from run_collision_safe_batch_hls_v1 import stop
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
OUT=ROOT/'data/derived/bus64_audit_recovery_supervision_20261030_v3'
PARENT=ROOT/'data/derived/recovery_acceptance_supervision_20261030_v1'
OLD_SETUP=ROOT/'data/derived/bus64_fresh_setup_supervision_20261030_v1'
PAIR=BASE/'collision_safe_bus64_pair_execution_v2'
REVIEW=ROOT/'results/collision_safe_bus64_pair_hls_audit_20261030_v3.json'
def read(p):return json.loads(p.read_text())
def matches(owner):
 p=process(owner['pid'])
 return bool(p and p['state']!='Z' and p['start_ticks']==owner['start_ticks'] and p['command']==owner['command'])
def main():
 def interrupted(signum,frame):raise SystemExit(128+signum)
 signal.signal(signal.SIGTERM,interrupted)
 require(not OUT.exists(),'Refuse duplicate recovery supervisor')
 old=ROOT/'data/derived/bus64_audit_recovery_supervision_20261030_v2'
 old_state=read(old/'state.json');old_plan=read(old/'plan.json')
 require(old_state['status']=='failed' and old_state['stage']=='pair_independent_audit' and not process(old_state['owner_pid']),'Previous recovery not terminal')
 old_receipt=read(old/'pair_independent_audit.receipt.json');old_log=old/'pair_independent_audit.log'
 require(old_receipt['exit_code']!=0 and old_receipt['abort_reason'] is None and old_receipt['log_sha256']==digest(old_log),'Wrong prior recovery failure')
 require('ValueError: Ambiguous restored callee search_batch_trace_top_v2_update_3' in old_log.read_text(),'Unexpected recovery failure')
 owners=old_plan['owners']
 for n,o in owners.items():
  current=read(Path(n)/'state.json')
  require(current['owner_pid']==o['pid'] and current['status'] in ('complete','failed') and not matches(o),'Original owner not terminal')
 steps=[dict(phase='pair_independent_audit',script='check_collision_safe_bus64_pair_v4.py',args=['--execution-root',str(PAIR),'--output',str(REVIEW)],report=str(REVIEW),accepted='collision_safe_bus64_pair_full8_C_and_HLS_independently_verified_RTL_pending',as_gib=16)]
 for mode in [0,1]:
  for phase,script,report,status,cap in [
   ('fresh_setup','prepare_collision_safe_bus64_cosim_v2.py',BASE/'collision_safe_bus64_cosim_setup_v2'/f'mode_{mode}/setup.json','collision_safe_bus64_full44_four_transaction_csim_and_fresh_setup_verified_rtl_pending',64),
   ('setup_audit','check_collision_safe_bus64_cosim_v2.py',ROOT/f'results/collision_safe_bus64_cosim_mode_{mode}_audit_20261030_v2.json','collision_safe_bus64_mode_full44_fresh_setup_independently_verified_RTL_pending',16),
   ('nonzero_prepare','prepare_collision_safe_bus64_nonzero_v2.py',BASE/'collision_safe_bus64_nonzero_preparation_v2'/f'mode_{mode}/preparation.json','collision_safe_bus64_full44_nonzero_inputs_prepared_not_executed',16),
   ('nonzero_audit','check_collision_safe_bus64_nonzero_v2.py',ROOT/f'results/collision_safe_bus64_nonzero_mode_{mode}_audit_20261030_v2.json','collision_safe_bus64_full44_inputs_all30_guards_all44_relocations_independently_verified',16)]:
   steps.append(dict(phase=f'mode_{mode}_{phase}',script=script,args=['--mode',str(mode)],mode=mode,report=str(report),accepted=status,as_gib=cap))
 for step in steps:require(not Path(step['report']).exists(),'Existing result')
 names={s['script'] for s in steps}|{'check_vitis_kernel.py','experiment_status_v6.py','owned_sim_resource_policy_v1.py','run_compact_native_stack_recovery_v3.py','run_collision_safe_batch_hls_v1.py','run_collision_safe_bus64_pair_v1.py','check_collision_safe_batch_hls_v1.py','prepare_collision_safe_bus64_pair_v1.py','search_kernel_memory_plan.py','prepare_compact_nonzero_axi_models_v1.py','check_compact_nonzero_axi_models_v1.py',Path(__file__).name}
 files={str(ROOT/'scripts'/n):digest(ROOT/'scripts'/n) for n in names}
 OUT.mkdir();atomic(OUT/'prior_recovery_failure.json',dict(files={str(p):digest(p) for p in [old/'state.json',old/'plan.json',old/'pair_independent_audit.receipt.json',old_log]}));atomic(OUT/'plan.json',dict(owners=owners,steps=steps,files=files,no_rtl_or_physical_launch=True,preserves_old_failure=True))
 state=dict(owner_pid=os.getpid(),status='running',stage='waiting_original_audit_terminal',completed=[]);atomic(OUT/'state.json',state);child=None
 try:
  while True:
   states={n:read(Path(n)/'state.json') for n in owners}
   live={n:matches(o) for n,o in owners.items()}
   for n,o in owners.items():
    require(states[n]['owner_pid']==o['pid'],'Owner changed')
    require(live[n] or states[n]['status'] in ('complete','failed'),'Owner disappeared without terminal state')
   require(states[str(PAIR)]['status']!='failed','Pair execution failed; no restart')
   if all(not v for v in live.values()):
    pair=states[str(PAIR)];parent=states[str(PARENT)];setup=states[str(OLD_SETUP)]
    require(pair['status']=='complete' and pair['completed_modes']==[0,1] and pair['stage']=='paired_hls_complete_independent_audit_pending','Incomplete pair')
    require(parent['jobs']['paired_bus64_HLS']['status']=='failed' and setup['status']=='failed','Expected preserved old rejection missing')
    receipt=read(PARENT/'paired_bus64_HLS.receipt.json');log=PARENT/'paired_bus64_HLS.log'
    require(receipt['exit_code']!=0 and receipt['abort_reason'] is None and receipt['log_sha256']==digest(log),'Old rejection not a clean checker failure')
    require('ValueError: Ambiguous restored callee search_batch_trace_top_v2_update_3' in log.read_text(),'Unexpected old failure; inspect before recovery')
    require(not (ROOT/'results/collision_safe_bus64_pair_hls_audit_20261030_v2.json').exists(),'Unexpected old acceptance')
    evidence={str(p):digest(p) for p in [PARENT/'state.json',PARENT/'paired_bus64_HLS.receipt.json',log,OLD_SETUP/'state.json',PAIR/'state.json']}
    atomic(OUT/'preserved_rejection.json',dict(files=evidence,reason='CSR sink-loop helper specialized as update rather than update_3'))
    break
   atomic(OUT/'observation.json',dict(owners_verified=live,stages={n:s.get('stage') for n,s in states.items()},monotonic_seconds=time.monotonic()))
   time.sleep(10)
  initial=observe()
  for step in steps:
   for n,h in files.items():require(digest(n)==h,'Frozen recovery code changed '+n)
   require(abort_reason(initial,observe()) is None,'New OOM/reset')
   require(not Path(step['report']).exists(),'Refuse overwrite')
   cap=step['as_gib']*1024**3
   command=['prlimit',f'--as={cap}:{cap}','--stack=67108864:67108864','--core=0:0','--',sys.executable,str(ROOT/'scripts'/step['script'])]+step['args']
   state['stage']=step['phase'];atomic(OUT/'state.json',state)
   started=time.monotonic();reason=None;log=OUT/(step['phase']+'.log')
   with log.open('x') as out:
    child=subprocess.Popen(command,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
    state['child_pid']=child.pid;atomic(OUT/'state.json',state)
    while child.poll() is None:
     reason=abort_reason(initial,observe())
     if reason:stop(child);break
     time.sleep(1)
    code=child.wait();child=None
   final=observe();reason=reason or abort_reason(initial,final)
   atomic(OUT/(step['phase']+'.receipt.json'),dict(command=command,exit_code=code,abort_reason=reason,elapsed_seconds=time.monotonic()-started,log_sha256=digest(log),initial_memory=initial,final_memory=final))
   require(code==0 and reason is None,'Recovery step failed '+step['phase'])
   report=read(Path(step['report']));require(report['status']==step['accepted'],'Wrong typed result')
   if 'mode' in step:require(report['graph_mode']==step['mode'],'Wrong mode')
   atomic(OUT/(step['phase']+'.result.json'),dict(report=step['report'],sha256=digest(step['report']),status=report['status']))
   state['completed'].append(step['phase']);atomic(OUT/'state.json',state)
  state.update(status='complete',stage='both_modes_full_nonzero_inputs_independently_audited_RTL_pending');atomic(OUT/'state.json',state)
 except BaseException as exc:
  if child is not None and child.poll() is None:stop(child)
  state.update(status='failed',error=str(exc));atomic(OUT/'state.json',state);raise
if __name__=='__main__':main()
