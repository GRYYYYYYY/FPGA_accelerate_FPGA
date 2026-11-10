"""Preserve the actual stale-fault retry counterexample, not a passing recovery."""
from pathlib import Path
import sys,json
from run_checkpoint_authority import sha

def main():
 p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='failed'
 for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256']
 d=p/'warm_q2_codec_v1';log=(d/'simulate.log').read_text();assert 'Fatal: owner recovery result 6/0 corrected=0/3 journal=3/0'in log
 rows=[t.split()for t in(d/'events.txt').read_text().splitlines()];assert [list(map(int,t[2:]))for t in rows if t[0]=='KD']==[[0,6,0,3]]
 assert len([t for t in rows if t[0]=='SOFT'])==len([t for t in rows if t[0]=='RESET'])==1
 rtl=(p/'sources/checkpoint_authority_reader.sv').read_text();assert 'assign fault=!rst&&(stopped||c_fault);'in rtl and 'stopped<=0;configured<=0;cfg_status<=0;cfg_rearmed<=1;'not in rtl
 a={'status':'passed','experiment_status':'failed_expected_counterexample','manifest_sha256':sha(p/'manifest.json'),'source_hashes':{n:sha(p/'sources'/n)for n in m['sources']},'counterexample':'First real snapshot SLVERR retained journal=3; explicit safe rearm still returns status6 before second target reset because stale authority fault poisons coordinator DRAIN. No successful recovery claim.','evidence':{n:sha(d/n)for n in ['events.txt','simulate.log','snapshot_axi.txt','live_axi.txt']},'auditor_sha256':sha(Path(__file__))}
 (p/'source_bound_audit.json').write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a))
if __name__=='__main__':main()
