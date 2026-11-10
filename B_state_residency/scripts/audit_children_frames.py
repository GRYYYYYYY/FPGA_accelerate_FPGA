from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for n,v in m['sources'].items():assert sha(out/'sources'/n)==v['sha256']==sha(Path(v['path']))
 assert sha(out/'runner.py')==m['runner_sha256']
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 assert len(m['commands'])==3 and all(c['exit_code']==0 for c in m['commands'])
 log=(out/'simulate.log').read_text();cases=[l for l in log.splitlines()if l.startswith('CASE ')];items=[l for l in log.splitlines()if l.startswith('ITEM ')]
 assert cases==['CASE '+str(i)+' '+s for i,s in enumerate(['resume_ok','reuse_ok','depth_stop','capacity_drain','count_stop','abort_drain','producer_stop','reset_empty','abort_admission'],1)]
 assert items==['ITEM 10 1','ITEM 20 3','ITEM 10 2','ITEM 40 4']
 assert 'CHILDREN_FRAMES_PASS cases=9 items=4'in log and 'Fatal:'not in log
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'cases':cases,'items':items,'scope':'Standalone static children/frame cursor component; mock producer. Not actual graph expander, dynamic-label re-read, immediate recursive scheduler or full cost/commit engine integration.'}
 (out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
