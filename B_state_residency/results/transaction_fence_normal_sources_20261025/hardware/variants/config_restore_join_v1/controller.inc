reg cf_load_valid=0,cf_load_rsp_ready=0;wire cf_load_ready,cf_load_rsp_valid,cf_load_status;
wire[5:0]cf_valid,cf_ready,cf_replies,cf_reply_ready,cf_sent,cf_retired;wire[17:0]cf_status;
wire[2303:0]cf_input,cf_payload;wire[3:0]cf_rsp_status;wire[63:0]cf_saved_design;wire[31:0]cf_saved_checkpoint;
assign cf_input[0+:384]={128'd0,q_cfg_revision,q_cfg_nets,q_cfg_nodes,q_cfg_connections,q_cfg_design,q_cfg_base};
assign cf_input[384+:384]={128'd0,g_cfg_edges,g_cfg_nodes,g_cfg_attrs_base,g_cfg_edges_base,g_cfg_offsets_base};
assign cf_input[768+:384]={288'd0,d_cfg_nodes,d_cfg_base};
assign cf_input[1152+:384]={192'd0,t_cfg_columns,t_cfg_rows,t_cfg_columns_base,t_cfg_rows_base};
assign cf_input[1536+:384]={128'd0,owner_cfg_capacity,owner_cfg_nodes,owner_cfg_allocator,owner_cfg_pool,owner_cfg_primary};
assign cf_input[1920+:384]={32'd0,k_cfg_version,cs_cfg_net_count,cs_cfg_nodes,cs_cfg_design_id,cs_cfg_nets,cs_cfg_prices,cs_cfg_history};
assign cf_ready={raw_cs_cfg_ready,raw_owner_cfg_ready,raw_t_cfg_ready,raw_d_cfg_ready,raw_g_cfg_ready,raw_q_cfg_ready}&{6{!rc_block}};
assign cf_replies={cs_cfg_rsp_valid,owner_cfg_rsp_valid,t_cfg_rsp_valid,d_cfg_rsp_valid,g_cfg_rsp_valid,q_cfg_rsp_valid};
assign cf_status={cs_cfg_status,owner_cfg_status,t_cfg_status,d_cfg_status,g_cfg_status,q_cfg_status};
config_restore_controller #(.MAX_CYCLES(1048576))config_restore(
 .clk(clk),.rst(k_cold_rst),.abort(1'b0),.backend_drained(label_drained&&owner_drained),.normal_retired(k_normal_retired),
 .load_valid(cf_load_valid),.load_ready(cf_load_ready),.load_authoritative(1'b1),.load_payload(cf_input),.load_design(k_saved_design),.load_checkpoint(k_saved_checkpoint),.load_rsp_valid(cf_load_rsp_valid),.load_rsp_ready(cf_load_rsp_ready),.load_status(cf_load_status),
 .start_valid(k_rcfg_valid),.start_ready(),.start_design(k_saved_design),.start_checkpoint(k_saved_checkpoint),.start_cookie(32'hf0010001),.start_version(k_new_version),.start_price(k_new_price),
 .cfg_valid(cf_valid),.cfg_ready(cf_ready),.cfg_payload(cf_payload),.cfg_rsp_valid(cf_replies),.cfg_rsp_ready(cf_reply_ready),.cfg_status(cf_status),
 .rsp_valid(cf_rsp_valid),.rsp_ready(!k_rcfg_valid),.rsp_status(cf_rsp_status),.rsp_cookie(cf_rsp_cookie),.busy(cf_busy),.fault(cf_fault),.sent(cf_sent),.retired(cf_retired),.saved_design(cf_saved_design),.saved_checkpoint(cf_saved_checkpoint));
assign k_rcfg_done=cf_rsp_valid;
