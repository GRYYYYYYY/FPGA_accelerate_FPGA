"""Prepare an isolated offer-priority interlock candidate; no production changes."""
from pathlib import Path
import datetime,difflib,json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from stage_static_cp_physical_common_v6 import BASE,sha,read

def main():
 out=R/'hardware/variants/publication_start_interlock_v1';report=R/'results/publication_start_interlock_preparation_20261104.json'
 assert not out.exists() and not report.exists()
 source=BASE/'stage_static_cp_synth_v1/sources/query_residency_system.sv'
 fm=read(BASE/'stage_static_cp_shadow_system_v7/manifest.json');sm=read(BASE/'stage_static_cp_synth_v1/manifest.json')
 assert sha(source)==sm['sources']['query_residency_system.sv']==fm['sources']['query_residency_system.sv']['sha256']
 old='.command_valid(ap_valid||cp_valid||qc_cp_valid)'
 new='.command_valid(jp_start||ap_valid||cp_valid||qc_cp_valid)'
 text=source.read_text();assert text.count(old)==1 and new not in text
 changed=text.replace(old,new);assert changed.replace(new,old)==text
 lease=BASE/'stage_static_cp_synth_v1/sources/checkpoint_lease_guard.sv';barrier=BASE/'stage_static_cp_synth_v1/sources/checkpoint_publish_barrier.sv'
 assert 'assign release_ready=!rst&&owned&&retired&&route_retired&&!command_busy&&!command_valid&&!test_reset;' in lease.read_text()
 assert 'assign start_ready=!rst&&state==IDLE&&lease_owned&&retired&&!stage_busy&&!fault&&prepared==0;' in barrier.read_text()
 out.mkdir();(out/'baseline').mkdir();(out/'candidate').mkdir()
 (out/'baseline/query_residency_system.sv').write_bytes(source.read_bytes())
 (out/'candidate/query_residency_system.sv').write_text(changed)
 (out/'candidate.patch').write_text(''.join(difflib.unified_diff(text.splitlines(True),changed.splitlines(True),fromfile='baseline/query_residency_system.sv',tofile='candidate/query_residency_system.sv')))
 evidence=[source,lease,barrier,R/'results/ka_publication_release_full_rtl_v5_counterexample_review_20261102.json',R/'results/ka_publication_release_contract_lineage_review_20261102.json']
 cases=[dict(case='same_cycle_start_release',expected='Eligible start accepted; release ready low and lease retained.'),
 dict(case='release_only',expected='Unchanged release acceptance when all original conditions permit.'),
 dict(case='held_start_valid_not_ready',expected='Release remains blocked even when start_ready=0. Potential liveness effect requires caller contract analysis.'),
 dict(case='held_release_valid',expected='No release during start or ownership; acceptance after transaction retires and start is withdrawn.'),
 dict(case='done_response_backpressure',expected='jp_owned prevents release until DONE response consumed.'),
 dict(case='cancel',expected='Retain lease through cancellation/discard and DONE response consumption.'),
 dict(case='release_on_done_consumption_edge',expected='Pre-edge jp_owned still prevents release; later cycle may accept.'),
 dict(case='release_after_done_consumption',expected='Release can proceed once publication is idle and no start/other blocking offers remain.'),
 dict(case='invalid_start_payload',expected='Existing rejection response retains lease until consumed; do not bypass original monitor.'),
 dict(case='unknown_start_control',expected='Four-state behavior requires explicit simulation and unknown-value assertions; no two-state inference accepted.')]
 record=dict(status='isolated_candidate_prepared_not_simulated',time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=sha(source),candidate_sha256=sha(out/'candidate/query_residency_system.sv'),
 exact_reversible_replacement=dict(before=old,after=new),evidence_sha256={str(p):sha(p) for p in evidence},tool_sha256=sha(__file__),
 arbitration='Raw publication start offer has priority over lease release; release_ready does not depend on start_ready.',
 reasoning='For known asserted jp_start, command_valid is true and release_ready is false. This local Boolean observation prevents concurrent acceptance at that guard; it does not establish integrated timing, liveness, four-state behavior or caller legality.',
 unresolved='Holding jp_start while it cannot be accepted also blocks release. Caller arbitration and forward progress remain to be established before selecting a repair.',
 planned_cases=cases,production_rtl_modified=False,rtl_simulation_run=False,synthesized=False,accepted_repair=False,
 prior_shadow_v7_applies_to_candidate=False,physical_v6_input_unchanged=True,
 scope='Candidate source only; preserve original counterexample and monitors. Full probe and directed protocol cases, then new synthesis/functional evidence are required for any production change.')
 with (out/'manifest.json').open('x') as f:f.write(json.dumps(record,indent=2,sort_keys=True)+'\n')
 with report.open('x') as f:f.write(json.dumps(record,indent=2,sort_keys=True)+'\n')
 assert sha(source)==record['source_sha256']
 print('ISOLATED_PUBLICATION_START_INTERLOCK_PREPARED_NOT_VALIDATED')
if __name__=='__main__':main()
