from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 inp=ROOT/'results/postprev_inputs_v7_20261025';run=ROOT/'results/postprev_full_sll_v7_20261025'
 ip=inp/'source_bound_audit.json';rp=run/'source_bound_audit.json';a=json.loads(ip.read_text());b=json.loads(rp.read_text())
 for p,g in [(inp,a),(run,b)]:assert g['status']=='passed'and g['manifest_sha256']==sha(p/'manifest.json')
 assert a['post_prefixes']==713 and a['sll']==a['causal_y_flip_from_minus_one']==12 and a['explicit_geometry_patches']==4
 assert b['trace_auditor_sha256']==sha(ROOT/'scripts/audit_postprev_trace.py') and b['identical_prior_rtl_modules']==62
 for case in ['full','pressure']:
  c=b['counts'][case];assert (c['expansions'],c['decisions'],c['early'],c['ordered_prefixes'],c['nonempty_clear_before_prev'],c['fresh_SLL_label_reads'],c['actual_center_calls'])==(1216,3063,66,713,66,12,713)
  assert c['seed_offers']==198 and c['external_internal_control_handshakes']==8 and c['all_label_backing_bytes_checked']==3145728
 old=ROOT/'results/candidate_occupied_revision_20261025.json';assert json.loads(old.read_text())['status']=='passed'
 result={'status':'passed','auditor_sha256':sha(Path(__file__)),'gates':{str(p):sha(p)for p in[ip,rp,old]},'scope':'Ordered prefix with actual Frontier/HLS, native label pager, coordinates and center helper. Four explicit geometry patches plus hasLaguna=1 stress; not natural SLL geometry.',
 'coverage_separation':'Current allowed candidates have occupancy0/refs0/index0. Previous occupied-state gate remains separate; no combined nonzero-price plus new post-prev claim.',
 'not_verified':['All23 cost words and total arithmetic binding','lb/upstream/visited commit and child OFFER','Immediate recursive lookahead and full search/traceback/owner commit','New joined fault/drain/reset/reload/default directory/synthesis/platform/board']}
 Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
