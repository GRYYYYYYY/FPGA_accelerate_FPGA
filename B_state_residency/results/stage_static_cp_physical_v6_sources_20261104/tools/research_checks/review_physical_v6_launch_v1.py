"""Main launch review: immutable preparation, no competing owners, exact commands."""
from pathlib import Path
import ast,datetime,json,os,shutil,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from stage_static_cp_physical_common_v6 import OUTPUT,BASE,REVIEW,read,sha,identity,host_identity,require_review,runtime_environment

def main():
 out=R/'results/stage_static_cp_physical_v6_launch_review_20261104.json';assert not out.exists()
 review=require_review(OUTPUT);m=read(OUTPUT/'manifest.json');assert sha(OUTPUT/'manifest.json')==review['prepared_manifest_sha256']
 assert m['status']=='prepared' and not m.get('active_process')
 for path,h in m['external_evidence_sha256'].items():assert sha(path)==h
 for n,h in m['inputs'].items():assert sha(OUTPUT/n)==h
 supervisor=R/'scripts/research_checks/supervise_physical_v6_v1.py';text=supervisor.read_text();ast.parse(text)
 commands=['run_stage_static_cp_physical_v6.py','inspect_stage_static_cp_physical_v6.py','audit_stage_static_cp_physical_v6.py']
 assert all(x in text for x in commands)
 assert "code=run('independent_inspection'" in text and "code=run('terminal_audit'" in text and "run('restored_reaudit'" in text
 assert 'child.wait()' in text and 'while True' not in text and 'kill(' not in text and 'terminate(' not in text
 assert "if code==0:" in text and "if passed:" in text
 assert "assert not S.exists()" in text and "require_review(P)" in text
 # Record live ownership; ignore only this command and its actual ancestors.
 ignored=set();pid=os.getpid()
 while pid>0 and pid not in ignored:
  ignored.add(pid)
  try:pid=int(Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()[1])
  except FileNotFoundError:break
 matched=[]
 for proc in Path('/proc').iterdir():
  if not proc.name.isdigit() or int(proc.name) in ignored:continue
  try:cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
  except (FileNotFoundError,PermissionError,ProcessLookupError):continue
  if any(x in cmd for x in [str(BASE),'run_stage_static_cp','supervise_physical_v6']):matched.append(dict(pid=int(proc.name),start_ticks=identity(proc.name),command=cmd))
 assert not matched,matched
 for name in ['stage_static_cp_shadow_system_v7','stage_static_cp_shadow_system_v7_supervision_v1','shadow_fixture_ready_controls_v3','ka_publication_release_full_rtl_v5']:
  old=read(BASE/name/'manifest.json');assert not old.get('active_process') and identity(old['runner_pid'])!=str(old['runner_start_ticks'])
 _,runtime=runtime_environment();assert runtime==review['runtime']
 c=Path('/sys/fs/cgroup');current=int((c/'memory.current').read_text());limit=int((c/'memory.max').read_text())
 assert shutil.disk_usage(BASE).free>20*(1<<30) and shutil.disk_usage(R).free>10*(1<<30)
 freeze=R/'results/stage_static_cp_physical_v6_launch_tools_20261104';assert not freeze.exists();freeze.mkdir()
 for path in [supervisor,Path(__file__)]:shutil.copyfile(path,freeze/path.name)
 record=dict(status='ready_for_single_authorized_attempt',time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),**host_identity(),
 preparation_review_sha256=sha(REVIEW),supervisor_sha256=sha(supervisor),reviewer_sha256=sha(__file__),runtime=runtime,
 mcp_receipt_sha256=sha(R/'results/stage_static_cp_physical_v6_mcp_sessions_20261104.json'),matched_processes=matched,
 memory_snapshot=dict(current_bytes=current,limit_bytes=limit),memory_admission_not_yet_performed=True,
 execution='Existing local batch flow retains real child wait/exit ownership; MCP session discovery empty.',
 physical_gate_open=False,full_system_functional_netlist_validated=True,timing_qualified=False,board_acceptance=False,
 retained_open_issue='start/release counterexample and caller arbitration unchanged; isolated repair requires new evidence',
 scope='One authorized attempt only after runner performs continuous 60s dual admission. Separate inspector and immutable parser audit, persistent archive, actual restore and reaudit. No automatic retry.')
 with out.open('x') as f:f.write(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print('PHYSICAL_V6_LAUNCH_REVIEWED',current,limit)
if __name__=='__main__':main()
