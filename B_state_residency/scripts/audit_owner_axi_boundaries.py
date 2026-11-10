from pathlib import Path
from collections import Counter
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 dep=ROOT/'results/owner_axi_v2_20261024';gate=json.loads((dep/'source_bound_audit.json').read_text());assert gate['status']=='passed' and gate['manifest_sha256']==sha(dep/'manifest.json') and sha(dep/'source_bound_audit.json')==m['functional_gate_sha256']
 for name,spec in m['sources'].items():assert sha(out/'sources'/name)==spec['sha256']
 for name in ['owner_state_store.sv','axi_file_memory.sv']:assert sha(out/'sources'/name)==sha(dep/'sources'/name)
 assert [c['stage']for c in m['commands']]==['compile','elaborate','simulate'] and all(c['exit_code']==0 for c in m['commands'])
 log=(out/'simulate.log').read_text();assert 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log and log.count('OWNER_BOUNDARIES_PASS ')==1
 assert 'OWNER_BOUNDARIES_PASS faults=22 recoveries=22 checks=97 cycles=8857' in log
 faults=Counter(map(int,re.findall(r'^OWNER_FAULT fixture=\d+ status=(\d+) drained=1$',log,re.M)))
 assert faults==Counter({9:6,6:6,12:4,11:2,0:2}),faults
 assert log.count('OWNER_PARTIAL_COMMIT writes=2 allocator_unchanged=1 backing_changed=1')==1
 assert log.count('OWNER_IDLE_FAULT kind=R')==log.count('OWNER_IDLE_FAULT kind=B')==1
 memory=bytearray(16384);base=0x1fffff000;read_addr=None;pending_b=False;counts=Counter()
 for line in (out/'axi.txt').read_text().splitlines():
  v=line.split()
  if v[0]=='RESET':
   assert read_addr is None and not pending_b;memory[:]=bytes(16384);counts['explicit_design_reloads']+=1
  elif v[0]=='H':
   assert read_addr is None and not pending_b
   offset=int(v[1]);memory[offset:offset+16]=int(v[2],16).to_bytes(16,'little');counts['host_corrupt_records']+=1
  elif v[0]=='A':
   assert read_addr is None and not pending_b and int(v[2])==1
   read_addr=int(v[1],16);assert read_addr%64==0 and base<=read_addr<=base+16384-64
  elif v[0]=='R':
   address=int(v[1],16);assert address==read_addr
   assert int(v[2],16).to_bytes(64,'little')==memory[address-base:address-base+64]
   if int(v[3]):counts['r_error_responses']+=1
   read_addr=None;counts['reads']+=1
  elif v[0]=='W':
   assert read_addr is None and not pending_b
   address,strobes,data=[int(x,16)for x in v[1:]];assert base<=address<=base+16384-64 and address%64==0
   assert strobes in [0xffff<<i for i in (0,16,32,48)]
   payload=data.to_bytes(64,'little');offset=address-base
   for i in range(64):
    if strobes>>i&1:memory[offset+i]=payload[i]
   pending_b=True;counts['writes']+=1
  else:
   assert v[0]=='B' and pending_b
   if int(v[1]):counts['b_error_responses']+=1
   pending_b=False;counts['bresponses']+=1
 assert not pending_b and read_addr is None and counts['r_error_responses']==1 and counts['b_error_responses']==2
 assert counts['writes']==counts['bresponses']
 assert bytes(memory)==(out/'actual.bin').read_bytes()==bytes(16384)
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'faults':22,'recoveries':22,'checks':97,'cycles':8857,'fault_status_counts':dict(faults),'axi':dict(counts),'partial_physical_commit_observed':True,'stalled_axi_valid_preserved':True,'last_b_timeout_tie_checked':True,'scope':'Actual RTL fault propagation, current single-beat transaction drain, explicit whole-design reload, and all AXI bytes. No physical rollback; invalid slave burst streams still require system isolation/reset.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
