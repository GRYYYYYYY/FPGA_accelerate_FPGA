"""Prepare an isolated proof-specific observer; no execution or acceptance."""
from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from run_shadow_payload_contract_controls_v1 import harness,CASES
B=Path('/tmp/B_state_residency_offer_20261025');parent=R/'hardware/variants/stage_static_cp_shadow_protocol_v5';target=R/'hardware/variants/stage_static_cp_shadow_fixture_ready_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
proof=R/'results/ka_as_ready_temporal_composition_review_20261101.json';d=json.loads(proof.read_text());assert d['status']=='current_fixture_two_state_RTL_KA_ready_compositional_safety_argument_reviewed';assert d['physical_gate_open'] is False
src=(parent/'shadow.sv').read_text();assert sha(parent/'shadow.sv')==json.loads((parent/'manifest.json').read_text())['files']['shadow.sv']
old='if(ka_active_checks==0||ka_stall_checks==0||ka_transfer_checks==0||ka_edge_checks==0||ka_idle_observations==0)'
new='if(ka_active_checks==0||ka_stall_checks!=0||ka_transfer_checks==0||ka_edge_checks==0||ka_idle_observations==0)'
needle='  if(actual_k_a_cookie!==expected_k_a_cookie||actual_k_a_checkpoint!==expected_k_a_checkpoint||actual_k_a_design!==expected_k_a_design)$fatal(1,"KA_META_MISMATCH phase=%0d time=%0t",at_edge,$time);'
extra='\n  if(actual_k_a_ready!==1\'b1||expected_k_a_ready!==1\'b1)$fatal(1,"KA_FIXTURE_READY_INVARIANT phase=%0d time=%0t",at_edge,$time);'
patches=[(old,new),(needle,needle+extra),('FULL_SHADOW_PROTOCOL_PASS outputs=346','FULL_SHADOW_FIXTURE_READY_CANDIDATE_PASS outputs=346')]
result=src
for a,b in patches:assert result.count(a)==1;result=result.replace(a,b,1)
reverse=result
for a,b in reversed(patches):assert reverse.count(b)==1;reverse=reverse.replace(b,a,1)
assert reverse==src
# Preserve every comparison and all CP/PW tasks byte-for-byte; added check is KA-only.
for task in ['check_cp_output','check_pw_output']:
 def body(s):return s.split('task '+task+';',1)[1].split('end endtask',1)[0]
 assert body(result)==body(src)
assert not target.exists();target.mkdir();(target/'shadow.sv').write_text(result)
# Generate bounded fake controls with KA ready1 by default; explicit faults remain selectable.
ports=json.loads((R/'results/stage_static_cp_port_schema_20261030.json').read_text())['ports'];control=harness(ports)
a="`else\nwire ka_ready=cp_m_ready;\n`endif";b="`elsif KA_UNEXPECTED_STALL\nwire ka_ready=cp_m_ready;\n`else\nwire ka_ready=1'b1;\n`endif"
assert control.count(a)==2;control=control.replace(a,b);(target/'control.sv').write_text(control)
cases=[]
for name,define,expected in CASES:
 if name=='ka_stall_flip':continue # Dedicated generic59 suite retains stalled payload fault coverage.
 if name=='ka_no_stalls':continue # Same behavior as new matching baseline.
 if name=='ka_no_transfers':expected='KA_FIXTURE_READY_INVARIANT'
 if name in ['matching','ready_nba']:expected='FULL_SHADOW_FIXTURE_READY_CANDIDATE_PASS'
 cases.append({'name':name,'define':define,'expected':expected})
cases.append({'name':'ka_unexpected_stall','define':'KA_UNEXPECTED_STALL','expected':'KA_FIXTURE_READY_INVARIANT'})
(target/'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
manifest={'status':'prepared_candidate_not_compiled_or_validated','parent_shadow_sha256':sha(parent/'shadow.sv'),'proof_report_sha256':sha(proof),'patches':[{'before':a,'after':b} for a,b in patches],'inverse_exact':True,'cp_pw_tasks_unchanged':True,'cases':len(cases),'policy':'Only current initialized source/parameter-matched legal fixture. Assert known ready1 on every valid KA observation, including pre-edge; require active/transfer/edge/idle coverage and zero stalls. Keep all original knownness/data/metadata/unconditional comparisons and CP/PW stall requirements.','scope':'Fake controls prepared only. No full shadow runner may consume this until actual independent controls/restore/review and exact full-netlist source bindings pass. Two-state theorem does not replace four-state comparisons.','not_reused':'New candidate pass marker deliberately differs from every old full-pass marker; old auditors must not accept it.','files':{n:sha(target/n) for n in ['shadow.sv','control.sv','cases.json']},'preparer_sha256':sha(Path(__file__)),'full_system_functional_netlist_validated':False,'physical_gate_open':False}
(target/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');out=R/'results/shadow_fixture_ready_observer_preparation_20261101.json';assert not out.exists();out.write_text(json.dumps(manifest,indent=2)+'\n');print('Prepared',len(cases),'controls; inverse exact; not executed')
