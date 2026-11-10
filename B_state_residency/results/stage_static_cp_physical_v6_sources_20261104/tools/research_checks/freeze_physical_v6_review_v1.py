"""Freeze the completed physical main review and verify a real restored review pack."""
from pathlib import Path
import datetime,json,shutil,sys,tarfile
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from stage_static_cp_physical_common_v6 import BASE,OUTPUT,TOOLS,read,sha,identity

def main():
 mainreview=R/'results/stage_static_cp_physical_v6_main_review_20261104.json';r=read(mainreview)
 assert r['status']=='physical_v6_terminal_main_reviewed_artifacts_valid_timing_and_drc_not_met'
 assert r['physical_artifacts_validated'] and r['archive_original_restored_all_sha_identical'] and r['readonly_original_auditor_evidence_assertions_passed']
 assert not r['timing_qualified'] and not r['board_acceptance']
 p=OUTPUT;m=read(p/'manifest.json');a=read(p/'source_bound_audit.json');assert r['audit']==a
 assert identity(m['runner_pid'])!=str(m['runner_start_ticks']) and not m.get('active_process')
 for path,h in r['evidence_sha256'].items():assert sha(path)==h
 freeze=R/'results/stage_static_cp_physical_v6_sources_20261104';report=R/'results/stage_static_cp_physical_v6_20261104.json'
 archive=R/'results/recovery_archives_20261102/stage_static_cp_physical_v6_review_20261104.tar.gz';restore=BASE/'stage_static_cp_physical_v6_review_actual_restore_20261104'
 assert all(not x.exists() for x in [freeze,report,archive,restore]);freeze.mkdir();files={}
 def copy(source,relative):
  source=Path(source);dest=freeze/relative;assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
  files[str(relative)]=dict(source=str(source),sha256=sha(source));assert sha(dest)==files[str(relative)]['sha256']
 for n in m['rtl']:copy(p/'sources'/n,Path('sources')/n)
 for n in m['inputs']:
  if n.startswith('bound/') and not n.endswith('.dcp'):copy(p/n,Path(n))
 for n in m['artifact_sha256']:
  if not n.endswith('.dcp'):copy(p/n,Path('artifacts')/n)
 im=read(p/'inspection/manifest.json')
 for n in im['artifact_sha256']:copy(p/'inspection'/n,Path('inspection')/n)
 for n in ['manifest.json','preparation.json','source_bound_audit.json','run.tcl','inputs/clock.xdc','inspection/manifest.json']:
  copy(p/n,Path('records')/n)
 for n in TOOLS+['audit_state_ooc_physical_v2.py','audit_state_route_recovery_v2.py','parse_state_timing_paths.py','run_checkpoint_authority.py']:
  copy(R/'scripts'/n,Path('tools')/n)
 for n in ['review_physical_v6_terminal_v1.py','freeze_physical_v6_review_v1.py','restore_physical_cp_reference_v1.py','supervise_physical_v6_v1.py','review_physical_v6_launch_v1.py']:
  copy(R/'scripts/research_checks'/n,Path('tools/research_checks')/n)
 reports=[mainreview]+[Path(x) for x in r['evidence_sha256'] if '/results/' in x]
 reports+=[R/'results/stage_static_cp_physical_v6_terminal_mcp_sessions_20261104.json']
 for path in dict.fromkeys(reports):copy(path,Path('reports')/path.name)
 for n in ['implement_state_ooc.tcl','inspect_state_route_v1.tcl']:copy(R/'hardware/scripts'/n,Path('templates')/n)
 ref=BASE/'checkpoint_edit_route_recovery_reference_20261104'
 for n in ['source_bound_audit.json','timing_routed.rpt','drc_routed.rpt','utilization_routed.rpt','constraints_routed.xdc','route_status.rpt']:copy(ref/n,Path('reference')/n)
 fm=dict(status='frozen',files=files,main_review_sha256=sha(mainreview),physical_artifacts_validated=True,timing_qualified=False,board_acceptance=False)
 (freeze/'manifest.json').write_text(json.dumps(fm,indent=2,sort_keys=True)+'\n')
 allfiles={str(x.relative_to(freeze)):sha(x) for x in freeze.rglob('*') if x.is_file()}
 with tarfile.open(archive,'w:gz') as tf:
  for n in allfiles:tf.add(freeze/n,arcname=n,recursive=False)
 restore.mkdir();seen=set()
 with tarfile.open(archive) as tf:
  for item in tf:
   n=Path(item.name);assert item.isfile() and not n.is_absolute() and '..' not in n.parts and item.name in allfiles and item.name not in seen;seen.add(item.name)
   dest=restore/n;dest.parent.mkdir(parents=True,exist_ok=True)
   with tf.extractfile(item) as f,dest.open('xb') as w:shutil.copyfileobj(f,w,1<<20)
   assert sha(dest)==allfiles[item.name]==sha(freeze/n)
 assert seen==set(allfiles)
 record=dict(status='physical_v6_main_reviewed_frozen_actual_restored_timing_not_closed',time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 physical_artifacts_validated=True,full_system_functional_netlist_validated=True,physical_gate_open=True,timing_qualified=False,board_acceptance=False,full_behavior_matrix_complete=False,candidate_selected=False,
 audit=a,main_review=str(mainreview),main_review_sha256=sha(mainreview),freeze_root=str(freeze),freeze_manifest_sha256=sha(freeze/'manifest.json'),
 review_archive=str(archive),review_archive_sha256=sha(archive),review_actual_restore=str(restore),review_files=len(allfiles),all_review_files_actual_restored_sha_identical=True,
 terminal_archive=r['archive'],terminal_archive_sha256=r['archive_sha256'],terminal_files=r['files'],comparison=r['comparison'],drc=r['drc'],
 production_rtl_modified=False,controls_rerun=False,full_shadow_rerun=False,implementation_rerun=False,freezer_sha256=sha(__file__),
 retained_limitations=r['interpretation'],scope='Accept reproducible physical artifact provenance and measurements only. Complete routing does not imply setup/DRC closure, board acceptance, general functional equivalence or production repair. Original 10ns OOC constraints and unresolved start/release issue retained.')
 with report.open('x') as f:f.write(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print('PHYSICAL_V6_REVIEW_FROZEN_ACTUAL_RESTORED',len(allfiles),sha(archive))
if __name__=='__main__':main()
