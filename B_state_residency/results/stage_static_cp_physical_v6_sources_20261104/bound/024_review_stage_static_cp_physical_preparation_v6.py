"""Independent preparation audit and actual archive restoration; no Vivado launch."""
from pathlib import Path
import ast, datetime, json, shutil, subprocess, sys, tarfile
from stage_static_cp_physical_common_v6 import ROOT,BASE,OUTPUT,REVIEW,TOOLS,read,sha,runtime_environment,memory_ok

def main():
 assert not REVIEW.exists()
 p=OUTPUT;m=read(p/'manifest.json');prepared=p/'preparation.json'
 assert sha(prepared)==sha(p/'manifest.json')
 assert m['status']=='prepared' and m['stage']=='awaiting_validated_runner'
 s=BASE/'stage_static_cp_synth_v1';f=BASE/'stage_static_cp_shadow_system_v7'
 sm,sa=read(s/'manifest.json'),read(s/'source_bound_audit.json')
 accepted=read(ROOT/'results/stage_static_cp_shadow_system_v7_20261103.json')
 fa=read(f/'source_bound_audit.json')
 assert accepted['audit']==fa and accepted['full_system_functional_netlist_validated']
 assert m['reference']==str(s) and m['full_system_reference']==str(f)
 assert m['parameters']==sm['parameters']==fa['parameters'] and len(m['parameters'])==13 and m['parameters']['SLOTS']==32
 assert m['part']=='xcu280-fsvh2892-2L-e' and m['clock_period_ns']==10 and m['top']=='query_residency_system'
 assert m['rtl']==sm['rtl'] and len(m['rtl'])==133
 for n in m['rtl']:assert sha(p/'sources'/n)==sm['sources'][n]==sha(s/'sources'/n)
 assert sha(p/'inputs/synthesized.dcp')==sa['artifact_sha256']['synth.dcp']==sha(s/'synth.dcp')
 assert (p/'inputs/clock.xdc').read_bytes()==(s/'clock.xdc').read_bytes()==b'create_clock -name core_clk -period 10.000 [get_ports clk]\n'
 for n,h in m['inputs'].items():assert sha(p/n)==h,n
 proof=m['external_evidence_sha256']
 for n,h in proof.items():assert sha(n)==h,n
 template=ROOT/'hardware/scripts/implement_state_ooc.tcl';text=template.read_text()
 assert (p/'run.tcl').read_text()==text.replace('@OUT@',str(p))
 assert sha(template)==m['template_sha256'] and sha(p/'run.tcl')==m['tcl_sha256']
 assert [text.index(x) for x in ['open_checkpoint','opt_design','place_design -directive Default','route_design -directive Default']]==sorted(text.index(x) for x in ['open_checkpoint','opt_design','place_design -directive Default','route_design -directive Default'])
 assert not any(x in text for x in ['read_xdc','set_false_path','set_multicycle_path','set_input_delay','set_output_delay','create_waiver','resume_placed'])
 assert not any((p/n).exists() for n in ['optimized.dcp','placed.dcp','routed.dcp','inspection','execution.lock'])
 # Exact migration of report parser; science acceptance rules must not weaken.
 old=(ROOT/'scripts/audit_stage_static_cp_physical_v3.py').read_text()
 new=(ROOT/'scripts/audit_stage_static_cp_physical_v6.py').read_text()
 assert old.split('def report_evidence(p):',1)[1].split('\ndef main():',1)[0]==new.split('def report_evidence(p):',1)[1].split('\ndef main():',1)[0]
 toolpaths=[ROOT/'scripts'/n for n in TOOLS]+[template,ROOT/'hardware/scripts/inspect_state_route_v1.tcl']
 toolpaths += [ROOT/'scripts'/n for n in ['audit_state_ooc_physical_v2.py','audit_state_route_recovery_v2.py','parse_state_timing_paths.py','run_checkpoint_authority.py']]
 for path in toolpaths:
  assert proof[str(path)]==sha(path)
  if path.suffix=='.py':ast.parse(path.read_text())
 for n in TOOLS:
  src=(ROOT/'scripts'/n).read_text()
  if n!=Path(__file__).name:
   assert 'B_state_residency_offer_20261025' not in src and 'from config_native_publication_synth_common_v1' not in src
   assert 'from host_edit_system_common_v1' not in src
 assert 'require_review(p)' in (ROOT/'scripts/run_stage_static_cp_physical_v6.py').read_text()
 assert 'flock' in (ROOT/'scripts/run_stage_static_cp_physical_v6.py').read_text()
 # Boundary controls are necessary to avoid relaxing admission on this 500GiB host.
 g=1<<30
 controls=[(225*g,500*g,True),(225*g+1,500*g,False),(225*g,300*g,True),(225*g,300*g-1,False),(74*g,100*g,True),(76*g,100*g,False)]
 for current,limit,expected in controls:assert memory_ok(current,limit)==expected
 _,runtime=runtime_environment()
 # Real runner rejects before any child or manifest mutation when review is absent.
 before=sha(p/'manifest.json')
 refusal=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/run_stage_static_cp_physical_v6.py'),str(p)],capture_output=True,text=True)
 assert refusal.returncode!=0 and 'stage_static_cp_physical_v6_preparation_review_20261104.json' in refusal.stderr
 assert sha(p/'manifest.json')==before and not (p/'runner.py').exists()
 (p/'pre_review_runner_refusal.log').write_text(refusal.stdout+refusal.stderr)
 archive=ROOT/'results/recovery_archives_20261102/stage_static_cp_physical_v6_prepared.tar.gz';assert not archive.exists()
 files={str(x.relative_to(p)):sha(x) for x in p.rglob('*') if x.is_file()}
 assert not any(x.is_symlink() for x in p.rglob('*'))
 with tarfile.open(archive,'w:gz') as tf:
  for n in files:tf.add(p/n,arcname=n,recursive=False)
 restore=BASE/'stage_static_cp_physical_v6_prepared_actual_restore';assert not restore.exists();restore.mkdir();seen=set()
 with tarfile.open(archive) as tf:
  for item in tf:
   n=Path(item.name);assert item.isfile() and not n.is_absolute() and '..' not in n.parts and item.name in files and item.name not in seen;seen.add(item.name)
   dst=restore/n;dst.parent.mkdir(parents=True,exist_ok=True)
   with tf.extractfile(item) as inp,dst.open('xb') as out:shutil.copyfileobj(inp,out,1<<20)
   assert sha(dst)==files[item.name]
 assert seen==set(files)
 record=dict(status='physical_v6_preparation_independently_audited_actual_restored',time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 prepared_manifest_sha256=sha(prepared),tool_sha256={str(x):sha(x) for x in toolpaths},archive=str(archive),archive_sha256=sha(archive),actual_restore=str(restore),file_sha256=files,
 production_sources=133,parameters=m['parameters'],part=m['part'],clock_period_ns=10,runtime=runtime,runner_refusal_exit_code=refusal.returncode,
 memory_boundary_controls=controls,report_parser_unchanged=True,full_system_functional_netlist_validated=True,physical_gate_open=False,timing_qualified=False,board_acceptance=False,
 scope='Preparation and actual restoration only. Runtime and tool/source bindings checked. No implementation executed. start/release counterexample remains open; original production source unchanged.')
 with REVIEW.open('x') as out:out.write(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print('PHYSICAL_V6_PREPARATION_INDEPENDENTLY_AUDITED',len(files))
if __name__=='__main__':main()
