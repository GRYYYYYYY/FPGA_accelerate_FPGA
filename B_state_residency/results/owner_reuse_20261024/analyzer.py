"""Measure reuse boundaries; do not equate a conditional opportunity with speedup."""
from pathlib import Path
from collections import Counter
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 dep=ROOT/'results/access_owner_v3_20261024';m=json.loads((dep/'manifest.json').read_text());g=json.loads((dep/'source_bound_audit.json').read_text());assert g['status']=='passed'and g['manifest_sha256']==sha(dep/'manifest.json')
 original=ROOT/'../_shared/assets/gpu_router_original/rewrite/cpp_router/src/main.cpp';source=original.read_text()
 assert 'int countSourceUses = searchCountUser(childRnode, c.netIdx);'in source
 cases={}
 for case,cm in m['cases'].items():
  d=dep/case;assert cm['artifacts']['observed.txt']==sha(d/'observed.txt')and cm['artifacts']['owner_axi.txt']==sha(d/'owner_axi.txt')
  commands=[];actions={};requests={}
  for line in (d/'observed.txt').open():
   r=line.split()
   if r[0]=='O':commands.append(('host',None,None))
   elif r[0]=='S'and int(r[2])in [4,6]:
    cid,kind,phase,node,net=map(int,r[1:6]);key=(node,net)
    requests.setdefault(cid,[]).append(key);commands.append(('service',cid,kind))
   elif r[0]=='D':actions[int(r[1])]=int(r[3])
  # Each raw operation starts with the allocator record read. Distinct regions
  # prevent a chain walk from being mistaken for another operation boundary.
  meta=json.loads((ROOT/'results/access_fabric_inputs_20261024/manifest.json').read_text())['cases'][cm['fixture']]
  allocator=0x51fffff000+((meta['nodes']*16+63)&~63)+4096+1024+4096
  read_counts=[]
  for line in (d/'owner_axi.txt').open():
   r=line.split()
   if r[0]=='A'and int(r[1],16)==allocator:read_counts.append(0)
   elif r[0]=='R':assert read_counts;read_counts[-1]+=1
  assert len(read_counts)==len(commands)
  duplicate_queries=sum(len(v)-len(set(v))for v in requests.values())
  reusable=Counter();conditional_reads=0
  for command,reads in zip(commands,read_counts):
   category,cid,kind=command
   if category=='service'and actions[cid]!=0:
    reusable[kind]+=1;conditional_reads+=reads
  assert duplicate_queries==0
  cases[case]={'owner_service_requests':sum(map(len,requests.values())),'within_child_duplicate_gets':duplicate_queries,'allowed_children_with_prior_owner_snapshot':sum(reusable.values()),'allowed_prior_kind_counts':dict(reusable),'conditional_cost_get_read_transactions':conditional_reads,'conditional_cost_get_axi_read_bytes':conditional_reads*64}
 out=ROOT/'results/owner_reuse_20261024';out.mkdir();(out/'analyzer.py').write_bytes(Path(__file__).read_bytes())
 result={'status':'measured','functional_gate_sha256':sha(dep/'source_bound_audit.json'),'original_source_sha256':sha(original),'analyzer_sha256':sha(Path(__file__)),'cases':cases,'conclusion':'No same-child repeated kind4/6 lookup in these fixtures. A duplicate-read cache confined to access cannot save reads here. Original evaluateCostAndPush reads count again for every allowed child, so retaining count/occupancy into cost may avoid a future GET only if the owner read lock spans both stages.','limitations':['Cost is not integrated; conditional transaction/byte counts are not observed cost traffic or speedup.','Current lock ends at access response retirement; retaining a snapshot afterward requires extending ownership or version validation.','No assumption that repeated query2/price4 identifies a unique design occupancy version.']}
 (out/'analysis.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
