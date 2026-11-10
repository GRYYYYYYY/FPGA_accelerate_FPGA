"""Record a fresh, bounded running/terminal snapshot without changing job state."""
from pathlib import Path
import datetime,json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from stage_static_cp_physical_common_v6 import BASE,sha,read,identity,audit_memory,host_identity

def main():
 out=R/'results/stage_static_cp_physical_v6_continuation_20261104.json';assert not out.exists()
 p=BASE/'stage_static_cp_physical_v6';s=BASE/'stage_static_cp_physical_v6_supervision_v1'
 m,sm=read(p/'manifest.json'),read(s/'manifest.json');admission=audit_memory(m)
 tracked=[]
 for path,d in [(p/'manifest.json',m),(s/'manifest.json',sm)]:
  tracked.append(dict(manifest=str(path),manifest_sha256=sha(path),status=d['status'],stage=d['stage'],pid=d['runner_pid'],start_ticks=d['runner_start_ticks'],current_start_ticks=identity(d['runner_pid']),active_process=d.get('active_process')))
 paths=[R/'results/stage_static_cp_physical_v6_preparation_review_20261104.json',R/'results/stage_static_cp_physical_v6_launch_review_20261104.json',R/'results/physical_v6_runtime_recovery_20261104.json',R/'results/publication_start_interlock_preparation_20261104.json']
 record=dict(time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),**host_identity(),status='physical_v6_submitted_after_preparation_review',
 tracked_processes=tracked,tool_session_id=42582,memory_admission=admission,memory_sample_count=len(m['memory_samples']),
 full_system_functional_netlist_validated=True,physical_gate_open=m.get('physical_gate_open',False),timing_qualified=False,board_acceptance=False,
 controls_rerun=False,full_shadow_rerun=False,production_rtl_modified=False,interlock_candidate='prepared_not_simulated_or_accepted',
 evidence_sha256={str(x):sha(x) for x in paths},milestones=(p/'milestones.txt').read_text() if (p/'milestones.txt').exists() else '',
 queued_steps=['finish current implementation','independent routed DCP inspection','terminal artifact audit','persistent archive and actual restore','byte-identical restored reaudit','main review'],
 next_action='Observe existing supervisor/runner; do not duplicate or restart. New failure or completed stages require main interpretation. Start/release candidate remains separate and requires directed/full RTL evidence before repair acceptance.')
 with out.open('x') as f:f.write(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print(record['time_utc'],m['stage'],m.get('physical_gate_open'),record['milestones'])
if __name__=='__main__':main()
