"""Summarize the independently audited natural capture and CPU replay."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];BASE=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 capture=BASE/'natural_query_v2';replay=BASE/'natural_query_replay_v1'
 a=json.loads((capture/'source_bound_audit.json').read_text());b=json.loads((replay/'source_bound_audit.json').read_text())
 assert a['status']==b['status']=='passed' and sha(capture/'source_bound_audit.json')==b['base_audit_sha256']
 for p,c in [(capture,a),(replay,b)]:assert sha(p/'manifest.json')==c['manifest_sha256']
 for n,d in b['compared'].items():assert sha(capture/n)==sha(replay/n)==d
 out=dict(status='passed',capture=str(capture),replay=str(replay),capture_audit_sha256=sha(capture/'source_bound_audit.json'),replay_audit_sha256=sha(replay/'source_bound_audit.json'),state=a['state'],event_counts=a['event_counts'],updated_nodes=a['updated_nodes'],created_transitions=a['created_transitions'],heap_clear_count=a['heap_clear_count'],full_node_count=a['nodes'],compared=b['compared'],scope='First natural logicnets prepared query, original CPU exact replay. No RTL replay, complete connection commit or speedup claim.')
 p=ROOT/'results/natural_query_20261025.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['event_counts']))
if __name__=='__main__':main()
