from pathlib import Path
import re
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/authority_rotate_v6/sources/tb_rotate.sv')
def ports(s):
 text=s[s.index(')(\n')+3:s.index('\n);')];out=[]
 for chunk in text.replace('\n',' ').split(','):
  m=re.match(r'\s*(input|output)\s+(wire|reg)\s*(\[[^]]+\])?\s*(\w+)\s*$',chunk)
  if m:d,_,w,n=m.groups();w=w or ''
  else:n=chunk.strip()
  out.append((d,w,n))
 return out

def make():
 source=BASE.read_text();s=source[:source.index('initial begin\n events=$fopen')].replace('module tb_rotate;', 'module tb_joint;')
 early='''
wire pc_owned,pc_acquire_ready,pc_release_ready,pc_safe;
wire k_fault,c_fault,c_load_rsp_valid,c_busy;
wire cfg_ready_core,admit_a,admit_k,admit_c;
reg pc_acquire_valid=0,pc_release_valid=0;
wire[2:0]prepared_bits,pub_ready,discard_ready_bits,pub,discard;
wire tx_owned,prepare_allowed,tx_done_valid,tx_start_ready,tx_commit_ready,tx_cancel_ready;
wire[1:0]tx_status;
reg tx_start_valid=0,tx_commit_valid=0,tx_cancel_valid=0,tx_done_ready=0,manifest_ready=1;
reg[31:0]effective_words[0:71];wire[2303:0]effective;
initial $readmemh("config_effective.hex",effective_words);
generate for(genvar z=0;z<72;z=z+1)begin assign effective[z*32+:32]=effective_words[z];end endgenerate
'''
 s=s.replace('module tb_joint;','module tb_joint;'+early)
 s=s.replace('.cfg_valid(cfg_valid)', '.cfg_valid(cfg_valid&&admit_a)').replace('.cfg_ready(cfg_ready)', '.cfg_ready(cfg_ready_core)')
 s=s.replace('.publish_valid(publish_valid)', '.publish_valid(pub[0])').replace('.discard_valid(discard_valid)', '.discard_valid(discard[0])').replace('.publish_permit(publish_permit)', '.publish_permit(pc_owned&&!fault&&!k_fault&&!c_fault)').replace('.cfg_permit(cfg_permit)', '.cfg_permit(cfg_permit&&(pc_owned||bound_generation==0))')
 s=s.replace('if(publish_valid&&publish_ready)', 'if(pub[0]&&publish_ready)').replace('if(discard_valid&&discard_ready)', 'if(discard[0]&&discard_ready)')
 extra=''
 for name,prefix,idx in [('recovery_coordinator','k',1),('config_restore_controller','c',2)]:
  ps=ports((HERE/(name+'.sv')).read_text());conn=[]
  specials={'clk':'clk','rst':'rst','cold_rst':'rst','backend_drained':'drained','normal_retired':f'!busy&&!{ "c"if prefix=="k"else"k"}_busy&&!cfg_rsp_valid&&!{ "c_load"if prefix=="k"else"k_cfg"}_rsp_valid','publish_valid':f'pub[{idx}]','discard_valid':f'discard[{idx}]','publish_permit':'pc_owned&&drained&&!fault&&!k_fault&&!c_fault'}
  for d,w,n in ps:
   if d=='input'and n in specials:v=specials[n]
   elif d=='input'and ((prefix=='k'and n=='cfg_valid')or(prefix=='c'and n=='load_valid')):
    extra+=f'reg {prefix}_{n}=0;\n';v=f'{prefix}_{n}&&admit_{prefix}'
   elif d=='output'and ((prefix=='k'and n=='cfg_ready')or(prefix=='c'and n=='load_ready')):
    extra+=f'wire {prefix}_{n},{prefix}_{n}_core;assign {prefix}_{n}={prefix}_{n}_core&&admit_{prefix};\n';v=f'{prefix}_{n}_core'
   else:
    v=prefix+'_'+n;extra+=f'{"reg"if d=="input"else"wire"} {w}{v}'+('=0;\n'if d=='input'else';\n')
   conn.append(f'.{n}({v})')
  extra+=f'{name} {prefix}_engine('+','.join(conn)+');\n'
 extra+='''
assign admit_a=!tx_owned?!pc_owned:(prepare_allowed&&cfg_stage);
assign admit_k=!tx_owned?!pc_owned:(prepare_allowed&&k_cfg_stage);
assign admit_c=!tx_owned?!pc_owned:(prepare_allowed&&c_load_stage);
assign cfg_ready=cfg_ready_core&&admit_a;
wire stage_busy=busy||k_busy||c_busy||cfg_rsp_valid||k_cfg_rsp_valid||c_load_rsp_valid;
wire retired_all=drained&&!stage_busy;
assign prepared_bits={c_staged_valid,k_staged_valid,staged_valid};
assign pub_ready={c_publish_ready,k_publish_ready,publish_ready};
assign discard_ready_bits={c_discard_ready,k_discard_ready,discard_ready};
checkpoint_lease_guard lease(.clk(clk),.rst(rst),.acquire_valid(pc_acquire_valid),.acquire_ready(pc_acquire_ready),.release_valid(pc_release_valid),.release_ready(pc_release_ready),.owned(pc_owned),.healthy(configured&&k_saved_design!=0&&c_saved_design!=0&&!fault&&!k_fault&&!c_fault&&retired_all),.retired(retired_all),.route_retired(1'b1),.no_offers(!cfg_valid&&!k_cfg_valid&&!c_load_valid&&!req_valid),.command_busy(tx_owned||tx_done_valid||stage_busy||(|prepared_bits)),.command_valid(tx_start_valid||tx_commit_valid||tx_cancel_valid||cfg_valid||k_cfg_valid||c_load_valid),.test_reset(1'b0),.safe(pc_safe));
checkpoint_publish_barrier barrier(.clk(clk),.rst(rst),.lease_owned(pc_owned),.retired(retired_all),.stage_busy(stage_busy),.fault(fault||k_fault||c_fault),.manifest_ready(manifest_ready),
.start_valid(tx_start_valid),.start_ready(tx_start_ready),.start_design(D),.start_generation(G2),.start_checkpoint(32'd18),.start_version(32'd4),.start_query(2'd2),.start_price(4'd4),
.commit_valid(tx_commit_valid),.commit_ready(tx_commit_ready),.cancel_valid(tx_cancel_valid),.cancel_ready(tx_cancel_ready),.owned(tx_owned),.prepare_allowed(prepare_allowed),.done_valid(tx_done_valid),.done_ready(tx_done_ready),.done_status(tx_status),
.prepared(prepared_bits),.publish_ready(pub_ready),.discard_ready(discard_ready_bits),.publish_valid(pub),.discard_valid(discard),
.a_design(bound_design),.a_generation(bound_generation),.a_checkpoint(bound_checkpoint),.k_design(k_saved_design),.k_checkpoint(k_saved_checkpoint),.k_version(k_active_version),.k_query(k_active_query),.k_price(k_active_price),.journal_count(k_journal_count),.c_design(c_saved_design),.c_checkpoint(c_saved_checkpoint),.c_version(c_active_version),
.sa_design(staged_design),.sa_generation(staged_generation),.sa_checkpoint(staged_checkpoint),.sk_design(k_staged_design),.sk_checkpoint(k_staged_checkpoint),.sk_version(k_staged_version),.sk_query(k_staged_query),.sk_price(k_staged_price),.sc_design(c_staged_design),.sc_checkpoint(c_staged_checkpoint),.sc_version(c_staged_version));
always @(posedge clk)if(!rst)begin
 if(c_cfg_valid||k_target_reset||k_reconfigure_valid||k_labels_valid||k_a_valid||k_o_valid)$fatal(1,"metadata transaction ran recovery/provider callbacks");
 if(c_abort)$fdisplay(events,"ABORT_CF %0d %0d %0d",cycles,c_saved_checkpoint,c_active_version);
 if(pc_acquire_valid&&pc_acquire_ready)$fdisplay(events,"LEASE %0d A",cycles);
 if(pc_release_valid&&pc_release_ready)$fdisplay(events,"LEASE %0d R",cycles);
 if(k_recover_valid&&k_recover_ready)$fdisplay(events,"KRQ %0d %0d %0d %0d",cycles,k_recover_checkpoint,k_recover_version,k_recover_query);
 if(k_rsp_valid&&k_rsp_ready)$fdisplay(events,"KRR %0d %0d %0d",cycles,k_rsp_status,k_rsp_cookie);
 if(k_cfg_valid&&k_cfg_ready)$fdisplay(events,"KC %0d %0d %0d %0d",cycles,k_cfg_stage,k_cfg_checkpoint,k_cfg_version);
 if(k_cfg_rsp_valid&&k_cfg_rsp_ready)$fdisplay(events,"KF %0d %0d %0d %0d",cycles,k_cfg_status,k_saved_checkpoint,k_journal_count);
 if(c_load_valid&&c_load_ready)$fdisplay(events,"CC %0d %0d %0d %0d",cycles,c_load_stage,c_load_checkpoint,c_load_payload[2240+:32]);
 if(c_load_rsp_valid&&c_load_rsp_ready)$fdisplay(events,"CF %0d %0d %0d %0d",cycles,c_load_status,c_saved_checkpoint,c_active_version);
 if(k_j_valid&&k_j_ready)$fdisplay(events,"J %0d %0d %0d",cycles,k_j_node,k_j_net);
 if(tx_commit_valid&&tx_commit_ready)$fdisplay(events,"COMMIT %0d %b",cycles,pub);
 if(tx_cancel_valid&&tx_cancel_ready)$fdisplay(events,"CANCEL %0d",cycles);
 if(tx_start_valid&&tx_start_ready)$fdisplay(events,"START %0d %0d %0d %016h",cycles,k_saved_checkpoint,k_journal_count,bound_generation);
 if(|pub)$fdisplay(events,"JOIN %0d %b %0d %0d %0d %016h",cycles,pub,k_saved_checkpoint,c_saved_checkpoint,k_journal_count,bound_generation);
 if(|(discard&discard_ready_bits))$fdisplay(events,"DROP %0d %b",cycles,discard&discard_ready_bits);
 if(tx_done_valid&&tx_done_ready)$fdisplay(events,"END %0d %0d %0d %0d %0d %016h",cycles,tx_status,k_saved_checkpoint,c_saved_checkpoint,k_journal_count,bound_generation);
end
task config_k(input bit shadow,input[31:0]cp,v,input integer expected);reg[31:0]old_cp,old_count;begin
 old_cp=k_saved_checkpoint;old_count=k_journal_count;k_cfg_stage=shadow;k_cfg_authoritative=1;k_cfg_design=D;k_cfg_checkpoint=cp;k_cfg_version=v;k_cfg_query=2;k_cfg_price=v[3:0];k_cfg_valid=1;
 do @(posedge clk);while(!k_cfg_ready);@(negedge clk);k_cfg_valid=0;wait(k_cfg_rsp_valid);@(negedge clk);check(k_cfg_status==expected,"coordinator prepare result");
 repeat(5)begin tick();if(shadow)check(k_saved_checkpoint==old_cp&&k_journal_count==old_count&&!k_staged_valid,"coordinator mutated before publication");end
 k_cfg_rsp_ready=1;tick();k_cfg_rsp_ready=0;tick();
end endtask
task config_c(input bit shadow,input[31:0]cp,v,input integer expected);reg[31:0]old_cp;begin
 old_cp=c_saved_checkpoint;c_load_stage=shadow;c_load_authoritative=1;c_load_design=D;c_load_checkpoint=cp;c_load_payload=effective;c_load_payload[2240+:32]=v;c_load_valid=1;
 do @(posedge clk);while(!c_load_ready);@(negedge clk);c_load_valid=0;wait(c_load_rsp_valid);@(negedge clk);check(c_load_status==expected,"config shadow result");
 repeat(5)begin tick();if(shadow)check(c_saved_checkpoint==old_cp&&c_active_payload==effective&&!c_staged_valid,"active config mutated before publication");end
 c_load_rsp_ready=1;tick();c_load_rsp_ready=0;tick();
end endtask
task begin_tx;begin
 pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;check(pc_owned,"real lease acquired");tx_start_valid=1;do @(posedge clk);while(!tx_start_ready);@(negedge clk);tx_start_valid=0;check(tx_owned&&prepare_allowed,"transaction owns lease");
end endtask
task end_tx(input integer expected);begin
 wait(tx_done_valid);@(negedge clk);check(tx_status==expected,"transaction completion");pc_release_valid=1;
 repeat(8)begin tick();check(pc_owned&&!pc_release_ready&&tx_done_valid&&tx_status==expected,"held result retains lease");end
 pc_release_valid=0;tx_done_ready=1;tick();tx_done_ready=0;tick();pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;check(!pc_owned&&!tx_owned,"release after result consumption");
end endtask
initial begin
 events=$fopen("events.txt","w");rst=1;repeat(4)tick();rst=0;cfg_permit=1;tick();
 config_bank(0,G1,17,OLD,0);config_k(0,17,4,0);config_c(0,17,4,0);
 for(integer i=0;i<6;i=i+1)begin k_j_node=warm_nodes[i];k_j_net=2717;k_j_op=1;k_j_valid=1;do @(posedge clk);while(!k_j_ready);@(negedge clk);k_j_valid=0;tick();end
 check(k_journal_count==6&&k_permit_work,"six old journal keys retained");get(G1,17,263946,2717,0,0,0);
 // No lease: a stage request must report rejection, not clear the old baseline.
 config_k(0,18,4,1);config_c(0,18,4,1);config_k(1,18,4,1);config_c(1,18,4,1);check(k_journal_count==6&&k_saved_checkpoint==17&&c_saved_checkpoint==17,"no-lease staging unchanged");
 begin_tx();config_bank(1,G2,18,WARM,0);config_k(1,18,5,1);config_c(1,18,5,1);config_k(1,19,4,0);config_c(1,18,4,0);
 check(prepared_bits==7&&!k_permit_work&&!k_j_ready&&!k_recover_ready,"prepared snapshot freezes coordinator");
 tx_commit_valid=1;do @(posedge clk);while(!tx_commit_ready);@(negedge clk);tx_commit_valid=0;end_tx(1);check(k_journal_count==6&&k_saved_checkpoint==17&&c_saved_checkpoint==17&&bound_generation==G1,"mismatched checkpoint canceled atomically");
 begin_tx();config_bank(1,G2,18,WARM,0);config_k(1,18,4,0);config_c(1,18,4,0);tx_cancel_valid=1;do @(posedge clk);while(!tx_cancel_ready);@(negedge clk);tx_cancel_valid=0;end_tx(2);check(k_journal_count==6&&k_saved_checkpoint==17&&c_saved_checkpoint==17&&bound_generation==G1,"explicit cancel preserves old state");
 begin_tx();config_bank(1,G2,18,WARM,0);config_k(1,18,4,0);config_c(1,18,4,0);
 c_abort=1;tx_commit_valid=1;#1;check(!tx_commit_ready&&pub==0,"CF abort masks joint publication");tick();c_abort=0;tx_commit_valid=0;check(!c_staged_valid&&c_saved_checkpoint==17&&k_journal_count==6,"CF abort leaves active baseline unchanged");
 tx_cancel_valid=1;do @(posedge clk);while(!tx_cancel_ready);@(negedge clk);tx_cancel_valid=0;end_tx(2);check(k_journal_count==6&&k_saved_checkpoint==17&&c_saved_checkpoint==17&&bound_generation==G1,"partial prepared cancellation preserved baseline");
 begin_tx();config_bank(1,G2,18,WARM,0);config_k(1,18,4,0);config_c(1,18,4,0);
 manifest_ready=0;repeat(5)begin tick();check(!tx_commit_ready&&pub==0&&k_journal_count==6,"manifest receipt required");end tx_commit_valid=0;manifest_ready=1;
 start_get(G1,17,263946,2717);wait(rsp_valid);@(negedge clk);tx_commit_valid=1;
 repeat(6)begin tick();check(!tx_commit_ready&&pub==0&&k_journal_count==6&&k_saved_checkpoint==17,"old reply prevents all three publications");end
 finish_get(0,0,0);@(negedge clk);tx_commit_valid=0;end_tx(0);
 check(bound_generation==G2&&bound_checkpoint==18&&k_saved_checkpoint==18&&c_saved_checkpoint==18&&k_journal_count==0&&c_active_payload==effective&&k_active_version==4&&k_active_query==2&&k_active_price==4&&k_permit_work,"all metadata published together");
 // A checkpoint publication may clear the journal, but not the attempt floor.
 k_recover_design=D;k_recover_checkpoint=18;k_recover_version=4;k_recover_query=3;k_recover_price=4;k_recover_cookie=77;k_recover_valid=1;
 do @(posedge clk);while(!k_recover_ready);@(negedge clk);k_recover_valid=0;wait(k_rsp_valid);@(negedge clk);check(k_rsp_status==1&&k_rsp_cookie==77,"attempt floor retained after publication");
 repeat(5)begin tick();check(k_rsp_valid&&k_rsp_status==1&&k_journal_count==0&&k_saved_checkpoint==18,"invalid recovery held without changing baseline");end
 k_rsp_ready=1;tick();k_rsp_ready=0;tick();check(k_active_version==4&&k_active_query==2&&k_active_price==4&&k_permit_work,"rejected recovery preserved context");
 get(G1,17,263946,2717,1,0,0);get(G2,18,263946,2717,0,1,1);get(G2,18,existing[0],existing[1],0,1,1);
 $fdisplay(events,"JOINT_DONE %0d %0d %0d %0d",checks,reads,k_journal_count,k_saved_checkpoint);$fflush(events);$display("CHECKPOINT_JOINT_PASS checks=%0d reads=%0d",checks,reads);$finish;
end
initial begin #2000000;$fatal(1,"timeout");end
endmodule
'''
 for n in ['k_fault','c_fault','c_load_rsp_valid','c_busy']:extra=extra.replace('wire '+n+';\n','')
 return s+extra
if __name__=='__main__':(HERE/'tb_joint.sv').write_text(make())
