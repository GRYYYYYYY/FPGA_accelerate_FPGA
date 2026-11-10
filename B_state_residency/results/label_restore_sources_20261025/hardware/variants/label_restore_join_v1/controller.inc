reg lr_s_valid=0;wire lr_start_valid=k_labels_valid,lr_rsp_ready=!k_labels_valid;wire lr_start_ready,lr_s_ready;
reg[31:0]lr_s_node=0;reg[159:0]lr_s_payload=0;reg lr_s_last=0;wire[3:0]lr_rsp_status;wire[31:0]lr_written,lr_verified;
wire lr_c_valid,lr_c_ready,lr_c_rsp_ready;wire[1:0]lr_c_op,lr_c_query;wire[3:0]lr_c_price;wire[31:0]lr_c_version;
wire lr_l_valid,lr_l_ready,lr_l_write,lr_l_rsp_ready,lr_l_rsp_valid,mux_h_l_ready,mux_h_l_rsp_valid;
wire[31:0]lr_l_node,lr_l_value;wire[2:0]lr_l_field;
assign lr_c_ready=lr_busy&&!rc_block&&raw_host_ctrl_ready;
assign lr_l_ready=lr_busy&&mux_h_l_ready;assign lr_l_rsp_valid=lr_busy&&mux_h_l_rsp_valid;
assign host_io_ready=!lr_busy&&mux_h_l_ready;assign host_io_rsp_valid=!lr_busy&&mux_h_l_rsp_valid;
label_restore_controller #(.MAX_RECORDS(512),.MAX_CYCLES(1048576))label_restore(
 .clk(clk),.rst(k_cold_rst),.abort(1'b0),.backend_drained(label_drained&&owner_drained),
 .start_valid(lr_start_valid),.start_ready(lr_start_ready),.start_design(k_saved_design),.expected_design(design_id),.start_checkpoint(k_saved_checkpoint),.expected_checkpoint(32'd17),
 .start_cookie(32'he0010001),.start_count(32'd328),.start_nodes(32'd9089009),.start_probe(32'd150697),.start_version(k_new_version),.start_query(k_new_query),.start_price(k_new_price),
 .s_valid(lr_s_valid),.s_ready(lr_s_ready),.s_node(lr_s_node),.s_cookie(32'he0010001),.s_payload(lr_s_payload),.s_last(lr_s_last),
 .rsp_valid(lr_rsp_valid),.rsp_ready(lr_rsp_ready),.rsp_status(lr_rsp_status),.rsp_cookie(lr_rsp_cookie),.written(lr_written),.verified(lr_verified),.busy(lr_busy),.fault(lr_fault),
 .c_valid(lr_c_valid),.c_ready(lr_c_ready),.c_op(lr_c_op),.c_query(lr_c_query),.c_price(lr_c_price),.c_version(lr_c_version),.c_rsp_valid(host_ctrl_rsp_valid&&lr_busy),.c_rsp_ready(lr_c_rsp_ready),.c_status(host_ctrl_status),
 .l_valid(lr_l_valid),.l_ready(lr_l_ready),.l_write(lr_l_write),.l_node(lr_l_node),.l_value(lr_l_value),.l_field(lr_l_field),.l_rsp_valid(lr_l_rsp_valid),.l_rsp_ready(lr_l_rsp_ready),.l_status(host_io_status),.l_present(host_io_present),.l_payload(host_io_payload));

assign k_labels_done=lr_rsp_valid;
