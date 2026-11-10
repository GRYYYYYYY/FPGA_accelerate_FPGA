"""Audit native preparation ripup capture against original prepared-query evidence."""
from pathlib import Path
import hashlib,json,struct,sys,mmap
from run_followup_query import sha
p=Path(sys.argv[1]).resolve();base=Path(sys.argv[2]).resolve()
a=json.loads((p/'source_bound_audit.json').read_text());assert a['status']=='passed'
for name in ['initial_nodes.u32','initial_overflow.u32','initial_caches.u32','initial_heap.u32','prices.u32','state.txt','events.txt','search_final_nodes.u32','search_final_heap.u32','router.result']:
 assert sha(p/name)==sha(base/name),name
lines=[s.split() for s in (p/'prepare_ripup.txt').read_text().splitlines()]
query=list(map(int,lines[0][1:]));path=list(map(int,lines[1][1:]));assert query[0]==int(json.loads((p/'manifest.json').read_text())['environment']['B_QUERY_SEQUENCE'])
before={int(s[1]):tuple(map(int,s[2:])) for s in lines if s[0]=='BEFORE'}
after={int(s[1]):tuple(map(int,s[2:])) for s in lines if s[0]=='AFTER'}
assert len(path)==len(set(path)) and set(before)==set(after)==set(path)
interior=path[1:-1] if path and path[0]==query[4] and query[5]==0 else path
changes=[]
with (p/'initial_nodes.u32').open('rb')as f:
 mm=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
 for node in path:
  old=before[node];new=after[node];u=struct.unpack_from('<11I',mm,node*44)
  assert tuple(v & 0xffffffff for v in new[:3])==u[6:9]
  if node in interior:
   assert old[3]>1 and new==(old[0],old[1]-1,old[2],old[3]-1)
   changes.append({'node':node,'refs_before':old[3],'refs_after':new[3],'occupancy':new[2]})
  else:assert new==old
result={'status':'passed','capture_audit_sha256':sha(p/'source_bound_audit.json'),'auditor_sha256':sha(Path(__file__)),'trace_sha256':sha(p/'prepare_ripup.txt'),'query':query,'path_sink_to_source':path,'native_decrements':changes,'unchanged_reference_files':10,'scope':'Observed original CPU preparation path and decrements, source reconstruction and complete route result identity. No native RTL consecutive-query execution.'}
(p/'prepare_trace_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
