"""Independent transcript/edge-trace/source audit for a bounded real-module slice."""
from pathlib import Path
import csv,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from stage_static_cp_physical_common_v6 import BASE,read,sha,identity,audit_memory

def main():
 p=Path(sys.argv[1]).resolve();assert p in [BASE/'publication_start_interlock_slice_v1',BASE/'publication_start_interlock_slice_v1_actual_restore']
 m=read(p/'manifest.json');assert m['status']=='observed' and m['stage']=='complete' and not m.get('active_process')
 assert identity(m['runner_pid'])!=str(m['runner_start_ticks'])
 assert sha(R/'scripts/research_checks/run_publication_interlock_slice_v1.py')==m['runner_sha256']
 for n,h in {**m['inputs'],**m['artifact_sha256']}.items():assert sha(p/n)==h
 for n,h in m['evidence_sha256'].items():assert sha(n)==h
 audit_memory(m)
 assert [(c['role'],c['stage']) for c in m['commands']]==[(role,stage) for role in ['original','candidate'] for stage in ['compile','elaborate','simulate']]
 for c in m['commands']:
  assert c['exit_code']==0 and identity(c['pid'])!=str(c['start_ticks'])
  assert sha(p/c['role']/(c['stage']+'.stdout.log'))==c['stdout_sha256']
  if c['stage']=='compile':assert ('ORIGINAL_WIRING' in c['argv'])==(c['role']=='original')
 for n in ['checkpoint_lease_guard.sv','checkpoint_publish_barrier.sv','tb_interlock.sv','run.tcl']:
  assert (p/'original'/n).read_bytes()==(p/'candidate'/n).read_bytes()
 for n in ['checkpoint_lease_guard.sv','checkpoint_publish_barrier.sv']:
  assert (p/'candidate'/n).read_bytes()==(BASE/'stage_static_cp_synth_v1/sources'/n).read_bytes()
 expected=[(1,'release_only'),(2,'simultaneous_start_held_release'),(3,'response_backpressure'),(4,'release_on_consumption_edge'),(5,'release_after_consumption'),(6,'held_start_not_ready'),(7,'cancel'),(8,'invalid_start_payload'),(9,'normal_commit'),(10,'unknown_start_observation')]
 old=(p/'original/simulate.log').read_text();new=(p/'candidate/simulate.log').read_text()
 assert old.count('Fatal:')==1 and re.search(r'^Fatal: INTERLOCK_CHECK SIMULTANEOUS_RELEASE_NOT_BLOCKED$',old,re.M)
 assert 'INTERLOCK_SLICE_PASS' not in old
 assert re.findall(r'^INTERLOCK_CASE id=(\d+) name=(\S+) time=(\d+)$',old,re.M)==[('1','release_only','66000')]
 assert not re.search(r'^(?:Fatal:|ERROR:|CRITICAL WARNING:)',new,re.M)
 markers=re.findall(r'^INTERLOCK_CASE id=(\d+) name=(\S+) time=(\d+)$',new,re.M)
 assert [(int(i),name) for i,name,t in markers]==expected
 assert all(int(b[2])>int(a[2]) for a,b in zip(markers,markers[1:]))
 terminal=re.findall(r'^INTERLOCK_SLICE_PASS cases=(\d+) checks=(\d+) cycles=(\d+) owned_checks=(\d+) time=(\d+)$',new,re.M);assert len(terminal)==1
 cases,checks,cycles,owned,time_ps=map(int,terminal[0]);assert cases==10 and checks>80 and owned>20 and time_ps<10000000
 with (p/'candidate/edges.csv').open() as f:rows=list(csv.DictReader(f))
 assert len(rows)==cycles and int(rows[-1]['time_ps'])+1000==time_ps
 assert [int(x['time_ps']) for x in rows]==list(range(5000,time_ps,10000))
 active=[x for x in rows if x['rst']=='0']
 starts=[x for x in active if x['start']==x['start_ready']=='1'];releases=[x for x in active if x['release']==x['release_ready']=='1']
 assert len(starts)==4 and len(releases)==6
 assert all(x['release_ready']=='0' for x in active if x['start']=='1')
 assert all(x['lease_owned']=='1' and x['release_ready']=='0' for x in active if x['publication_owned']=='1')
 assert len([x for x in active if x['start']=='1' and x['start_ready']=='0' and x['release']=='1'])==3
 simultaneous=[x for x in starts if x['release']=='1'];assert len(simultaneous)==2 and all(x['release_ready']=='0' for x in simultaneous)
 consumed=[x for x in active if x['done']==x['done_ready']=='1'];assert len(consumed)==4 and all(x['release_ready']=='0' and x['lease_owned']=='1' for x in consumed)
 unknown=[x for x in active if x['start']=='x'];assert len(unknown)==1 and unknown[0]['release_ready']=='x'
 for prev,nxt in zip(rows,rows[1:]):
  if prev['rst']=='1' or nxt['rst']=='1':continue
  if prev['start']==prev['start_ready']=='1':assert nxt['publication_owned']==nxt['lease_owned']=='1'
  if prev['release']==prev['release_ready']=='1':assert nxt['lease_owned']=='0'
  if prev['done']==prev['done_ready']=='1':assert nxt['publication_owned']=='0' and nxt['lease_owned']=='1'
  if prev['start']=='x':assert nxt['publication_owned']=='0' and nxt['lease_owned']=='1'
 warnings={}
 for role in ['original','candidate']:
  for stage in ['compile','elaborate']:
   t=(p/role/(stage+'.stdout.log')).read_text();assert not re.search(r'^(?:ERROR:|Fatal:|CRITICAL WARNING:)',t,re.M)
   warnings[role+'/'+stage]=[line for line in t.splitlines() if line.startswith('WARNING:')]
 result=dict(status='passed',audit_kind='bounded_actual_lease_barrier_slice_original_negative_and_candidate_positive',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(__file__),
 original_expected_failure='INTERLOCK_CHECK SIMULTANEOUS_RELEASE_NOT_BLOCKED',candidate_cases=expected,checks=checks,cycles=cycles,owned_checks=owned,finish_time_ps=time_ps,
 edge_trace=dict(rows=len(rows),start_transfers=len(starts),release_transfers=len(releases),simultaneous_offers_accepted_start_only=len(simultaneous),held_start_not_ready_cycles=3,done_consumptions=len(consumed),unknown_start_samples=1,sha256=sha(p/'candidate/edges.csv')),
 warnings=warnings,candidate_full_system_validated=False,candidate_synthesized=False,production_repair_accepted=False,production_rtl_modified=False,
 limitations=['Only two real production modules; full-query surrounding arbitration/retirement/metadata agents are modeled.',
 'Held raw start blocks release even when start_open=0. This test observes that behavior; it does not prove caller forward progress or endorse a caller contract.',
 'Unknown-start propagation is a four-state RTL observation, not hardware/metastability safety.',
 'No arbitrary-input formal proof, complete-query candidate run, new synthesis, post-route simulation or board proof. Original full RTL counterexample retained.'])
 target=p/'source_bound_audit.json';assert not target.exists()
 target.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print('INTERLOCK_SLICE_INDEPENDENT_AUDIT_PASSED',cases,checks,cycles)
if __name__=='__main__':main()
