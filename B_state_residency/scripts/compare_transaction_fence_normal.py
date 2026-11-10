"""Compare routing semantics and complete images against the pre-fence normal baseline."""
from pathlib import Path
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 old=ROOT/'results/route_join_drain_rtl_v1';new=ROOT/'results/transaction_fence_normal_rtl_v1';cases={}
 for p in [old,new]:assert json.loads((p/'source_bound_audit.json').read_text())['status']=='passed'
 for case in ['full','pressure']:
  rows=[[l.split()for l in(p/case/'natural_trace.txt').read_text().splitlines()]for p in [old,new]]
  tags=['P','O','C','W','A','E','S','M','LQ','V','F','FQ','FR','R','T','I','RL','RA','RC','RO','RB','SO','ST'];counts={}
  for tag in tags:
   values=[[t[2:]for t in r if t[0]==tag and not(tag=='FR'and len(t)==2)]for r in rows]
   assert values[0]==values[1],(case,tag);counts[tag]=len(values[0])
  images={}
  for name in ['owners.bin','design.bin','cost.bin','labels.bin']:
   assert sha(old/case/name)==sha(new/case/name),(case,name);images[name]=sha(new/case/name)
  axiequal={n:sha(old/case/n)==sha(new/case/n)for n in [t+'_axi.txt'for t in ['graph','design','label','owner','cost','qstate','table']]}
  cycles=[]
  for p in [old,new]:
   m=json.loads((p/'manifest.json').read_text());cycles.append(int(re.search(r'cycles=(\d+)',m['cases'][case]['result'])[1]))
  cases[case]=dict(matching_semantic_events=counts,image_sha256=images,axi_file_byte_identical=axiequal,old_cycles=cycles[0],fenced_cycles=cycles[1],cycle_increase=cycles[1]-cycles[0],cycle_increase_percent=(cycles[1]/cycles[0]-1)*100)
 result=dict(status='passed',old_audit_sha256=sha(old/'source_bound_audit.json'),new_audit_sha256=sha(new/'source_bound_audit.json'),auditor_sha256=sha(Path(__file__)),cases=cases,scope='Whole testbench wall cycles including boot/import/prepare/route/ripup. Behavioral simulation, not board speed or CPU speedup; journal adapter and recovery services were added along with fence.')
 (ROOT/'results/transaction_fence_normal_comparison_20261025.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
