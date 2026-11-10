"""Independent vector/ownership replay and source-bound cost service audit."""
from pathlib import Path
from collections import Counter
from itertools import permutations
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=ROOT/'results/cost_service_v2_20261024';m=read(out/'manifest.json')
 assert m['status']=='passed'
 for name,spec in m['sources'].items():assert sha(out/'sources'/name)==spec['sha256']==sha(Path(spec['path'])),name
 for name,digest in m['artifacts'].items():assert sha(out/name)==digest,name
 assert sha(out/'runner.py')==m['runner_sha256']
 assert len(m['commands'])==5 and all(c['exit_code']==0 for c in m['commands'])
 gate=Path(m['hls_gate']['path']);assert sha(gate)==m['hls_gate']['sha256']
 hg=read(gate);assert hg['status']=='passed' and hg['rtl_bit_exact_on_all_vectors']
 hls=gate.parent;hm=read(hls/'manifest.json');assert sha(hls/'manifest.json')==hg['manifest_sha256']
 assert sha(out/'vectors.txt')==m['vectors_sha256']==hm['vectors_sha256']==sha(hls/'vectors.txt')
 for name,digest in hm['generated_rtl_artifacts'].items():
  if '/syn/verilog/' in name and Path(name).suffix in ('.v','.dat'):assert sha(out/'sources'/Path(name).name)==digest
 vec=[s.split() for s in (out/'vectors.txt').read_text().splitlines()];assert len(vec)==21576 and all(len(v)==29 for v in vec)
 orders=[];faults=[]
 for line in (out/'collector_cases.txt').read_text().splitlines():
  v=line.split()
  if v[0]=='ORDER':orders.append(tuple(map(int,v[1:])))
  elif v[0]=='FAULT':faults.append(int(v[1]))
  else:assert v==['END','120','18']
 assert Counter(orders)==Counter(permutations(range(5))) and faults==list(range(18))
 pending=None;requests=responses=resets=cancelled=0;seen=[];groups=Counter();statuses=Counter();last_cookie=0
 for line in (out/'transactions.txt').read_text().splitlines():
  v=line.split()
  if v[0]=='RESET':
   resets+=1;cancelled+=pending is not None;pending=None
  elif v[0]=='Q':
   assert pending is None
   cookie,index,query,price,active=map(int,v[1:]);assert cookie==last_cookie+1;last_cookie=cookie
   assert 0<=index<len(vec) and 0<=query<4 and 0<=price<16
   requests+=1;pending=(cookie,index,query,price,active)
  elif v[0]=='R':
   assert pending is not None
   cookie,query,price,status=map(int,v[1:5]);words=[int(x,16) for x in v[5:]]
   ic,index,iq,ip,active=pending;assert (cookie,query,price)==(ic,iq,ip)
   expected_status=1 if cookie==21577 else 2 if cookie==21578 else 0
   assert status==expected_status and (active==0)==(status==1)
   assert words==([0]*5 if status else [int(x,16)for x in vec[index][24:]])
   if cookie<=21576:seen.append(index);groups[int(vec[index][0])]+=1
   statuses[status]+=1;responses+=1;pending=None
  elif v[0]=='END':assert tuple(map(int,v[1:]))==(requests,responses,resets) and pending is None
  else:raise AssertionError(v)
 assert seen==list(range(21576)) and (requests,responses,resets,cancelled)==(23019,22299,721,720)
 logs=(out/'cost_memory_call.log').read_text()+(out/'cost_service.log').read_text()
 assert not re.search(r'Fatal:|ERROR:',logs) and logs.count('$finish called')==2
 assert 'COST_MEMORY_CALL_PASS permutations=120 fault_cases=18 timeout_boundary=1' in logs
 match=re.search(r'COST_SERVICE_PASS vectors=21576 reset_offsets=720 accepted=(\d+) responded=(\d+) resets=(\d+) early_writes=(\d+) all_writes=(\d+) completions=(\d+) cycles=(\d+)',logs);assert match
 nums=list(map(int,match.groups()));assert nums[:3]==[requests,responses,resets] and nums[3]>=21576*4
 latency=re.search(r'COST_MAX latency=(\d+) index=(\d+)',logs);assert latency and int(latency[1])<720
 # Preserve failure and prove v2 only changed the testbench scheduling.
 neg=ROOT/'results/cost_service_20261024';nm=read(neg/'manifest.json');assert nm['status']=='failed'
 assert 'Fatal: early outputs rejected' in (neg/'cost_memory_call.log').read_text()
 for name in ['cost_memory_call.sv','cost_service.sv','tb_cost_service.sv']:
  assert sha(out/'sources'/name)==sha(neg/'sources'/name)
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),
  'vectors':len(vec),'groups':dict(groups),'responses':responses,'requests':requests,'resets':resets,
  'reset_cancelled':cancelled,'statuses':dict(statuses),'output_words_compared':5*(responses-2),
  'collector_permutations':len(orders),'fault_cases':len(faults),'timeout_completion_boundary':True,
  'early_output_writes':nums[3],'all_output_writes':nums[4],'hls_completions':nums[5],'cycles':nums[6],
  'max_service_latency_cycles':int(latency[1]),'reset_sweep_vector_index':int(latency[2]),
  'scope':'Actual exact_v2 HLS with snapshot/collector, external owner and synchronous cold reset. No full hardware search, routed timing or board performance.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
