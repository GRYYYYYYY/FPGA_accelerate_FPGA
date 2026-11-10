"""Source-bound Boolean composition of phase-wide administrative exclusion."""
from pathlib import Path
import json,hashlib,itertools,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');S=B/'stage_static_cp_shadow_system_v6/sources'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
reports=[R/'results'/n for n in ['ka_lease_temporal_boundary_v1_review_20261101.json','ka_publication_discard_lease_unit_v1_review_20261101.json','ka_ap_ownership_busy_formal_v1_review_20261031.json','ka_as_no_ap_owned_formal_v1_review_20261031.json']]
for p in reports:
 d=j(p)
 for name,h in d['file_sha256'].items():
  if name.startswith('repo/'):
   f=R/name[5:]
  else:f=B/name
  # Archives use some explicitly named bound files; originals are separately source-bound below.
  if f.exists():assert sha(f)==h,(p,name)
q=(S/'query_residency_system.sv').read_text();r=(S/'residency_system.sv').read_text();c=(S/'recovery_coordinator.sv').read_text();b=(S/'checkpoint_publish_barrier.sv').read_text()
checks={
'query_residency_system.sv':['wire ap_offer=ap_allow&&ap_valid;','assign k_a_ready=!ap_offer&&!ap_owned&&ap_native_ready;','.req_valid(!ap_owned&&(k_a_valid||ap_offer))','.stage_busy(as_busy||as_cfg_lease||k_busy||(|jp_reply))','.lease_owned(pc_owned)','.publish_valid(jp_pv[0])','.discard_valid(jp_dv[0])','.rearm_valid(as_attempt_reset)', '.cfg_valid((!boot_pending||boot_admin_allowed)&&as_cfg_valid&&(as_initial_safe||(jp_prepare&&jp_authority_stage)))'],
'residency_system.sv':['assign as_attempt_reset=k_attempt_reset;','.attempt_reset(k_attempt_reset)'],
'recovery_coordinator.sv':['assign busy=!cold_rst&&(owned||state!=NORMAL||rsp_valid);','assign attempt_reset=!cold_rst&&state==REARM&&retry_safe&&!a_rsp_valid&&!o_rsp_valid;','assign a_valid=!cold_rst&&state==AS;'],
'checkpoint_publish_barrier.sv':['assign prepare_allowed=!rst&&state==OPEN&&lease_owned&&!fault&&!commit_valid&&!cancel_valid;','assign commit_ready=!rst&&state==OPEN&&lease_owned&&retired&&!stage_busy&&!fault&&manifest_ready&&(&prepared)&&(&publish_ready)&&!cancel_valid;','assign publish_valid={3{commit_valid&&commit_ready&&stage_ok&&base_ok}};']}
for n,lines in checks.items():
 for line in lines:assert line in (S/n).read_text(),line
assert '!k_busy' in next(l for l in q.splitlines() if l.startswith('wire as_initial_safe='))
assert '!k_busy' in next(l for l in q.splitlines() if l.startswith('wire ap_allow='))
assert 'NORMAL=0' in c and 'REARM=12' in c and 'AS=4' in c
# Check exact proof assertions used as premises, not merely report status strings.
lease=(B/'ka_as_lease_staging_boundary_formal_v1/harness.sv').read_text()
assert 'if(f_lease_owned) begin' in lease and 'assert(f_coordinator_state==0);' in lease
ap=(B/'ka_as_no_ap_owned_formal_v1/harness.sv').read_text()
assert 'if(f_coordinator_state>=2 && f_coordinator_state<=9) assert(!f_ap_owned);' in ap
ownership=(B/'ka_ap_ownership_busy_formal_v1/harness.sv').read_text()
assert 'assert(as_busy)' in ownership
counts={str(s):0 for s in range(1,10)}
for state in range(1,10):
 for owned,authority_busy,quiet,raw_ap,raw_cfg,raw_prepare,raw_publish,raw_discard in itertools.product([False,True],repeat=8):
  # Independently proved initialized invariants: lease=>NORMAL, AP-owned=>busy,
  # and phases2..9=>!AP-owned. DRAIN only needs AP absence when quiet.
  lease_owned=False;k_busy=True
  if owned and not authority_busy:continue
  if state>=2 and owned:continue
  if quiet and authority_busy:continue
  initial_safe=False
  prepare=raw_prepare and lease_owned
  cfg=raw_cfg and (initial_safe or prepare)
  stage_busy=authority_busy or k_busy
  publish=raw_publish and lease_owned and not stage_busy
  discard=raw_discard and lease_owned  # independently proved nonzero discard=>lease
  rearm=(state==12)
  offer=raw_ap and not k_busy
  assert not(cfg or publish or discard or rearm or offer)
  if quiet:assert not owned
  a_valid=(state==4)
  req_valid=not owned and (a_valid or offer)
  if quiet:assert req_valid==a_valid
  counts[str(state)]+=1
cap=B/'ka_as_history_phase_exclusion_evidence_v1';cap.mkdir();files={'reviewer.py':Path(__file__)}
for n in checks:files['sources/'+n]=S/n
for p in reports:files['reports/'+p.name]=p
for p in [B/'ka_as_lease_staging_boundary_formal_v1/harness.sv',B/'ka_as_no_ap_owned_formal_v1/harness.sv',B/'ka_ap_ownership_busy_formal_v1/harness.sv']:files['harnesses/'+p.parent.name+'.sv']=p
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,p in files.items():t.add(p,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,p in files.items():assert sha(p)==sha(cap/'restored'/n)
out=R/'results/ka_as_history_phase_exclusion_review_20261101.json';assert not out.exists()
d={'status':'phase_1_through_9_administrative_and_quiet_request_exclusion_boolean_composition_reviewed','checked_rows_by_state':counts,'findings':['All phases1..9 exclude authority cfg/publish/discard/rearm and AP offer, by reviewed lease temporal and discard phase contracts plus exact source gates.','In DRAIN, quiet implies AP-owned absent through separately proved AP-owned=>authority busy. Phases2..9 independently exclude AP-owned.','During quiet phases1..9 authority req_valid equals coordinator a_valid, meeting the no-request premise outside AS.'],'limits':['This is a two-state compositional source review, not a new monolithic formal run.','Final all-contract integration, configured qualification, memory/reset compatibility and quiet-to-ready binding remain pending.','No change to failed shadow v6 or its stalled coverage gate.'],'dependency_report_sha256':{p.name:sha(p) for p in reports},'file_sha256':{n:sha(p) for n,p in files.items()},'archive_sha256':sha(cap/'evidence.tar'),'source_contract_integration_reviewed':False,'full_system_functional_netlist_validated':False,'physical_gate_open':False}
out.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'status':d['status'],'archive_sha256':d['archive_sha256']}))
