"""Single owner for authorized physical v6 run, terminal audit and durable actual restore.
No automatic retry or production mutation; final scientific acceptance requires main review.
"""
from pathlib import Path
import sys,json,subprocess,os,time,socket,tarfile,shutil,datetime
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from stage_static_cp_physical_common_v6 import sha,read,identity,require_review
B=Path('/tmp/B_state_residency_recovery_20261102');P=B/'stage_static_cp_physical_v6';S=B/'stage_static_cp_physical_v6_supervision_v1'
def main():
 require_review(P)
 launch=read(R/'results/stage_static_cp_physical_v6_launch_review_20261104.json')
 assert launch['supervisor_sha256']==sha(Path(__file__)) and launch['status']=='ready_for_single_authorized_attempt'
 assert not S.exists() and read(P/'manifest.json')['status']=='prepared';S.mkdir()
 m=dict(status='running',stage='launch',hostname=socket.gethostname(),boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),runner_pid=os.getpid(),runner_start_ticks=identity(os.getpid()),tool_sha256=sha(Path(__file__)),commands=[],full_system_functional_netlist_validated=True,physical_gate_open=False)
 def save():
  q=S/'manifest.pending.json';q.write_text(json.dumps(m,indent=2)+'\n');q.replace(S/'manifest.json')
 def run(stage,argv):
  m['stage']=stage;begin=time.monotonic();save()
  with (S/(stage+'.log')).open('x') as out:
   child=subprocess.Popen(argv,stdout=out,stderr=subprocess.STDOUT);ticks=identity(child.pid)
   m['active_process']=dict(pid=child.pid,start_ticks=ticks,stage=stage,argv=argv);save();code=child.wait()
  m.pop('active_process',None);m['commands'].append(dict(stage=stage,argv=argv,pid=child.pid,start_ticks=ticks,exit_code=code,elapsed_s=time.monotonic()-begin,log_sha256=sha(S/(stage+'.log'))));save();print(stage,code,flush=True);return code
 save()
 try:
  code=run('physical_run',[sys.executable,'-B',str(R/'scripts/run_stage_static_cp_physical_v6.py'),str(P)])
  assert (P/'manifest.json').exists(),'Runner refused before starting; no run archive to preserve'
  terminal=read(P/'manifest.json');assert not terminal.get('active_process')
  assert identity(terminal['runner_pid'])!=str(terminal['runner_start_ticks'])
  if code==0:
   code=run('independent_inspection',[sys.executable,'-B',str(R/'scripts/inspect_stage_static_cp_physical_v6.py'),str(P)])
  if code==0:
   code=run('terminal_audit',[sys.executable,'-B',str(R/'scripts/audit_stage_static_cp_physical_v6.py'),str(P)])
  passed=code==0 and (P/'source_bound_audit.json').exists()
  m['stage']='preserve_terminal';save()
  files={str(f.relative_to(P)):sha(f) for f in P.rglob('*') if f.is_file()}
  for f in P.rglob('*'):assert not f.is_symlink(),'Refuse ambiguous symlink in new run archive'
  archive=R/'results/recovery_archives_20261102/stage_static_cp_physical_v6_terminal.tar.gz';assert not archive.exists()
  with tarfile.open(archive,'w:gz') as tf:
   for n in files:tf.add(P/n,arcname=n,recursive=False)
  ah=sha(archive);m.update(archive=str(archive),archive_sha256=ah,files=len(files),stage='actual_restore');save()
  restored=B/'stage_static_cp_physical_v6_terminal_actual_restore';assert not restored.exists();restored.mkdir();seen=set()
  with tarfile.open(archive) as tf:
   for item in tf:
    n=Path(item.name);assert item.isfile() and not n.is_absolute() and '..' not in n.parts and item.name in files and item.name not in seen;seen.add(item.name)
    dst=restored/n;dst.parent.mkdir(parents=True,exist_ok=True)
    with tf.extractfile(item) as inp,dst.open('xb') as out:shutil.copyfileobj(inp,out,1<<20)
    assert sha(dst)==files[item.name]
  assert seen==set(files)
  original=P
  if passed:
   # The immutable auditor requires its exact original root. Preserve the entire
   # original; install the restored bytes there; regenerate only the restored audit.
   original=B/'stage_static_cp_physical_v6_preserved_terminal';assert not original.exists();P.rename(original);restored.rename(P)
   expected=(P/'source_bound_audit.json').read_bytes();(S/'expected_restored_audit.json').write_bytes(expected)
   (P/'source_bound_audit.json').unlink() # restored expendable copy only; archive/original retained
   assert run('restored_reaudit',[sys.executable,'-B',str(R/'scripts/audit_stage_static_cp_physical_v6.py'),str(P)])==0
   assert (P/'source_bound_audit.json').read_bytes()==expected
   restored=P
  for n,h in files.items():assert sha(original/n)==h==sha(restored/n)
  report=dict(physical_admitted=terminal.get('physical_gate_open',False),timing_qualified=False,board_acceptance=False,status='terminal_audited_and_actual_restored_awaiting_main_review' if passed else 'failed_terminal_preserved_and_actual_restored_not_accepted',time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),run_root=str(P),original_preserved=str(original),archive=str(archive),archive_sha256=ah,actual_restore=str(restored),all_restored_files_byte_identical=True,file_sha256=files,supervisor_tool_sha256=sha(Path(__file__)),commands=m['commands'],full_system_functional_netlist_validated=True,physical_gate_open=False,scope='Automatic deterministic terminal handling only. Main model must interpret complete evidence before scientific/physical acceptance. No retry or production RTL change.')
  result=R/'results/stage_static_cp_physical_v6_terminal_preservation_20261104.json';assert not result.exists();result.write_text(json.dumps(report,indent=2)+'\n')
  m.update(status=report['status'],stage='complete',terminal_report=str(result),terminal_report_sha256=sha(result),actual_restore=str(restored),physical_gate_open=terminal.get('physical_gate_open',False))
 except BaseException as exc:
  m.update(status='supervision_failed_requires_main_review',error=repr(exc));raise
 finally:save()
if __name__=='__main__':main()
