from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 inp=ROOT/'results/candidate_occupied_inputs_v2_20261025';run=ROOT/'results/candidate_occupied_full_20261025'
 ia=inp/'source_bound_audit.json';ra=run/'source_bound_audit.json';a=json.loads(ia.read_text());b=json.loads(ra.read_text())
 for d,g in [(inp,a),(run,b)]:assert g['status']=='passed' and g['manifest_sha256']==sha(d/'manifest.json')
 assert b['identical_prior_rtl_modules']==64 and a['edited_nodes']==8 and a['overflow_records']==54
 for case in ['full','pressure']:
  c=b['counts'][case];assert (c['expansions'],c['decisions'],c['early'],c['prefetch_calls'],c['prefetch_occupied'],c['prefetch_same_net'])==(1212,3022,60,785,12,6)
  assert c['price_indices']==[0,1,2,3,4,5,15,16,31,32]
 gate=ROOT/'results/cost_inputs_prefetch_boundaries_v2_20261025/source_bound_audit.json';g=json.loads(gate.read_text());assert g['status']=='passed'
 m=json.loads((run/'manifest.json').read_text());assert m['sources']['priced/cost_inputs_prefetch.sv']['sha256']==g['controller_sha256']
 result={'status':'passed','auditor_sha256':sha(Path(__file__)),'gates':{str(p):sha(p)for p in [ia,ra,gate]},'scope':'Actual candidate-triggered nonzero owner/history/price/net AXI reads on real graph with scripted occupancies and fresh unchanged original CPU oracle; same64 RTL/model modules.', 'not_verified':['Naturally observed route congestion updates','Host SET during this experiment','Post-prev geometry and complete cost23 production','Frontier/label commit/full route and board']}
 Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
