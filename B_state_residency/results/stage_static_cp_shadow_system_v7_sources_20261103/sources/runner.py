"""One complete independently prepared v7 shadow; retain exact child terminal receipts."""
from pathlib import Path
import json,sys,os,time,subprocess,copy,shutil,socket
from shadow_recovered_evidence_v7 import ROOT,BASE,read,sha,identity
from stage_static_cp_shadow_common_v7_revision2 import TARGET,REFERENCE,evidence,MARKER
from shadow_prepared_runtime_v7 import validate_preparation,check_admission
from shadow_terminal_receipt_v1 import record_child_exit,record_exception

def main():
 p=Path(sys.argv[1]).resolve();assert p==TARGET and not (p/'manifest.json').exists()
 pr=validate_preparation(p);review=ROOT/'results/stage_static_cp_shadow_v7_preparation_review_20261102.json';rv=read(review)
 assert rv['status']=='full_shadow_v7_preparation_independently_reviewed_not_executed' and rv['preparation_sha256']==sha(p/'preparation.json')
 for n,h in rv['tools'].items():assert sha(ROOT/'scripts'/n)==h
 rm,proof=evidence();assert all(pr['predecessors'].get(k)==v for k,v in proof.items())
 assert not os.environ.get('LD_PRELOAD');d=p/'full';assert not list(d.glob('*.bin'))
 m=copy.deepcopy(rm);m.pop('active_process',None)
 m.update(status='running',stage='wait_memory',mode='full_netlist_shadow_fixture_ready_v7',runner_pid=os.getpid(),runner_start_ticks=identity(os.getpid()),runner_sha256=sha(Path(__file__)),hostname=socket.gethostname(),boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),pid_namespace=os.readlink('/proc/self/ns/pid'),cgroup_namespace=os.readlink('/proc/self/ns/cgroup'),preparation_sha256=sha(p/'preparation.json'),preparation_review_sha256=sha(review),stage_reference=str(REFERENCE),stage_reference_audit_sha256=pr['reference_audit_sha256'],sources=pr['sources'],predecessors=pr['predecessors'],bound=pr['bound'],shadow_inputs=pr['shadow_inputs'],namespace_sha256=pr['namespace_sha256'],synthesis_netlist_sha256=pr['synthesis_netlist_sha256'],original_vendor_glbl_sha256=pr['original_vendor_glbl_sha256'],run_tcl_sha256=pr['run_tcl_sha256'],memory_policy=pr['memory_policy'],memory_samples=[],cases={'full':dict(status='running',commands=[])},unconditional_outputs=342,qualified_outputs=['cp_m_data','k_a_node','k_a_net','p_m_wdata'],clock_lead_ps=1,all_pin_strict_equivalence=False,scope=pr['scope'],full_system_functional_netlist_validated=False,physical_gate_open=False)
 def save():
  temp=p/'manifest.pending.json';temp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');temp.replace(p/'manifest.json')
 # Atomic ownership claim after all prelaunch checks. A second runner cannot enter.
 with (p/'manifest.json').open('x') as f:json.dump(m,f,indent=2)
 child=None
 try:
  stable=None;deadline=time.monotonic()+10800
  while True:
   cg=Path('/sys/fs/cgroup');cur=int((cg/'memory.current').read_text());lim=int((cg/'memory.max').read_text());now=time.monotonic()
   ok=cur<=225*1024**3 and cur*4<=lim*3
   stable=(now if stable is None else stable) if ok else None
   row=dict(time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),monotonic=now,current_bytes=cur,limit_bytes=lim,stable_seconds=0 if stable is None else now-stable)
   m['memory_samples'].append(row);save()
   if row['stable_seconds']>=60:m['memory_admission']=row;check_admission(m);save();break
   assert now<deadline,'Memory admission observation expired without launching simulation';time.sleep(5)
  validate_preparation(p);m['stage']='prepare_fresh_inputs';save();plan=read(p/'input_plan.json');regions=plan['regions']
  assert sha(plan['binding'])==plan['binding_sha256']
  for n,k in [('design.bin','design'),('cost.bin','cost_history_prices_nets'),('allocator.bin','owner_allocator')]:shutil.copyfile(regions[k]['path'],d/n)
  with (d/'owners.bin').open('xb') as out:
   for k in ['owners','owner_pool','owner_allocator']:
    with Path(regions[k]['path']).open('rb') as inp:shutil.copyfileobj(inp,out,1<<20)
  for n in ['snapshot.bin','pool.bin','g3.bin']:shutil.copyfile(d/'owners.bin',d/n)
  with (d/'labels.bin').open('xb') as out:out.truncate(3145728)
  m['fresh_input_sha256']={n:sha(d/n) for n in ['design.bin','cost.bin','allocator.bin','owners.bin','snapshot.bin','pool.bin','g3.bin','labels.bin']};save()
  for cmd in pr['commands']:
   validate_preparation(p);stage=cmd['stage'];argv=cmd['argv'];m['stage']=stage;begin=time.monotonic();save()
   with (d/(stage+'.stdout.log')).open('x') as log:
    child=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT);pid=child.pid;ticks=identity(pid)
    m['active_process']=dict(stage=stage,pid=pid,start_ticks=ticks,argv=argv);save();code=child.wait()
   record_child_exit(m,code);m['cases']['full']['commands'].append(dict(stage=stage,argv=argv,pid=pid,start_ticks=ticks,exit_code=code,elapsed_s=time.monotonic()-begin,stdout_sha256=sha(d/(stage+'.stdout.log'))));save();assert code==0,stage
   print('FULL_SHADOW_V7',stage,'exit0',flush=True)
  log=(d/'simulate.log').read_text()
  for marker in [MARKER,'CP_TRANSFER_MONITOR_END words=1560','PAYLOAD_GROUP_PASS group=KA','PAYLOAD_GROUP_PASS group=PW','PAYLOAD_TRANSFER_MONITOR_END ka=26 pw=8223 aw=','ROUTE_PATH_BANK_PASS','ROUTE_STAGE_BANK_PASS','HOST_EDIT_NATIVE_PASS','FOURTH_WARM_PASS polls=83 expands=82 candidates=402 costs=231','$finish called']:assert log.count(marker)==1,marker
  assert 'Fatal:' not in log and 'ERROR:' not in log and 'FATAL_ERROR:' not in log
  m.update(status='observed',stage='complete');m['cases']['full']['status']='observed'
 except BaseException as exc:record_exception(m,exc,child);raise
 finally:save()
 print('FULL_SHADOW_V7_OBSERVED_REQUIRES_INDEPENDENT_AUDIT',p,flush=True)
if __name__=='__main__':main()
