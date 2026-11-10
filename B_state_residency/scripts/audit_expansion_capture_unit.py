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
 log=(out/'simulate.log').read_text();events=[l for l in log.splitlines()if l.startswith(('ITEM ','RESULT '))]
 assert events==['ITEM 10 1','ITEM 20 3','RESULT 20 1','ITEM 10 2','RESULT 10 2']
 assert 'EXPANSION_CAPTURE_UNIT_PASS nested=1 replies=2 items=3'in log and 'Fatal:'not in log
 full=Path(sys.argv[2]).resolve();fm=json.loads((full/'source_bound_audit.json').read_text());assert fm['status']=='passed'and fm['manifest_sha256']==sha(full/'manifest.json')
 for n in ['children_frames.sv','expansion_capture.sv']:assert sha(out/'sources'/n)==sha(full/'sources/capture'/n)
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'full_capture_audit_sha256':sha(full/'source_bound_audit.json'),'events':events,'scope':'Same capture RTL, mock expander; nested parent resume and offered result backpressure/request exclusion. Not real expander nested requests or joined fault recovery.'}
 (out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
