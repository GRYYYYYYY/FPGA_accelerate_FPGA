"""Prepare a bounded actual-full-RTL cold-start probe; no production changes."""
from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_recovery_20261102');OLD=Path('/tmp/B_state_residency_offer_20261025');ref=B/'stage_static_cp_host_full_static_v1';p=B/'ka_publication_release_full_rtl_v4';assert not p.exists()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()
m=json.loads((ref/'manifest.json').read_text());assert m['status']=='observed';assert sha(ref/'source_bound_audit.json')=='f087aaff4c300605867c02d9fadf149b67125ebb6d9e13f6599edc7dbd01c770';assert m['parameters']['SLOTS']==32
p.mkdir();(p/'sources').mkdir();(p/'full').mkdir()
source_receipts={}
for n,e in m['sources'].items():
 src=ref/'sources'/n;assert sha(src)==e['sha256'];dest=p/'sources'/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest);source_receipts[n]=sha(dest)
production=[n for n in m['rtl'] if n not in ['tb_directory_observer.sv','tb_query_fault.sv','axi_file_memory.sv']];assert len(production)==133
v6_report=R/'results/stage_static_cp_shadow_v6_failure_preservation_20261031.json'
v6=json.loads(v6_report.read_text())['files']['stage_static_cp_shadow_system_v6']
for n in production:assert sha(p/'sources'/n)==v6['sources/'+n]
tb=p/'sources/tb_query_fault.sv';s=tb.read_text();anchor=" ap_get(208292,6632,64'h100000001,0,1,2);ap_get(208292,17601,64'h100000001,0,2,2);ap_get(558358,23916,64'h100000001,0,1,2);";assert s.count(anchor)==1
call=' publication_release_overlap_probe;\n';s=s.replace(anchor,call+anchor,1)
task='''
// Verification-only early probe after the original first lease acquisition.
task publication_release_overlap_probe;begin
 @(negedge clk);
 while(pc_release_ready!==1'b1 || jp_start_ready!==1'b1) @(negedge clk);
 if(pc_owned!==1'b1||jp_owned!==1'b0||bench_rst!==1'b0||k_cold_rst!==1'b0||system.publication.start_ok!==1'b1)
  $fatal(1,"full probe precondition/metadata not established");
 $display("FULL_PROBE_READY cycle=%0d time=%0t generation=%h checkpoint=%0d version=%0d",cycles,$time,as_bound_generation,k_saved_checkpoint,query_version);
 $fdisplay(trace,"FULL_PROBE_READY %0d %0t",cycles,$time);
 jp_start=1;pc_release_valid=1;
 #1;if(jp_start_ready!==1'b1||pc_release_ready!==1'b1)$fatal(1,"full probe simultaneous admission absent");
 @(posedge clk);$display("FULL_SIMULTANEOUS_ACCEPT cycle=%0d time=%0t start=%b release=%b",cycles,$time,jp_start_ready,pc_release_ready);
 #1;if(jp_owned!==1'b1||pc_owned!==1'b0)$fatal(1,"full probe ownership split absent");
 $display("FULL_OWNERSHIP_SPLIT cycle=%0d time=%0t publication=%b lease=%b",cycles,$time,jp_owned,pc_owned);
 @(negedge clk);jp_start=0;pc_release_valid=0;
 @(posedge clk);#1;if(jp_done!==1'b1||jp_result!==2'd3||jp_owned!==1'b1||pc_owned!==1'b0)$fatal(1,"full probe halt output absent");
 $display("FULL_RTL_RELEASE_OVERLAP_OBSERVED cycle=%0d time=%0t status=%0d",cycles,$time,jp_result);
 $fdisplay(trace,"FULL_RTL_RELEASE_OVERLAP_OBSERVED %0d %0t %0d",cycles,$time,jp_result);
 $finish;
end endtask
initial begin #100000;$fatal(1,"full probe 100us watchdog");end
'''
assert s.count('endmodule')==1;s=s.replace('endmodule',task+'endmodule',1);tb.write_text(s)
assert s.replace(call,'',1).replace(task,'',1)==(ref/'sources/tb_query_fault.sv').read_text();source_receipts['tb_query_fault.sv']=sha(tb)
for key in ['scoreboards','next_scoreboards','third_scoreboards','fourth_scoreboards']:
 for n,h in m[key].items():assert sha(ref/n)==h;shutil.copyfile(ref/n,p/n)
