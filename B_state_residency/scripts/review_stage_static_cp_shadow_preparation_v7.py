"""Independent new-full preparation review, real default rejection and actual restore; no simulation."""
from pathlib import Path
import json,sys,subprocess,hashlib,tarfile,shutil,datetime,ast
from shadow_recovered_evidence_v7 import ROOT,BASE,OLD,read,sha,RECOVERED
from stage_static_cp_shadow_common_v7_revision2 import TARGET,REFERENCE,SYNTH,VARIANT,CANDIDATE,evidence,MARKER
from check_stage_static_cp_fixture_parameters_v1 import defines,fixture_parameters
from namespace_functional_netlist_v1 import namespace

def main():
 p=TARGET;pr=read(p/'preparation.json');rm,proof=evidence();ra=read(REFERENCE/'source_bound_audit.json');sm=read(SYNTH/'manifest.json')
 assert pr['status']=='full_shadow_v7_prepared_not_executed' and not (p/'manifest.json').exists()
 assert not list((p/'full').glob('*.bin'))
 assert all(pr['predecessors'].get(k)==v for k,v in proof.items())
 assert pr['reference_manifest_sha256']==sha(REFERENCE/'manifest.json') and pr['reference_audit_sha256']==sha(REFERENCE/'source_bound_audit.json')
 for n,e in pr['bound'].items():assert sha(p/'bound'/n)==e['sha256']==sha(e['source'])
 assert {e['source']:e['sha256'] for e in pr['bound'].values()}==pr['predecessors']
 assert pr['rtl']==rm['rtl'] and len(pr['rtl'])==136 and len(sm['rtl'])==133
 assert set(pr['sources'])==set(rm['sources'])
 for n,e in pr['sources'].items():
  assert sha(p/'sources'/n)==e['sha256']
  if n not in ['runner.py','tb_query_fault.sv']:assert e['sha256']==rm['sources'][n]['sha256']
 for n in sm['rtl']:assert sha(p/'sources'/n)==sm['sources'][n]
 params=fixture_parameters((p/'sources/tb_query_fault.sv').read_text(),(SYNTH/'sources/query_residency_system.sv').read_text(),defines(pr['commands'][0]['argv']))
 assert params==pr['parameters']==rm['parameters']==sm['parameters'] and len(params)==13 and params['SLOTS']==32
 # Full TB changes only its terminal checker call. All stimulus and original monitors remain.
 tb=(p/'sources/tb_query_fault.sv').read_text();parent=(REFERENCE/'sources/tb_query_fault.sv').read_text();needle='stage_static_cp_shadow.finish_and_check;$finish;'
 assert tb.count(needle)==1 and tb.replace(needle,'$finish;',1)==parent
 assert tb==(VARIANT/'tb_query_fault.sv').read_text()
 assert 'publication_release_overlap_probe' not in tb
 checker=(p/'sources/shadow.sv').read_text();cm=read(CANDIDATE/'manifest.json')
 assert checker==(CANDIDATE/'shadow.sv').read_text();inverse=checker
 for change in reversed(cm['patches']):assert inverse.count(change['after'])==1;inverse=inverse.replace(change['after'],change['before'],1)
 assert inverse==(ROOT/'hardware/variants/stage_static_cp_shadow_protocol_v5/shadow.sv').read_text()
 assert checker.count('FULL_SHADOW_MISMATCH port=')==342
 for task in ['check_cp_output','check_pw_output']:
  assert checker.split('task '+task+';',1)[1].split('end endtask',1)[0]==inverse.split('task '+task+';',1)[1].split('end endtask',1)[0]
 assert pr['expected_marker']==MARKER and checker.count(MARKER)==1 and 'FULL_SHADOW_PROTOCOL_PASS' not in checker
 net,ns=namespace((SYNTH/'synth.v').read_text());assert (p/'sources/shadow_netlist.v').read_text()==net
 ns.update(source_sha256=sha(SYNTH/'synth.v'),output_sha256=sha(p/'sources/shadow_netlist.v'));assert read(p/'namespace.json')==ns and sha(p/'namespace.json')==pr['namespace_sha256']
 expected_files=['shadow_netlist.v','shadow.sv','glbl.v','cp_transfer_monitor.sv','payload_transfer_monitor.sv'];assert set(pr['shadow_inputs'])==set(expected_files)
 for n,h in pr['shadow_inputs'].items():assert sha(p/'sources'/n)==h
 glbl=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/data/verilog/src/glbl.v');assert sha(glbl)==pr['original_vendor_glbl_sha256']==sha(p/'sources/glbl.v')
 for n,original in [('cp_transfer_monitor.sv','tb_shadow_cp_transfer_monitor_v1.sv'),('payload_transfer_monitor.sv','tb_shadow_payload_transfer_monitor_v1.sv')]:assert sha(p/'sources'/n)==sha(ROOT/'hardware/tests'/original)
 assert sha(p/'full/run.tcl')==pr['run_tcl_sha256']==sha(REFERENCE/'full/run.tcl')
 for old,new in zip(rm['cases']['full']['commands'],pr['commands']):
  expected=[v.replace(str(OLD/REFERENCE.name),str(p)).replace(str(OLD)+'/',str(BASE)+'/').replace(str(ROOT/'results/transaction_fence_static_join_rtl_v1/authority.txt'),str(BASE/'transaction_fence_static_join_rtl_v1/authority.txt')) for v in old['argv']]
  if old['stage']=='compile':expected+=['--define','SHADOW_NETLIST_TOP='+ns['shadow_top']]+[str(p/'sources'/n) for n in expected_files]
  if old['stage']=='elaborate':expected+=['stage_static_cp_shadow','shadow_cp_transfer_monitor','shadow_payload_transfer_monitor','glbl','-L','unisims_ver','--O0']
  assert new==dict(stage=old['stage'],argv=expected)
 assert len(pr['commands'])==3 and not any(str(OLD) in token for c in pr['commands'] for token in c['argv'])
 for key in ['scoreboards','next_scoreboards','third_scoreboards','fourth_scoreboards']:
  for n,h in rm[key].items():assert sha(p/n)==h
 plan=read(p/'input_plan.json');assert sha(p/'input_plan.json')==pr['input_plan_sha256'] and sha(plan['binding'])==rm['binding_sha256']==plan['binding_sha256']
 original_regions=read(plan['binding'])['regions'];assert set(plan['regions'])=={'design','owners','owner_pool','owner_allocator','cost_history_prices_nets'}
 for k,e in plan['regions'].items():
  old=original_regions[k];assert plan['original_regions'][k]==old and e==dict(old,path=str(BASE/Path(old['path']).relative_to(OLD)))
  assert Path(e['path']).stat().st_size==e['bytes'] and sha(e['path'])==e['sha256']
 readonly={}
 for token in pr['commands'][-1]['argv']:
  if '=' not in token:continue
  value=token.split('=',1)[1];f=Path(value)
  if f.is_absolute() and not f.is_relative_to(p/'full'):readonly[value]=dict(bytes=f.stat().st_size,sha256=sha(f))
 assert readonly==pr['read_only_inputs'] and len(readonly)==24
 assert pr['memory_policy']==dict(total_current_max_gib=225,cgroup_max_fraction_numerator=3,cgroup_max_fraction_denominator=4,stable_seconds=60,poll_seconds=5)
 for n,h in pr['tools'].items():assert sha(ROOT/'scripts'/n)==h;ast.parse((ROOT/'scripts'/n).read_text())
 # Real command-level rejection before review exists; no manifest, child or fresh image created.
 review=ROOT/'results/stage_static_cp_shadow_v7_preparation_review_20261102.json';assert not review.exists()
 command=[sys.executable,'-B',str(ROOT/'scripts/run_stage_static_cp_shadow_system_v7.py'),str(p)]
 proc=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 log=ROOT/'results/stage_static_cp_shadow_v7_pre_review_rejection_20261102.log';assert not log.exists();log.write_text(proc.stdout)
 assert proc.returncode!=0 and 'FileNotFoundError' in proc.stdout and str(review) in proc.stdout
 assert not (p/'manifest.json').exists() and not list((p/'full').glob('*.bin')) and not list((p/'full').glob('*.log'))
 # Preserve the entire prepared root and exact tools; independently restore every regular file.
 archive=ROOT/'results/recovery_archives_20261102/stage_static_cp_shadow_v7_prepared.tar.gz';assert not archive.exists()
 files={str(f.relative_to(p)):f for f in p.rglob('*') if f.is_file()}
 for n in pr['tools']:files['review_tools/'+n]=ROOT/'scripts'/n
 hashes={n:sha(f) for n,f in files.items()}
 with tarfile.open(archive,'w:gz') as tf:
  for n,f in files.items():tf.add(f,arcname=n,recursive=False)
 restore=BASE/'stage_static_cp_shadow_v7_prepared_actual_restore';assert not restore.exists();restore.mkdir();seen=set()
 with tarfile.open(archive) as tf:
  for m in tf:
   n=Path(m.name);assert m.isfile() and not n.is_absolute() and '..' not in n.parts and m.name in hashes and m.name not in seen;seen.add(m.name)
   dst=restore/n;dst.parent.mkdir(parents=True,exist_ok=True)
   with tf.extractfile(m) as inp,dst.open('xb') as out:shutil.copyfileobj(inp,out,1<<20)
   assert sha(dst)==hashes[m.name]
 assert seen==set(hashes)
 result=dict(status='full_shadow_v7_preparation_independently_reviewed_not_executed',time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),preparation_sha256=sha(p/'preparation.json'),tools=pr['tools'],production_sources=133,original_compile_files=136,additional_compile_files=5,parameters=params,read_only_inputs=24,external_comparisons_required=len(ra['outputs']),required_transfers=dict(CP=1560,KA=26,PW=8223),tb_inverse_exact=True,checker_inverse_exact=True,unconditional_outputs=342,cp_pw_tasks_unchanged=True,default_rejection=dict(command=command,exit_code=proc.returncode,log=str(log),log_sha256=sha(log),manifest_created=False,fresh_images_created=False),archive=str(archive),archive_sha256=sha(archive),actual_restore=str(restore),file_sha256=hashes,actual_restore_byte_identical=True,recovered_predecessor_paths=RECOVERED,full_system_functional_netlist_validated=False,physical_gate_open=False,scope='Preparation and actual restore only. No new full simulation or solver/58-control rerun. Complete original fixture and all acceptance checks retained; execution may start only through the reviewed runner.')
 review.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(result['status'],len(files),result['archive_sha256'])
if __name__=='__main__':main()
