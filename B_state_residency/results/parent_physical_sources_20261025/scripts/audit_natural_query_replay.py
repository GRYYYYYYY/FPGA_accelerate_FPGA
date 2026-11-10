"""Bind replay construction, original source, restored input and byte comparisons."""
from pathlib import Path
import hashlib,json,sys,importlib.util
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());base=Path(m['base']);a=json.loads((base/'source_bound_audit.json').read_text());bm=json.loads((base/'manifest.json').read_text())
 assert m['status']==a['status']==bm['status']=='passed'
 assert sha(base/'source_bound_audit.json')==m['base_audit_sha256'] and sha(base/'manifest.json')==a['manifest_sha256']
 assert sha(Path(bm['input']))==bm['input_sha256']
 for name,d in m['sources'].items():assert sha(p/'sources'/name)==d
 for name,d in m['artifacts'].items():assert sha(p/name)==d
 for name,d in bm['sources'].items():assert sha(p/'sources'/name)==d
 dp=p/'sources/make_replay.py';assert sha(dp)==sha(ROOT/'adapters/natural_query_v1/make_replay.py')
 sp=importlib.util.spec_from_file_location('maker',dp);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
 assert mod.make((p/'sources/router.cpp').read_text()).encode()==(p/'sources/replay.cpp').read_bytes()
 assert len(m['commands'])==2 and all(c['exit_code']==0 for c in m['commands'])
 expected={'initial_nodes.u32','initial_overflow.u32','initial_caches.u32','prices.u32','state.txt','initial_heap.u32','events.txt','search_final_nodes.u32','search_final_heap.u32'}
 assert set(m['compared'])==expected
 for name,d in m['compared'].items():assert sha(p/name)==sha(base/name)==d
 result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),base_audit_sha256=sha(base/'source_bound_audit.json'),compared=m['compared'],event_counts=a['event_counts'],nodes=a['nodes'],scope='Restored natural prepared-query CPU search using original loop and actual Router cost/filter/push; nine byte-identical snapshots/events. No RTL or independent mathematical cost proof.')
 (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
