from pathlib import Path
import json,hashlib,re,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=Path(sys.argv[1]);m=json.loads((p/'manifest.json').read_text());assert m['status']=='passed' and len(m['commands'])==3 and all(c['exit_code']==0 for c in m['commands'])
 for n,v in m['sources'].items():assert sha(p/'sources'/n)==v,n
 for n,v in m['artifacts'].items():assert sha(p/n)==v,n
 log=(p/'simulate.log').read_text();assert 'PARENT_UPSTREAM_BOUNDS_PASS checks=21 parent_reads=15 prev_writes=21 clears=1'in log and 'Fatal:'not in log and '$finish called'in log
 rows=[t.split()for t in log.splitlines()if t.startswith('CHECK ')];assert len(rows)==21
 expected_deltas=[1,0,1,1,1,1,1,1,1,1,1,1,1,0,1,1,0,0,0,1,0];expected_codes=[0]*16+[2,2,2,0,0]
 for i,t in enumerate(rows):assert int(t[1])==i+1 and int(t[2])==expected_codes[i] and int(t[3])==expected_deltas[i]
 r=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),checks=21,parent_reads=15,prev_writes=21,clears=1,scope='Actual post module and arithmetic, mocked native/geometry/frontier responders. Cold/hit, host-write lease gap, parent/context switches, self aliases, absent-record refill, EARLY, write error, timeout, abort and late drift response hold. Not AXI integrated error recovery proof.')
 (p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
