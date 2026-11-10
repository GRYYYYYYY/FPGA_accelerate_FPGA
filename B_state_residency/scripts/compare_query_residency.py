"""Compare equal-work natural RTL traces; no extrapolated speedup."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];BASE=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 baseline=BASE/'natural_query_rtl_v1';resident=BASE/'natural_query_resident_v2';bounds=BASE/'connection_resident_bounds_v1'
 gates={}
 for p in [baseline,resident,bounds]:
  a=json.loads((p/'source_bound_audit.json').read_text());assert a['status']=='passed'and a['manifest_sha256']==sha(p/'manifest.json');gates[p.name]=sha(p/'source_bound_audit.json')
 b=json.loads((baseline/'source_bound_audit.json').read_text());r=json.loads((resident/'source_bound_audit.json').read_text());comparison={}
 for case in ['full','pressure']:
  names=['natural_trace.txt','design.bin','labels.bin','owners.bin','cost.bin','graph_axi.txt','design_axi.txt','label_axi.txt','owner_axi.txt','cost_axi.txt','table_axi.txt']
  same={name:sha(resident/case/name)for name in names}
  for name,v in same.items():assert v==sha(baseline/case/name),(case,name)
  assert (resident/case/'qstate_axi.txt').read_text().splitlines()==(baseline/case/'qstate_axi.txt').read_text().splitlines()[:2]
  bc=b['counts'][case];rc=r['counts'][case];assert bc['State_R']==72 and rc['State_R']==1 and bc['cycles']==rc['cycles']
  P=[l.split()for l in(resident/case/'natural_trace.txt').read_text().splitlines()if l.startswith('P ')];window=int(P[-1][1])-int(P[0][1])
  comparison[case]=dict(baseline_state_reads=72,resident_state_reads=1,saved_read_beats=71,saved_read_bytes=71*64,baseline_cycles=bc['cycles'],resident_cycles=rc['cycles'],first_to_target_poll_cycles=window,byte_identical_nonstate_artifacts=same)
 result=dict(status='passed',auditor_sha256=sha(Path(__file__)),audits=gates,comparison=comparison,scope='Same natural query, same TB, full non-State byte and cycle trace equality. 71 64B reads removed, no measured search or total simulation latency improvement. No board claim.')
 (ROOT/'results/query_residency_20261025.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
