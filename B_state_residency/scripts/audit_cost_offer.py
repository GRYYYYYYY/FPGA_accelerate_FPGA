from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for name,v in m['sources'].items():assert sha(out/'sources'/name)==v['sha256']==sha(Path(v['path']))
 assert sha(out/'runner.py')==m['runner_sha256']
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 assert len(m['commands'])==3 and all(x['exit_code']==0 for x in m['commands'])
 log=(out/'simulate.log').read_text();rows=[list(map(int,l.split()[1:]))for l in log.splitlines()if l.startswith('CASE ')]
 expected=[[1,0,3,4,0]]+[[i,1,3,3 if i==7 else 4,1]for i in range(2,9)]+[[9,2,65536,65536,1],[10,1,3,65536,1]]+[[i,3,3,3,1]for i in range(11,15)]+[[15,0,3,4,1]]
 assert rows==expected and 'COST_OFFER_UNIT_PASS cases=16'in log and 'Fatal:'not in log
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'responses':rows,'scope':'Mock frontier backend component protocol only; FULL is injected, not actual full heap or joined AXI recovery.'}
 (out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print('COST_OFFER_UNIT_AUDITED')
if __name__=='__main__':main()
