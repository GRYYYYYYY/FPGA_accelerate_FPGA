from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed' and len(m['commands'])==3 and all(c['exit_code']==0 for c in m['commands'])
 for n,item in m['sources'].items():assert sha(out/'sources'/n)==item['sha256']
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 assert sha(out/'runner.py')==m['runner_sha256']
 base=ROOT/'results/candidate_commit_pilot_20261025';bm=json.loads((base/'manifest.json').read_text());assert m['sources']['cost_label_commit.sv']['sha256']==bm['sources']['commit/cost_label_commit.sv']['sha256']
 pack=lambda words:sum(w<<(32*i)for i,w in enumerate(words))
 initial=0;lb=pack([0x7fc12345,0,9,17,1]);up=pack([0x7fc12345,0x80000000,9,17,1]);final=pack([0x7fc12345,0x80000000,9,0x80000021,1])
 pairs=[(0,7,final,0),(1,0,initial,1),(1,1,lb,1),(1,3,up,1),(1,0,initial,1),(1,0,initial,1),(1,0,initial,1),(2,0,initial,1),(2,0,initial,1),(2,0,initial,1),(2,1,lb,1),(0,7,final,1)]
 expected=[(i+1,*p)for i,p in enumerate(pairs)];observed=[]
 log=(out/'simulate.log').read_text()
 for line in log.splitlines():
  t=line.split()
  if t and t[0]=='CASE':assert len(t)==6;observed.append(tuple(map(int,t[1:4]))+(int(t[4],16),int(t[5])))
 assert observed==expected and 'IDLEFAULT 13'in log and 'COST_LABEL_COMMIT_UNIT_PASS cases=13'in log and 'Fatal:'not in log and '$finish called'in log
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'cases':13,'response_records_independently_checked':12,'scope':'Same standalone commit RTL with mocked native replies: ordered/stalled ACKs, raw32 data, bad field/status/presence/prev, abort exposed/pending command drain, timeout, full version drift, late offered-response fault and idle spurious response. Not actual joined AXI fault/reload.'}
 (out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
