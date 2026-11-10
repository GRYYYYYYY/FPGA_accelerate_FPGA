from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=Path(sys.argv[1]);m=json.loads((p/'manifest.json').read_text());assert m['status']=='passed' and all(c['exit_code']==0 for c in m['commands'])
 for n,v in m['sources'].items():assert sha(p/'sources'/n)==v['sha256']
 for n,v in m['artifacts'].items():assert sha(p/n)==v
 s=(p/'simulate.log').read_text();assert 'CONNECTION_RESIDENT_PASS successes=195 errors=11 AR=199'in s and 'Fatal:'not in s and '$finish called'in s
 data=(ROOT/'results/connection_state_inputs_20261025/connections.bin').read_bytes();assert hashlib.sha256(data).hexdigest()==m['input_sha256']
 rows=[l.split()for l in s.splitlines()if l.startswith('ROW ')];assert len(rows)==195
 for _,i,v in rows:assert int(v,16).to_bytes(64,'little')==data[int(i)*64:(int(i)+1)*64]
 r=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),successes=195,errors=11,AR=199,scope='Original 182 real-row/fault/drain regression plus cache hits, lock gaps, reopen, full-version/price/query changes, wrong net/sink/cross, profile reset, full-design rejection and late drift held response. No synthesis/board claim.')
 (p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
