reg k_cfg_valid=0,k_cfg_rsp_ready=0,k_rec_valid=0,k_rsp_ready=0,k_rcfg_done=0,k_labels_done=0;
wire k_cfg_ready,k_cfg_rsp_valid,k_cfg_status,k_rec_ready,k_rsp_valid,k_fault,k_busy,k_permit;
reg[31:0]k_checkpoint=17,k_cfg_version=3;reg[1:0]k_cfg_query=1;reg[3:0]k_cfg_price=3;
wire[3:0]k_rsp_status;wire[31:0]k_rsp_cookie,k_corrected,k_count,k_new_version,k_saved_checkpoint;wire[63:0]k_saved_design;wire[1:0]k_new_query;wire[3:0]k_new_price;
wire k_rcfg_valid,k_labels_valid,k_full,k_j_valid,k_j_ready;wire[31:0]k_j_node,k_j_net;wire[2:0]k_j_op;
wire k_a_valid,k_a_rsp_ready;reg k_a_ready=0,k_a_rsp_valid=0;wire[31:0]k_a_node,k_a_net,k_a_cookie,k_a_checkpoint;wire[63:0]k_a_design;
reg[31:0]k_a_rsp_cookie=0,k_a_rsp_checkpoint=0,k_a_refs=0,k_a_occ=0;reg[63:0]k_a_rsp_design=0;reg[3:0]k_a_status=0;
wire k_o_valid,k_o_ready,k_o_rsp_valid,k_o_rsp_ready;wire[2:0]k_o_op;wire[31:0]k_o_node,k_o_net,k_o_cookie;
wire mux_h_o_ready,mux_h_o_rsp_valid;
wire[31:0]journal_count=k_count;
assign recover_open=k_permit;
assign host_owner_req_ready=!k_busy&&mux_h_o_ready;
assign host_owner_rsp_valid=!k_busy&&mux_h_o_rsp_valid;
assign k_o_ready=k_busy&&mux_h_o_ready;
assign k_o_rsp_valid=k_busy&&mux_h_o_rsp_valid;
recovery_coordinator #(.ENTRIES(32),.RESET_HOLD(5),.MAX_CYCLES(1048576)) recovery_ctl(
 .clk(clk),.cold_rst(k_cold_rst),.abort(1'b0),.backend_drained(label_drained&&owner_drained),.normal_retired(k_normal_retired),
 .cfg_valid(k_cfg_valid),.cfg_ready(k_cfg_ready),.cfg_authoritative(1'b1),.cfg_design(design_id),.cfg_checkpoint(k_checkpoint),.cfg_version(k_cfg_version),.cfg_query(k_cfg_query),.cfg_price(k_cfg_price),
 .cfg_rsp_valid(k_cfg_rsp_valid),.cfg_rsp_ready(k_cfg_rsp_ready),.cfg_status(k_cfg_status),
 .j_valid(k_j_valid),.j_ready(k_j_ready),.j_node(k_j_node),.j_net(k_j_net),.j_op(k_j_op),.journal_count(k_count),.journal_full(k_full),.permit_work(k_permit),
 .recover_valid(k_rec_valid),.recover_ready(k_rec_ready),.recover_cookie(32'hc0010001),.recover_checkpoint(32'd17),.recover_version(32'd4),.recover_design(design_id),.recover_query(2'd2),.recover_price(4'd4),
 .target_reset(k_target_reset),.reconfigure_valid(k_rcfg_valid),.reconfigure_done(k_rcfg_done),.labels_valid(k_labels_valid),.labels_done(k_labels_done),
 .saved_design(k_saved_design),.saved_checkpoint(k_saved_checkpoint),.new_version(k_new_version),.new_query(k_new_query),.new_price(k_new_price),
 .rsp_valid(k_rsp_valid),.rsp_ready(k_rsp_ready),.rsp_status(k_rsp_status),.rsp_cookie(k_rsp_cookie),.rsp_corrected(k_corrected),.busy(k_busy),.fault(k_fault),
 .a_valid(k_a_valid),.a_ready(k_a_ready),.a_node(k_a_node),.a_net(k_a_net),.a_cookie(k_a_cookie),.a_checkpoint(k_a_checkpoint),.a_design(k_a_design),
 .a_rsp_valid(k_a_rsp_valid),.a_rsp_ready(k_a_rsp_ready),.a_status(k_a_status),.a_rsp_cookie(k_a_rsp_cookie),.a_rsp_checkpoint(k_a_rsp_checkpoint),.a_rsp_design(k_a_rsp_design),.a_refs(k_a_refs),.a_occupancy(k_a_occ),
 .o_valid(k_o_valid),.o_ready(k_o_ready),.o_op(k_o_op),.o_node(k_o_node),.o_net(k_o_net),.o_cookie(k_o_cookie),
 .o_rsp_valid(k_o_rsp_valid),.o_rsp_ready(k_o_rsp_ready),.o_status(host_owner_rsp_status),.o_rsp_cookie(host_owner_rsp_cookie),.o_count(host_owner_rsp_count),.o_occupancy(host_owner_rsp_occupancy));
reg[31:0]authority_node[0:5],authority_net[0:5],authority_refs0[0:5],authority_occ0[0:5],authority_refs1[0:5],authority_occ1[0:5];
integer auth_fd,auth_rc,auth_i,auth_match,auth_delay=0;string auth_path;
initial begin
 if(!$value$plusargs("authority=%s",auth_path))$fatal(1,"authority path");auth_fd=$fopen(auth_path,"r");if(!auth_fd)$fatal(1,"authority file");
 for(auth_i=0;auth_i<6;auth_i=auth_i+1)begin
  auth_rc=$fscanf(auth_fd,"%d %d %d %d %d %d",authority_node[auth_i],authority_net[auth_i],authority_refs0[auth_i],authority_occ0[auth_i],authority_refs1[auth_i],authority_occ1[auth_i]);if(auth_rc!=6)$fatal(1,"authority row");
 end
end
