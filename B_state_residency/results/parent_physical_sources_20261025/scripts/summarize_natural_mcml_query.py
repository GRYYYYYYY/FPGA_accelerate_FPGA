from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];BASE=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 c=BASE/'natural_mcml_query_v1';r=BASE/'natural_mcml_query_replay_v1';a=json.loads((c/'source_bound_audit.json').read_text());b=json.loads((r/'source_bound_audit.json').read_text());m=json.loads((c/'manifest.json').read_text())
 assert a['status']==b['status']=='passed'and a['manifest_sha256']==sha(c/'manifest.json')and b['manifest_sha256']==sha(r/'manifest.json')and b['base_audit_sha256']==sha(c/'source_bound_audit.json')
 for name,h in b['compared'].items():assert sha(c/name)==sha(r/name)==h
 rows=[l.split()for l in(c/'events.txt').read_text().splitlines()];w=[t for t in rows if t[0]=='W'];parent=None;unused=[];kids=[];seen=0
 for t in rows:
  if t[0]=='E':
   if parent is not None and seen<len(kids):unused.append(dict(parent=parent,unprocessed_children=kids[seen:]))
   parent=int(t[1]);kids=[];seen=0
  elif t[0]=='K':kids.append(int(t[2]))
  elif t[0]=='C':seen+=1
 if seen<len(kids):unused.append(dict(parent=parent,unprocessed_children=kids[seen:]))
 assert len(unused)==1 and len(unused[0]['unprocessed_children'])==1
 result=dict(status='passed',capture=str(c),replay=str(r),capture_audit_sha256=sha(c/'source_bound_audit.json'),replay_audit_sha256=sha(r/'source_bound_audit.json'),input_sha256=m['input_sha256'],full_route_sha256=m['reference_result_sha256'],state=a['state'],event_counts=a['event_counts'],created_transitions=a['created_transitions'],nodes=a['nodes'],target_clear_count=a['heap_clear_count'],unused_filtered_children=unused,compared=b['compared'],scope='Second real-design first prepared query, complete original-route hash gate and exact restored CPU search. No MCML input codec/RTL test or parent-cache performance yet.')
 (ROOT/'results/natural_mcml_query_20261025.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status='passed',event_counts=result['event_counts'],unused=unused)))
if __name__=='__main__':main()