for f in (p/'sources').rglob('*.dat'):shutil.copyfile(f,p/'full'/f.name)
objects=['clk','bench_rst','k_cold_rst','pc_acquire_valid','pc_acquire_ready','pc_release_valid','pc_release_ready','pc_owned','jp_start','jp_start_ready','jp_owned','jp_done','jp_result','system.publication.start_ok']
(p/'full/run.tcl').write_text('open_vcd probe.vcd\nlog_vcd [get_objects {'+' '.join('/tb_candidate_offer/'+n.replace('.','/') for n in objects)+'}]\nrun 200 us\nclose_vcd\nquit\n')
commands=[]
for c in m['cases']['full']['commands']:
 argv=[v.replace(str(OLD/ref.name),str(p)).replace(str(OLD)+'/',str(B)+'/').replace(str(R/'results/transaction_fence_static_join_rtl_v1/authority.txt'),str(B/'transaction_fence_static_join_rtl_v1/authority.txt')) for v in c['argv']]
 if Path(argv[0]).name=='xsim':argv+=['-onfinish','stop']
 commands.append(argv)
assert len(commands)==3
binding=Path(m['binding']);assert sha(binding)==m['binding_sha256'];regions=json.loads(binding.read_text())['regions'];plan={k:regions[k] for k in ['design','owners','owner_pool','owner_allocator','cost_history_prices_nets']}
original_plan=plan
plan={k:dict(e,path=str(B/Path(e['path']).relative_to(OLD))) for k,e in original_plan.items()}
for e in plan.values():assert Path(e['path']).stat().st_size==e['bytes'] and sha(Path(e['path']))==e['sha256']
(p/'input_plan.json').write_text(json.dumps({'binding':str(binding),'binding_sha256':sha(binding),'original_regions':original_plan,'regions':plan,'note':'Fresh writable initial images must be built from these originals after memory admission; never copy final reference/full images.'},indent=2)+'\n')
receipt={'status':'prepared_not_running','reference':str(ref),'reference_audit_sha256':sha(ref/'source_bound_audit.json'),'parameters':m['parameters'],'sources':source_receipts,'production_count':133,'production_sha256':{n:sha(p/'sources'/n) for n in production},'commands':commands,'tb_parent_sha256':sha(ref/'sources/tb_query_fault.sv'),'tb_sha256':sha(tb),'verification_call':call,'verification_task':task,'run_tcl_sha256':sha(p/'full/run.tcl'),'input_plan_sha256':sha(p/'input_plan.json'),'memory_policy':{'total_current_max_gib':225,'stable_seconds':60,'poll_seconds':5},'expected_markers':['FULL_PROBE_READY','FULL_SIMULTANEOUS_ACCEPT','FULL_OWNERSHIP_SPLIT','FULL_RTL_RELEASE_OVERLAP_OBSERVED'],'scope':'Actual 133 production sources and SLOTS32/13 parameters, original cold boot and first lease acquisition; only additive TB early probe/finish. Not original full regression or gate netlist validation. Caller protocol legality remains separate.','full_system_functional_netlist_validated':False,'physical_gate_open':False}
# New-host preparation evidence. This does not establish termination on the old host.
parent=R/'scripts/research_checks/prepare_publication_release_full_rtl_v2.py'
old_tb=R/'hardware/variants/ka_publication_release_full_rtl_v2/tb_query_fault.sv'
assert tb.read_bytes()==old_tb.read_bytes()
review=R/'results/new_host_next_cost_restore_reaudit_20261102.json'
rr=json.loads(review.read_text());assert rr['status']=='actual_restored_CPU_reaudit_passed_byte_identical'
cost_review=R/'results/new_host_next_cost_reconstruction_review_20261102.json'
cr=json.loads(cost_review.read_text());next_cost=B/'followup_iter2_next_cost_v1/cost_vectors.txt'
assert sha(next_cost)==cr['file_sha256']['followup_iter2_next_cost_v1/cost_vectors.txt']
read_inputs={}
for token in commands[-1]:
 if '=' not in token:continue
 key,value=token.split('=',1);path=Path(value)
 if not path.is_absolute():continue
 if path.is_relative_to(p/'full'):continue
 assert path.is_file(),path
 read_inputs[value]={'bytes':path.stat().st_size,'sha256':sha(path)}
assert not any(str(OLD) in token for command in commands for token in command)
assert not list((p/'full').glob('*.bin'))
receipt.update(parent_preparer_sha256=sha(parent),parent_tb_sha256=sha(old_tb),
 source_comparison_report_sha256=sha(v6_report),read_only_inputs=read_inputs,
 recovery_review_sha256=sha(review),cost_reconstruction_review_sha256=sha(cost_review),
 old_host_backend_status='unconfirmed',execution_authority_resolved=False,
 input_recovery_scope='Original initial region hashes retained; cost2 independently regenerated and audited, historical cost2 SHA unavailable.')
(p/'preparation.json').write_text(json.dumps(receipt,indent=2)+'\n')
v=R/'hardware/variants/ka_publication_release_full_rtl_v4';v.mkdir();(v/'tb_query_fault.sv').write_bytes(tb.read_bytes());print(p)
