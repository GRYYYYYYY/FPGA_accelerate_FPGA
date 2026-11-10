assign f_route_payload={30'd0,rc_req_sequence,32'd2717,rc_req_sink,32'd65185,rc_req_cookie,rc_req_slot,rc_req_op};
transaction_fence #(.LANES(16),.REQ_BITS(2432),.RSP_BITS(256),.ADMIN_FIRST(14),.CALLBACK_MASK(16'h037f))fence(
 .clk(clk),.rst(k_cold_rst),.work_permit(k_permit),.normal_fault(fault||rc_fault||k_fault||cf_fault||lr_fault),.backend_drained(f_all_drained),.backend_idle(f_backend_idle),.route_block(rc_block),
 .s_valid(f_sv),.s_ready(f_sr),.s_payload(f_sp),.s_rsp_valid(f_srv),.s_rsp_ready(f_srr),.s_rsp_payload(f_srp),
 .cb_valid(f_cbv),.cb_ready(f_cbr),.cb_payload(f_cbp),.cb_rsp_valid(f_cbrv),.cb_rsp_ready(f_cbrr),.cb_rsp_payload(f_cbrp),
 .d_valid(f_dv),.d_ready(f_dr),.d_payload(f_dp),.d_rsp_valid(f_drv),.d_rsp_ready(f_drr),.d_rsp_payload(f_drp),
 .route_valid(rc_req_valid),.route_ready(rc_req_ready),.route_payload(f_route_payload),.route_rsp_valid(rc_rsp_valid),.route_rsp_ready(rc_rsp_ready),
 .backend_route_valid(f_broute_valid),.backend_route_ready(f_broute_ready),.backend_route_payload(f_broute_payload),.backend_route_rsp_valid(f_broute_rsp_valid),.backend_route_rsp_ready(f_broute_rsp_ready),.route_error(rc_rsp_status!=0),
 .recover_valid(k_rec_valid),.recover_ready(k_rec_ready),.backend_recover_valid(f_brecover_valid),.backend_recover_ready(f_brecover_ready),
 .recover_rsp_valid(k_rsp_valid),.recover_rsp_ready(k_rsp_ready),.backend_recover_rsp_valid(f_brecover_rsp_valid),.backend_recover_rsp_ready(f_brecover_rsp_ready),.recover_error(k_rsp_status!=0),
 .normal_retired(f_normal_retired),.recovery_owned(f_recovery_owned),.fault(f_fault),.phase(f_phase),.callback_pending(f_pending));
