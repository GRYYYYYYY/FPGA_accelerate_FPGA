"""Preserve both original rejection and candidate pass, restore and reaudit."""
from pathlib import Path
import datetime,json,shutil,subprocess,sys,tarfile
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from stage_static_cp_physical_common_v6 import BASE,read,sha,identity

def main():
 p=BASE/'publication_start_interlock_slice_v1';m=read(p/'manifest.json');a=read(p/'source_bound_audit.json')
 assert m['status']=='observed' and m['stage']=='complete' and a['status']=='passed' and not m.get('active_process')
 assert identity(m['runner_pid'])!=str(m['runner_start_ticks'])
 assert a['manifest_sha256']==sha(p/'manifest.json')
 for n,h in m['artifact_sha256'].items():assert sha(p/n)==h
 tools=p/'review_tools';assert not tools.exists();tools.mkdir()
 sources=[R/'scripts/research_checks'/n for n in ['run_publication_interlock_slice_v1.py','audit_publication_interlock_slice_v1.py','preserve_publication_interlock_slice_v1.py','prepare_publication_start_interlock_v1.py']]
 sources += [R/'scripts/stage_static_cp_physical_common_v6.py']
 for src in sources:shutil.copyfile(src,tools/src.name)
 candidate=p/'candidate_source';candidate.mkdir()
 for sub in ['baseline','candidate']:
  (candidate/sub).mkdir();shutil.copyfile(R/'hardware/variants/publication_start_interlock_v1'/sub/'query_residency_system.sv',candidate/sub/'query_residency_system.sv')
 shutil.copyfile(R/'hardware/variants/publication_start_interlock_v1/manifest.json',candidate/'manifest.json')
 files={str(f.relative_to(p)):sha(f) for f in p.rglob('*') if f.is_file()};assert not any(f.is_symlink() for f in p.rglob('*'))
 archive=R/'results/recovery_archives_20261102/publication_start_interlock_slice_v1_terminal.tar.gz';restore=BASE/'publication_start_interlock_slice_v1_actual_restore'
 assert not archive.exists() and not restore.exists()
 with tarfile.open(archive,'w:gz') as tf:
  for n in files:tf.add(p/n,arcname=n,recursive=False)
 restore.mkdir();seen=set()
 with tarfile.open(archive) as tf:
  for item in tf:
   n=Path(item.name);assert item.isfile() and not n.is_absolute() and '..' not in n.parts and item.name in files and item.name not in seen;seen.add(item.name)
   dst=restore/n;dst.parent.mkdir(parents=True,exist_ok=True)
   with tf.extractfile(item) as f,dst.open('xb') as w:shutil.copyfileobj(f,w,1<<20)
   assert sha(dst)==files[item.name]
 assert seen==set(files)
 expected=(restore/'source_bound_audit.json').read_bytes();(restore/'source_bound_audit.json').unlink()
 argv=[sys.executable,'-B',str(R/'scripts/research_checks/audit_publication_interlock_slice_v1.py'),str(restore)]
 log=R/'results/publication_start_interlock_slice_v1_restore_reaudit_20261104.log'
 with log.open('x') as f:r=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0 and (restore/'source_bound_audit.json').read_bytes()==expected
 for n,h in files.items():assert sha(p/n)==h==sha(restore/n)
 report=R/'results/publication_start_interlock_slice_v1_review_20261104.json';assert not report.exists()
 record=dict(status='bounded_real_module_interlock_slice_audited_actual_restored',time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 audit=a,manifest_sha256=sha(p/'manifest.json'),audit_sha256=sha(p/'source_bound_audit.json'),runner_pid=m['runner_pid'],runner_start_ticks=m['runner_start_ticks'],current_runner_start_ticks=identity(m['runner_pid']),
 archive=str(archive),archive_sha256=sha(archive),actual_restore=str(restore),file_sha256=files,all_restored_files_sha_identical=True,restored_audit_byte_identical=True,
 restore_reaudit_command=argv,restore_reaudit_exit_code=r.returncode,restore_reaudit_log_sha256=sha(log),preserver_sha256=sha(__file__),
 original_full_rtl_counterexample_preserved=True,candidate_full_system_validated=False,production_repair_accepted=False,production_rtl_modified=False,
 scope=m['scope'],next_work='Keep original failing full probe. Build separate full-query candidate probe with original monitors intact, fresh inputs and exact one-source delta, and classify caller arbitration/liveness. Do not inherit original v7 or physical v6 acceptance for changed source.')
 with report.open('x') as f:f.write(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print('INTERLOCK_SLICE_ACTUAL_RESTORED_REAUDITED',len(files),sha(archive))
if __name__=='__main__':main()
