"""New-host full shadow gate; original functional gates plus restored fixture-ready proof/control evidence."""
from pathlib import Path
import json
from shadow_recovered_evidence_v7 import ROOT,BASE,read,sha,identity,RECOVERED
from stage_static_cp_shadow_predecessor_v7b import evidence as parent_evidence,REFERENCE,SYNTH
TARGET=BASE/'stage_static_cp_shadow_system_v7'
VARIANT=ROOT/'hardware/variants/stage_static_cp_shadow_system_v7'
CANDIDATE=ROOT/'hardware/variants/stage_static_cp_shadow_fixture_ready_v2'
PARENT=ROOT/'hardware/variants/stage_static_cp_shadow_protocol_v5'
MARKER='FULL_SHADOW_FIXTURE_READY_CANDIDATE_PASS outputs=346 unconditional=342 qualified=cp_m_data,k_a_node,k_a_net,p_m_wdata'

def evidence():
 fm,proof=parent_evidence()
 def bind(p):p=Path(p);proof[str(p)]=sha(p);return read(p)
 # Reuse the actual restored/re-audited 58 cases, without launching any controls.
 p=ROOT/'results/shadow_fixture_ready_controls_v3_review_20261102.json';r=bind(p)
 assert r['status']=='actual58_fixture_ready_controls_audited_restored_and_reaudited' and r['positive_cases']==2 and r['expected_rejection_cases']==56
 assert r['reaudit_exit_code']==0 and r['restored_audit_byte_identical'] and r['all_restored_files_byte_identical']
 assert sha(r['archive'])==r['archive_sha256'];rest=Path(r['actual_restore'])
 for n,h in r['file_sha256'].items():assert sha(rest/n)==h
 assert len(r['audit']['outcomes'])==58
 cm=bind(CANDIDATE/'manifest.json')
 for n,h in cm['files'].items():assert sha(CANDIDATE/n)==h;proof[str(CANDIDATE/n)]=h
 assert r['audit']['checker_sha256']==sha(CANDIDATE/'shadow.sv')
 assert cm['proof_report_sha256']==sha(ROOT/'results/ka_as_ready_temporal_composition_review_20261101.json')
 s=(CANDIDATE/'shadow.sv').read_text()
 for patch in reversed(cm['patches']):assert s.count(patch['after'])==1;s=s.replace(patch['after'],patch['before'],1)
 assert s==(PARENT/'shadow.sv').read_text()
 assert (VARIANT/'shadow.sv').read_bytes()==(CANDIDATE/'shadow.sv').read_bytes()
 assert (VARIANT/'tb_query_fault.sv').read_bytes()==(PARENT/'tb_query_fault.sv').read_bytes()
 bind(VARIANT/'manifest.json');proof[str(VARIANT/'shadow.sv')]=sha(VARIANT/'shadow.sv');proof[str(VARIANT/'tb_query_fault.sv')]=sha(VARIANT/'tb_query_fault.sv')
 # Historical control failures stay failures; their indexed bytes support the logger history.
 hr=bind(ROOT/'results/shadow_control_predecessors_recovery_20261102.json');assert len(hr['recovered'])==7
 for name in hr['recovered']:
  ip=ROOT/'results/offer_archives_20261025'/(name+'.json');idx=bind(ip)
  assert sha(idx['archive'])==idx['archive_sha256']
  for n,h in idx['members'].items():assert sha(BASE/name/n)==h
 gate=bind(ROOT/'results/shadow_ka_dependency_gate_review_20261102.json')
 assert gate['status']=='restored_KA_dependencies_source_core_parameters_and_fixture_contracts_reviewed'
 assert gate['parameters']==fm['parameters'] and gate['production_sources']==133 and len(gate['readonly_original_audits'])==20
 for n,h in gate['bound_reports'].items():assert sha(ROOT/'results'/n)==h;proof[str(ROOT/'results'/n)]=h
 for n,h in gate['bound_evidence'].items():assert sha(n)==h;proof[n]=h
 rec=read(ROOT/'results/shadow_ka_dependency_actual_restore_20261102.json')
 for ar in rec['archives'].values():
  assert sha(ar['archive'])==ar['archive_sha256']
  for n,h in ar['file_sha256'].items():assert sha(Path(ar['actual_restore'])/n)==h
 core=bind(ROOT/'results/shadow_authority_core_copy_20261102.json');assert core['temporary_inspection_terminal_closed']
 for ar in core['archives']:
  assert sha(ar['archive'])==ar['archive_sha256']
  for n,h in ar['file_sha256'].items():assert sha(BASE/'shadow_authority_core_actual_restore_v1'/n)==h
 # Retain real failed full-v6 verdict. It is not promoted by this new policy.
 fail=bind(ROOT/'results/stage_static_cp_shadow_v6_failure_preservation_20261031.json')
 assert fail['status']=='failed_v6_scene_actual_restore_byte_identical_not_functional_acceptance' and not fail['full_system_functional_netlist_validated']
 for n in read(SYNTH/'manifest.json')['rtl']:assert sha(REFERENCE/'sources'/n)==fail['files']['stage_static_cp_shadow_system_v6']['sources/'+n]
 oldcheck=bind(ROOT/'results/old_host_original_jobs_controller_check_20261102.json')
 bind(ROOT/'results/ka_publication_release_full_rtl_v5_counterexample_review_20261102.json')
 for n in ['shadow_recovered_evidence_v7.py','stage_static_cp_shadow_predecessor_v7a.py','stage_static_cp_shadow_predecessor_v7b.py','stage_static_cp_shadow_common_v7.py','shadow_terminal_receipt_v1.py','check_shadow_payload_transfer_logs_v1.py']:
  proof[str(ROOT/'scripts'/n)]=sha(ROOT/'scripts'/n)
 return fm,proof
