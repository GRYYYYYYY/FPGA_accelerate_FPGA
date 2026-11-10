"""Review compositional two-state KA readiness argument; never grants netlist acceptance."""
from pathlib import Path
import json,hashlib,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');S=B/'stage_static_cp_shadow_system_v6/sources'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
names=['ka_as_ready_history_composition_receipt_review_20261101.json','ka_as_history_handshake_bindings_review_20261101.json','ka_as_history_phase_exclusion_review_20261101.json','ka_as_history_phase_exclusion_source_binding_supplement_20261101.json','ka_as_quiet_memory_environment_review_20261101.json','ka_as_configured_contract_bindings_review_20261101.json','ka_as_quiet_ready_output_binding_review_20261101.json','ka_as_component_parameters_review_20261101.json']
reports=[R/'results'/n for n in names]
for p in reports:
 d=j(p);assert d['full_system_functional_netlist_validated'] is False and d['physical_gate_open'] is False
h=B/'ka_as_ready_history_composition_formal_v1/harness.sv';text=h.read_text();assert text.count('assume(')==5 and text.count('assert(')==6
assert 'if(a_valid) assert(f_authority_quiet);' in text and 'if(a_valid) assert(a_ready);' in text
m=j(h.parent/'manifest.json');assert m['status']=='observed';assert sha(h)==m['harness_sha256']
for entry in m['commands']:
 log=h.parent/(entry['stage']+'.log');assert sha(log)==entry['log_sha256'] and entry['exit_code']==0
 if entry['stage']!='prepare':assert 'Status: PASSED' in log.read_text()
c=(S/'recovery_coordinator.sv').read_text();assert 'state<=NORMAL;configured<=0;' in c
assert 'DRAIN:if(backend_drained&&normal_retired)begin if(stopped||fail_now)state<=FAILWAIT;else begin reset_ticks<=0;state<=RESET;end end' in c
assert 'AS:if(a_ready)state<=AW;' in c
assert 'AW:if(a_rsp_valid)begin' in c and 'else begin wanted_refs<=a_refs;wanted_occ<=a_occupancy;o_op<=0;state<=OS;end' in c
# The only direct AS assignments are RECONFIG and NEXT paths, all explicitly reviewed.
assert c.count('state<=AS;')==4
assert 'else if(journal_count==0)state<=LABELS;else begin index<=0;verify_pass<=0;state<=AS;end' in c
assert 'else if(index+1<journal_count)begin index<=index+1;state<=AS;end' in c
assert 'repair_retry<=1;deferred_capacity<=0;index<=0;state<=AS;' in c
assert 'verify_pass<=1;index<=0;state<=AS;' in c
cap=B/'ka_as_ready_temporal_composition_evidence_v1';cap.mkdir();files={'reviewer.py':Path(__file__),'history_harness.sv':h,'coordinator_source.sv':S/'recovery_coordinator.sv','history_manifest.json':h.parent/'manifest.json'}
for p in reports:files['reviews/'+p.name]=p
for stage in ['prepare','bmc','induction','cover']:files['logs/'+stage+'.log']=h.parent/(stage+'.log')
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,p in files.items():t.add(p,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,p in files.items():assert sha(p)==sha(cap/'restored'/n)
d={'status':'current_fixture_two_state_RTL_KA_ready_compositional_safety_argument_reviewed','theorem':'For initialized, current-parameter RTL control traces compatible with the reviewed legal single-beat read-only fixture memory, coordinator k_a_valid implies k_a_ready at sampled non-cold-reset cycles.','method':'Compositional inference from independently checked component induction/combinational results plus exact source clock/reset, phase, parameter and handshake bindings; not a new monolithic formal run.','temporal_argument':['Initial cold reset puts coordinator in NORMAL, so AS assertion is vacuous before recovery.','Successful DRAIN establishes authority quiet from actual drained/retired/abort aggregation.','Phases1..9 have no admin/AP offer; with quiet, AP-owned is absent and authority request is absent outside AS. Independent quiet/no-fault persistence preserves Q until first AS.','In AS, independently established configured/admin/AP exclusions and Q satisfy the unconditional combinational sufficient-ready lemma, yielding ready without assuming AS=>ready as an input contract.','AS may consume the request and become AW, where Q is not asserted. A successful AW response is the exact authority response handshake; local retirement re-establishes Q on entry to OS.','OS/OW/NEXT preserve Q with no authority request, including correction/deferred/retry paths to subsequent AS. Failures cannot jump directly to AS; new attempts return through DRAIN.','The checked conditional history induction establishes these state invariants; its four assumptions are supplied by the independent binding and component reviews, including configured qualification.'],'noncircularity':'Q history relies on DRAIN/response retirement and request/admin exclusion, configured relies on metadata/retirement/persistence; neither is derived from KA readiness. Only the final sufficient-ready implication uses Q/configured.','limitations':['Two-state RTL/control theorem at current parameters and legal fixture memory, not arbitrary AXI, all parameters, four-state gate equivalence, timing or board behavior.','The existing full shadow v6 remains failed for missing KA stalled coverage. This report does not waive or alter that checker, accept that run, or open physical gates.','Any future verification policy or new full shadow version needs separate reviewed controls and explicit provenance; do not edit bound failed versions.'],'dependency_report_sha256':{p.name:sha(p) for p in reports},'archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(p) for n,p in files.items()},'full_system_functional_netlist_validated':False,'physical_gate_open':False}
out=R/'results/ka_as_ready_temporal_composition_review_20261101.json';assert not out.exists();out.write_text(json.dumps(d,indent=2)+'\n');print(d['status'],d['archive_sha256'])
