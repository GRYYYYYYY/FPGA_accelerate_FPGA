"""Prepare full fixture v7 without fresh mutable images or simulator execution."""
from pathlib import Path
import json,shutil,sys,ast
from shadow_recovered_evidence_v7 import ROOT,BASE,OLD,read,sha
from stage_static_cp_shadow_common_v7_revision2 import TARGET,REFERENCE,SYNTH,VARIANT,evidence,MARKER
from namespace_functional_netlist_v1 import namespace
TOOLS=['prepare_stage_static_cp_shadow_system_v7.py','run_stage_static_cp_shadow_system_v7.py','audit_stage_static_cp_shadow_system_v7.py','review_stage_static_cp_shadow_preparation_v7.py','shadow_prepared_runtime_v7.py','stage_static_cp_shadow_common_v7_revision2.py','stage_static_cp_shadow_predecessor_v7a.py','stage_static_cp_shadow_predecessor_v7b.py','shadow_recovered_evidence_v7.py','namespace_functional_netlist_v1.py','shadow_terminal_receipt_v1.py','check_shadow_payload_transfer_logs_v1.py','check_host_edit_trace_v1.py']
def main():
 assert not TARGET.exists();rm,proof=evidence()
 for n in TOOLS:
  f=ROOT/'scripts'/n;ast.parse(f.read_text());proof[str(f)]=sha(f)
 assert not any(Path(x).is_relative_to(OLD) for x in proof)
 p=TARGET;p.mkdir();src=p/'sources';src.mkdir();d=p/'full';d.mkdir();(p/'bound').mkdir()
 sources={}
 for n,e in rm['sources'].items():
  f=REFERENCE/'sources'/n;assert sha(f)==e['sha256'];q=src/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q);sources[n]=dict(path=str(q),sha256=sha(q))
 for n,f in [('tb_query_fault.sv',VARIANT/'tb_query_fault.sv'),('runner.py',ROOT/'scripts/run_stage_static_cp_shadow_system_v7.py')]:shutil.copyfile(f,src/n);sources[n]=dict(path=str(src/n),sha256=sha(src/n))
 for k in ['scoreboards','next_scoreboards','third_scoreboards','fourth_scoreboards']:
  for n,h in rm[k].items():assert sha(REFERENCE/n)==h;shutil.copyfile(REFERENCE/n,p/n)
 for f in src.rglob('*.dat'):shutil.copyfile(f,d/f.name)
 shutil.copyfile(REFERENCE/'full/run.tcl',d/'run.tcl')
 net,ns=namespace((SYNTH/'synth.v').read_text());(src/'shadow_netlist.v').write_text(net);ns.update(source_sha256=sha(SYNTH/'synth.v'),output_sha256=sha(src/'shadow_netlist.v'));(p/'namespace.json').write_text(json.dumps(ns,indent=2,sort_keys=True)+'\n')
 glbl=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/data/verilog/src/glbl.v')
 for f,n in [(VARIANT/'shadow.sv','shadow.sv'),(glbl,'glbl.v'),(ROOT/'hardware/tests/tb_shadow_cp_transfer_monitor_v1.sv','cp_transfer_monitor.sv'),(ROOT/'hardware/tests/tb_shadow_payload_transfer_monitor_v1.sv','payload_transfer_monitor.sv')]:shutil.copyfile(f,src/n)
 additional=['shadow_netlist.v','shadow.sv','glbl.v','cp_transfer_monitor.sv','payload_transfer_monitor.sv']
 commands=[]
 for c in rm['cases']['full']['commands']:
  argv=[v.replace(str(OLD/REFERENCE.name),str(p)).replace(str(OLD)+'/',str(BASE)+'/').replace(str(ROOT/'results/transaction_fence_static_join_rtl_v1/authority.txt'),str(BASE/'transaction_fence_static_join_rtl_v1/authority.txt')) for v in c['argv']]
  if c['stage']=='compile':argv+=['--define','SHADOW_NETLIST_TOP='+ns['shadow_top']]+[str(src/n) for n in additional]
  elif c['stage']=='elaborate':argv+=['stage_static_cp_shadow','shadow_cp_transfer_monitor','shadow_payload_transfer_monitor','glbl','-L','unisims_ver','--O0']
  commands.append(dict(stage=c['stage'],argv=argv))
 assert [c['stage'] for c in commands]==['compile','elaborate','simulate']
 assert not any(str(OLD) in arg for c in commands for arg in c['argv'])
 readonly={}
 for arg in commands[-1]['argv']:
  if '=' not in arg:continue
  key,value=arg.split('=',1);f=Path(value)
  if not f.is_absolute() or f.is_relative_to(d):continue
  assert f.is_file();readonly[value]=dict(bytes=f.stat().st_size,sha256=sha(f))
 # Reuse the proven input recovery mapping, not the early probe testbench or final images.
 original_plan=read(BASE/'ka_publication_release_full_rtl_v5/input_plan.json');assert sha(original_plan['binding'])==rm['binding_sha256']==original_plan['binding_sha256']
 expected=read(original_plan['binding'])['regions']
 for k,e in original_plan['regions'].items():
  assert original_plan['original_regions'][k]==expected[k]
  assert e['sha256']==expected[k]['sha256'] and Path(e['path']).stat().st_size==e['bytes'] and sha(e['path'])==e['sha256']
 (p/'input_plan.json').write_text(json.dumps(original_plan,indent=2)+'\n')
 cp=ROOT/'results/new_host_next_cost_reconstruction_review_20261102.json';cr=read(cp);cost=BASE/'followup_iter2_next_cost_v1/cost_vectors.txt';assert sha(cost)==cr['file_sha256']['followup_iter2_next_cost_v1/cost_vectors.txt']
 for f in [cp,ROOT/'results/new_host_next_cost_restore_reaudit_20261102.json',BASE/'ka_publication_release_full_rtl_v5/input_plan.json']:proof[str(f)]=sha(f)
 bound={}
 for i,(name,h) in enumerate(sorted(proof.items())):
  f=Path(name);assert sha(f)==h;n=f'{i:03d}_{f.name}';shutil.copyfile(f,p/'bound'/n);bound[n]=dict(source=name,sha256=h)
 prep=dict(status='full_shadow_v7_prepared_not_executed',reference=str(REFERENCE),reference_manifest_sha256=sha(REFERENCE/'manifest.json'),reference_audit_sha256=sha(REFERENCE/'source_bound_audit.json'),parameters=rm['parameters'],rtl=rm['rtl'],sources=sources,shadow_inputs={n:sha(src/n) for n in additional},namespace_sha256=sha(p/'namespace.json'),synthesis_netlist_sha256=sha(SYNTH/'synth.v'),original_vendor_glbl_sha256=sha(glbl),run_tcl_sha256=sha(d/'run.tcl'),input_plan_sha256=sha(p/'input_plan.json'),read_only_inputs=readonly,commands=commands,predecessors=proof,bound=bound,tools={n:sha(ROOT/'scripts'/n) for n in TOOLS},memory_policy=dict(total_current_max_gib=225,cgroup_max_fraction_numerator=3,cgroup_max_fraction_denominator=4,stable_seconds=60,poll_seconds=5),expected_marker=MARKER,scope='Full original SLOTS32 fixture, fresh initial images, 133 production sources, 136 original compilation units + 5 shadow units. KA ready1/zero-stall policy only; 342 unconditional comparisons, CP/PW stalls, all payload and original monitors remain. 27 external files and 1560CP/26KA/8223PW required. No early probe.',full_system_functional_netlist_validated=False,physical_gate_open=False)
 assert not list(d.glob('*.bin')) and not (p/'manifest.json').exists()
 (p/'preparation.json').write_text(json.dumps(prep,indent=2,sort_keys=True)+'\n');print('FULL_SHADOW_V7_PREPARED',p,len(proof),len(readonly))
if __name__=='__main__':main()
