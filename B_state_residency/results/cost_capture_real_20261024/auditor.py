"""Bind complete-route noninterference and sampled full arithmetic packets."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from build_cost_capture_router import generate

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/cost_capture_real_20261024';base=ROOT/'results/search_cost_real_20261024'
 m=json.loads((out/'manifest.json').read_text());bm=json.loads((base/'manifest.json').read_text());assert m['status']==bm['status']=='passed'
 assert m['baseline_manifest_sha256']==sha(base/'manifest.json') and m['baseline_audit_sha256']==sha(base/'source_bound_audit.json')
 assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
 assert sha(ROOT/'scripts/verify_cost_capture_real.py')==m['runner_sha256']==sha(out/'verify_cost_capture_real.py')
 assert sha(ROOT/'adapters/build_cost_capture_router.py')==m['generator_sha256']==sha(out/'build_cost_capture_router.py')
 for name,d in m['sources'].items():assert sha(out/name)==d
 generated=generate((base/'sources/trace.cpp').read_text(),(base/'sources/real_trace.hpp').read_text())
 assert (out/'sources/trace.cpp').read_text()==generated[0] and (out/'sources/real_trace.hpp').read_text()==generated[1]
 assert generated[0].count('\n')==(base/'sources/trace.cpp').read_text().count('\n')
 for p in (base/'sources').iterdir():
  if p.name not in ['trace.cpp','real_trace.hpp']:assert sha(out/'sources'/p.name)==bm['sources'][str(p.relative_to(base))]
 assert sha(out/'sources/cost_observe.hpp')==sha(ROOT/'hardware/search/cost_observe.hpp')
 assert sha(out/'router_cost_capture')==m['binary_sha256'] and all(c['exit_code']==0 for c in m['commands'])
 for field,file in [('result_sha256','trace.result'),('accesses_sha256','trace.accesses'),('metadata_sha256','trace.jsonl')]:assert m[field]==bm[field]==sha(out/file)
 assert m['attempts']==570286 and m['metrics']['pushes']==130334832
 assert m['cost_packets_sha256']==sha(out/'cost_packets.txt')
 previous=0;selected=0;rounds={};first={};last=[]
 for line in (out/'cost_packets.txt').read_text().splitlines():
  v=line.split()
  if v[0]=='END':last=list(map(int,v[1:]));continue
  assert v[0]=='V' and len(v)==34
  call,it,conn,parent,child=map(int,v[1:6]);assert call>previous and 0<=parent<9089009 and 0<=child<9089009
  assert call%8192==0 or first.get(it,0)<32
  first[it]=first.get(it,0)+1;rounds[it]=rounds.get(it,0)+1;previous=call;selected+=1
  assert all(0<=int(x,16)<2**32 for x in v[6:])
 assert last==[129764546,selected] and selected>15000 and set(rounds)==set(range(1,13))
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'total_evaluations':last[0],'selected_packets':selected,'per_iteration':rounds,'all_attempt_metadata_equal':True,'route_result_equal':True,'captured_label_accesses_equal':True,'scope':'Complete CPU route noninterference; every 8192nd cost evaluation plus first32 per iteration sampled. Packets carry all23 inputs and5 observed arithmetic outputs. Not exhaustive operand trace and not RTL.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
