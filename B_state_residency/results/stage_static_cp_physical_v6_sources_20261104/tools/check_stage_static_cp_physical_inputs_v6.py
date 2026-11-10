"""Read-only gate for accepted v7 evidence and exact recovered synthesis."""
from pathlib import Path
from stage_static_cp_physical_common_v6 import ROOT,BASE,sha,read,identity,runtime_environment
TARGET=BASE/'stage_static_cp_synth_v1'
FULL=BASE/'stage_static_cp_shadow_system_v7'

def evidence():
 accepted=ROOT/'results/stage_static_cp_shadow_system_v7_20261103.json'
 assert sha(accepted)=='9c162f1a621b5e119316f9295da806e7827245c1f40cf94e4c353a5ec8ca6f2c'
 r=read(accepted);review=read(r['main_review'])
 assert r['status']=='full_capacity_fixture_ready_shadow_main_reviewed_frozen_actual_restored'
 assert r['full_system_functional_netlist_validated'] and review['full_system_functional_netlist_validated']
 assert sha(r['main_review'])==r['main_review_sha256']
 assert review['status']=='full_shadow_v7_actual_restore_main_reviewed'
 assert review['readonly_original_auditor_all_assertions_passed'] and review['deterministic_audit_identical']
 assert r['all_review_files_actual_restored_sha_identical'] and review['archive_original_restored_all_sha_identical']
 for key in ['terminal','review']:assert sha(r[key+'_archive'])==r[key+'_archive_sha256']
 freeze=Path(r['freeze_root']);assert sha(freeze/'manifest.json')==r['freeze_manifest_sha256']
 for n,e in read(freeze/'manifest.json')['files'].items():
  assert sha(freeze/n)==e['sha256']==sha(Path(r['review_actual_restore'])/n)
 terminal=ROOT/'results/stage_static_cp_shadow_v7_terminal_preservation_20261102.json';t=read(terminal)
 assert t['archive_sha256']==r['terminal_archive_sha256'] and t['all_restored_files_byte_identical']
 assert len(t['file_sha256'])==687
 for n,h in t['file_sha256'].items():assert sha(FULL/n)==h,n
 fm,fa=read(FULL/'manifest.json'),read(FULL/'source_bound_audit.json')
 assert r['audit']==review['audit']==fa and fa['manifest_sha256']==sha(FULL/'manifest.json')
 assert fm['stage']=='complete' and fm['status']=='observed' and not fm.get('active_process')
 assert identity(fm['runner_pid'])!=str(fm['runner_start_ticks'])
 assert fa['shadow_checks']==9323986 and fa['shadow_outputs']==346 and fa['unconditional_outputs']==342
 assert fa['qualified_outputs']==['cp_m_data','k_a_node','k_a_net','p_m_wdata'] and not fa['all_pin_strict_equivalence']
 assert fa['clock_lead_ps']==1 and fa['cp_export_words']==1560 and fa['cp_export_frames']==10
 assert fa['cp_protocol_counts']['transfers']==1560
 assert all(fa['cp_protocol_counts'][k]>0 for k in ['active','stalled','edges','idle'])
 assert set(fa['payload_group_counts'])=={'KA','PW'}
 for group,v in fa['payload_group_counts'].items():
  assert all(v[k]>0 for k in ['active','transfers','edges','idle'])
  assert (v['stalled']==0 if group=='KA' else v['stalled']>0)
 assert fa['fixture_ready_policy']=='KA valid requires known ready1 at sample/pre-edge; zero KA stalls, nonzero CP/PW stalls'
 assert fa['authority_transfers']['requests']==26 and fa['pager_write_transfers']['write_beats']==8223 and fa['pager_write_transfers']['addresses']==2831
 assert len(fa['exact_comparisons'])==27
 for n,e in fa['exact_comparisons'].items():assert sha(FULL/'full'/n)==e['sha256'] and (FULL/'full'/n).stat().st_size==e['bytes']
 assert sha(FULL/'full/shadow_cp_export.log')==fa['cp_transfer_log_sha256']
 for n,h in fa['payload_log_sha256'].items():assert sha(FULL/'full'/n)==h
 assert sha(ROOT/'scripts/check_shadow_payload_transfer_logs_v1.py')==fa['transfer_parser_sha256']
 m,a=read(TARGET/'manifest.json'),read(TARGET/'source_bound_audit.json')
 recovery=ROOT/'results/shadow_synthesis_new_host_recovery_review_20261102.json';rec=read(recovery)
 assert len(rec['recovered']['selected_files'])==192
 for n,h in rec['recovered']['selected_files'].items():assert sha(TARGET/n)==h,n
 assert read(ROOT/'results/stage_static_cp_synth_20261030.json')['audit']==a
 assert m['stage']=='complete' and m['exit_code']==0 and not m.get('active_process')
 assert not a['critical_warnings'] and not a['timing_loop_warnings']
 assert a['facts']['latches']==a['facts']['blackboxes']==a['check_timing_counts']['loops']==0
 assert m['parameters']==fm['parameters']==fa['parameters']==a['parameters']
 assert len(m['parameters'])==13 and m['parameters']['SLOTS']==32 and m['part']=='xcu280-fsvh2892-2L-e'
 assert len(m['rtl'])==len(set(m['rtl']))==133
 for n in m['rtl']:assert sha(TARGET/'sources'/n)==m['sources'][n]==fm['sources'][n]['sha256']==sha(FULL/'sources'/n)
 assert sha(TARGET/'synth.dcp')==a['artifact_sha256']['synth.dcp']
 assert sha(TARGET/'synth.v')==a['artifact_sha256']['synth.v']==fm['synthesis_netlist_sha256']
 assert (TARGET/'clock.xdc').read_text()=='create_clock -name core_clk -period 10.000 [get_ports clk]\n'
 runtime_environment()
 files=[accepted,Path(r['main_review']),freeze/'manifest.json',terminal,recovery,
 FULL/'manifest.json',FULL/'source_bound_audit.json',TARGET/'manifest.json',TARGET/'source_bound_audit.json',TARGET/'synth.dcp',TARGET/'clock.xdc',
 ROOT/'results/stage_static_cp_synth_20261030.json',ROOT/'results/physical_v6_runtime_recovery_20261104.json',ROOT/'results/udev_runtime_recovery_20261030.json',
 ROOT/'results/ka_publication_release_full_rtl_v5_counterexample_review_20261102.json',ROOT/'results/ka_publication_release_contract_lineage_review_20261102.json',
 ROOT/'hardware/scripts/implement_state_ooc.tcl',ROOT/'hardware/scripts/inspect_state_route_v1.tcl']
 return {str(p):sha(p) for p in files}
if __name__=='__main__':print('STATIC_STAGE_PHYSICAL_V6_INPUTS_ACCEPTED',len(evidence()))
