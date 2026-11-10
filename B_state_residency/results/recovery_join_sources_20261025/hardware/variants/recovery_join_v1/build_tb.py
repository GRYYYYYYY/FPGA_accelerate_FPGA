from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def make():
 s=(ROOT/'hardware/variants/route_recovery_v1/tb_route_recovery.sv').read_text()
 s=s.replace('reg recover_open=1,recovering=0;', 'wire recover_open;reg recovering=0;reg k_cold_rst=1,k_normal_retired=1;wire k_target_reset;')
 s=s.replace('reg[31:0]journal[0:31];integer journal_count=0,ji,observed_refs=0,repairs=0;', 'integer repairs=0;')
 s=s.replace('reg  rst=0;', 'reg bench_rst=0;wire rst=bench_rst||k_target_reset;')
 assert s.count('.backend_drained(label_drained&&owner_drained)')==1
 s=s.replace('.backend_drained(label_drained&&owner_drained)', '.backend_drained(label_drained&&owner_drained),.j_valid(k_j_valid),.j_ready(k_j_ready),.j_node(k_j_node),.j_net(k_j_net),.j_op(k_j_op)')
 for port,old,new in [
  ('h_o_valid','host_owner_req_valid','k_busy?k_o_valid:host_owner_req_valid'),('h_o_op','host_owner_req_op','k_busy?k_o_op:host_owner_req_op'),
  ('h_o_node','host_owner_req_node','k_busy?k_o_node:host_owner_req_node'),('h_o_net','host_owner_req_net','k_busy?k_o_net:host_owner_req_net'),('h_o_cookie','host_owner_req_cookie','k_busy?k_o_cookie:host_owner_req_cookie'),
  ('h_o_ready','host_owner_req_ready','mux_h_o_ready'),('h_o_rsp_valid','host_owner_rsp_valid','mux_h_o_rsp_valid'),('h_o_rsp_ready','host_owner_rsp_ready','k_busy?k_o_rsp_ready:host_owner_rsp_ready')]:
  needle='.'+port+'('+old+')';assert needle in s,needle;s=s.replace(needle,'.'+port+'('+new+')')
 needle='route_commit_host_adapter #';s=s.replace(needle,(Path(__file__).parent/'coordinator.inc').read_text()+'\n'+needle,1)
 a=s.index('always @(posedge clk)if(!rst&&armed&&!recovering&&route_join.o_valid');b=s.index('task configure_all;',a);s=s[:a]+s[b:]
 a=s.index('task recovery_owner(');b=s.index('initial begin\n trace=$fopen',a);s=s[:a]+'''task install_checkpoint;begin
 @(negedge clk);k_cfg_valid=1;do @(posedge clk);while(!k_cfg_ready);@(negedge clk);k_cfg_valid=0;
 wait(k_cfg_rsp_valid);@(negedge clk);if(k_cfg_status)$fatal(1,"checkpoint install");k_cfg_rsp_ready=1;@(negedge clk);k_cfg_rsp_ready=0;
 $fdisplay(trace,"KC %0d %0d",cycles,k_saved_checkpoint);
end endtask
'''+s[b:]
 s=s.replace(' rst=1;design_id=', ' bench_rst=1;k_cold_rst=1;design_id=').replace('repeat(5)@(negedge clk);rst=0;', 'repeat(5)@(negedge clk);bench_rst=0;k_cold_rst=0;\n install_checkpoint;')
 # The RTL coordinator, not the TB, now drives reset and owner repair.
 a=s.index(' // No reset until both protocol observers');b=s.index(' control(0);\n // Probe fresh',a)
 s=s[:a]+''' k_rec_valid=1;recovering=1;armed=0;injected_abort=0;injected_drift=0;
 host_ctrl_valid=0;host_io_valid=0;host_owner_req_valid=0;host_design_req_valid=0;expand_valid=0;seed_valid=0;
 q_cfg_valid=0;g_cfg_valid=0;d_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;cs_cfg_valid=0;
 do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rcfg_valid);@(negedge clk);
 restore_epoch=k_new_query;restore_version=k_new_version;cs_cfg_version=k_new_version;
 rc_req_valid=1;expand_valid=1;seed_valid=1;
 configure_all;k_rcfg_done=1;@(negedge clk);k_rcfg_done=0;
 wait(k_labels_valid);@(negedge clk);repairs=k_corrected;$fdisplay(trace,"AUTH %0d %0d",cycles,k_corrected);
'''+s[b:]
 a=s.index(' rc_req_valid=0;expand_valid=0;seed_valid=0;recover_open=1;');s=s[:a]+s[a:].replace(' rc_req_valid=0;expand_valid=0;seed_valid=0;recover_open=1;', ''' rc_req_valid=0;expand_valid=0;seed_valid=0;k_labels_done=1;
 wait(k_rsp_valid);@(negedge clk);if(k_rsp_status||k_rsp_cookie!=32'hc0010001||k_fault||k_count!=0)$fatal(1,"coordinator recovery result");
 repeat(5)begin @(negedge clk);if(recover_open||!k_rsp_valid)$fatal(1,"coordinator response gate");end
 $fdisplay(trace,"KD %0d %0d %0d",cycles,k_rsp_status,k_corrected);
 k_labels_done=0;k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;wait(recover_open);''',1)
 needle=' control(1);control(2);\n if(fault||rc_fault||repairs!='
 assert needle in s;s=s.replace(needle,''' k_checkpoint=18;k_cfg_version=restore_version;k_cfg_query=restore_epoch;k_cfg_price=restore_version[3:0];install_checkpoint;
 if(k_count||k_fault)$fatal(1,"committed checkpoint publication");
 control(1);control(2);
 if(fault||rc_fault||repairs!=''',1)
 s=s.replace('if(fault&&!armed)$fatal','if(fault&&!armed&&(!recovering||recover_open))$fatal')
 s=s.replace('ROUTE_RECOVERY_PASS', 'RECOVERY_JOIN_PASS')
 s=s.replace('initial begin\n trace=$fopen',(Path(__file__).parent/'observer.inc').read_text()+'\ninitial begin\n trace=$fopen',1)
 return s
if __name__=='__main__':(Path(__file__).parent/'tb_recovery_join.sv').write_text(make())
