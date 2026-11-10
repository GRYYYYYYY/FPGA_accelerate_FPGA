"""Check exact source bindings and Boolean consequence of reviewed safety results."""
from pathlib import Path
import json,hashlib,itertools,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');S=B/'stage_static_cp_shadow_system_v6/sources'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
reports={
 'lease_temporal':R/'results/ka_lease_temporal_boundary_v1_review_20261101.json',
 'discard_phase':R/'results/ka_publication_discard_lease_unit_v1_review_20261101.json',
 'combinational':R/'results/ka_as_admin_combinational_formal_v1_review_20261031.json'}
assert j(reports['lease_temporal'])['status']=='actual_lease_temporal_boundary_overapproximation_inductively_proved_fault_control_restored'
assert j(reports['discard_phase'])['status']=='original_two_module_discard_nonzero_implies_lease_owned_inductively_proved_dependency_control_restored'
assert j(reports['combinational'])['status']=='actual_as_native_initial_publish_rearm_combinational_exclusion_proved_staging_overlap_assignment_restored'
query=(S/'query_residency_system.sv').read_text();barrier=(S/'checkpoint_publish_barrier.sv').read_text();coordinator=(S/'recovery_coordinator.sv').read_text()
for report in [j(reports['discard_phase']),j(reports['combinational'])]:
 for name in ['query_residency_system.sv','checkpoint_publish_barrier.sv']:
  hashes={h for f,h in report['file_sha256'].items() if f.endswith('/'+name)};assert hashes and hashes=={sha(S/name)}
manifest=j(B/'ka_as_lease_staging_boundary_formal_v1/manifest.json')
for name in ['query_residency_system.sv','checkpoint_publish_barrier.sv','recovery_coordinator.sv']:
 e=manifest['sources'][name];assert e['sha256']==sha(S/name)
pub=query.split('checkpoint_publish_barrier publication(',1)[1].split(';',1)[0];lease=next(l for l in query.splitlines() if 'checkpoint_lease_guard checkpoint_lease(' in l);authority=query.split('checkpoint_authority_rotator authority(',1)[1].split(';',1)[0]
for x in ['.clk(clk)','.rst(rst||k_cold_rst)','.lease_owned(pc_owned)','.discard_valid(jp_dv)']:assert x in pub
for x in ['.clk(clk)','.rst(rst||k_cold_rst)','.owned(pc_owned)']:assert x in lease
assert '||jp_owned||' in lease and '.discard_valid(jp_dv[0])' in authority
assert "assign discard_valid=(!rst&&state==CANCEL)?prepared:3'd0;" in barrier
assert 'assign a_valid=!cold_rst&&state==AS;' in coordinator
residency=(S/'residency_system.sv').read_text();coor=next(l for l in residency.splitlines() if ' recovery_ctl(' in l);assert '.cold_rst(k_cold_rst)' in coor and '.a_valid(k_a_valid)' in coor
for name in ['query_residency_system.sv','search_residency_system.sv']:assert '.k_a_valid(k_a_valid)' in (S/name).read_text()
# C=cold reset, G=global reset, A=AS-valid, L=lease, D=any discard, H=authority bit.
allowed=[]
for C,G,A,L,D,H in itertools.product([False,True],repeat=6):
 common=C or G
 if A and C:continue                       # original coordinator combinational reset gate
 if not C and A and L:continue             # reviewed temporal proof
 if common and D:continue                   # original publication discard reset gate
 if not common and D and not L:continue     # reviewed full two-module phase guarantee
 if H and not D:continue                    # actual bit-zero wiring
 assert not(A and H)
 allowed.append([int(v) for v in [C,G,A,L,D,H]])
cap=B/'ka_as_authority_admin_composition_evidence_v1';cap.mkdir();files={'reviewer.py':Path(__file__)}
for key,p in reports.items():files['reports/'+p.name]=p
for name in ['query_residency_system.sv','search_residency_system.sv','residency_system.sv','recovery_coordinator.sv','checkpoint_publish_barrier.sv','checkpoint_lease_guard.sv']:files['sources/'+name]=S/name
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,f in files.items():t.add(f,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,f in files.items():assert sha(f)==sha(cap/'restored'/n)
report={'status':'reviewed_component_safety_composition_as_excludes_authority_cfg_publish_discard_rearm','proof_report_sha256':{k:sha(p) for k,p in reports.items()},'checked_boolean_rows':allowed,'source_bindings':{'publication_instance':pub,'lease_instance':lease,'authority_instance':authority},'consequence':'After initial cold reset in current parameter-matched two-state RTL, AS-valid excludes authority cfg_valid, publish_valid, discard_valid and rearm_valid. Discard consequence checks both reset cases and exact vector bit wiring.','scope':'Compositional safety consequence of reviewed inductive/combination results and source wiring; not a new monolithic formal run, XZ/all-parameter proof, fixture full regression, or KA-ready proof. No publication-owned implies lease-owned premise used.','remaining':['Authority reader IDLE/codec busy/response retirement and drained persistence at each AS.','Compose payload/ready and KA coverage requirements without waiver.','Full initialized publication/release reproduction still waiting memory; caller protocol legality remains separate.'],'archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(f) for n,f in files.items()},'reviewer_sha256':sha(Path(__file__)),'full_system_functional_netlist_validated':False,'physical_gate_open':False};out=R/'results/ka_as_authority_admin_composition_20261101.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'archive_sha256':report['archive_sha256'],'files':len(files)}))
