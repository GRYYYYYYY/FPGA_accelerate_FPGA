"""Check frozen original differential, full replay and every final backing byte."""
from pathlib import Path
import hashlib,json,re,struct,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from verify_owner_store import extract
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=ROOT/'results/owner_store_v2_20261024';base=ROOT/'results/owner_profile_real_v4_20261024'
 m=read(out/'manifest.json');assert m['status']=='passed'
 gate=read(base/'source_bound_audit.json');assert gate['status']=='passed' and gate['manifest_sha256']==sha(base/'manifest.json')
 assert m['baseline_gate_sha256']==sha(base/'source_bound_audit.json')
 assert m['events_sha256']==sha(base/'owner.events')==read(base/'manifest.json')['owner_events_sha256']
 original=Path(m['original_path']);assert sha(original)==m['original_sha256']
 assert (out/'sources/original_owner.inc').read_text()==extract(original.read_text())
 assert sha(ROOT/'scripts/verify_owner_store.py')==m['runner_sha256']==sha(out/'runner.py')
 for name,digest in m['sources'].items():
  assert sha(out/'sources'/name)==digest
  if name!='original_owner.inc':assert sha(ROOT/'hardware/search/owner_state_v1'/name)==digest
 for name,digest in m['artifacts'].items():assert sha(out/name)==digest
 assert [c['stage']for c in m['commands']]==['build','unit','real'] and all(c['exit_code']==0 for c in m['commands'])
 assert '-fsanitize=undefined' in m['commands'][0]['argv'] and '-fno-sanitize-recover=all' in m['commands'][0]['argv']
 unit=(out/'unit.log').read_text();assert 'OWNER_UNIT_PASS random_mutations=200000 queried_nets=3200000 refs_limit=65535 occupancy_limit=65535 distinct_nets=256 capacity_reuse=1 stale_plan=1' in unit
 real=(out/'real.log').read_text();match=re.fullmatch(r'OWNER_REPLAY_PASS events=(\d+) capacity=(\d+) peak_live=(\d+) planned_record_writes=(\d+) max_writes=(\d+) final_live=(\d+)\n',real);assert match
 events,capacity,peak_live,writes,max_writes,final_live=map(int,match.groups())
 assert (events,capacity,peak_live,final_live)==(18515060,65536,53734,0) and max_writes<=4
 last={};seen=0;markers=0
 with (base/'owner.events').open('rb')as f:
  while b:=f.read(32*65536):
   assert len(b)%32==0
   for op,node,net,count,occ,owner,refs,overflow in struct.iter_unpack('<8I',b):
    if op==0:markers+=1;continue
    assert op in (1,2);seen+=1
    if occ:last[node]=(occ,owner,refs,overflow)
    else:last.pop(node,None)
 assert seen==events and markers==1 and len(last)==722477
 assert all(occ==1 and overflow==0 and owner<2**31 and 0<refs<=65535 for occ,owner,refs,overflow in last.values())
 primary=(out/'final.primary').read_bytes();assert len(primary)==9089009*16
 for node,r in enumerate(struct.iter_unpack('<4I',primary)):
  state=last.pop(node,None)
  expected=(state[1]+1,0x10000|state[2],0,0)if state else (0,0,0,0)
  assert r==expected,(node,r,expected)
 assert not last
 pool=list(struct.iter_unpack('<4I',(out/'final.pool').read_bytes()));assert len(pool)==capacity
 allocator=struct.unpack('<4I',(out/'final.allocator').read_bytes())
 allocated,free_head,live,reserved=allocator
 assert allocated==peak_live and live==reserved==0
 free=set();ptr=free_head
 while ptr:
  assert 0<ptr<=allocated and ptr not in free;free.add(ptr)
  net,refs,next_ptr,padding=pool[ptr-1]
  assert net==refs==padding==0;ptr=next_ptr
 assert len(free)==allocated
 assert all(r==(0,0,0,0)for r in pool[allocated:])
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'random_mutations':200000,'original_function_queries':3200000,'real_mutations':events,'pool_capacity':capacity,'peak_pool_entries':peak_live,'max_planned_record_writes':max_writes,'planned_record_writes':writes,'full_primary_bytes_verified':len(primary),'full_pool_bytes_verified':capacity*16,'allocator_bytes_verified':16,'final_live_nodes':722477,'all_free_entries_reachable':True,'scope':'CPU executable storage layout, mutation plans and independent final backing verification; no AXI handshakes, B-error behavior, RTL or hardware performance proven.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
