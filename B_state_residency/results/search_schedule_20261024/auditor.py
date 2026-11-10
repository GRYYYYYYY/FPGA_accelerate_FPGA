"""Derive measured queue/recursive-push requirements from every real search attempt."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 base=ROOT/'results/search_cost_real_20261024';gate=json.loads((base/'source_bound_audit.json').read_text());m=json.loads((base/'manifest.json').read_text())
 assert gate['status']=='passed' and gate['manifest_sha256']==sha(base/'manifest.json')
 assert m['metadata_sha256']==sha(base/'trace.jsonl')
 s=dict(attempts=0,pushes=0,polls=0,cleared=0,cleared_attempts=0,max_peak=0)
 for line in (base/'trace.jsonl').open():
  x=json.loads(line);assert x['record']=='attempt'
  assert x['frontier_pushes']==x['frontier_polls']+x['frontier_cleared']
  s['attempts']+=1;s['pushes']+=x['frontier_pushes'];s['polls']+=x['frontier_polls'];s['cleared']+=x['frontier_cleared'];s['cleared_attempts']+=x['frontier_cleared']>0;s['max_peak']=max(s['max_peak'],x['frontier_peak'])
 assert s==dict(attempts=570286,pushes=130334832,polls=48292082,cleared=82042750,cleared_attempts=570286,max_peak=38638)
 assert s['pushes']==m['metrics']['pushes']
 source=(base/'sources/trace.cpp').read_text();a=source.index('    void push(State& st,');b=source.index('    void evaluateCostAndPush(',a);push=source[a:b]
 assert 'tl_pushes++;' in push and 'if (lookahead)' in push and 'exploreAndExpand(st, child);' in push and 'st.queue->offer(newTotal, child);' in push
 r={'status':'passed','counts':s,'lookahead_pushes_in_this_run':0,'basis':'Each push increments tl_pushes and takes either recursive lookahead or queue offer. Full-run queue offers equal all tl_pushes; thus this exact fixture has no lookahead pushes. Every attempt clears a nonempty queue. This does not establish a bound on other devices/designs or remove recursive search semantics.','real_gate_sha256':sha(base/'source_bound_audit.json'),'metadata_sha256':m['metadata_sha256'],'push_function_sha256':hashlib.sha256(push.encode()).hexdigest(),'auditor_sha256':sha(Path(__file__))}
 out=ROOT/'results/search_schedule_20261024';out.mkdir(exist_ok=True)
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
