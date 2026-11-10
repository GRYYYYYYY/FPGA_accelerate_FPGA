`timescale 1ns/1ps
`default_nettype none
module stage_static_cp_shadow;
localparam integer SHIFT_NS=200;
integer checks=0,reset_edges=0;
time last_checked=0;
reg armed=0;
// Nonblocking delayed assignments preserve every transition (transport).
reg drive_baseline_retired;
initial drive_baseline_retired <= #SHIFT_NS tb_candidate_offer.system.baseline_retired;
always @(tb_candidate_offer.system.baseline_retired) drive_baseline_retired <= #SHIFT_NS tb_candidate_offer.system.baseline_retired;
reg drive_restore_seed_enable;
initial drive_restore_seed_enable <= #SHIFT_NS tb_candidate_offer.system.restore_seed_enable;
always @(tb_candidate_offer.system.restore_seed_enable) drive_restore_seed_enable <= #SHIFT_NS tb_candidate_offer.system.restore_seed_enable;
reg drive_baseline_permit;
initial drive_baseline_permit <= #SHIFT_NS tb_candidate_offer.system.baseline_permit;
always @(tb_candidate_offer.system.baseline_permit) drive_baseline_permit <= #SHIFT_NS tb_candidate_offer.system.baseline_permit;
reg [63:0] drive_baseline_epoch;
initial drive_baseline_epoch <= #SHIFT_NS tb_candidate_offer.system.baseline_epoch;
always @(tb_candidate_offer.system.baseline_epoch) drive_baseline_epoch <= #SHIFT_NS tb_candidate_offer.system.baseline_epoch;
wire actual_baseline_req_valid;
reg expected_baseline_req_valid;
initial expected_baseline_req_valid <= #SHIFT_NS tb_candidate_offer.system.baseline_req_valid;
always @(tb_candidate_offer.system.baseline_req_valid) expected_baseline_req_valid <= #SHIFT_NS tb_candidate_offer.system.baseline_req_valid;
reg drive_baseline_req_ready;
initial drive_baseline_req_ready <= #SHIFT_NS tb_candidate_offer.system.baseline_req_ready;
always @(tb_candidate_offer.system.baseline_req_ready) drive_baseline_req_ready <= #SHIFT_NS tb_candidate_offer.system.baseline_req_ready;
wire [31:0] actual_baseline_req_node;
reg [31:0] expected_baseline_req_node;
initial expected_baseline_req_node <= #SHIFT_NS tb_candidate_offer.system.baseline_req_node;
always @(tb_candidate_offer.system.baseline_req_node) expected_baseline_req_node <= #SHIFT_NS tb_candidate_offer.system.baseline_req_node;
wire [63:0] actual_baseline_req_epoch;
reg [63:0] expected_baseline_req_epoch;
initial expected_baseline_req_epoch <= #SHIFT_NS tb_candidate_offer.system.baseline_req_epoch;
always @(tb_candidate_offer.system.baseline_req_epoch) expected_baseline_req_epoch <= #SHIFT_NS tb_candidate_offer.system.baseline_req_epoch;
reg drive_baseline_rsp_valid;
initial drive_baseline_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.baseline_rsp_valid;
always @(tb_candidate_offer.system.baseline_rsp_valid) drive_baseline_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.baseline_rsp_valid;
wire actual_baseline_rsp_ready;
reg expected_baseline_rsp_ready;
initial expected_baseline_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.baseline_rsp_ready;
always @(tb_candidate_offer.system.baseline_rsp_ready) expected_baseline_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.baseline_rsp_ready;
reg [3:0] drive_baseline_rsp_status;
initial drive_baseline_rsp_status <= #SHIFT_NS tb_candidate_offer.system.baseline_rsp_status;
always @(tb_candidate_offer.system.baseline_rsp_status) drive_baseline_rsp_status <= #SHIFT_NS tb_candidate_offer.system.baseline_rsp_status;
reg [31:0] drive_baseline_rsp_node;
initial drive_baseline_rsp_node <= #SHIFT_NS tb_candidate_offer.system.baseline_rsp_node;
always @(tb_candidate_offer.system.baseline_rsp_node) drive_baseline_rsp_node <= #SHIFT_NS tb_candidate_offer.system.baseline_rsp_node;
reg [63:0] drive_baseline_rsp_epoch;
initial drive_baseline_rsp_epoch <= #SHIFT_NS tb_candidate_offer.system.baseline_rsp_epoch;
always @(tb_candidate_offer.system.baseline_rsp_epoch) drive_baseline_rsp_epoch <= #SHIFT_NS tb_candidate_offer.system.baseline_rsp_epoch;
reg [159:0] drive_baseline_rsp_payload;
initial drive_baseline_rsp_payload <= #SHIFT_NS tb_candidate_offer.system.baseline_rsp_payload;
always @(tb_candidate_offer.system.baseline_rsp_payload) drive_baseline_rsp_payload <= #SHIFT_NS tb_candidate_offer.system.baseline_rsp_payload;
reg drive_wm_enable;
initial drive_wm_enable <= #SHIFT_NS tb_candidate_offer.system.wm_enable;
always @(tb_candidate_offer.system.wm_enable) drive_wm_enable <= #SHIFT_NS tb_candidate_offer.system.wm_enable;
reg [31:0] drive_wm_source_version;
initial drive_wm_source_version <= #SHIFT_NS tb_candidate_offer.system.wm_source_version;
always @(tb_candidate_offer.system.wm_source_version) drive_wm_source_version <= #SHIFT_NS tb_candidate_offer.system.wm_source_version;
reg [1:0] drive_wm_source_query;
initial drive_wm_source_query <= #SHIFT_NS tb_candidate_offer.system.wm_source_query;
always @(tb_candidate_offer.system.wm_source_query) drive_wm_source_query <= #SHIFT_NS tb_candidate_offer.system.wm_source_query;
reg [3:0] drive_wm_source_price;
initial drive_wm_source_price <= #SHIFT_NS tb_candidate_offer.system.wm_source_price;
always @(tb_candidate_offer.system.wm_source_price) drive_wm_source_price <= #SHIFT_NS tb_candidate_offer.system.wm_source_price;
reg [31:0] drive_wm_path_crc;
initial drive_wm_path_crc <= #SHIFT_NS tb_candidate_offer.system.wm_path_crc;
always @(tb_candidate_offer.system.wm_path_crc) drive_wm_path_crc <= #SHIFT_NS tb_candidate_offer.system.wm_path_crc;
reg [31:0] drive_wm_query_crc;
initial drive_wm_query_crc <= #SHIFT_NS tb_candidate_offer.system.wm_query_crc;
always @(tb_candidate_offer.system.wm_query_crc) drive_wm_query_crc <= #SHIFT_NS tb_candidate_offer.system.wm_query_crc;
wire actual_wm_owned;
reg expected_wm_owned;
initial expected_wm_owned <= #SHIFT_NS tb_candidate_offer.system.wm_owned;
always @(tb_candidate_offer.system.wm_owned) expected_wm_owned <= #SHIFT_NS tb_candidate_offer.system.wm_owned;
wire actual_wm_fault;
reg expected_wm_fault;
initial expected_wm_fault <= #SHIFT_NS tb_candidate_offer.system.wm_fault;
always @(tb_candidate_offer.system.wm_fault) expected_wm_fault <= #SHIFT_NS tb_candidate_offer.system.wm_fault;
wire actual_wm_joined;
reg expected_wm_joined;
initial expected_wm_joined <= #SHIFT_NS tb_candidate_offer.system.wm_joined;
always @(tb_candidate_offer.system.wm_joined) expected_wm_joined <= #SHIFT_NS tb_candidate_offer.system.wm_joined;
wire [2:0] actual_wm_receipts;
reg [2:0] expected_wm_receipts;
initial expected_wm_receipts <= #SHIFT_NS tb_candidate_offer.system.wm_receipts;
always @(tb_candidate_offer.system.wm_receipts) expected_wm_receipts <= #SHIFT_NS tb_candidate_offer.system.wm_receipts;
reg drive_ap_valid;
initial drive_ap_valid <= #SHIFT_NS tb_candidate_offer.system.ap_valid;
always @(tb_candidate_offer.system.ap_valid) drive_ap_valid <= #SHIFT_NS tb_candidate_offer.system.ap_valid;
reg drive_ap_rsp_ready;
initial drive_ap_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.ap_rsp_ready;
always @(tb_candidate_offer.system.ap_rsp_ready) drive_ap_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.ap_rsp_ready;
wire actual_ap_ready;
reg expected_ap_ready;
initial expected_ap_ready <= #SHIFT_NS tb_candidate_offer.system.ap_ready;
always @(tb_candidate_offer.system.ap_ready) expected_ap_ready <= #SHIFT_NS tb_candidate_offer.system.ap_ready;
wire actual_ap_rsp_valid;
reg expected_ap_rsp_valid;
initial expected_ap_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.ap_rsp_valid;
always @(tb_candidate_offer.system.ap_rsp_valid) expected_ap_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.ap_rsp_valid;
reg [63:0] drive_ap_design;
initial drive_ap_design <= #SHIFT_NS tb_candidate_offer.system.ap_design;
always @(tb_candidate_offer.system.ap_design) drive_ap_design <= #SHIFT_NS tb_candidate_offer.system.ap_design;
reg [63:0] drive_ap_generation;
initial drive_ap_generation <= #SHIFT_NS tb_candidate_offer.system.ap_generation;
always @(tb_candidate_offer.system.ap_generation) drive_ap_generation <= #SHIFT_NS tb_candidate_offer.system.ap_generation;
reg [31:0] drive_ap_checkpoint;
initial drive_ap_checkpoint <= #SHIFT_NS tb_candidate_offer.system.ap_checkpoint;
always @(tb_candidate_offer.system.ap_checkpoint) drive_ap_checkpoint <= #SHIFT_NS tb_candidate_offer.system.ap_checkpoint;
reg [31:0] drive_ap_node;
initial drive_ap_node <= #SHIFT_NS tb_candidate_offer.system.ap_node;
always @(tb_candidate_offer.system.ap_node) drive_ap_node <= #SHIFT_NS tb_candidate_offer.system.ap_node;
reg [31:0] drive_ap_net;
initial drive_ap_net <= #SHIFT_NS tb_candidate_offer.system.ap_net;
always @(tb_candidate_offer.system.ap_net) drive_ap_net <= #SHIFT_NS tb_candidate_offer.system.ap_net;
reg [31:0] drive_ap_cookie;
initial drive_ap_cookie <= #SHIFT_NS tb_candidate_offer.system.ap_cookie;
always @(tb_candidate_offer.system.ap_cookie) drive_ap_cookie <= #SHIFT_NS tb_candidate_offer.system.ap_cookie;
wire [63:0] actual_ap_rsp_design;
reg [63:0] expected_ap_rsp_design;
initial expected_ap_rsp_design <= #SHIFT_NS tb_candidate_offer.system.ap_rsp_design;
always @(tb_candidate_offer.system.ap_rsp_design) expected_ap_rsp_design <= #SHIFT_NS tb_candidate_offer.system.ap_rsp_design;
wire [63:0] actual_ap_rsp_generation;
reg [63:0] expected_ap_rsp_generation;
initial expected_ap_rsp_generation <= #SHIFT_NS tb_candidate_offer.system.ap_rsp_generation;
always @(tb_candidate_offer.system.ap_rsp_generation) expected_ap_rsp_generation <= #SHIFT_NS tb_candidate_offer.system.ap_rsp_generation;
wire [31:0] actual_ap_rsp_checkpoint;
reg [31:0] expected_ap_rsp_checkpoint;
initial expected_ap_rsp_checkpoint <= #SHIFT_NS tb_candidate_offer.system.ap_rsp_checkpoint;
always @(tb_candidate_offer.system.ap_rsp_checkpoint) expected_ap_rsp_checkpoint <= #SHIFT_NS tb_candidate_offer.system.ap_rsp_checkpoint;
wire [31:0] actual_ap_rsp_cookie;
reg [31:0] expected_ap_rsp_cookie;
initial expected_ap_rsp_cookie <= #SHIFT_NS tb_candidate_offer.system.ap_rsp_cookie;
always @(tb_candidate_offer.system.ap_rsp_cookie) expected_ap_rsp_cookie <= #SHIFT_NS tb_candidate_offer.system.ap_rsp_cookie;
wire [31:0] actual_ap_refs;
reg [31:0] expected_ap_refs;
initial expected_ap_refs <= #SHIFT_NS tb_candidate_offer.system.ap_refs;
always @(tb_candidate_offer.system.ap_refs) expected_ap_refs <= #SHIFT_NS tb_candidate_offer.system.ap_refs;
wire [31:0] actual_ap_occ;
reg [31:0] expected_ap_occ;
initial expected_ap_occ <= #SHIFT_NS tb_candidate_offer.system.ap_occ;
always @(tb_candidate_offer.system.ap_occ) expected_ap_occ <= #SHIFT_NS tb_candidate_offer.system.ap_occ;
wire [3:0] actual_ap_status;
reg [3:0] expected_ap_status;
initial expected_ap_status <= #SHIFT_NS tb_candidate_offer.system.ap_status;
always @(tb_candidate_offer.system.ap_status) expected_ap_status <= #SHIFT_NS tb_candidate_offer.system.ap_status;
reg drive_jp_start;
initial drive_jp_start <= #SHIFT_NS tb_candidate_offer.system.jp_start;
always @(tb_candidate_offer.system.jp_start) drive_jp_start <= #SHIFT_NS tb_candidate_offer.system.jp_start;
wire actual_jp_start_ready;
reg expected_jp_start_ready;
initial expected_jp_start_ready <= #SHIFT_NS tb_candidate_offer.system.jp_start_ready;
always @(tb_candidate_offer.system.jp_start_ready) expected_jp_start_ready <= #SHIFT_NS tb_candidate_offer.system.jp_start_ready;
reg drive_jp_commit;
initial drive_jp_commit <= #SHIFT_NS tb_candidate_offer.system.jp_commit;
always @(tb_candidate_offer.system.jp_commit) drive_jp_commit <= #SHIFT_NS tb_candidate_offer.system.jp_commit;
wire actual_jp_commit_ready;
reg expected_jp_commit_ready;
initial expected_jp_commit_ready <= #SHIFT_NS tb_candidate_offer.system.jp_commit_ready;
always @(tb_candidate_offer.system.jp_commit_ready) expected_jp_commit_ready <= #SHIFT_NS tb_candidate_offer.system.jp_commit_ready;
reg drive_jp_cancel;
initial drive_jp_cancel <= #SHIFT_NS tb_candidate_offer.system.jp_cancel;
always @(tb_candidate_offer.system.jp_cancel) drive_jp_cancel <= #SHIFT_NS tb_candidate_offer.system.jp_cancel;
wire actual_jp_cancel_ready;
reg expected_jp_cancel_ready;
initial expected_jp_cancel_ready <= #SHIFT_NS tb_candidate_offer.system.jp_cancel_ready;
always @(tb_candidate_offer.system.jp_cancel_ready) expected_jp_cancel_ready <= #SHIFT_NS tb_candidate_offer.system.jp_cancel_ready;
wire actual_jp_owned;
reg expected_jp_owned;
initial expected_jp_owned <= #SHIFT_NS tb_candidate_offer.system.jp_owned;
always @(tb_candidate_offer.system.jp_owned) expected_jp_owned <= #SHIFT_NS tb_candidate_offer.system.jp_owned;
wire actual_jp_done;
reg expected_jp_done;
initial expected_jp_done <= #SHIFT_NS tb_candidate_offer.system.jp_done;
always @(tb_candidate_offer.system.jp_done) expected_jp_done <= #SHIFT_NS tb_candidate_offer.system.jp_done;
reg drive_jp_done_ready;
initial drive_jp_done_ready <= #SHIFT_NS tb_candidate_offer.system.jp_done_ready;
always @(tb_candidate_offer.system.jp_done_ready) drive_jp_done_ready <= #SHIFT_NS tb_candidate_offer.system.jp_done_ready;
wire [1:0] actual_jp_result;
reg [1:0] expected_jp_result;
initial expected_jp_result <= #SHIFT_NS tb_candidate_offer.system.jp_result;
always @(tb_candidate_offer.system.jp_result) expected_jp_result <= #SHIFT_NS tb_candidate_offer.system.jp_result;
reg drive_jp_manifest_ready;
initial drive_jp_manifest_ready <= #SHIFT_NS tb_candidate_offer.system.jp_manifest_ready;
always @(tb_candidate_offer.system.jp_manifest_ready) drive_jp_manifest_ready <= #SHIFT_NS tb_candidate_offer.system.jp_manifest_ready;
reg [63:0] drive_jp_generation;
initial drive_jp_generation <= #SHIFT_NS tb_candidate_offer.system.jp_generation;
always @(tb_candidate_offer.system.jp_generation) drive_jp_generation <= #SHIFT_NS tb_candidate_offer.system.jp_generation;
reg [63:0] drive_jp_design;
initial drive_jp_design <= #SHIFT_NS tb_candidate_offer.system.jp_design;
always @(tb_candidate_offer.system.jp_design) drive_jp_design <= #SHIFT_NS tb_candidate_offer.system.jp_design;
reg [31:0] drive_jp_checkpoint;
initial drive_jp_checkpoint <= #SHIFT_NS tb_candidate_offer.system.jp_checkpoint;
always @(tb_candidate_offer.system.jp_checkpoint) drive_jp_checkpoint <= #SHIFT_NS tb_candidate_offer.system.jp_checkpoint;
reg [31:0] drive_jp_version;
initial drive_jp_version <= #SHIFT_NS tb_candidate_offer.system.jp_version;
always @(tb_candidate_offer.system.jp_version) drive_jp_version <= #SHIFT_NS tb_candidate_offer.system.jp_version;
reg [1:0] drive_jp_query;
initial drive_jp_query <= #SHIFT_NS tb_candidate_offer.system.jp_query;
always @(tb_candidate_offer.system.jp_query) drive_jp_query <= #SHIFT_NS tb_candidate_offer.system.jp_query;
reg [3:0] drive_jp_price;
initial drive_jp_price <= #SHIFT_NS tb_candidate_offer.system.jp_price;
always @(tb_candidate_offer.system.jp_price) drive_jp_price <= #SHIFT_NS tb_candidate_offer.system.jp_price;
reg [1:0] drive_jp_load;
initial drive_jp_load <= #SHIFT_NS tb_candidate_offer.system.jp_load;
always @(tb_candidate_offer.system.jp_load) drive_jp_load <= #SHIFT_NS tb_candidate_offer.system.jp_load;
reg [1:0] drive_jp_ack;
initial drive_jp_ack <= #SHIFT_NS tb_candidate_offer.system.jp_ack;
always @(tb_candidate_offer.system.jp_ack) drive_jp_ack <= #SHIFT_NS tb_candidate_offer.system.jp_ack;
wire [1:0] actual_jp_ready;
reg [1:0] expected_jp_ready;
initial expected_jp_ready <= #SHIFT_NS tb_candidate_offer.system.jp_ready;
always @(tb_candidate_offer.system.jp_ready) expected_jp_ready <= #SHIFT_NS tb_candidate_offer.system.jp_ready;
wire [1:0] actual_jp_reply;
reg [1:0] expected_jp_reply;
initial expected_jp_reply <= #SHIFT_NS tb_candidate_offer.system.jp_reply;
always @(tb_candidate_offer.system.jp_reply) expected_jp_reply <= #SHIFT_NS tb_candidate_offer.system.jp_reply;
wire [1:0] actual_jp_status;
reg [1:0] expected_jp_status;
initial expected_jp_status <= #SHIFT_NS tb_candidate_offer.system.jp_status;
always @(tb_candidate_offer.system.jp_status) expected_jp_status <= #SHIFT_NS tb_candidate_offer.system.jp_status;
reg drive_jp_authority_stage;
initial drive_jp_authority_stage <= #SHIFT_NS tb_candidate_offer.system.jp_authority_stage;
always @(tb_candidate_offer.system.jp_authority_stage) drive_jp_authority_stage <= #SHIFT_NS tb_candidate_offer.system.jp_authority_stage;
reg drive_boot_required;
initial drive_boot_required <= #SHIFT_NS tb_candidate_offer.system.boot_required;
always @(tb_candidate_offer.system.boot_required) drive_boot_required <= #SHIFT_NS tb_candidate_offer.system.boot_required;
reg drive_boot_cfg_valid;
initial drive_boot_cfg_valid <= #SHIFT_NS tb_candidate_offer.system.boot_cfg_valid;
always @(tb_candidate_offer.system.boot_cfg_valid) drive_boot_cfg_valid <= #SHIFT_NS tb_candidate_offer.system.boot_cfg_valid;
wire actual_boot_cfg_ready;
reg expected_boot_cfg_ready;
initial expected_boot_cfg_ready <= #SHIFT_NS tb_candidate_offer.system.boot_cfg_ready;
always @(tb_candidate_offer.system.boot_cfg_ready) expected_boot_cfg_ready <= #SHIFT_NS tb_candidate_offer.system.boot_cfg_ready;
reg [63:0] drive_boot_design;
initial drive_boot_design <= #SHIFT_NS tb_candidate_offer.system.boot_design;
always @(tb_candidate_offer.system.boot_design) drive_boot_design <= #SHIFT_NS tb_candidate_offer.system.boot_design;
reg [63:0] drive_boot_generation;
initial drive_boot_generation <= #SHIFT_NS tb_candidate_offer.system.boot_generation;
always @(tb_candidate_offer.system.boot_generation) drive_boot_generation <= #SHIFT_NS tb_candidate_offer.system.boot_generation;
reg [31:0] drive_boot_checkpoint;
initial drive_boot_checkpoint <= #SHIFT_NS tb_candidate_offer.system.boot_checkpoint;
always @(tb_candidate_offer.system.boot_checkpoint) drive_boot_checkpoint <= #SHIFT_NS tb_candidate_offer.system.boot_checkpoint;
reg [31:0] drive_boot_version;
initial drive_boot_version <= #SHIFT_NS tb_candidate_offer.system.boot_version;
always @(tb_candidate_offer.system.boot_version) drive_boot_version <= #SHIFT_NS tb_candidate_offer.system.boot_version;
reg [31:0] drive_boot_nodes;
initial drive_boot_nodes <= #SHIFT_NS tb_candidate_offer.system.boot_nodes;
always @(tb_candidate_offer.system.boot_nodes) drive_boot_nodes <= #SHIFT_NS tb_candidate_offer.system.boot_nodes;
reg [31:0] drive_boot_label_count;
initial drive_boot_label_count <= #SHIFT_NS tb_candidate_offer.system.boot_label_count;
always @(tb_candidate_offer.system.boot_label_count) drive_boot_label_count <= #SHIFT_NS tb_candidate_offer.system.boot_label_count;
reg [31:0] drive_boot_label_crc;
initial drive_boot_label_crc <= #SHIFT_NS tb_candidate_offer.system.boot_label_crc;
always @(tb_candidate_offer.system.boot_label_crc) drive_boot_label_crc <= #SHIFT_NS tb_candidate_offer.system.boot_label_crc;
reg [31:0] drive_boot_path_crc;
initial drive_boot_path_crc <= #SHIFT_NS tb_candidate_offer.system.boot_path_crc;
always @(tb_candidate_offer.system.boot_path_crc) drive_boot_path_crc <= #SHIFT_NS tb_candidate_offer.system.boot_path_crc;
reg [31:0] drive_boot_query_crc;
initial drive_boot_query_crc <= #SHIFT_NS tb_candidate_offer.system.boot_query_crc;
always @(tb_candidate_offer.system.boot_query_crc) drive_boot_query_crc <= #SHIFT_NS tb_candidate_offer.system.boot_query_crc;
reg [1:0] drive_boot_query;
initial drive_boot_query <= #SHIFT_NS tb_candidate_offer.system.boot_query;
always @(tb_candidate_offer.system.boot_query) drive_boot_query <= #SHIFT_NS tb_candidate_offer.system.boot_query;
reg [3:0] drive_boot_slots;
initial drive_boot_slots <= #SHIFT_NS tb_candidate_offer.system.boot_slots;
always @(tb_candidate_offer.system.boot_slots) drive_boot_slots <= #SHIFT_NS tb_candidate_offer.system.boot_slots;
reg [3:0] drive_boot_price;
initial drive_boot_price <= #SHIFT_NS tb_candidate_offer.system.boot_price;
always @(tb_candidate_offer.system.boot_price) drive_boot_price <= #SHIFT_NS tb_candidate_offer.system.boot_price;
reg [2303:0] drive_boot_payload;
initial drive_boot_payload <= #SHIFT_NS tb_candidate_offer.system.boot_payload;
always @(tb_candidate_offer.system.boot_payload) drive_boot_payload <= #SHIFT_NS tb_candidate_offer.system.boot_payload;
wire actual_boot_pending;
reg expected_boot_pending;
initial expected_boot_pending <= #SHIFT_NS tb_candidate_offer.system.boot_pending;
always @(tb_candidate_offer.system.boot_pending) expected_boot_pending <= #SHIFT_NS tb_candidate_offer.system.boot_pending;
wire actual_boot_rsp_valid;
reg expected_boot_rsp_valid;
initial expected_boot_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.boot_rsp_valid;
always @(tb_candidate_offer.system.boot_rsp_valid) expected_boot_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.boot_rsp_valid;
reg drive_boot_rsp_ready;
initial drive_boot_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.boot_rsp_ready;
always @(tb_candidate_offer.system.boot_rsp_ready) drive_boot_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.boot_rsp_ready;
wire [3:0] actual_boot_status;
reg [3:0] expected_boot_status;
initial expected_boot_status <= #SHIFT_NS tb_candidate_offer.system.boot_status;
always @(tb_candidate_offer.system.boot_status) expected_boot_status <= #SHIFT_NS tb_candidate_offer.system.boot_status;
reg drive_boot_verify_valid;
initial drive_boot_verify_valid <= #SHIFT_NS tb_candidate_offer.system.boot_verify_valid;
always @(tb_candidate_offer.system.boot_verify_valid) drive_boot_verify_valid <= #SHIFT_NS tb_candidate_offer.system.boot_verify_valid;
wire actual_boot_verify_ready;
reg expected_boot_verify_ready;
initial expected_boot_verify_ready <= #SHIFT_NS tb_candidate_offer.system.boot_verify_ready;
always @(tb_candidate_offer.system.boot_verify_ready) expected_boot_verify_ready <= #SHIFT_NS tb_candidate_offer.system.boot_verify_ready;
wire [31:0] actual_boot_verified_count;
reg [31:0] expected_boot_verified_count;
initial expected_boot_verified_count <= #SHIFT_NS tb_candidate_offer.system.boot_verified_count;
always @(tb_candidate_offer.system.boot_verified_count) expected_boot_verified_count <= #SHIFT_NS tb_candidate_offer.system.boot_verified_count;
wire [3:0] actual_boot_verify_status;
reg [3:0] expected_boot_verify_status;
initial expected_boot_verify_status <= #SHIFT_NS tb_candidate_offer.system.boot_verify_status;
always @(tb_candidate_offer.system.boot_verify_status) expected_boot_verify_status <= #SHIFT_NS tb_candidate_offer.system.boot_verify_status;
wire [4:0] actual_boot_receipts;
reg [4:0] expected_boot_receipts;
initial expected_boot_receipts <= #SHIFT_NS tb_candidate_offer.system.boot_receipts;
always @(tb_candidate_offer.system.boot_receipts) expected_boot_receipts <= #SHIFT_NS tb_candidate_offer.system.boot_receipts;
wire [7:0] actual_boot_config_receipts;
reg [7:0] expected_boot_config_receipts;
initial expected_boot_config_receipts <= #SHIFT_NS tb_candidate_offer.system.boot_config_receipts;
always @(tb_candidate_offer.system.boot_config_receipts) expected_boot_config_receipts <= #SHIFT_NS tb_candidate_offer.system.boot_config_receipts;
reg [63:0] drive_qc_cp_generation;
initial drive_qc_cp_generation <= #SHIFT_NS tb_candidate_offer.system.qc_cp_generation;
always @(tb_candidate_offer.system.qc_cp_generation) drive_qc_cp_generation <= #SHIFT_NS tb_candidate_offer.system.qc_cp_generation;
reg drive_qc_cp_valid;
initial drive_qc_cp_valid <= #SHIFT_NS tb_candidate_offer.system.qc_cp_valid;
always @(tb_candidate_offer.system.qc_cp_valid) drive_qc_cp_valid <= #SHIFT_NS tb_candidate_offer.system.qc_cp_valid;
reg drive_qc_cp_restore;
initial drive_qc_cp_restore <= #SHIFT_NS tb_candidate_offer.system.qc_cp_restore;
always @(tb_candidate_offer.system.qc_cp_restore) drive_qc_cp_restore <= #SHIFT_NS tb_candidate_offer.system.qc_cp_restore;
reg drive_qc_cp_rsp_ready;
initial drive_qc_cp_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.qc_cp_rsp_ready;
always @(tb_candidate_offer.system.qc_cp_rsp_ready) drive_qc_cp_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.qc_cp_rsp_ready;
reg drive_qc_cp_s_valid;
initial drive_qc_cp_s_valid <= #SHIFT_NS tb_candidate_offer.system.qc_cp_s_valid;
always @(tb_candidate_offer.system.qc_cp_s_valid) drive_qc_cp_s_valid <= #SHIFT_NS tb_candidate_offer.system.qc_cp_s_valid;
reg drive_qc_cp_s_last;
initial drive_qc_cp_s_last <= #SHIFT_NS tb_candidate_offer.system.qc_cp_s_last;
always @(tb_candidate_offer.system.qc_cp_s_last) drive_qc_cp_s_last <= #SHIFT_NS tb_candidate_offer.system.qc_cp_s_last;
reg drive_qc_cp_m_ready;
initial drive_qc_cp_m_ready <= #SHIFT_NS tb_candidate_offer.system.qc_cp_m_ready;
always @(tb_candidate_offer.system.qc_cp_m_ready) drive_qc_cp_m_ready <= #SHIFT_NS tb_candidate_offer.system.qc_cp_m_ready;
reg drive_qc_cp_test_reset;
initial drive_qc_cp_test_reset <= #SHIFT_NS tb_candidate_offer.system.qc_cp_test_reset;
always @(tb_candidate_offer.system.qc_cp_test_reset) drive_qc_cp_test_reset <= #SHIFT_NS tb_candidate_offer.system.qc_cp_test_reset;
wire actual_qc_cp_ready;
reg expected_qc_cp_ready;
initial expected_qc_cp_ready <= #SHIFT_NS tb_candidate_offer.system.qc_cp_ready;
always @(tb_candidate_offer.system.qc_cp_ready) expected_qc_cp_ready <= #SHIFT_NS tb_candidate_offer.system.qc_cp_ready;
wire actual_qc_cp_busy;
reg expected_qc_cp_busy;
initial expected_qc_cp_busy <= #SHIFT_NS tb_candidate_offer.system.qc_cp_busy;
always @(tb_candidate_offer.system.qc_cp_busy) expected_qc_cp_busy <= #SHIFT_NS tb_candidate_offer.system.qc_cp_busy;
wire actual_qc_cp_rsp_valid;
reg expected_qc_cp_rsp_valid;
initial expected_qc_cp_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.qc_cp_rsp_valid;
always @(tb_candidate_offer.system.qc_cp_rsp_valid) expected_qc_cp_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.qc_cp_rsp_valid;
wire actual_qc_cp_s_ready;
reg expected_qc_cp_s_ready;
initial expected_qc_cp_s_ready <= #SHIFT_NS tb_candidate_offer.system.qc_cp_s_ready;
always @(tb_candidate_offer.system.qc_cp_s_ready) expected_qc_cp_s_ready <= #SHIFT_NS tb_candidate_offer.system.qc_cp_s_ready;
wire actual_qc_cp_m_valid;
reg expected_qc_cp_m_valid;
initial expected_qc_cp_m_valid <= #SHIFT_NS tb_candidate_offer.system.qc_cp_m_valid;
always @(tb_candidate_offer.system.qc_cp_m_valid) expected_qc_cp_m_valid <= #SHIFT_NS tb_candidate_offer.system.qc_cp_m_valid;
wire actual_qc_cp_m_last;
reg expected_qc_cp_m_last;
initial expected_qc_cp_m_last <= #SHIFT_NS tb_candidate_offer.system.qc_cp_m_last;
always @(tb_candidate_offer.system.qc_cp_m_last) expected_qc_cp_m_last <= #SHIFT_NS tb_candidate_offer.system.qc_cp_m_last;
wire actual_qc_restore_pending;
reg expected_qc_restore_pending;
initial expected_qc_restore_pending <= #SHIFT_NS tb_candidate_offer.system.qc_restore_pending;
always @(tb_candidate_offer.system.qc_restore_pending) expected_qc_restore_pending <= #SHIFT_NS tb_candidate_offer.system.qc_restore_pending;
reg [31:0] drive_qc_cp_expected_crc;
initial drive_qc_cp_expected_crc <= #SHIFT_NS tb_candidate_offer.system.qc_cp_expected_crc;
always @(tb_candidate_offer.system.qc_cp_expected_crc) drive_qc_cp_expected_crc <= #SHIFT_NS tb_candidate_offer.system.qc_cp_expected_crc;
reg [31:0] drive_qc_cp_s_index;
initial drive_qc_cp_s_index <= #SHIFT_NS tb_candidate_offer.system.qc_cp_s_index;
always @(tb_candidate_offer.system.qc_cp_s_index) drive_qc_cp_s_index <= #SHIFT_NS tb_candidate_offer.system.qc_cp_s_index;
reg [31:0] drive_qc_cp_s_data;
initial drive_qc_cp_s_data <= #SHIFT_NS tb_candidate_offer.system.qc_cp_s_data;
always @(tb_candidate_offer.system.qc_cp_s_data) drive_qc_cp_s_data <= #SHIFT_NS tb_candidate_offer.system.qc_cp_s_data;
wire [31:0] actual_qc_cp_crc;
reg [31:0] expected_qc_cp_crc;
initial expected_qc_cp_crc <= #SHIFT_NS tb_candidate_offer.system.qc_cp_crc;
always @(tb_candidate_offer.system.qc_cp_crc) expected_qc_cp_crc <= #SHIFT_NS tb_candidate_offer.system.qc_cp_crc;
wire [31:0] actual_qc_cp_m_index;
reg [31:0] expected_qc_cp_m_index;
initial expected_qc_cp_m_index <= #SHIFT_NS tb_candidate_offer.system.qc_cp_m_index;
always @(tb_candidate_offer.system.qc_cp_m_index) expected_qc_cp_m_index <= #SHIFT_NS tb_candidate_offer.system.qc_cp_m_index;
wire [31:0] actual_qc_cp_m_data;
reg [31:0] expected_qc_cp_m_data;
initial expected_qc_cp_m_data <= #SHIFT_NS tb_candidate_offer.system.qc_cp_m_data;
always @(tb_candidate_offer.system.qc_cp_m_data) expected_qc_cp_m_data <= #SHIFT_NS tb_candidate_offer.system.qc_cp_m_data;
wire [3:0] actual_qc_cp_status;
reg [3:0] expected_qc_cp_status;
initial expected_qc_cp_status <= #SHIFT_NS tb_candidate_offer.system.qc_cp_status;
always @(tb_candidate_offer.system.qc_cp_status) expected_qc_cp_status <= #SHIFT_NS tb_candidate_offer.system.qc_cp_status;
reg drive_as_cfg_valid;
initial drive_as_cfg_valid <= #SHIFT_NS tb_candidate_offer.system.as_cfg_valid;
always @(tb_candidate_offer.system.as_cfg_valid) drive_as_cfg_valid <= #SHIFT_NS tb_candidate_offer.system.as_cfg_valid;
wire actual_as_cfg_ready;
reg expected_as_cfg_ready;
initial expected_as_cfg_ready <= #SHIFT_NS tb_candidate_offer.system.as_cfg_ready;
always @(tb_candidate_offer.system.as_cfg_ready) expected_as_cfg_ready <= #SHIFT_NS tb_candidate_offer.system.as_cfg_ready;
reg [63:0] drive_as_cfg_design;
initial drive_as_cfg_design <= #SHIFT_NS tb_candidate_offer.system.as_cfg_design;
always @(tb_candidate_offer.system.as_cfg_design) drive_as_cfg_design <= #SHIFT_NS tb_candidate_offer.system.as_cfg_design;
reg [63:0] drive_as_cfg_generation;
initial drive_as_cfg_generation <= #SHIFT_NS tb_candidate_offer.system.as_cfg_generation;
always @(tb_candidate_offer.system.as_cfg_generation) drive_as_cfg_generation <= #SHIFT_NS tb_candidate_offer.system.as_cfg_generation;
reg [63:0] drive_as_cfg_primary;
initial drive_as_cfg_primary <= #SHIFT_NS tb_candidate_offer.system.as_cfg_primary;
always @(tb_candidate_offer.system.as_cfg_primary) drive_as_cfg_primary <= #SHIFT_NS tb_candidate_offer.system.as_cfg_primary;
reg [63:0] drive_as_cfg_pool;
initial drive_as_cfg_pool <= #SHIFT_NS tb_candidate_offer.system.as_cfg_pool;
always @(tb_candidate_offer.system.as_cfg_pool) drive_as_cfg_pool <= #SHIFT_NS tb_candidate_offer.system.as_cfg_pool;
reg [63:0] drive_as_cfg_allocator;
initial drive_as_cfg_allocator <= #SHIFT_NS tb_candidate_offer.system.as_cfg_allocator;
always @(tb_candidate_offer.system.as_cfg_allocator) drive_as_cfg_allocator <= #SHIFT_NS tb_candidate_offer.system.as_cfg_allocator;
reg [31:0] drive_as_cfg_checkpoint;
initial drive_as_cfg_checkpoint <= #SHIFT_NS tb_candidate_offer.system.as_cfg_checkpoint;
always @(tb_candidate_offer.system.as_cfg_checkpoint) drive_as_cfg_checkpoint <= #SHIFT_NS tb_candidate_offer.system.as_cfg_checkpoint;
reg [31:0] drive_as_cfg_nodes;
initial drive_as_cfg_nodes <= #SHIFT_NS tb_candidate_offer.system.as_cfg_nodes;
always @(tb_candidate_offer.system.as_cfg_nodes) drive_as_cfg_nodes <= #SHIFT_NS tb_candidate_offer.system.as_cfg_nodes;
reg [31:0] drive_as_cfg_nets;
initial drive_as_cfg_nets <= #SHIFT_NS tb_candidate_offer.system.as_cfg_nets;
always @(tb_candidate_offer.system.as_cfg_nets) drive_as_cfg_nets <= #SHIFT_NS tb_candidate_offer.system.as_cfg_nets;
reg [31:0] drive_as_cfg_capacity;
initial drive_as_cfg_capacity <= #SHIFT_NS tb_candidate_offer.system.as_cfg_capacity;
always @(tb_candidate_offer.system.as_cfg_capacity) drive_as_cfg_capacity <= #SHIFT_NS tb_candidate_offer.system.as_cfg_capacity;
wire actual_as_configured;
reg expected_as_configured;
initial expected_as_configured <= #SHIFT_NS tb_candidate_offer.system.as_configured;
always @(tb_candidate_offer.system.as_configured) expected_as_configured <= #SHIFT_NS tb_candidate_offer.system.as_configured;
wire [63:0] actual_as_bound_design;
reg [63:0] expected_as_bound_design;
initial expected_as_bound_design <= #SHIFT_NS tb_candidate_offer.system.as_bound_design;
always @(tb_candidate_offer.system.as_bound_design) expected_as_bound_design <= #SHIFT_NS tb_candidate_offer.system.as_bound_design;
wire [63:0] actual_as_bound_generation;
reg [63:0] expected_as_bound_generation;
initial expected_as_bound_generation <= #SHIFT_NS tb_candidate_offer.system.as_bound_generation;
always @(tb_candidate_offer.system.as_bound_generation) expected_as_bound_generation <= #SHIFT_NS tb_candidate_offer.system.as_bound_generation;
wire [31:0] actual_as_bound_checkpoint;
reg [31:0] expected_as_bound_checkpoint;
initial expected_as_bound_checkpoint <= #SHIFT_NS tb_candidate_offer.system.as_bound_checkpoint;
always @(tb_candidate_offer.system.as_bound_checkpoint) expected_as_bound_checkpoint <= #SHIFT_NS tb_candidate_offer.system.as_bound_checkpoint;
wire [63:0] actual_as_m_araddr;
reg [63:0] expected_as_m_araddr;
initial expected_as_m_araddr <= #SHIFT_NS tb_candidate_offer.system.as_m_araddr;
always @(tb_candidate_offer.system.as_m_araddr) expected_as_m_araddr <= #SHIFT_NS tb_candidate_offer.system.as_m_araddr;
wire [7:0] actual_as_m_arlen;
reg [7:0] expected_as_m_arlen;
initial expected_as_m_arlen <= #SHIFT_NS tb_candidate_offer.system.as_m_arlen;
always @(tb_candidate_offer.system.as_m_arlen) expected_as_m_arlen <= #SHIFT_NS tb_candidate_offer.system.as_m_arlen;
wire [2:0] actual_as_m_arsize;
reg [2:0] expected_as_m_arsize;
initial expected_as_m_arsize <= #SHIFT_NS tb_candidate_offer.system.as_m_arsize;
always @(tb_candidate_offer.system.as_m_arsize) expected_as_m_arsize <= #SHIFT_NS tb_candidate_offer.system.as_m_arsize;
wire [1:0] actual_as_m_arburst;
reg [1:0] expected_as_m_arburst;
initial expected_as_m_arburst <= #SHIFT_NS tb_candidate_offer.system.as_m_arburst;
always @(tb_candidate_offer.system.as_m_arburst) expected_as_m_arburst <= #SHIFT_NS tb_candidate_offer.system.as_m_arburst;
wire [3:0] actual_as_m_arid;
reg [3:0] expected_as_m_arid;
initial expected_as_m_arid <= #SHIFT_NS tb_candidate_offer.system.as_m_arid;
always @(tb_candidate_offer.system.as_m_arid) expected_as_m_arid <= #SHIFT_NS tb_candidate_offer.system.as_m_arid;
wire actual_as_m_arvalid;
reg expected_as_m_arvalid;
initial expected_as_m_arvalid <= #SHIFT_NS tb_candidate_offer.system.as_m_arvalid;
always @(tb_candidate_offer.system.as_m_arvalid) expected_as_m_arvalid <= #SHIFT_NS tb_candidate_offer.system.as_m_arvalid;
reg drive_as_m_arready;
initial drive_as_m_arready <= #SHIFT_NS tb_candidate_offer.system.as_m_arready;
always @(tb_candidate_offer.system.as_m_arready) drive_as_m_arready <= #SHIFT_NS tb_candidate_offer.system.as_m_arready;
reg [511:0] drive_as_m_rdata;
initial drive_as_m_rdata <= #SHIFT_NS tb_candidate_offer.system.as_m_rdata;
always @(tb_candidate_offer.system.as_m_rdata) drive_as_m_rdata <= #SHIFT_NS tb_candidate_offer.system.as_m_rdata;
reg [3:0] drive_as_m_rid;
initial drive_as_m_rid <= #SHIFT_NS tb_candidate_offer.system.as_m_rid;
always @(tb_candidate_offer.system.as_m_rid) drive_as_m_rid <= #SHIFT_NS tb_candidate_offer.system.as_m_rid;
reg [1:0] drive_as_m_rresp;
initial drive_as_m_rresp <= #SHIFT_NS tb_candidate_offer.system.as_m_rresp;
always @(tb_candidate_offer.system.as_m_rresp) drive_as_m_rresp <= #SHIFT_NS tb_candidate_offer.system.as_m_rresp;
reg drive_as_m_rlast;
initial drive_as_m_rlast <= #SHIFT_NS tb_candidate_offer.system.as_m_rlast;
always @(tb_candidate_offer.system.as_m_rlast) drive_as_m_rlast <= #SHIFT_NS tb_candidate_offer.system.as_m_rlast;
reg drive_as_m_rvalid;
initial drive_as_m_rvalid <= #SHIFT_NS tb_candidate_offer.system.as_m_rvalid;
always @(tb_candidate_offer.system.as_m_rvalid) drive_as_m_rvalid <= #SHIFT_NS tb_candidate_offer.system.as_m_rvalid;
wire actual_as_m_rready;
reg expected_as_m_rready;
initial expected_as_m_rready <= #SHIFT_NS tb_candidate_offer.system.as_m_rready;
always @(tb_candidate_offer.system.as_m_rready) expected_as_m_rready <= #SHIFT_NS tb_candidate_offer.system.as_m_rready;
wire [63:0] actual_as_m_awaddr;
reg [63:0] expected_as_m_awaddr;
initial expected_as_m_awaddr <= #SHIFT_NS tb_candidate_offer.system.as_m_awaddr;
always @(tb_candidate_offer.system.as_m_awaddr) expected_as_m_awaddr <= #SHIFT_NS tb_candidate_offer.system.as_m_awaddr;
wire [7:0] actual_as_m_awlen;
reg [7:0] expected_as_m_awlen;
initial expected_as_m_awlen <= #SHIFT_NS tb_candidate_offer.system.as_m_awlen;
always @(tb_candidate_offer.system.as_m_awlen) expected_as_m_awlen <= #SHIFT_NS tb_candidate_offer.system.as_m_awlen;
wire [2:0] actual_as_m_awsize;
reg [2:0] expected_as_m_awsize;
initial expected_as_m_awsize <= #SHIFT_NS tb_candidate_offer.system.as_m_awsize;
always @(tb_candidate_offer.system.as_m_awsize) expected_as_m_awsize <= #SHIFT_NS tb_candidate_offer.system.as_m_awsize;
wire [1:0] actual_as_m_awburst;
reg [1:0] expected_as_m_awburst;
initial expected_as_m_awburst <= #SHIFT_NS tb_candidate_offer.system.as_m_awburst;
always @(tb_candidate_offer.system.as_m_awburst) expected_as_m_awburst <= #SHIFT_NS tb_candidate_offer.system.as_m_awburst;
wire [3:0] actual_as_m_awid;
reg [3:0] expected_as_m_awid;
initial expected_as_m_awid <= #SHIFT_NS tb_candidate_offer.system.as_m_awid;
always @(tb_candidate_offer.system.as_m_awid) expected_as_m_awid <= #SHIFT_NS tb_candidate_offer.system.as_m_awid;
wire actual_as_m_awvalid;
reg expected_as_m_awvalid;
initial expected_as_m_awvalid <= #SHIFT_NS tb_candidate_offer.system.as_m_awvalid;
always @(tb_candidate_offer.system.as_m_awvalid) expected_as_m_awvalid <= #SHIFT_NS tb_candidate_offer.system.as_m_awvalid;
reg drive_as_m_awready;
initial drive_as_m_awready <= #SHIFT_NS tb_candidate_offer.system.as_m_awready;
always @(tb_candidate_offer.system.as_m_awready) drive_as_m_awready <= #SHIFT_NS tb_candidate_offer.system.as_m_awready;
wire [511:0] actual_as_m_wdata;
reg [511:0] expected_as_m_wdata;
initial expected_as_m_wdata <= #SHIFT_NS tb_candidate_offer.system.as_m_wdata;
always @(tb_candidate_offer.system.as_m_wdata) expected_as_m_wdata <= #SHIFT_NS tb_candidate_offer.system.as_m_wdata;
wire [63:0] actual_as_m_wstrb;
reg [63:0] expected_as_m_wstrb;
initial expected_as_m_wstrb <= #SHIFT_NS tb_candidate_offer.system.as_m_wstrb;
always @(tb_candidate_offer.system.as_m_wstrb) expected_as_m_wstrb <= #SHIFT_NS tb_candidate_offer.system.as_m_wstrb;
wire actual_as_m_wlast;
reg expected_as_m_wlast;
initial expected_as_m_wlast <= #SHIFT_NS tb_candidate_offer.system.as_m_wlast;
always @(tb_candidate_offer.system.as_m_wlast) expected_as_m_wlast <= #SHIFT_NS tb_candidate_offer.system.as_m_wlast;
wire actual_as_m_wvalid;
reg expected_as_m_wvalid;
initial expected_as_m_wvalid <= #SHIFT_NS tb_candidate_offer.system.as_m_wvalid;
always @(tb_candidate_offer.system.as_m_wvalid) expected_as_m_wvalid <= #SHIFT_NS tb_candidate_offer.system.as_m_wvalid;
reg drive_as_m_wready;
initial drive_as_m_wready <= #SHIFT_NS tb_candidate_offer.system.as_m_wready;
always @(tb_candidate_offer.system.as_m_wready) drive_as_m_wready <= #SHIFT_NS tb_candidate_offer.system.as_m_wready;
reg [3:0] drive_as_m_bid;
initial drive_as_m_bid <= #SHIFT_NS tb_candidate_offer.system.as_m_bid;
always @(tb_candidate_offer.system.as_m_bid) drive_as_m_bid <= #SHIFT_NS tb_candidate_offer.system.as_m_bid;
reg [1:0] drive_as_m_bresp;
initial drive_as_m_bresp <= #SHIFT_NS tb_candidate_offer.system.as_m_bresp;
always @(tb_candidate_offer.system.as_m_bresp) drive_as_m_bresp <= #SHIFT_NS tb_candidate_offer.system.as_m_bresp;
reg drive_as_m_bvalid;
initial drive_as_m_bvalid <= #SHIFT_NS tb_candidate_offer.system.as_m_bvalid;
always @(tb_candidate_offer.system.as_m_bvalid) drive_as_m_bvalid <= #SHIFT_NS tb_candidate_offer.system.as_m_bvalid;
wire actual_as_m_bready;
reg expected_as_m_bready;
initial expected_as_m_bready <= #SHIFT_NS tb_candidate_offer.system.as_m_bready;
always @(tb_candidate_offer.system.as_m_bready) expected_as_m_bready <= #SHIFT_NS tb_candidate_offer.system.as_m_bready;
wire actual_as_cfg_rsp_valid;
reg expected_as_cfg_rsp_valid;
initial expected_as_cfg_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.as_cfg_rsp_valid;
always @(tb_candidate_offer.system.as_cfg_rsp_valid) expected_as_cfg_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.as_cfg_rsp_valid;
reg drive_as_cfg_rsp_ready;
initial drive_as_cfg_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.as_cfg_rsp_ready;
always @(tb_candidate_offer.system.as_cfg_rsp_ready) drive_as_cfg_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.as_cfg_rsp_ready;
wire [2:0] actual_as_cfg_status;
reg [2:0] expected_as_cfg_status;
initial expected_as_cfg_status <= #SHIFT_NS tb_candidate_offer.system.as_cfg_status;
always @(tb_candidate_offer.system.as_cfg_status) expected_as_cfg_status <= #SHIFT_NS tb_candidate_offer.system.as_cfg_status;
wire actual_as_busy;
reg expected_as_busy;
initial expected_as_busy <= #SHIFT_NS tb_candidate_offer.system.as_busy;
always @(tb_candidate_offer.system.as_busy) expected_as_busy <= #SHIFT_NS tb_candidate_offer.system.as_busy;
wire actual_as_fault;
reg expected_as_fault;
initial expected_as_fault <= #SHIFT_NS tb_candidate_offer.system.as_fault;
always @(tb_candidate_offer.system.as_fault) expected_as_fault <= #SHIFT_NS tb_candidate_offer.system.as_fault;
wire actual_as_drained;
reg expected_as_drained;
initial expected_as_drained <= #SHIFT_NS tb_candidate_offer.system.as_drained;
always @(tb_candidate_offer.system.as_drained) expected_as_drained <= #SHIFT_NS tb_candidate_offer.system.as_drained;
wire actual_as_retired;
reg expected_as_retired;
initial expected_as_retired <= #SHIFT_NS tb_candidate_offer.system.as_retired;
always @(tb_candidate_offer.system.as_retired) expected_as_retired <= #SHIFT_NS tb_candidate_offer.system.as_retired;
wire [63:0] actual_as_rsp_generation;
reg [63:0] expected_as_rsp_generation;
initial expected_as_rsp_generation <= #SHIFT_NS tb_candidate_offer.system.as_rsp_generation;
always @(tb_candidate_offer.system.as_rsp_generation) expected_as_rsp_generation <= #SHIFT_NS tb_candidate_offer.system.as_rsp_generation;
reg drive_cp_valid;
initial drive_cp_valid <= #SHIFT_NS tb_candidate_offer.system.cp_valid;
always @(tb_candidate_offer.system.cp_valid) drive_cp_valid <= #SHIFT_NS tb_candidate_offer.system.cp_valid;
reg drive_cp_restore;
initial drive_cp_restore <= #SHIFT_NS tb_candidate_offer.system.cp_restore;
always @(tb_candidate_offer.system.cp_restore) drive_cp_restore <= #SHIFT_NS tb_candidate_offer.system.cp_restore;
wire actual_cp_ready;
reg expected_cp_ready;
initial expected_cp_ready <= #SHIFT_NS tb_candidate_offer.system.cp_ready;
always @(tb_candidate_offer.system.cp_ready) expected_cp_ready <= #SHIFT_NS tb_candidate_offer.system.cp_ready;
wire actual_cp_busy;
reg expected_cp_busy;
initial expected_cp_busy <= #SHIFT_NS tb_candidate_offer.system.cp_busy;
always @(tb_candidate_offer.system.cp_busy) expected_cp_busy <= #SHIFT_NS tb_candidate_offer.system.cp_busy;
wire actual_cp_rsp_valid;
reg expected_cp_rsp_valid;
initial expected_cp_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.cp_rsp_valid;
always @(tb_candidate_offer.system.cp_rsp_valid) expected_cp_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.cp_rsp_valid;
reg drive_cp_rsp_ready;
initial drive_cp_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.cp_rsp_ready;
always @(tb_candidate_offer.system.cp_rsp_ready) drive_cp_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.cp_rsp_ready;
wire [3:0] actual_cp_status;
reg [3:0] expected_cp_status;
initial expected_cp_status <= #SHIFT_NS tb_candidate_offer.system.cp_status;
always @(tb_candidate_offer.system.cp_status) expected_cp_status <= #SHIFT_NS tb_candidate_offer.system.cp_status;
wire [31:0] actual_cp_crc;
reg [31:0] expected_cp_crc;
initial expected_cp_crc <= #SHIFT_NS tb_candidate_offer.system.cp_crc;
always @(tb_candidate_offer.system.cp_crc) expected_cp_crc <= #SHIFT_NS tb_candidate_offer.system.cp_crc;
reg [63:0] drive_cp_design;
initial drive_cp_design <= #SHIFT_NS tb_candidate_offer.system.cp_design;
always @(tb_candidate_offer.system.cp_design) drive_cp_design <= #SHIFT_NS tb_candidate_offer.system.cp_design;
reg [31:0] drive_cp_nodes;
initial drive_cp_nodes <= #SHIFT_NS tb_candidate_offer.system.cp_nodes;
always @(tb_candidate_offer.system.cp_nodes) drive_cp_nodes <= #SHIFT_NS tb_candidate_offer.system.cp_nodes;
reg [31:0] drive_cp_nets;
initial drive_cp_nets <= #SHIFT_NS tb_candidate_offer.system.cp_nets;
always @(tb_candidate_offer.system.cp_nets) drive_cp_nets <= #SHIFT_NS tb_candidate_offer.system.cp_nets;
reg [31:0] drive_cp_expected_crc;
initial drive_cp_expected_crc <= #SHIFT_NS tb_candidate_offer.system.cp_expected_crc;
always @(tb_candidate_offer.system.cp_expected_crc) drive_cp_expected_crc <= #SHIFT_NS tb_candidate_offer.system.cp_expected_crc;
reg drive_cp_s_valid;
initial drive_cp_s_valid <= #SHIFT_NS tb_candidate_offer.system.cp_s_valid;
always @(tb_candidate_offer.system.cp_s_valid) drive_cp_s_valid <= #SHIFT_NS tb_candidate_offer.system.cp_s_valid;
wire actual_cp_s_ready;
reg expected_cp_s_ready;
initial expected_cp_s_ready <= #SHIFT_NS tb_candidate_offer.system.cp_s_ready;
always @(tb_candidate_offer.system.cp_s_ready) expected_cp_s_ready <= #SHIFT_NS tb_candidate_offer.system.cp_s_ready;
reg [31:0] drive_cp_s_index;
initial drive_cp_s_index <= #SHIFT_NS tb_candidate_offer.system.cp_s_index;
always @(tb_candidate_offer.system.cp_s_index) drive_cp_s_index <= #SHIFT_NS tb_candidate_offer.system.cp_s_index;
reg [31:0] drive_cp_s_data;
initial drive_cp_s_data <= #SHIFT_NS tb_candidate_offer.system.cp_s_data;
always @(tb_candidate_offer.system.cp_s_data) drive_cp_s_data <= #SHIFT_NS tb_candidate_offer.system.cp_s_data;
reg drive_cp_s_last;
initial drive_cp_s_last <= #SHIFT_NS tb_candidate_offer.system.cp_s_last;
always @(tb_candidate_offer.system.cp_s_last) drive_cp_s_last <= #SHIFT_NS tb_candidate_offer.system.cp_s_last;
wire actual_cp_m_valid;
reg expected_cp_m_valid;
initial expected_cp_m_valid <= #SHIFT_NS tb_candidate_offer.system.cp_m_valid;
always @(tb_candidate_offer.system.cp_m_valid) expected_cp_m_valid <= #SHIFT_NS tb_candidate_offer.system.cp_m_valid;
reg drive_cp_m_ready;
initial drive_cp_m_ready <= #SHIFT_NS tb_candidate_offer.system.cp_m_ready;
always @(tb_candidate_offer.system.cp_m_ready) drive_cp_m_ready <= #SHIFT_NS tb_candidate_offer.system.cp_m_ready;
wire [31:0] actual_cp_m_index;
reg [31:0] expected_cp_m_index;
initial expected_cp_m_index <= #SHIFT_NS tb_candidate_offer.system.cp_m_index;
always @(tb_candidate_offer.system.cp_m_index) expected_cp_m_index <= #SHIFT_NS tb_candidate_offer.system.cp_m_index;
wire [31:0] actual_cp_m_data;
reg [31:0] expected_cp_m_data;
initial expected_cp_m_data <= #SHIFT_NS tb_candidate_offer.system.cp_m_data;
always @(tb_candidate_offer.system.cp_m_data) expected_cp_m_data <= #SHIFT_NS tb_candidate_offer.system.cp_m_data;
wire actual_cp_m_last;
reg expected_cp_m_last;
initial expected_cp_m_last <= #SHIFT_NS tb_candidate_offer.system.cp_m_last;
always @(tb_candidate_offer.system.cp_m_last) expected_cp_m_last <= #SHIFT_NS tb_candidate_offer.system.cp_m_last;
reg drive_cp_test_reset;
initial drive_cp_test_reset <= #SHIFT_NS tb_candidate_offer.system.cp_test_reset;
always @(tb_candidate_offer.system.cp_test_reset) drive_cp_test_reset <= #SHIFT_NS tb_candidate_offer.system.cp_test_reset;
wire actual_pc_route_retired;
reg expected_pc_route_retired;
initial expected_pc_route_retired <= #SHIFT_NS tb_candidate_offer.system.pc_route_retired;
always @(tb_candidate_offer.system.pc_route_retired) expected_pc_route_retired <= #SHIFT_NS tb_candidate_offer.system.pc_route_retired;
reg drive_pc_acquire_valid;
initial drive_pc_acquire_valid <= #SHIFT_NS tb_candidate_offer.system.pc_acquire_valid;
always @(tb_candidate_offer.system.pc_acquire_valid) drive_pc_acquire_valid <= #SHIFT_NS tb_candidate_offer.system.pc_acquire_valid;
wire actual_pc_acquire_ready;
reg expected_pc_acquire_ready;
initial expected_pc_acquire_ready <= #SHIFT_NS tb_candidate_offer.system.pc_acquire_ready;
always @(tb_candidate_offer.system.pc_acquire_ready) expected_pc_acquire_ready <= #SHIFT_NS tb_candidate_offer.system.pc_acquire_ready;
wire actual_pc_owned;
reg expected_pc_owned;
initial expected_pc_owned <= #SHIFT_NS tb_candidate_offer.system.pc_owned;
always @(tb_candidate_offer.system.pc_owned) expected_pc_owned <= #SHIFT_NS tb_candidate_offer.system.pc_owned;
reg drive_pc_release_valid;
initial drive_pc_release_valid <= #SHIFT_NS tb_candidate_offer.system.pc_release_valid;
always @(tb_candidate_offer.system.pc_release_valid) drive_pc_release_valid <= #SHIFT_NS tb_candidate_offer.system.pc_release_valid;
wire actual_pc_release_ready;
reg expected_pc_release_ready;
initial expected_pc_release_ready <= #SHIFT_NS tb_candidate_offer.system.pc_release_ready;
always @(tb_candidate_offer.system.pc_release_ready) expected_pc_release_ready <= #SHIFT_NS tb_candidate_offer.system.pc_release_ready;
reg drive_abort;
initial drive_abort <= #SHIFT_NS tb_candidate_offer.system.abort;
always @(tb_candidate_offer.system.abort) drive_abort <= #SHIFT_NS tb_candidate_offer.system.abort;
wire actual_busy;
reg expected_busy;
initial expected_busy <= #SHIFT_NS tb_candidate_offer.system.busy;
always @(tb_candidate_offer.system.busy) expected_busy <= #SHIFT_NS tb_candidate_offer.system.busy;
wire actual_cc_busy;
reg expected_cc_busy;
initial expected_cc_busy <= #SHIFT_NS tb_candidate_offer.system.cc_busy;
always @(tb_candidate_offer.system.cc_busy) expected_cc_busy <= #SHIFT_NS tb_candidate_offer.system.cc_busy;
wire actual_cc_fault;
reg expected_cc_fault;
initial expected_cc_fault <= #SHIFT_NS tb_candidate_offer.system.cc_fault;
always @(tb_candidate_offer.system.cc_fault) expected_cc_fault <= #SHIFT_NS tb_candidate_offer.system.cc_fault;
wire actual_cf_fault;
reg expected_cf_fault;
initial expected_cf_fault <= #SHIFT_NS tb_candidate_offer.system.cf_fault;
always @(tb_candidate_offer.system.cf_fault) expected_cf_fault <= #SHIFT_NS tb_candidate_offer.system.cf_fault;
reg drive_clk;
initial drive_clk <= #SHIFT_NS tb_candidate_offer.system.clk;
always @(tb_candidate_offer.system.clk) drive_clk <= #SHIFT_NS tb_candidate_offer.system.clk;
wire actual_cost_lease;
reg expected_cost_lease;
initial expected_cost_lease <= #SHIFT_NS tb_candidate_offer.system.cost_lease;
always @(tb_candidate_offer.system.cost_lease) expected_cost_lease <= #SHIFT_NS tb_candidate_offer.system.cost_lease;
wire actual_cs_busy;
reg expected_cs_busy;
initial expected_cs_busy <= #SHIFT_NS tb_candidate_offer.system.cs_busy;
always @(tb_candidate_offer.system.cs_busy) expected_cs_busy <= #SHIFT_NS tb_candidate_offer.system.cs_busy;
wire actual_cs_configured;
reg expected_cs_configured;
initial expected_cs_configured <= #SHIFT_NS tb_candidate_offer.system.cs_configured;
always @(tb_candidate_offer.system.cs_configured) expected_cs_configured <= #SHIFT_NS tb_candidate_offer.system.cs_configured;
wire [63:0] actual_cs_design_id;
reg [63:0] expected_cs_design_id;
initial expected_cs_design_id <= #SHIFT_NS tb_candidate_offer.system.cs_design_id;
always @(tb_candidate_offer.system.cs_design_id) expected_cs_design_id <= #SHIFT_NS tb_candidate_offer.system.cs_design_id;
wire actual_cs_editing;
reg expected_cs_editing;
initial expected_cs_editing <= #SHIFT_NS tb_candidate_offer.system.cs_editing;
always @(tb_candidate_offer.system.cs_editing) expected_cs_editing <= #SHIFT_NS tb_candidate_offer.system.cs_editing;
wire actual_cs_fault;
reg expected_cs_fault;
initial expected_cs_fault <= #SHIFT_NS tb_candidate_offer.system.cs_fault;
always @(tb_candidate_offer.system.cs_fault) expected_cs_fault <= #SHIFT_NS tb_candidate_offer.system.cs_fault;
wire [63:0] actual_cs_m_araddr;
reg [63:0] expected_cs_m_araddr;
initial expected_cs_m_araddr <= #SHIFT_NS tb_candidate_offer.system.cs_m_araddr;
always @(tb_candidate_offer.system.cs_m_araddr) expected_cs_m_araddr <= #SHIFT_NS tb_candidate_offer.system.cs_m_araddr;
wire [1:0] actual_cs_m_arburst;
reg [1:0] expected_cs_m_arburst;
initial expected_cs_m_arburst <= #SHIFT_NS tb_candidate_offer.system.cs_m_arburst;
always @(tb_candidate_offer.system.cs_m_arburst) expected_cs_m_arburst <= #SHIFT_NS tb_candidate_offer.system.cs_m_arburst;
wire [3:0] actual_cs_m_arid;
reg [3:0] expected_cs_m_arid;
initial expected_cs_m_arid <= #SHIFT_NS tb_candidate_offer.system.cs_m_arid;
always @(tb_candidate_offer.system.cs_m_arid) expected_cs_m_arid <= #SHIFT_NS tb_candidate_offer.system.cs_m_arid;
wire [7:0] actual_cs_m_arlen;
reg [7:0] expected_cs_m_arlen;
initial expected_cs_m_arlen <= #SHIFT_NS tb_candidate_offer.system.cs_m_arlen;
always @(tb_candidate_offer.system.cs_m_arlen) expected_cs_m_arlen <= #SHIFT_NS tb_candidate_offer.system.cs_m_arlen;
reg drive_cs_m_arready;
initial drive_cs_m_arready <= #SHIFT_NS tb_candidate_offer.system.cs_m_arready;
always @(tb_candidate_offer.system.cs_m_arready) drive_cs_m_arready <= #SHIFT_NS tb_candidate_offer.system.cs_m_arready;
wire [2:0] actual_cs_m_arsize;
reg [2:0] expected_cs_m_arsize;
initial expected_cs_m_arsize <= #SHIFT_NS tb_candidate_offer.system.cs_m_arsize;
always @(tb_candidate_offer.system.cs_m_arsize) expected_cs_m_arsize <= #SHIFT_NS tb_candidate_offer.system.cs_m_arsize;
wire actual_cs_m_arvalid;
reg expected_cs_m_arvalid;
initial expected_cs_m_arvalid <= #SHIFT_NS tb_candidate_offer.system.cs_m_arvalid;
always @(tb_candidate_offer.system.cs_m_arvalid) expected_cs_m_arvalid <= #SHIFT_NS tb_candidate_offer.system.cs_m_arvalid;
wire [63:0] actual_cs_m_awaddr;
reg [63:0] expected_cs_m_awaddr;
initial expected_cs_m_awaddr <= #SHIFT_NS tb_candidate_offer.system.cs_m_awaddr;
always @(tb_candidate_offer.system.cs_m_awaddr) expected_cs_m_awaddr <= #SHIFT_NS tb_candidate_offer.system.cs_m_awaddr;
wire [1:0] actual_cs_m_awburst;
reg [1:0] expected_cs_m_awburst;
initial expected_cs_m_awburst <= #SHIFT_NS tb_candidate_offer.system.cs_m_awburst;
always @(tb_candidate_offer.system.cs_m_awburst) expected_cs_m_awburst <= #SHIFT_NS tb_candidate_offer.system.cs_m_awburst;
wire [3:0] actual_cs_m_awid;
reg [3:0] expected_cs_m_awid;
initial expected_cs_m_awid <= #SHIFT_NS tb_candidate_offer.system.cs_m_awid;
always @(tb_candidate_offer.system.cs_m_awid) expected_cs_m_awid <= #SHIFT_NS tb_candidate_offer.system.cs_m_awid;
wire [7:0] actual_cs_m_awlen;
reg [7:0] expected_cs_m_awlen;
initial expected_cs_m_awlen <= #SHIFT_NS tb_candidate_offer.system.cs_m_awlen;
always @(tb_candidate_offer.system.cs_m_awlen) expected_cs_m_awlen <= #SHIFT_NS tb_candidate_offer.system.cs_m_awlen;
reg drive_cs_m_awready;
initial drive_cs_m_awready <= #SHIFT_NS tb_candidate_offer.system.cs_m_awready;
always @(tb_candidate_offer.system.cs_m_awready) drive_cs_m_awready <= #SHIFT_NS tb_candidate_offer.system.cs_m_awready;
wire [2:0] actual_cs_m_awsize;
reg [2:0] expected_cs_m_awsize;
initial expected_cs_m_awsize <= #SHIFT_NS tb_candidate_offer.system.cs_m_awsize;
always @(tb_candidate_offer.system.cs_m_awsize) expected_cs_m_awsize <= #SHIFT_NS tb_candidate_offer.system.cs_m_awsize;
wire actual_cs_m_awvalid;
reg expected_cs_m_awvalid;
initial expected_cs_m_awvalid <= #SHIFT_NS tb_candidate_offer.system.cs_m_awvalid;
always @(tb_candidate_offer.system.cs_m_awvalid) expected_cs_m_awvalid <= #SHIFT_NS tb_candidate_offer.system.cs_m_awvalid;
reg [3:0] drive_cs_m_bid;
initial drive_cs_m_bid <= #SHIFT_NS tb_candidate_offer.system.cs_m_bid;
always @(tb_candidate_offer.system.cs_m_bid) drive_cs_m_bid <= #SHIFT_NS tb_candidate_offer.system.cs_m_bid;
wire actual_cs_m_bready;
reg expected_cs_m_bready;
initial expected_cs_m_bready <= #SHIFT_NS tb_candidate_offer.system.cs_m_bready;
always @(tb_candidate_offer.system.cs_m_bready) expected_cs_m_bready <= #SHIFT_NS tb_candidate_offer.system.cs_m_bready;
reg [1:0] drive_cs_m_bresp;
initial drive_cs_m_bresp <= #SHIFT_NS tb_candidate_offer.system.cs_m_bresp;
always @(tb_candidate_offer.system.cs_m_bresp) drive_cs_m_bresp <= #SHIFT_NS tb_candidate_offer.system.cs_m_bresp;
reg drive_cs_m_bvalid;
initial drive_cs_m_bvalid <= #SHIFT_NS tb_candidate_offer.system.cs_m_bvalid;
always @(tb_candidate_offer.system.cs_m_bvalid) drive_cs_m_bvalid <= #SHIFT_NS tb_candidate_offer.system.cs_m_bvalid;
reg [511:0] drive_cs_m_rdata;
initial drive_cs_m_rdata <= #SHIFT_NS tb_candidate_offer.system.cs_m_rdata;
always @(tb_candidate_offer.system.cs_m_rdata) drive_cs_m_rdata <= #SHIFT_NS tb_candidate_offer.system.cs_m_rdata;
reg [3:0] drive_cs_m_rid;
initial drive_cs_m_rid <= #SHIFT_NS tb_candidate_offer.system.cs_m_rid;
always @(tb_candidate_offer.system.cs_m_rid) drive_cs_m_rid <= #SHIFT_NS tb_candidate_offer.system.cs_m_rid;
reg drive_cs_m_rlast;
initial drive_cs_m_rlast <= #SHIFT_NS tb_candidate_offer.system.cs_m_rlast;
always @(tb_candidate_offer.system.cs_m_rlast) drive_cs_m_rlast <= #SHIFT_NS tb_candidate_offer.system.cs_m_rlast;
wire actual_cs_m_rready;
reg expected_cs_m_rready;
initial expected_cs_m_rready <= #SHIFT_NS tb_candidate_offer.system.cs_m_rready;
always @(tb_candidate_offer.system.cs_m_rready) expected_cs_m_rready <= #SHIFT_NS tb_candidate_offer.system.cs_m_rready;
reg [1:0] drive_cs_m_rresp;
initial drive_cs_m_rresp <= #SHIFT_NS tb_candidate_offer.system.cs_m_rresp;
always @(tb_candidate_offer.system.cs_m_rresp) drive_cs_m_rresp <= #SHIFT_NS tb_candidate_offer.system.cs_m_rresp;
reg drive_cs_m_rvalid;
initial drive_cs_m_rvalid <= #SHIFT_NS tb_candidate_offer.system.cs_m_rvalid;
always @(tb_candidate_offer.system.cs_m_rvalid) drive_cs_m_rvalid <= #SHIFT_NS tb_candidate_offer.system.cs_m_rvalid;
wire [511:0] actual_cs_m_wdata;
reg [511:0] expected_cs_m_wdata;
initial expected_cs_m_wdata <= #SHIFT_NS tb_candidate_offer.system.cs_m_wdata;
always @(tb_candidate_offer.system.cs_m_wdata) expected_cs_m_wdata <= #SHIFT_NS tb_candidate_offer.system.cs_m_wdata;
wire actual_cs_m_wlast;
reg expected_cs_m_wlast;
initial expected_cs_m_wlast <= #SHIFT_NS tb_candidate_offer.system.cs_m_wlast;
always @(tb_candidate_offer.system.cs_m_wlast) expected_cs_m_wlast <= #SHIFT_NS tb_candidate_offer.system.cs_m_wlast;
reg drive_cs_m_wready;
initial drive_cs_m_wready <= #SHIFT_NS tb_candidate_offer.system.cs_m_wready;
always @(tb_candidate_offer.system.cs_m_wready) drive_cs_m_wready <= #SHIFT_NS tb_candidate_offer.system.cs_m_wready;
wire [63:0] actual_cs_m_wstrb;
reg [63:0] expected_cs_m_wstrb;
initial expected_cs_m_wstrb <= #SHIFT_NS tb_candidate_offer.system.cs_m_wstrb;
always @(tb_candidate_offer.system.cs_m_wstrb) expected_cs_m_wstrb <= #SHIFT_NS tb_candidate_offer.system.cs_m_wstrb;
wire actual_cs_m_wvalid;
reg expected_cs_m_wvalid;
initial expected_cs_m_wvalid <= #SHIFT_NS tb_candidate_offer.system.cs_m_wvalid;
always @(tb_candidate_offer.system.cs_m_wvalid) expected_cs_m_wvalid <= #SHIFT_NS tb_candidate_offer.system.cs_m_wvalid;
wire [31:0] actual_cs_published_version;
reg [31:0] expected_cs_published_version;
initial expected_cs_published_version <= #SHIFT_NS tb_candidate_offer.system.cs_published_version;
always @(tb_candidate_offer.system.cs_published_version) expected_cs_published_version <= #SHIFT_NS tb_candidate_offer.system.cs_published_version;
wire actual_cs_ready_for_query;
reg expected_cs_ready_for_query;
initial expected_cs_ready_for_query <= #SHIFT_NS tb_candidate_offer.system.cs_ready_for_query;
always @(tb_candidate_offer.system.cs_ready_for_query) expected_cs_ready_for_query <= #SHIFT_NS tb_candidate_offer.system.cs_ready_for_query;
wire actual_d_configured;
reg expected_d_configured;
initial expected_d_configured <= #SHIFT_NS tb_candidate_offer.system.d_configured;
always @(tb_candidate_offer.system.d_configured) expected_d_configured <= #SHIFT_NS tb_candidate_offer.system.d_configured;
wire [63:0] actual_d_m_araddr;
reg [63:0] expected_d_m_araddr;
initial expected_d_m_araddr <= #SHIFT_NS tb_candidate_offer.system.d_m_araddr;
always @(tb_candidate_offer.system.d_m_araddr) expected_d_m_araddr <= #SHIFT_NS tb_candidate_offer.system.d_m_araddr;
wire [1:0] actual_d_m_arburst;
reg [1:0] expected_d_m_arburst;
initial expected_d_m_arburst <= #SHIFT_NS tb_candidate_offer.system.d_m_arburst;
always @(tb_candidate_offer.system.d_m_arburst) expected_d_m_arburst <= #SHIFT_NS tb_candidate_offer.system.d_m_arburst;
wire [3:0] actual_d_m_arid;
reg [3:0] expected_d_m_arid;
initial expected_d_m_arid <= #SHIFT_NS tb_candidate_offer.system.d_m_arid;
always @(tb_candidate_offer.system.d_m_arid) expected_d_m_arid <= #SHIFT_NS tb_candidate_offer.system.d_m_arid;
wire [7:0] actual_d_m_arlen;
reg [7:0] expected_d_m_arlen;
initial expected_d_m_arlen <= #SHIFT_NS tb_candidate_offer.system.d_m_arlen;
always @(tb_candidate_offer.system.d_m_arlen) expected_d_m_arlen <= #SHIFT_NS tb_candidate_offer.system.d_m_arlen;
reg drive_d_m_arready;
initial drive_d_m_arready <= #SHIFT_NS tb_candidate_offer.system.d_m_arready;
always @(tb_candidate_offer.system.d_m_arready) drive_d_m_arready <= #SHIFT_NS tb_candidate_offer.system.d_m_arready;
wire [2:0] actual_d_m_arsize;
reg [2:0] expected_d_m_arsize;
initial expected_d_m_arsize <= #SHIFT_NS tb_candidate_offer.system.d_m_arsize;
always @(tb_candidate_offer.system.d_m_arsize) expected_d_m_arsize <= #SHIFT_NS tb_candidate_offer.system.d_m_arsize;
wire actual_d_m_arvalid;
reg expected_d_m_arvalid;
initial expected_d_m_arvalid <= #SHIFT_NS tb_candidate_offer.system.d_m_arvalid;
always @(tb_candidate_offer.system.d_m_arvalid) expected_d_m_arvalid <= #SHIFT_NS tb_candidate_offer.system.d_m_arvalid;
wire [63:0] actual_d_m_awaddr;
reg [63:0] expected_d_m_awaddr;
initial expected_d_m_awaddr <= #SHIFT_NS tb_candidate_offer.system.d_m_awaddr;
always @(tb_candidate_offer.system.d_m_awaddr) expected_d_m_awaddr <= #SHIFT_NS tb_candidate_offer.system.d_m_awaddr;
wire [1:0] actual_d_m_awburst;
reg [1:0] expected_d_m_awburst;
initial expected_d_m_awburst <= #SHIFT_NS tb_candidate_offer.system.d_m_awburst;
always @(tb_candidate_offer.system.d_m_awburst) expected_d_m_awburst <= #SHIFT_NS tb_candidate_offer.system.d_m_awburst;
wire [3:0] actual_d_m_awid;
reg [3:0] expected_d_m_awid;
initial expected_d_m_awid <= #SHIFT_NS tb_candidate_offer.system.d_m_awid;
always @(tb_candidate_offer.system.d_m_awid) expected_d_m_awid <= #SHIFT_NS tb_candidate_offer.system.d_m_awid;
wire [7:0] actual_d_m_awlen;
reg [7:0] expected_d_m_awlen;
initial expected_d_m_awlen <= #SHIFT_NS tb_candidate_offer.system.d_m_awlen;
always @(tb_candidate_offer.system.d_m_awlen) expected_d_m_awlen <= #SHIFT_NS tb_candidate_offer.system.d_m_awlen;
reg drive_d_m_awready;
initial drive_d_m_awready <= #SHIFT_NS tb_candidate_offer.system.d_m_awready;
always @(tb_candidate_offer.system.d_m_awready) drive_d_m_awready <= #SHIFT_NS tb_candidate_offer.system.d_m_awready;
wire [2:0] actual_d_m_awsize;
reg [2:0] expected_d_m_awsize;
initial expected_d_m_awsize <= #SHIFT_NS tb_candidate_offer.system.d_m_awsize;
always @(tb_candidate_offer.system.d_m_awsize) expected_d_m_awsize <= #SHIFT_NS tb_candidate_offer.system.d_m_awsize;
wire actual_d_m_awvalid;
reg expected_d_m_awvalid;
initial expected_d_m_awvalid <= #SHIFT_NS tb_candidate_offer.system.d_m_awvalid;
always @(tb_candidate_offer.system.d_m_awvalid) expected_d_m_awvalid <= #SHIFT_NS tb_candidate_offer.system.d_m_awvalid;
reg [3:0] drive_d_m_bid;
initial drive_d_m_bid <= #SHIFT_NS tb_candidate_offer.system.d_m_bid;
always @(tb_candidate_offer.system.d_m_bid) drive_d_m_bid <= #SHIFT_NS tb_candidate_offer.system.d_m_bid;
wire actual_d_m_bready;
reg expected_d_m_bready;
initial expected_d_m_bready <= #SHIFT_NS tb_candidate_offer.system.d_m_bready;
always @(tb_candidate_offer.system.d_m_bready) expected_d_m_bready <= #SHIFT_NS tb_candidate_offer.system.d_m_bready;
reg [1:0] drive_d_m_bresp;
initial drive_d_m_bresp <= #SHIFT_NS tb_candidate_offer.system.d_m_bresp;
always @(tb_candidate_offer.system.d_m_bresp) drive_d_m_bresp <= #SHIFT_NS tb_candidate_offer.system.d_m_bresp;
reg drive_d_m_bvalid;
initial drive_d_m_bvalid <= #SHIFT_NS tb_candidate_offer.system.d_m_bvalid;
always @(tb_candidate_offer.system.d_m_bvalid) drive_d_m_bvalid <= #SHIFT_NS tb_candidate_offer.system.d_m_bvalid;
reg [511:0] drive_d_m_rdata;
initial drive_d_m_rdata <= #SHIFT_NS tb_candidate_offer.system.d_m_rdata;
always @(tb_candidate_offer.system.d_m_rdata) drive_d_m_rdata <= #SHIFT_NS tb_candidate_offer.system.d_m_rdata;
reg [3:0] drive_d_m_rid;
initial drive_d_m_rid <= #SHIFT_NS tb_candidate_offer.system.d_m_rid;
always @(tb_candidate_offer.system.d_m_rid) drive_d_m_rid <= #SHIFT_NS tb_candidate_offer.system.d_m_rid;
reg drive_d_m_rlast;
initial drive_d_m_rlast <= #SHIFT_NS tb_candidate_offer.system.d_m_rlast;
always @(tb_candidate_offer.system.d_m_rlast) drive_d_m_rlast <= #SHIFT_NS tb_candidate_offer.system.d_m_rlast;
wire actual_d_m_rready;
reg expected_d_m_rready;
initial expected_d_m_rready <= #SHIFT_NS tb_candidate_offer.system.d_m_rready;
always @(tb_candidate_offer.system.d_m_rready) expected_d_m_rready <= #SHIFT_NS tb_candidate_offer.system.d_m_rready;
reg [1:0] drive_d_m_rresp;
initial drive_d_m_rresp <= #SHIFT_NS tb_candidate_offer.system.d_m_rresp;
always @(tb_candidate_offer.system.d_m_rresp) drive_d_m_rresp <= #SHIFT_NS tb_candidate_offer.system.d_m_rresp;
reg drive_d_m_rvalid;
initial drive_d_m_rvalid <= #SHIFT_NS tb_candidate_offer.system.d_m_rvalid;
always @(tb_candidate_offer.system.d_m_rvalid) drive_d_m_rvalid <= #SHIFT_NS tb_candidate_offer.system.d_m_rvalid;
wire [511:0] actual_d_m_wdata;
reg [511:0] expected_d_m_wdata;
initial expected_d_m_wdata <= #SHIFT_NS tb_candidate_offer.system.d_m_wdata;
always @(tb_candidate_offer.system.d_m_wdata) expected_d_m_wdata <= #SHIFT_NS tb_candidate_offer.system.d_m_wdata;
wire actual_d_m_wlast;
reg expected_d_m_wlast;
initial expected_d_m_wlast <= #SHIFT_NS tb_candidate_offer.system.d_m_wlast;
always @(tb_candidate_offer.system.d_m_wlast) expected_d_m_wlast <= #SHIFT_NS tb_candidate_offer.system.d_m_wlast;
reg drive_d_m_wready;
initial drive_d_m_wready <= #SHIFT_NS tb_candidate_offer.system.d_m_wready;
always @(tb_candidate_offer.system.d_m_wready) drive_d_m_wready <= #SHIFT_NS tb_candidate_offer.system.d_m_wready;
wire [63:0] actual_d_m_wstrb;
reg [63:0] expected_d_m_wstrb;
initial expected_d_m_wstrb <= #SHIFT_NS tb_candidate_offer.system.d_m_wstrb;
always @(tb_candidate_offer.system.d_m_wstrb) expected_d_m_wstrb <= #SHIFT_NS tb_candidate_offer.system.d_m_wstrb;
wire actual_d_m_wvalid;
reg expected_d_m_wvalid;
initial expected_d_m_wvalid <= #SHIFT_NS tb_candidate_offer.system.d_m_wvalid;
always @(tb_candidate_offer.system.d_m_wvalid) expected_d_m_wvalid <= #SHIFT_NS tb_candidate_offer.system.d_m_wvalid;
reg [63:0] drive_design_id;
initial drive_design_id <= #SHIFT_NS tb_candidate_offer.system.design_id;
always @(tb_candidate_offer.system.design_id) drive_design_id <= #SHIFT_NS tb_candidate_offer.system.design_id;
wire actual_f_all_drained;
reg expected_f_all_drained;
initial expected_f_all_drained <= #SHIFT_NS tb_candidate_offer.system.f_all_drained;
always @(tb_candidate_offer.system.f_all_drained) expected_f_all_drained <= #SHIFT_NS tb_candidate_offer.system.f_all_drained;
wire actual_f_backend_idle;
reg expected_f_backend_idle;
initial expected_f_backend_idle <= #SHIFT_NS tb_candidate_offer.system.f_backend_idle;
always @(tb_candidate_offer.system.f_backend_idle) expected_f_backend_idle <= #SHIFT_NS tb_candidate_offer.system.f_backend_idle;
wire actual_f_fault;
reg expected_f_fault;
initial expected_f_fault <= #SHIFT_NS tb_candidate_offer.system.f_fault;
always @(tb_candidate_offer.system.f_fault) expected_f_fault <= #SHIFT_NS tb_candidate_offer.system.f_fault;
wire actual_f_normal_retired;
reg expected_f_normal_retired;
initial expected_f_normal_retired <= #SHIFT_NS tb_candidate_offer.system.f_normal_retired;
always @(tb_candidate_offer.system.f_normal_retired) expected_f_normal_retired <= #SHIFT_NS tb_candidate_offer.system.f_normal_retired;
wire [3:0] actual_f_phase;
reg [3:0] expected_f_phase;
initial expected_f_phase <= #SHIFT_NS tb_candidate_offer.system.f_phase;
always @(tb_candidate_offer.system.f_phase) expected_f_phase <= #SHIFT_NS tb_candidate_offer.system.f_phase;
wire actual_f_recovery_owned;
reg expected_f_recovery_owned;
initial expected_f_recovery_owned <= #SHIFT_NS tb_candidate_offer.system.f_recovery_owned;
always @(tb_candidate_offer.system.f_recovery_owned) expected_f_recovery_owned <= #SHIFT_NS tb_candidate_offer.system.f_recovery_owned;
reg [191:0] drive_f_route_payload;
initial drive_f_route_payload <= #SHIFT_NS tb_candidate_offer.system.f_route_payload;
always @(tb_candidate_offer.system.f_route_payload) drive_f_route_payload <= #SHIFT_NS tb_candidate_offer.system.f_route_payload;
reg [38911:0] drive_f_sp;
initial drive_f_sp <= #SHIFT_NS tb_candidate_offer.system.f_sp;
always @(tb_candidate_offer.system.f_sp) drive_f_sp <= #SHIFT_NS tb_candidate_offer.system.f_sp;
wire [15:0] actual_f_sr;
reg [15:0] expected_f_sr;
initial expected_f_sr <= #SHIFT_NS tb_candidate_offer.system.f_sr;
always @(tb_candidate_offer.system.f_sr) expected_f_sr <= #SHIFT_NS tb_candidate_offer.system.f_sr;
wire [4095:0] actual_f_srp;
reg [4095:0] expected_f_srp;
initial expected_f_srp <= #SHIFT_NS tb_candidate_offer.system.f_srp;
always @(tb_candidate_offer.system.f_srp) expected_f_srp <= #SHIFT_NS tb_candidate_offer.system.f_srp;
reg [15:0] drive_f_srr;
initial drive_f_srr <= #SHIFT_NS tb_candidate_offer.system.f_srr;
always @(tb_candidate_offer.system.f_srr) drive_f_srr <= #SHIFT_NS tb_candidate_offer.system.f_srr;
wire [15:0] actual_f_srv;
reg [15:0] expected_f_srv;
initial expected_f_srv <= #SHIFT_NS tb_candidate_offer.system.f_srv;
always @(tb_candidate_offer.system.f_srv) expected_f_srv <= #SHIFT_NS tb_candidate_offer.system.f_srv;
reg [15:0] drive_f_sv;
initial drive_f_sv <= #SHIFT_NS tb_candidate_offer.system.f_sv;
always @(tb_candidate_offer.system.f_sv) drive_f_sv <= #SHIFT_NS tb_candidate_offer.system.f_sv;
wire actual_fault;
reg expected_fault;
initial expected_fault <= #SHIFT_NS tb_candidate_offer.system.fault;
always @(tb_candidate_offer.system.fault) expected_fault <= #SHIFT_NS tb_candidate_offer.system.fault;
wire actual_g_configured;
reg expected_g_configured;
initial expected_g_configured <= #SHIFT_NS tb_candidate_offer.system.g_configured;
always @(tb_candidate_offer.system.g_configured) expected_g_configured <= #SHIFT_NS tb_candidate_offer.system.g_configured;
wire [63:0] actual_g_m_araddr;
reg [63:0] expected_g_m_araddr;
initial expected_g_m_araddr <= #SHIFT_NS tb_candidate_offer.system.g_m_araddr;
always @(tb_candidate_offer.system.g_m_araddr) expected_g_m_araddr <= #SHIFT_NS tb_candidate_offer.system.g_m_araddr;
wire [1:0] actual_g_m_arburst;
reg [1:0] expected_g_m_arburst;
initial expected_g_m_arburst <= #SHIFT_NS tb_candidate_offer.system.g_m_arburst;
always @(tb_candidate_offer.system.g_m_arburst) expected_g_m_arburst <= #SHIFT_NS tb_candidate_offer.system.g_m_arburst;
wire [3:0] actual_g_m_arid;
reg [3:0] expected_g_m_arid;
initial expected_g_m_arid <= #SHIFT_NS tb_candidate_offer.system.g_m_arid;
always @(tb_candidate_offer.system.g_m_arid) expected_g_m_arid <= #SHIFT_NS tb_candidate_offer.system.g_m_arid;
wire [7:0] actual_g_m_arlen;
reg [7:0] expected_g_m_arlen;
initial expected_g_m_arlen <= #SHIFT_NS tb_candidate_offer.system.g_m_arlen;
always @(tb_candidate_offer.system.g_m_arlen) expected_g_m_arlen <= #SHIFT_NS tb_candidate_offer.system.g_m_arlen;
reg drive_g_m_arready;
initial drive_g_m_arready <= #SHIFT_NS tb_candidate_offer.system.g_m_arready;
always @(tb_candidate_offer.system.g_m_arready) drive_g_m_arready <= #SHIFT_NS tb_candidate_offer.system.g_m_arready;
wire [2:0] actual_g_m_arsize;
reg [2:0] expected_g_m_arsize;
initial expected_g_m_arsize <= #SHIFT_NS tb_candidate_offer.system.g_m_arsize;
always @(tb_candidate_offer.system.g_m_arsize) expected_g_m_arsize <= #SHIFT_NS tb_candidate_offer.system.g_m_arsize;
wire actual_g_m_arvalid;
reg expected_g_m_arvalid;
initial expected_g_m_arvalid <= #SHIFT_NS tb_candidate_offer.system.g_m_arvalid;
always @(tb_candidate_offer.system.g_m_arvalid) expected_g_m_arvalid <= #SHIFT_NS tb_candidate_offer.system.g_m_arvalid;
reg [511:0] drive_g_m_rdata;
initial drive_g_m_rdata <= #SHIFT_NS tb_candidate_offer.system.g_m_rdata;
always @(tb_candidate_offer.system.g_m_rdata) drive_g_m_rdata <= #SHIFT_NS tb_candidate_offer.system.g_m_rdata;
reg [3:0] drive_g_m_rid;
initial drive_g_m_rid <= #SHIFT_NS tb_candidate_offer.system.g_m_rid;
always @(tb_candidate_offer.system.g_m_rid) drive_g_m_rid <= #SHIFT_NS tb_candidate_offer.system.g_m_rid;
reg drive_g_m_rlast;
initial drive_g_m_rlast <= #SHIFT_NS tb_candidate_offer.system.g_m_rlast;
always @(tb_candidate_offer.system.g_m_rlast) drive_g_m_rlast <= #SHIFT_NS tb_candidate_offer.system.g_m_rlast;
wire actual_g_m_rready;
reg expected_g_m_rready;
initial expected_g_m_rready <= #SHIFT_NS tb_candidate_offer.system.g_m_rready;
always @(tb_candidate_offer.system.g_m_rready) expected_g_m_rready <= #SHIFT_NS tb_candidate_offer.system.g_m_rready;
reg [1:0] drive_g_m_rresp;
initial drive_g_m_rresp <= #SHIFT_NS tb_candidate_offer.system.g_m_rresp;
always @(tb_candidate_offer.system.g_m_rresp) drive_g_m_rresp <= #SHIFT_NS tb_candidate_offer.system.g_m_rresp;
reg drive_g_m_rvalid;
initial drive_g_m_rvalid <= #SHIFT_NS tb_candidate_offer.system.g_m_rvalid;
always @(tb_candidate_offer.system.g_m_rvalid) drive_g_m_rvalid <= #SHIFT_NS tb_candidate_offer.system.g_m_rvalid;
wire [31:0] actual_k_a_checkpoint;
reg [31:0] expected_k_a_checkpoint;
initial expected_k_a_checkpoint <= #SHIFT_NS tb_candidate_offer.system.k_a_checkpoint;
always @(tb_candidate_offer.system.k_a_checkpoint) expected_k_a_checkpoint <= #SHIFT_NS tb_candidate_offer.system.k_a_checkpoint;
wire [31:0] actual_k_a_cookie;
reg [31:0] expected_k_a_cookie;
initial expected_k_a_cookie <= #SHIFT_NS tb_candidate_offer.system.k_a_cookie;
always @(tb_candidate_offer.system.k_a_cookie) expected_k_a_cookie <= #SHIFT_NS tb_candidate_offer.system.k_a_cookie;
wire [63:0] actual_k_a_design;
reg [63:0] expected_k_a_design;
initial expected_k_a_design <= #SHIFT_NS tb_candidate_offer.system.k_a_design;
always @(tb_candidate_offer.system.k_a_design) expected_k_a_design <= #SHIFT_NS tb_candidate_offer.system.k_a_design;
wire [31:0] actual_k_a_net;
reg [31:0] expected_k_a_net;
initial expected_k_a_net <= #SHIFT_NS tb_candidate_offer.system.k_a_net;
always @(tb_candidate_offer.system.k_a_net) expected_k_a_net <= #SHIFT_NS tb_candidate_offer.system.k_a_net;
wire [31:0] actual_k_a_node;
reg [31:0] expected_k_a_node;
initial expected_k_a_node <= #SHIFT_NS tb_candidate_offer.system.k_a_node;
always @(tb_candidate_offer.system.k_a_node) expected_k_a_node <= #SHIFT_NS tb_candidate_offer.system.k_a_node;
wire [31:0] actual_k_a_occ;
reg [31:0] expected_k_a_occ;
initial expected_k_a_occ <= #SHIFT_NS tb_candidate_offer.system.k_a_occ;
always @(tb_candidate_offer.system.k_a_occ) expected_k_a_occ <= #SHIFT_NS tb_candidate_offer.system.k_a_occ;
wire actual_k_a_ready;
reg expected_k_a_ready;
initial expected_k_a_ready <= #SHIFT_NS tb_candidate_offer.system.k_a_ready;
always @(tb_candidate_offer.system.k_a_ready) expected_k_a_ready <= #SHIFT_NS tb_candidate_offer.system.k_a_ready;
wire [31:0] actual_k_a_refs;
reg [31:0] expected_k_a_refs;
initial expected_k_a_refs <= #SHIFT_NS tb_candidate_offer.system.k_a_refs;
always @(tb_candidate_offer.system.k_a_refs) expected_k_a_refs <= #SHIFT_NS tb_candidate_offer.system.k_a_refs;
wire [31:0] actual_k_a_rsp_checkpoint;
reg [31:0] expected_k_a_rsp_checkpoint;
initial expected_k_a_rsp_checkpoint <= #SHIFT_NS tb_candidate_offer.system.k_a_rsp_checkpoint;
always @(tb_candidate_offer.system.k_a_rsp_checkpoint) expected_k_a_rsp_checkpoint <= #SHIFT_NS tb_candidate_offer.system.k_a_rsp_checkpoint;
wire [31:0] actual_k_a_rsp_cookie;
reg [31:0] expected_k_a_rsp_cookie;
initial expected_k_a_rsp_cookie <= #SHIFT_NS tb_candidate_offer.system.k_a_rsp_cookie;
always @(tb_candidate_offer.system.k_a_rsp_cookie) expected_k_a_rsp_cookie <= #SHIFT_NS tb_candidate_offer.system.k_a_rsp_cookie;
wire [63:0] actual_k_a_rsp_design;
reg [63:0] expected_k_a_rsp_design;
initial expected_k_a_rsp_design <= #SHIFT_NS tb_candidate_offer.system.k_a_rsp_design;
always @(tb_candidate_offer.system.k_a_rsp_design) expected_k_a_rsp_design <= #SHIFT_NS tb_candidate_offer.system.k_a_rsp_design;
wire actual_k_a_rsp_ready;
reg expected_k_a_rsp_ready;
initial expected_k_a_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.k_a_rsp_ready;
always @(tb_candidate_offer.system.k_a_rsp_ready) expected_k_a_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.k_a_rsp_ready;
wire actual_k_a_rsp_valid;
reg expected_k_a_rsp_valid;
initial expected_k_a_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.k_a_rsp_valid;
always @(tb_candidate_offer.system.k_a_rsp_valid) expected_k_a_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.k_a_rsp_valid;
wire [3:0] actual_k_a_status;
reg [3:0] expected_k_a_status;
initial expected_k_a_status <= #SHIFT_NS tb_candidate_offer.system.k_a_status;
always @(tb_candidate_offer.system.k_a_status) expected_k_a_status <= #SHIFT_NS tb_candidate_offer.system.k_a_status;
wire actual_k_a_valid;
reg expected_k_a_valid;
initial expected_k_a_valid <= #SHIFT_NS tb_candidate_offer.system.k_a_valid;
always @(tb_candidate_offer.system.k_a_valid) expected_k_a_valid <= #SHIFT_NS tb_candidate_offer.system.k_a_valid;
wire actual_k_busy;
reg expected_k_busy;
initial expected_k_busy <= #SHIFT_NS tb_candidate_offer.system.k_busy;
always @(tb_candidate_offer.system.k_busy) expected_k_busy <= #SHIFT_NS tb_candidate_offer.system.k_busy;
reg drive_k_cold_rst;
initial drive_k_cold_rst <= #SHIFT_NS tb_candidate_offer.system.k_cold_rst;
always @(tb_candidate_offer.system.k_cold_rst) drive_k_cold_rst <= #SHIFT_NS tb_candidate_offer.system.k_cold_rst;
wire [31:0] actual_k_corrected;
reg [31:0] expected_k_corrected;
initial expected_k_corrected <= #SHIFT_NS tb_candidate_offer.system.k_corrected;
always @(tb_candidate_offer.system.k_corrected) expected_k_corrected <= #SHIFT_NS tb_candidate_offer.system.k_corrected;
wire [31:0] actual_k_count;
reg [31:0] expected_k_count;
initial expected_k_count <= #SHIFT_NS tb_candidate_offer.system.k_count;
always @(tb_candidate_offer.system.k_count) expected_k_count <= #SHIFT_NS tb_candidate_offer.system.k_count;
wire actual_k_fault;
reg expected_k_fault;
initial expected_k_fault <= #SHIFT_NS tb_candidate_offer.system.k_fault;
always @(tb_candidate_offer.system.k_fault) expected_k_fault <= #SHIFT_NS tb_candidate_offer.system.k_fault;
wire actual_k_full;
reg expected_k_full;
initial expected_k_full <= #SHIFT_NS tb_candidate_offer.system.k_full;
always @(tb_candidate_offer.system.k_full) expected_k_full <= #SHIFT_NS tb_candidate_offer.system.k_full;
wire actual_k_permit;
reg expected_k_permit;
initial expected_k_permit <= #SHIFT_NS tb_candidate_offer.system.k_permit;
always @(tb_candidate_offer.system.k_permit) expected_k_permit <= #SHIFT_NS tb_candidate_offer.system.k_permit;
wire actual_k_rec_ready;
reg expected_k_rec_ready;
initial expected_k_rec_ready <= #SHIFT_NS tb_candidate_offer.system.k_rec_ready;
always @(tb_candidate_offer.system.k_rec_ready) expected_k_rec_ready <= #SHIFT_NS tb_candidate_offer.system.k_rec_ready;
reg drive_k_rec_valid;
initial drive_k_rec_valid <= #SHIFT_NS tb_candidate_offer.system.k_rec_valid;
always @(tb_candidate_offer.system.k_rec_valid) drive_k_rec_valid <= #SHIFT_NS tb_candidate_offer.system.k_rec_valid;
wire [31:0] actual_k_rsp_cookie;
reg [31:0] expected_k_rsp_cookie;
initial expected_k_rsp_cookie <= #SHIFT_NS tb_candidate_offer.system.k_rsp_cookie;
always @(tb_candidate_offer.system.k_rsp_cookie) expected_k_rsp_cookie <= #SHIFT_NS tb_candidate_offer.system.k_rsp_cookie;
reg drive_k_rsp_ready;
initial drive_k_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.k_rsp_ready;
always @(tb_candidate_offer.system.k_rsp_ready) drive_k_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.k_rsp_ready;
wire [3:0] actual_k_rsp_status;
reg [3:0] expected_k_rsp_status;
initial expected_k_rsp_status <= #SHIFT_NS tb_candidate_offer.system.k_rsp_status;
always @(tb_candidate_offer.system.k_rsp_status) expected_k_rsp_status <= #SHIFT_NS tb_candidate_offer.system.k_rsp_status;
wire actual_k_rsp_valid;
reg expected_k_rsp_valid;
initial expected_k_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.k_rsp_valid;
always @(tb_candidate_offer.system.k_rsp_valid) expected_k_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.k_rsp_valid;
wire [31:0] actual_k_saved_checkpoint;
reg [31:0] expected_k_saved_checkpoint;
initial expected_k_saved_checkpoint <= #SHIFT_NS tb_candidate_offer.system.k_saved_checkpoint;
always @(tb_candidate_offer.system.k_saved_checkpoint) expected_k_saved_checkpoint <= #SHIFT_NS tb_candidate_offer.system.k_saved_checkpoint;
wire [63:0] actual_k_saved_design;
reg [63:0] expected_k_saved_design;
initial expected_k_saved_design <= #SHIFT_NS tb_candidate_offer.system.k_saved_design;
always @(tb_candidate_offer.system.k_saved_design) expected_k_saved_design <= #SHIFT_NS tb_candidate_offer.system.k_saved_design;
wire actual_k_target_reset;
reg expected_k_target_reset;
initial expected_k_target_reset <= #SHIFT_NS tb_candidate_offer.system.k_target_reset;
always @(tb_candidate_offer.system.k_target_reset) expected_k_target_reset <= #SHIFT_NS tb_candidate_offer.system.k_target_reset;
wire actual_lr_fault;
reg expected_lr_fault;
initial expected_lr_fault <= #SHIFT_NS tb_candidate_offer.system.lr_fault;
always @(tb_candidate_offer.system.lr_fault) expected_lr_fault <= #SHIFT_NS tb_candidate_offer.system.lr_fault;
wire [3:0] actual_lr_rsp_status;
reg [3:0] expected_lr_rsp_status;
initial expected_lr_rsp_status <= #SHIFT_NS tb_candidate_offer.system.lr_rsp_status;
always @(tb_candidate_offer.system.lr_rsp_status) expected_lr_rsp_status <= #SHIFT_NS tb_candidate_offer.system.lr_rsp_status;
reg [31:0] drive_lr_s_cookie;
initial drive_lr_s_cookie <= #SHIFT_NS tb_candidate_offer.system.lr_s_cookie;
always @(tb_candidate_offer.system.lr_s_cookie) drive_lr_s_cookie <= #SHIFT_NS tb_candidate_offer.system.lr_s_cookie;
reg drive_lr_s_last;
initial drive_lr_s_last <= #SHIFT_NS tb_candidate_offer.system.lr_s_last;
always @(tb_candidate_offer.system.lr_s_last) drive_lr_s_last <= #SHIFT_NS tb_candidate_offer.system.lr_s_last;
reg [31:0] drive_lr_s_node;
initial drive_lr_s_node <= #SHIFT_NS tb_candidate_offer.system.lr_s_node;
always @(tb_candidate_offer.system.lr_s_node) drive_lr_s_node <= #SHIFT_NS tb_candidate_offer.system.lr_s_node;
reg [159:0] drive_lr_s_payload;
initial drive_lr_s_payload <= #SHIFT_NS tb_candidate_offer.system.lr_s_payload;
always @(tb_candidate_offer.system.lr_s_payload) drive_lr_s_payload <= #SHIFT_NS tb_candidate_offer.system.lr_s_payload;
wire actual_lr_s_ready;
reg expected_lr_s_ready;
initial expected_lr_s_ready <= #SHIFT_NS tb_candidate_offer.system.lr_s_ready;
always @(tb_candidate_offer.system.lr_s_ready) expected_lr_s_ready <= #SHIFT_NS tb_candidate_offer.system.lr_s_ready;
reg drive_lr_s_valid;
initial drive_lr_s_valid <= #SHIFT_NS tb_candidate_offer.system.lr_s_valid;
always @(tb_candidate_offer.system.lr_s_valid) drive_lr_s_valid <= #SHIFT_NS tb_candidate_offer.system.lr_s_valid;
wire [31:0] actual_lr_verified;
reg [31:0] expected_lr_verified;
initial expected_lr_verified <= #SHIFT_NS tb_candidate_offer.system.lr_verified;
always @(tb_candidate_offer.system.lr_verified) expected_lr_verified <= #SHIFT_NS tb_candidate_offer.system.lr_verified;
wire [31:0] actual_lr_written;
reg [31:0] expected_lr_written;
initial expected_lr_written <= #SHIFT_NS tb_candidate_offer.system.lr_written;
always @(tb_candidate_offer.system.lr_written) expected_lr_written <= #SHIFT_NS tb_candidate_offer.system.lr_written;
wire actual_operation_pending;
reg expected_operation_pending;
initial expected_operation_pending <= #SHIFT_NS tb_candidate_offer.system.operation_pending;
always @(tb_candidate_offer.system.operation_pending) expected_operation_pending <= #SHIFT_NS tb_candidate_offer.system.operation_pending;
wire [31:0] actual_out_action;
reg [31:0] expected_out_action;
initial expected_out_action <= #SHIFT_NS tb_candidate_offer.system.out_action;
always @(tb_candidate_offer.system.out_action) expected_out_action <= #SHIFT_NS tb_candidate_offer.system.out_action;
wire [255:0] actual_out_attrs;
reg [255:0] expected_out_attrs;
initial expected_out_attrs <= #SHIFT_NS tb_candidate_offer.system.out_attrs;
always @(tb_candidate_offer.system.out_attrs) expected_out_attrs <= #SHIFT_NS tb_candidate_offer.system.out_attrs;
wire [31:0] actual_out_bits;
reg [31:0] expected_out_bits;
initial expected_out_bits <= #SHIFT_NS tb_candidate_offer.system.out_bits;
always @(tb_candidate_offer.system.out_bits) expected_out_bits <= #SHIFT_NS tb_candidate_offer.system.out_bits;
wire [2:0] actual_out_commit_acked;
reg [2:0] expected_out_commit_acked;
initial expected_out_commit_acked <= #SHIFT_NS tb_candidate_offer.system.out_commit_acked;
always @(tb_candidate_offer.system.out_commit_acked) expected_out_commit_acked <= #SHIFT_NS tb_candidate_offer.system.out_commit_acked;
wire [159:0] actual_out_commit_payload;
reg [159:0] expected_out_commit_payload;
initial expected_out_commit_payload <= #SHIFT_NS tb_candidate_offer.system.out_commit_payload;
always @(tb_candidate_offer.system.out_commit_payload) expected_out_commit_payload <= #SHIFT_NS tb_candidate_offer.system.out_commit_payload;
wire [3:0] actual_out_commit_status;
reg [3:0] expected_out_commit_status;
initial expected_out_commit_status <= #SHIFT_NS tb_candidate_offer.system.out_commit_status;
always @(tb_candidate_offer.system.out_commit_status) expected_out_commit_status <= #SHIFT_NS tb_candidate_offer.system.out_commit_status;
wire actual_out_commit_valid;
reg expected_out_commit_valid;
initial expected_out_commit_valid <= #SHIFT_NS tb_candidate_offer.system.out_commit_valid;
always @(tb_candidate_offer.system.out_commit_valid) expected_out_commit_valid <= #SHIFT_NS tb_candidate_offer.system.out_commit_valid;
wire [447:0] actual_out_config;
reg [447:0] expected_out_config;
initial expected_out_config <= #SHIFT_NS tb_candidate_offer.system.out_config;
always @(tb_candidate_offer.system.out_config) expected_out_config <= #SHIFT_NS tb_candidate_offer.system.out_config;
wire [31:0] actual_out_connection;
reg [31:0] expected_out_connection;
initial expected_out_connection <= #SHIFT_NS tb_candidate_offer.system.out_connection;
always @(tb_candidate_offer.system.out_connection) expected_out_connection <= #SHIFT_NS tb_candidate_offer.system.out_connection;
wire [31:0] actual_out_cookie;
reg [31:0] expected_out_cookie;
initial expected_out_cookie <= #SHIFT_NS tb_candidate_offer.system.out_cookie;
always @(tb_candidate_offer.system.out_cookie) expected_out_cookie <= #SHIFT_NS tb_candidate_offer.system.out_cookie;
wire [415:0] actual_out_cost_geometry;
reg [415:0] expected_out_cost_geometry;
initial expected_out_cost_geometry <= #SHIFT_NS tb_candidate_offer.system.out_cost_geometry;
always @(tb_candidate_offer.system.out_cost_geometry) expected_out_cost_geometry <= #SHIFT_NS tb_candidate_offer.system.out_cost_geometry;
wire [127:0] actual_out_cost_geometry_result;
reg [127:0] expected_out_cost_geometry_result;
initial expected_out_cost_geometry_result <= #SHIFT_NS tb_candidate_offer.system.out_cost_geometry_result;
always @(tb_candidate_offer.system.out_cost_geometry_result) expected_out_cost_geometry_result <= #SHIFT_NS tb_candidate_offer.system.out_cost_geometry_result;
wire [735:0] actual_out_cost_packet;
reg [735:0] expected_out_cost_packet;
initial expected_out_cost_packet <= #SHIFT_NS tb_candidate_offer.system.out_cost_packet;
always @(tb_candidate_offer.system.out_cost_packet) expected_out_cost_packet <= #SHIFT_NS tb_candidate_offer.system.out_cost_packet;
wire [3:0] actual_out_cost_status;
reg [3:0] expected_out_cost_status;
initial expected_out_cost_status <= #SHIFT_NS tb_candidate_offer.system.out_cost_status;
always @(tb_candidate_offer.system.out_cost_status) expected_out_cost_status <= #SHIFT_NS tb_candidate_offer.system.out_cost_status;
wire actual_out_cost_valid;
reg expected_out_cost_valid;
initial expected_out_cost_valid <= #SHIFT_NS tb_candidate_offer.system.out_cost_valid;
always @(tb_candidate_offer.system.out_cost_valid) expected_out_cost_valid <= #SHIFT_NS tb_candidate_offer.system.out_cost_valid;
wire [159:0] actual_out_cost_words;
reg [159:0] expected_out_cost_words;
initial expected_out_cost_words <= #SHIFT_NS tb_candidate_offer.system.out_cost_words;
always @(tb_candidate_offer.system.out_cost_words) expected_out_cost_words <= #SHIFT_NS tb_candidate_offer.system.out_cost_words;
wire [31:0] actual_out_node;
reg [31:0] expected_out_node;
initial expected_out_node <= #SHIFT_NS tb_candidate_offer.system.out_node;
always @(tb_candidate_offer.system.out_node) expected_out_node <= #SHIFT_NS tb_candidate_offer.system.out_node;
wire [31:0] actual_out_offer_before;
reg [31:0] expected_out_offer_before;
initial expected_out_offer_before <= #SHIFT_NS tb_candidate_offer.system.out_offer_before;
always @(tb_candidate_offer.system.out_offer_before) expected_out_offer_before <= #SHIFT_NS tb_candidate_offer.system.out_offer_before;
wire [31:0] actual_out_offer_key;
reg [31:0] expected_out_offer_key;
initial expected_out_offer_key <= #SHIFT_NS tb_candidate_offer.system.out_offer_key;
always @(tb_candidate_offer.system.out_offer_key) expected_out_offer_key <= #SHIFT_NS tb_candidate_offer.system.out_offer_key;
wire [31:0] actual_out_offer_node;
reg [31:0] expected_out_offer_node;
initial expected_out_offer_node <= #SHIFT_NS tb_candidate_offer.system.out_offer_node;
always @(tb_candidate_offer.system.out_offer_node) expected_out_offer_node <= #SHIFT_NS tb_candidate_offer.system.out_offer_node;
wire [31:0] actual_out_offer_size;
reg [31:0] expected_out_offer_size;
initial expected_out_offer_size <= #SHIFT_NS tb_candidate_offer.system.out_offer_size;
always @(tb_candidate_offer.system.out_offer_size) expected_out_offer_size <= #SHIFT_NS tb_candidate_offer.system.out_offer_size;
wire [3:0] actual_out_offer_status;
reg [3:0] expected_out_offer_status;
initial expected_out_offer_status <= #SHIFT_NS tb_candidate_offer.system.out_offer_status;
always @(tb_candidate_offer.system.out_offer_status) expected_out_offer_status <= #SHIFT_NS tb_candidate_offer.system.out_offer_status;
wire actual_out_offer_valid;
reg expected_out_offer_valid;
initial expected_out_offer_valid <= #SHIFT_NS tb_candidate_offer.system.out_offer_valid;
always @(tb_candidate_offer.system.out_offer_valid) expected_out_offer_valid <= #SHIFT_NS tb_candidate_offer.system.out_offer_valid;
wire [511:0] actual_out_params;
reg [511:0] expected_out_params;
initial expected_out_params <= #SHIFT_NS tb_candidate_offer.system.out_params;
always @(tb_candidate_offer.system.out_params) expected_out_params <= #SHIFT_NS tb_candidate_offer.system.out_params;
wire actual_out_params_valid;
reg expected_out_params_valid;
initial expected_out_params_valid <= #SHIFT_NS tb_candidate_offer.system.out_params_valid;
always @(tb_candidate_offer.system.out_params_valid) expected_out_params_valid <= #SHIFT_NS tb_candidate_offer.system.out_params_valid;
wire [31:0] actual_out_position;
reg [31:0] expected_out_position;
initial expected_out_position <= #SHIFT_NS tb_candidate_offer.system.out_position;
always @(tb_candidate_offer.system.out_position) expected_out_position <= #SHIFT_NS tb_candidate_offer.system.out_position;
wire [255:0] actual_out_post_attrs;
reg [255:0] expected_out_post_attrs;
initial expected_out_post_attrs <= #SHIFT_NS tb_candidate_offer.system.out_post_attrs;
always @(tb_candidate_offer.system.out_post_attrs) expected_out_post_attrs <= #SHIFT_NS tb_candidate_offer.system.out_post_attrs;
wire [31:0] actual_out_post_distance;
reg [31:0] expected_out_post_distance;
initial expected_out_post_distance <= #SHIFT_NS tb_candidate_offer.system.out_post_distance;
always @(tb_candidate_offer.system.out_post_distance) expected_out_post_distance <= #SHIFT_NS tb_candidate_offer.system.out_post_distance;
wire actual_out_post_prev_read;
reg expected_out_post_prev_read;
initial expected_out_post_prev_read <= #SHIFT_NS tb_candidate_offer.system.out_post_prev_read;
always @(tb_candidate_offer.system.out_post_prev_read) expected_out_post_prev_read <= #SHIFT_NS tb_candidate_offer.system.out_post_prev_read;
wire [3:0] actual_out_post_status;
reg [3:0] expected_out_post_status;
initial expected_out_post_status <= #SHIFT_NS tb_candidate_offer.system.out_post_status;
always @(tb_candidate_offer.system.out_post_status) expected_out_post_status <= #SHIFT_NS tb_candidate_offer.system.out_post_status;
wire [31:0] actual_out_post_upstream;
reg [31:0] expected_out_post_upstream;
initial expected_out_post_upstream <= #SHIFT_NS tb_candidate_offer.system.out_post_upstream;
always @(tb_candidate_offer.system.out_post_upstream) expected_out_post_upstream <= #SHIFT_NS tb_candidate_offer.system.out_post_upstream;
wire actual_out_post_valid;
reg expected_out_post_valid;
initial expected_out_post_valid <= #SHIFT_NS tb_candidate_offer.system.out_post_valid;
always @(tb_candidate_offer.system.out_post_valid) expected_out_post_valid <= #SHIFT_NS tb_candidate_offer.system.out_post_valid;
wire [31:0] actual_out_post_x;
reg [31:0] expected_out_post_x;
initial expected_out_post_x <= #SHIFT_NS tb_candidate_offer.system.out_post_x;
always @(tb_candidate_offer.system.out_post_x) expected_out_post_x <= #SHIFT_NS tb_candidate_offer.system.out_post_x;
wire [31:0] actual_out_post_y;
reg [31:0] expected_out_post_y;
initial expected_out_post_y <= #SHIFT_NS tb_candidate_offer.system.out_post_y;
always @(tb_candidate_offer.system.out_post_y) expected_out_post_y <= #SHIFT_NS tb_candidate_offer.system.out_post_y;
wire [31:0] actual_out_prep_count;
reg [31:0] expected_out_prep_count;
initial expected_out_prep_count <= #SHIFT_NS tb_candidate_offer.system.out_prep_count;
always @(tb_candidate_offer.system.out_prep_count) expected_out_prep_count <= #SHIFT_NS tb_candidate_offer.system.out_prep_count;
wire [31:0] actual_out_prep_history;
reg [31:0] expected_out_prep_history;
initial expected_out_prep_history <= #SHIFT_NS tb_candidate_offer.system.out_prep_history;
always @(tb_candidate_offer.system.out_prep_history) expected_out_prep_history <= #SHIFT_NS tb_candidate_offer.system.out_prep_history;
wire [127:0] actual_out_prep_net_data;
reg [127:0] expected_out_prep_net_data;
initial expected_out_prep_net_data <= #SHIFT_NS tb_candidate_offer.system.out_prep_net_data;
always @(tb_candidate_offer.system.out_prep_net_data) expected_out_prep_net_data <= #SHIFT_NS tb_candidate_offer.system.out_prep_net_data;
wire [31:0] actual_out_prep_occupancy;
reg [31:0] expected_out_prep_occupancy;
initial expected_out_prep_occupancy <= #SHIFT_NS tb_candidate_offer.system.out_prep_occupancy;
always @(tb_candidate_offer.system.out_prep_occupancy) expected_out_prep_occupancy <= #SHIFT_NS tb_candidate_offer.system.out_prep_occupancy;
wire [31:0] actual_out_prep_price_index;
reg [31:0] expected_out_prep_price_index;
initial expected_out_prep_price_index <= #SHIFT_NS tb_candidate_offer.system.out_prep_price_index;
always @(tb_candidate_offer.system.out_prep_price_index) expected_out_prep_price_index <= #SHIFT_NS tb_candidate_offer.system.out_prep_price_index;
wire [31:0] actual_out_prep_price_value;
reg [31:0] expected_out_prep_price_value;
initial expected_out_prep_price_value <= #SHIFT_NS tb_candidate_offer.system.out_prep_price_value;
always @(tb_candidate_offer.system.out_prep_price_value) expected_out_prep_price_value <= #SHIFT_NS tb_candidate_offer.system.out_prep_price_value;
wire [3:0] actual_out_prep_status;
reg [3:0] expected_out_prep_status;
initial expected_out_prep_status <= #SHIFT_NS tb_candidate_offer.system.out_prep_status;
always @(tb_candidate_offer.system.out_prep_status) expected_out_prep_status <= #SHIFT_NS tb_candidate_offer.system.out_prep_status;
wire actual_out_prep_valid;
reg expected_out_prep_valid;
initial expected_out_prep_valid <= #SHIFT_NS tb_candidate_offer.system.out_prep_valid;
always @(tb_candidate_offer.system.out_prep_valid) expected_out_prep_valid <= #SHIFT_NS tb_candidate_offer.system.out_prep_valid;
wire [31:0] actual_out_profile_revision;
reg [31:0] expected_out_profile_revision;
initial expected_out_profile_revision <= #SHIFT_NS tb_candidate_offer.system.out_profile_revision;
always @(tb_candidate_offer.system.out_profile_revision) expected_out_profile_revision <= #SHIFT_NS tb_candidate_offer.system.out_profile_revision;
reg drive_out_ready;
initial drive_out_ready <= #SHIFT_NS tb_candidate_offer.system.out_ready;
always @(tb_candidate_offer.system.out_ready) drive_out_ready <= #SHIFT_NS tb_candidate_offer.system.out_ready;
wire [31:0] actual_out_sequence;
reg [31:0] expected_out_sequence;
initial expected_out_sequence <= #SHIFT_NS tb_candidate_offer.system.out_sequence;
always @(tb_candidate_offer.system.out_sequence) expected_out_sequence <= #SHIFT_NS tb_candidate_offer.system.out_sequence;
wire [31:0] actual_out_services;
reg [31:0] expected_out_services;
initial expected_out_services <= #SHIFT_NS tb_candidate_offer.system.out_services;
always @(tb_candidate_offer.system.out_services) expected_out_services <= #SHIFT_NS tb_candidate_offer.system.out_services;
wire [31:0] actual_out_steps;
reg [31:0] expected_out_steps;
initial expected_out_steps <= #SHIFT_NS tb_candidate_offer.system.out_steps;
always @(tb_candidate_offer.system.out_steps) expected_out_steps <= #SHIFT_NS tb_candidate_offer.system.out_steps;
wire actual_out_valid;
reg expected_out_valid;
initial expected_out_valid <= #SHIFT_NS tb_candidate_offer.system.out_valid;
always @(tb_candidate_offer.system.out_valid) expected_out_valid <= #SHIFT_NS tb_candidate_offer.system.out_valid;
wire actual_owner_configured;
reg expected_owner_configured;
initial expected_owner_configured <= #SHIFT_NS tb_candidate_offer.system.owner_configured;
always @(tb_candidate_offer.system.owner_configured) expected_owner_configured <= #SHIFT_NS tb_candidate_offer.system.owner_configured;
wire [63:0] actual_owner_m_araddr;
reg [63:0] expected_owner_m_araddr;
initial expected_owner_m_araddr <= #SHIFT_NS tb_candidate_offer.system.owner_m_araddr;
always @(tb_candidate_offer.system.owner_m_araddr) expected_owner_m_araddr <= #SHIFT_NS tb_candidate_offer.system.owner_m_araddr;
wire [1:0] actual_owner_m_arburst;
reg [1:0] expected_owner_m_arburst;
initial expected_owner_m_arburst <= #SHIFT_NS tb_candidate_offer.system.owner_m_arburst;
always @(tb_candidate_offer.system.owner_m_arburst) expected_owner_m_arburst <= #SHIFT_NS tb_candidate_offer.system.owner_m_arburst;
wire [3:0] actual_owner_m_arid;
reg [3:0] expected_owner_m_arid;
initial expected_owner_m_arid <= #SHIFT_NS tb_candidate_offer.system.owner_m_arid;
always @(tb_candidate_offer.system.owner_m_arid) expected_owner_m_arid <= #SHIFT_NS tb_candidate_offer.system.owner_m_arid;
wire [7:0] actual_owner_m_arlen;
reg [7:0] expected_owner_m_arlen;
initial expected_owner_m_arlen <= #SHIFT_NS tb_candidate_offer.system.owner_m_arlen;
always @(tb_candidate_offer.system.owner_m_arlen) expected_owner_m_arlen <= #SHIFT_NS tb_candidate_offer.system.owner_m_arlen;
reg drive_owner_m_arready;
initial drive_owner_m_arready <= #SHIFT_NS tb_candidate_offer.system.owner_m_arready;
always @(tb_candidate_offer.system.owner_m_arready) drive_owner_m_arready <= #SHIFT_NS tb_candidate_offer.system.owner_m_arready;
wire [2:0] actual_owner_m_arsize;
reg [2:0] expected_owner_m_arsize;
initial expected_owner_m_arsize <= #SHIFT_NS tb_candidate_offer.system.owner_m_arsize;
always @(tb_candidate_offer.system.owner_m_arsize) expected_owner_m_arsize <= #SHIFT_NS tb_candidate_offer.system.owner_m_arsize;
wire actual_owner_m_arvalid;
reg expected_owner_m_arvalid;
initial expected_owner_m_arvalid <= #SHIFT_NS tb_candidate_offer.system.owner_m_arvalid;
always @(tb_candidate_offer.system.owner_m_arvalid) expected_owner_m_arvalid <= #SHIFT_NS tb_candidate_offer.system.owner_m_arvalid;
wire [63:0] actual_owner_m_awaddr;
reg [63:0] expected_owner_m_awaddr;
initial expected_owner_m_awaddr <= #SHIFT_NS tb_candidate_offer.system.owner_m_awaddr;
always @(tb_candidate_offer.system.owner_m_awaddr) expected_owner_m_awaddr <= #SHIFT_NS tb_candidate_offer.system.owner_m_awaddr;
wire [1:0] actual_owner_m_awburst;
reg [1:0] expected_owner_m_awburst;
initial expected_owner_m_awburst <= #SHIFT_NS tb_candidate_offer.system.owner_m_awburst;
always @(tb_candidate_offer.system.owner_m_awburst) expected_owner_m_awburst <= #SHIFT_NS tb_candidate_offer.system.owner_m_awburst;
wire [3:0] actual_owner_m_awid;
reg [3:0] expected_owner_m_awid;
initial expected_owner_m_awid <= #SHIFT_NS tb_candidate_offer.system.owner_m_awid;
always @(tb_candidate_offer.system.owner_m_awid) expected_owner_m_awid <= #SHIFT_NS tb_candidate_offer.system.owner_m_awid;
wire [7:0] actual_owner_m_awlen;
reg [7:0] expected_owner_m_awlen;
initial expected_owner_m_awlen <= #SHIFT_NS tb_candidate_offer.system.owner_m_awlen;
always @(tb_candidate_offer.system.owner_m_awlen) expected_owner_m_awlen <= #SHIFT_NS tb_candidate_offer.system.owner_m_awlen;
reg drive_owner_m_awready;
initial drive_owner_m_awready <= #SHIFT_NS tb_candidate_offer.system.owner_m_awready;
always @(tb_candidate_offer.system.owner_m_awready) drive_owner_m_awready <= #SHIFT_NS tb_candidate_offer.system.owner_m_awready;
wire [2:0] actual_owner_m_awsize;
reg [2:0] expected_owner_m_awsize;
initial expected_owner_m_awsize <= #SHIFT_NS tb_candidate_offer.system.owner_m_awsize;
always @(tb_candidate_offer.system.owner_m_awsize) expected_owner_m_awsize <= #SHIFT_NS tb_candidate_offer.system.owner_m_awsize;
wire actual_owner_m_awvalid;
reg expected_owner_m_awvalid;
initial expected_owner_m_awvalid <= #SHIFT_NS tb_candidate_offer.system.owner_m_awvalid;
always @(tb_candidate_offer.system.owner_m_awvalid) expected_owner_m_awvalid <= #SHIFT_NS tb_candidate_offer.system.owner_m_awvalid;
reg [3:0] drive_owner_m_bid;
initial drive_owner_m_bid <= #SHIFT_NS tb_candidate_offer.system.owner_m_bid;
always @(tb_candidate_offer.system.owner_m_bid) drive_owner_m_bid <= #SHIFT_NS tb_candidate_offer.system.owner_m_bid;
wire actual_owner_m_bready;
reg expected_owner_m_bready;
initial expected_owner_m_bready <= #SHIFT_NS tb_candidate_offer.system.owner_m_bready;
always @(tb_candidate_offer.system.owner_m_bready) expected_owner_m_bready <= #SHIFT_NS tb_candidate_offer.system.owner_m_bready;
reg [1:0] drive_owner_m_bresp;
initial drive_owner_m_bresp <= #SHIFT_NS tb_candidate_offer.system.owner_m_bresp;
always @(tb_candidate_offer.system.owner_m_bresp) drive_owner_m_bresp <= #SHIFT_NS tb_candidate_offer.system.owner_m_bresp;
reg drive_owner_m_bvalid;
initial drive_owner_m_bvalid <= #SHIFT_NS tb_candidate_offer.system.owner_m_bvalid;
always @(tb_candidate_offer.system.owner_m_bvalid) drive_owner_m_bvalid <= #SHIFT_NS tb_candidate_offer.system.owner_m_bvalid;
reg [511:0] drive_owner_m_rdata;
initial drive_owner_m_rdata <= #SHIFT_NS tb_candidate_offer.system.owner_m_rdata;
always @(tb_candidate_offer.system.owner_m_rdata) drive_owner_m_rdata <= #SHIFT_NS tb_candidate_offer.system.owner_m_rdata;
reg [3:0] drive_owner_m_rid;
initial drive_owner_m_rid <= #SHIFT_NS tb_candidate_offer.system.owner_m_rid;
always @(tb_candidate_offer.system.owner_m_rid) drive_owner_m_rid <= #SHIFT_NS tb_candidate_offer.system.owner_m_rid;
reg drive_owner_m_rlast;
initial drive_owner_m_rlast <= #SHIFT_NS tb_candidate_offer.system.owner_m_rlast;
always @(tb_candidate_offer.system.owner_m_rlast) drive_owner_m_rlast <= #SHIFT_NS tb_candidate_offer.system.owner_m_rlast;
wire actual_owner_m_rready;
reg expected_owner_m_rready;
initial expected_owner_m_rready <= #SHIFT_NS tb_candidate_offer.system.owner_m_rready;
always @(tb_candidate_offer.system.owner_m_rready) expected_owner_m_rready <= #SHIFT_NS tb_candidate_offer.system.owner_m_rready;
reg [1:0] drive_owner_m_rresp;
initial drive_owner_m_rresp <= #SHIFT_NS tb_candidate_offer.system.owner_m_rresp;
always @(tb_candidate_offer.system.owner_m_rresp) drive_owner_m_rresp <= #SHIFT_NS tb_candidate_offer.system.owner_m_rresp;
reg drive_owner_m_rvalid;
initial drive_owner_m_rvalid <= #SHIFT_NS tb_candidate_offer.system.owner_m_rvalid;
always @(tb_candidate_offer.system.owner_m_rvalid) drive_owner_m_rvalid <= #SHIFT_NS tb_candidate_offer.system.owner_m_rvalid;
wire [511:0] actual_owner_m_wdata;
reg [511:0] expected_owner_m_wdata;
initial expected_owner_m_wdata <= #SHIFT_NS tb_candidate_offer.system.owner_m_wdata;
always @(tb_candidate_offer.system.owner_m_wdata) expected_owner_m_wdata <= #SHIFT_NS tb_candidate_offer.system.owner_m_wdata;
wire actual_owner_m_wlast;
reg expected_owner_m_wlast;
initial expected_owner_m_wlast <= #SHIFT_NS tb_candidate_offer.system.owner_m_wlast;
always @(tb_candidate_offer.system.owner_m_wlast) expected_owner_m_wlast <= #SHIFT_NS tb_candidate_offer.system.owner_m_wlast;
reg drive_owner_m_wready;
initial drive_owner_m_wready <= #SHIFT_NS tb_candidate_offer.system.owner_m_wready;
always @(tb_candidate_offer.system.owner_m_wready) drive_owner_m_wready <= #SHIFT_NS tb_candidate_offer.system.owner_m_wready;
wire [63:0] actual_owner_m_wstrb;
reg [63:0] expected_owner_m_wstrb;
initial expected_owner_m_wstrb <= #SHIFT_NS tb_candidate_offer.system.owner_m_wstrb;
always @(tb_candidate_offer.system.owner_m_wstrb) expected_owner_m_wstrb <= #SHIFT_NS tb_candidate_offer.system.owner_m_wstrb;
wire actual_owner_m_wvalid;
reg expected_owner_m_wvalid;
initial expected_owner_m_wvalid <= #SHIFT_NS tb_candidate_offer.system.owner_m_wvalid;
always @(tb_candidate_offer.system.owner_m_wvalid) expected_owner_m_wvalid <= #SHIFT_NS tb_candidate_offer.system.owner_m_wvalid;
wire actual_p_active;
reg expected_p_active;
initial expected_p_active <= #SHIFT_NS tb_candidate_offer.system.p_active;
always @(tb_candidate_offer.system.p_active) expected_p_active <= #SHIFT_NS tb_candidate_offer.system.p_active;
wire [3:0] actual_p_active_price;
reg [3:0] expected_p_active_price;
initial expected_p_active_price <= #SHIFT_NS tb_candidate_offer.system.p_active_price;
always @(tb_candidate_offer.system.p_active_price) expected_p_active_price <= #SHIFT_NS tb_candidate_offer.system.p_active_price;
wire [1:0] actual_p_active_query;
reg [1:0] expected_p_active_query;
initial expected_p_active_query <= #SHIFT_NS tb_candidate_offer.system.p_active_query;
always @(tb_candidate_offer.system.p_active_query) expected_p_active_query <= #SHIFT_NS tb_candidate_offer.system.p_active_query;
wire [31:0] actual_p_m_araddr;
reg [31:0] expected_p_m_araddr;
initial expected_p_m_araddr <= #SHIFT_NS tb_candidate_offer.system.p_m_araddr;
always @(tb_candidate_offer.system.p_m_araddr) expected_p_m_araddr <= #SHIFT_NS tb_candidate_offer.system.p_m_araddr;
wire [1:0] actual_p_m_arburst;
reg [1:0] expected_p_m_arburst;
initial expected_p_m_arburst <= #SHIFT_NS tb_candidate_offer.system.p_m_arburst;
always @(tb_candidate_offer.system.p_m_arburst) expected_p_m_arburst <= #SHIFT_NS tb_candidate_offer.system.p_m_arburst;
wire [3:0] actual_p_m_arid;
reg [3:0] expected_p_m_arid;
initial expected_p_m_arid <= #SHIFT_NS tb_candidate_offer.system.p_m_arid;
always @(tb_candidate_offer.system.p_m_arid) expected_p_m_arid <= #SHIFT_NS tb_candidate_offer.system.p_m_arid;
wire [7:0] actual_p_m_arlen;
reg [7:0] expected_p_m_arlen;
initial expected_p_m_arlen <= #SHIFT_NS tb_candidate_offer.system.p_m_arlen;
always @(tb_candidate_offer.system.p_m_arlen) expected_p_m_arlen <= #SHIFT_NS tb_candidate_offer.system.p_m_arlen;
reg drive_p_m_arready;
initial drive_p_m_arready <= #SHIFT_NS tb_candidate_offer.system.p_m_arready;
always @(tb_candidate_offer.system.p_m_arready) drive_p_m_arready <= #SHIFT_NS tb_candidate_offer.system.p_m_arready;
wire [2:0] actual_p_m_arsize;
reg [2:0] expected_p_m_arsize;
initial expected_p_m_arsize <= #SHIFT_NS tb_candidate_offer.system.p_m_arsize;
always @(tb_candidate_offer.system.p_m_arsize) expected_p_m_arsize <= #SHIFT_NS tb_candidate_offer.system.p_m_arsize;
wire actual_p_m_arvalid;
reg expected_p_m_arvalid;
initial expected_p_m_arvalid <= #SHIFT_NS tb_candidate_offer.system.p_m_arvalid;
always @(tb_candidate_offer.system.p_m_arvalid) expected_p_m_arvalid <= #SHIFT_NS tb_candidate_offer.system.p_m_arvalid;
wire [31:0] actual_p_m_awaddr;
reg [31:0] expected_p_m_awaddr;
initial expected_p_m_awaddr <= #SHIFT_NS tb_candidate_offer.system.p_m_awaddr;
always @(tb_candidate_offer.system.p_m_awaddr) expected_p_m_awaddr <= #SHIFT_NS tb_candidate_offer.system.p_m_awaddr;
wire [1:0] actual_p_m_awburst;
reg [1:0] expected_p_m_awburst;
initial expected_p_m_awburst <= #SHIFT_NS tb_candidate_offer.system.p_m_awburst;
always @(tb_candidate_offer.system.p_m_awburst) expected_p_m_awburst <= #SHIFT_NS tb_candidate_offer.system.p_m_awburst;
wire [3:0] actual_p_m_awid;
reg [3:0] expected_p_m_awid;
initial expected_p_m_awid <= #SHIFT_NS tb_candidate_offer.system.p_m_awid;
always @(tb_candidate_offer.system.p_m_awid) expected_p_m_awid <= #SHIFT_NS tb_candidate_offer.system.p_m_awid;
wire [7:0] actual_p_m_awlen;
reg [7:0] expected_p_m_awlen;
initial expected_p_m_awlen <= #SHIFT_NS tb_candidate_offer.system.p_m_awlen;
always @(tb_candidate_offer.system.p_m_awlen) expected_p_m_awlen <= #SHIFT_NS tb_candidate_offer.system.p_m_awlen;
reg drive_p_m_awready;
initial drive_p_m_awready <= #SHIFT_NS tb_candidate_offer.system.p_m_awready;
always @(tb_candidate_offer.system.p_m_awready) drive_p_m_awready <= #SHIFT_NS tb_candidate_offer.system.p_m_awready;
wire [2:0] actual_p_m_awsize;
reg [2:0] expected_p_m_awsize;
initial expected_p_m_awsize <= #SHIFT_NS tb_candidate_offer.system.p_m_awsize;
always @(tb_candidate_offer.system.p_m_awsize) expected_p_m_awsize <= #SHIFT_NS tb_candidate_offer.system.p_m_awsize;
wire actual_p_m_awvalid;
reg expected_p_m_awvalid;
initial expected_p_m_awvalid <= #SHIFT_NS tb_candidate_offer.system.p_m_awvalid;
always @(tb_candidate_offer.system.p_m_awvalid) expected_p_m_awvalid <= #SHIFT_NS tb_candidate_offer.system.p_m_awvalid;
reg [3:0] drive_p_m_bid;
initial drive_p_m_bid <= #SHIFT_NS tb_candidate_offer.system.p_m_bid;
always @(tb_candidate_offer.system.p_m_bid) drive_p_m_bid <= #SHIFT_NS tb_candidate_offer.system.p_m_bid;
wire actual_p_m_bready;
reg expected_p_m_bready;
initial expected_p_m_bready <= #SHIFT_NS tb_candidate_offer.system.p_m_bready;
always @(tb_candidate_offer.system.p_m_bready) expected_p_m_bready <= #SHIFT_NS tb_candidate_offer.system.p_m_bready;
reg [1:0] drive_p_m_bresp;
initial drive_p_m_bresp <= #SHIFT_NS tb_candidate_offer.system.p_m_bresp;
always @(tb_candidate_offer.system.p_m_bresp) drive_p_m_bresp <= #SHIFT_NS tb_candidate_offer.system.p_m_bresp;
reg drive_p_m_bvalid;
initial drive_p_m_bvalid <= #SHIFT_NS tb_candidate_offer.system.p_m_bvalid;
always @(tb_candidate_offer.system.p_m_bvalid) drive_p_m_bvalid <= #SHIFT_NS tb_candidate_offer.system.p_m_bvalid;
reg [511:0] drive_p_m_rdata;
initial drive_p_m_rdata <= #SHIFT_NS tb_candidate_offer.system.p_m_rdata;
always @(tb_candidate_offer.system.p_m_rdata) drive_p_m_rdata <= #SHIFT_NS tb_candidate_offer.system.p_m_rdata;
reg [3:0] drive_p_m_rid;
initial drive_p_m_rid <= #SHIFT_NS tb_candidate_offer.system.p_m_rid;
always @(tb_candidate_offer.system.p_m_rid) drive_p_m_rid <= #SHIFT_NS tb_candidate_offer.system.p_m_rid;
reg drive_p_m_rlast;
initial drive_p_m_rlast <= #SHIFT_NS tb_candidate_offer.system.p_m_rlast;
always @(tb_candidate_offer.system.p_m_rlast) drive_p_m_rlast <= #SHIFT_NS tb_candidate_offer.system.p_m_rlast;
wire actual_p_m_rready;
reg expected_p_m_rready;
initial expected_p_m_rready <= #SHIFT_NS tb_candidate_offer.system.p_m_rready;
always @(tb_candidate_offer.system.p_m_rready) expected_p_m_rready <= #SHIFT_NS tb_candidate_offer.system.p_m_rready;
reg [1:0] drive_p_m_rresp;
initial drive_p_m_rresp <= #SHIFT_NS tb_candidate_offer.system.p_m_rresp;
always @(tb_candidate_offer.system.p_m_rresp) drive_p_m_rresp <= #SHIFT_NS tb_candidate_offer.system.p_m_rresp;
reg drive_p_m_rvalid;
initial drive_p_m_rvalid <= #SHIFT_NS tb_candidate_offer.system.p_m_rvalid;
always @(tb_candidate_offer.system.p_m_rvalid) drive_p_m_rvalid <= #SHIFT_NS tb_candidate_offer.system.p_m_rvalid;
wire [511:0] actual_p_m_wdata;
reg [511:0] expected_p_m_wdata;
initial expected_p_m_wdata <= #SHIFT_NS tb_candidate_offer.system.p_m_wdata;
always @(tb_candidate_offer.system.p_m_wdata) expected_p_m_wdata <= #SHIFT_NS tb_candidate_offer.system.p_m_wdata;
wire actual_p_m_wlast;
reg expected_p_m_wlast;
initial expected_p_m_wlast <= #SHIFT_NS tb_candidate_offer.system.p_m_wlast;
always @(tb_candidate_offer.system.p_m_wlast) expected_p_m_wlast <= #SHIFT_NS tb_candidate_offer.system.p_m_wlast;
reg drive_p_m_wready;
initial drive_p_m_wready <= #SHIFT_NS tb_candidate_offer.system.p_m_wready;
always @(tb_candidate_offer.system.p_m_wready) drive_p_m_wready <= #SHIFT_NS tb_candidate_offer.system.p_m_wready;
wire [63:0] actual_p_m_wstrb;
reg [63:0] expected_p_m_wstrb;
initial expected_p_m_wstrb <= #SHIFT_NS tb_candidate_offer.system.p_m_wstrb;
always @(tb_candidate_offer.system.p_m_wstrb) expected_p_m_wstrb <= #SHIFT_NS tb_candidate_offer.system.p_m_wstrb;
wire actual_p_m_wvalid;
reg expected_p_m_wvalid;
initial expected_p_m_wvalid <= #SHIFT_NS tb_candidate_offer.system.p_m_wvalid;
always @(tb_candidate_offer.system.p_m_wvalid) expected_p_m_wvalid <= #SHIFT_NS tb_candidate_offer.system.p_m_wvalid;
wire actual_q_busy;
reg expected_q_busy;
initial expected_q_busy <= #SHIFT_NS tb_candidate_offer.system.q_busy;
always @(tb_candidate_offer.system.q_busy) expected_q_busy <= #SHIFT_NS tb_candidate_offer.system.q_busy;
wire actual_q_configured;
reg expected_q_configured;
initial expected_q_configured <= #SHIFT_NS tb_candidate_offer.system.q_configured;
always @(tb_candidate_offer.system.q_configured) expected_q_configured <= #SHIFT_NS tb_candidate_offer.system.q_configured;
wire actual_q_fault;
reg expected_q_fault;
initial expected_q_fault <= #SHIFT_NS tb_candidate_offer.system.q_fault;
always @(tb_candidate_offer.system.q_fault) expected_q_fault <= #SHIFT_NS tb_candidate_offer.system.q_fault;
wire [63:0] actual_q_m_araddr;
reg [63:0] expected_q_m_araddr;
initial expected_q_m_araddr <= #SHIFT_NS tb_candidate_offer.system.q_m_araddr;
always @(tb_candidate_offer.system.q_m_araddr) expected_q_m_araddr <= #SHIFT_NS tb_candidate_offer.system.q_m_araddr;
wire [1:0] actual_q_m_arburst;
reg [1:0] expected_q_m_arburst;
initial expected_q_m_arburst <= #SHIFT_NS tb_candidate_offer.system.q_m_arburst;
always @(tb_candidate_offer.system.q_m_arburst) expected_q_m_arburst <= #SHIFT_NS tb_candidate_offer.system.q_m_arburst;
wire [3:0] actual_q_m_arid;
reg [3:0] expected_q_m_arid;
initial expected_q_m_arid <= #SHIFT_NS tb_candidate_offer.system.q_m_arid;
always @(tb_candidate_offer.system.q_m_arid) expected_q_m_arid <= #SHIFT_NS tb_candidate_offer.system.q_m_arid;
wire [7:0] actual_q_m_arlen;
reg [7:0] expected_q_m_arlen;
initial expected_q_m_arlen <= #SHIFT_NS tb_candidate_offer.system.q_m_arlen;
always @(tb_candidate_offer.system.q_m_arlen) expected_q_m_arlen <= #SHIFT_NS tb_candidate_offer.system.q_m_arlen;
reg drive_q_m_arready;
initial drive_q_m_arready <= #SHIFT_NS tb_candidate_offer.system.q_m_arready;
always @(tb_candidate_offer.system.q_m_arready) drive_q_m_arready <= #SHIFT_NS tb_candidate_offer.system.q_m_arready;
wire [2:0] actual_q_m_arsize;
reg [2:0] expected_q_m_arsize;
initial expected_q_m_arsize <= #SHIFT_NS tb_candidate_offer.system.q_m_arsize;
always @(tb_candidate_offer.system.q_m_arsize) expected_q_m_arsize <= #SHIFT_NS tb_candidate_offer.system.q_m_arsize;
wire actual_q_m_arvalid;
reg expected_q_m_arvalid;
initial expected_q_m_arvalid <= #SHIFT_NS tb_candidate_offer.system.q_m_arvalid;
always @(tb_candidate_offer.system.q_m_arvalid) expected_q_m_arvalid <= #SHIFT_NS tb_candidate_offer.system.q_m_arvalid;
reg [511:0] drive_q_m_rdata;
initial drive_q_m_rdata <= #SHIFT_NS tb_candidate_offer.system.q_m_rdata;
always @(tb_candidate_offer.system.q_m_rdata) drive_q_m_rdata <= #SHIFT_NS tb_candidate_offer.system.q_m_rdata;
reg [3:0] drive_q_m_rid;
initial drive_q_m_rid <= #SHIFT_NS tb_candidate_offer.system.q_m_rid;
always @(tb_candidate_offer.system.q_m_rid) drive_q_m_rid <= #SHIFT_NS tb_candidate_offer.system.q_m_rid;
reg drive_q_m_rlast;
initial drive_q_m_rlast <= #SHIFT_NS tb_candidate_offer.system.q_m_rlast;
always @(tb_candidate_offer.system.q_m_rlast) drive_q_m_rlast <= #SHIFT_NS tb_candidate_offer.system.q_m_rlast;
wire actual_q_m_rready;
reg expected_q_m_rready;
initial expected_q_m_rready <= #SHIFT_NS tb_candidate_offer.system.q_m_rready;
always @(tb_candidate_offer.system.q_m_rready) expected_q_m_rready <= #SHIFT_NS tb_candidate_offer.system.q_m_rready;
reg [1:0] drive_q_m_rresp;
initial drive_q_m_rresp <= #SHIFT_NS tb_candidate_offer.system.q_m_rresp;
always @(tb_candidate_offer.system.q_m_rresp) drive_q_m_rresp <= #SHIFT_NS tb_candidate_offer.system.q_m_rresp;
reg drive_q_m_rvalid;
initial drive_q_m_rvalid <= #SHIFT_NS tb_candidate_offer.system.q_m_rvalid;
always @(tb_candidate_offer.system.q_m_rvalid) drive_q_m_rvalid <= #SHIFT_NS tb_candidate_offer.system.q_m_rvalid;
wire actual_query_ready;
reg expected_query_ready;
initial expected_query_ready <= #SHIFT_NS tb_candidate_offer.system.query_ready;
always @(tb_candidate_offer.system.query_ready) expected_query_ready <= #SHIFT_NS tb_candidate_offer.system.query_ready;
wire [31:0] actual_query_version;
reg [31:0] expected_query_version;
initial expected_query_version <= #SHIFT_NS tb_candidate_offer.system.query_version;
always @(tb_candidate_offer.system.query_version) expected_query_version <= #SHIFT_NS tb_candidate_offer.system.query_version;
wire actual_rc_block;
reg expected_rc_block;
initial expected_rc_block <= #SHIFT_NS tb_candidate_offer.system.rc_block;
always @(tb_candidate_offer.system.rc_block) expected_rc_block <= #SHIFT_NS tb_candidate_offer.system.rc_block;
wire actual_rc_busy;
reg expected_rc_busy;
initial expected_rc_busy <= #SHIFT_NS tb_candidate_offer.system.rc_busy;
always @(tb_candidate_offer.system.rc_busy) expected_rc_busy <= #SHIFT_NS tb_candidate_offer.system.rc_busy;
wire actual_rc_fault;
reg expected_rc_fault;
initial expected_rc_fault <= #SHIFT_NS tb_candidate_offer.system.rc_fault;
always @(tb_candidate_offer.system.rc_fault) expected_rc_fault <= #SHIFT_NS tb_candidate_offer.system.rc_fault;
wire actual_rc_req_ready;
reg expected_rc_req_ready;
initial expected_rc_req_ready <= #SHIFT_NS tb_candidate_offer.system.rc_req_ready;
always @(tb_candidate_offer.system.rc_req_ready) expected_rc_req_ready <= #SHIFT_NS tb_candidate_offer.system.rc_req_ready;
reg drive_rc_req_valid;
initial drive_rc_req_valid <= #SHIFT_NS tb_candidate_offer.system.rc_req_valid;
always @(tb_candidate_offer.system.rc_req_valid) drive_rc_req_valid <= #SHIFT_NS tb_candidate_offer.system.rc_req_valid;
wire [31:0] actual_rc_rsp_acked;
reg [31:0] expected_rc_rsp_acked;
initial expected_rc_rsp_acked <= #SHIFT_NS tb_candidate_offer.system.rc_rsp_acked;
always @(tb_candidate_offer.system.rc_rsp_acked) expected_rc_rsp_acked <= #SHIFT_NS tb_candidate_offer.system.rc_rsp_acked;
wire [31:0] actual_rc_rsp_cookie;
reg [31:0] expected_rc_rsp_cookie;
initial expected_rc_rsp_cookie <= #SHIFT_NS tb_candidate_offer.system.rc_rsp_cookie;
always @(tb_candidate_offer.system.rc_rsp_cookie) expected_rc_rsp_cookie <= #SHIFT_NS tb_candidate_offer.system.rc_rsp_cookie;
wire [31:0] actual_rc_rsp_nodes;
reg [31:0] expected_rc_rsp_nodes;
initial expected_rc_rsp_nodes <= #SHIFT_NS tb_candidate_offer.system.rc_rsp_nodes;
always @(tb_candidate_offer.system.rc_rsp_nodes) expected_rc_rsp_nodes <= #SHIFT_NS tb_candidate_offer.system.rc_rsp_nodes;
reg drive_rc_rsp_ready;
initial drive_rc_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.rc_rsp_ready;
always @(tb_candidate_offer.system.rc_rsp_ready) drive_rc_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.rc_rsp_ready;
wire [3:0] actual_rc_rsp_status;
reg [3:0] expected_rc_rsp_status;
initial expected_rc_rsp_status <= #SHIFT_NS tb_candidate_offer.system.rc_rsp_status;
always @(tb_candidate_offer.system.rc_rsp_status) expected_rc_rsp_status <= #SHIFT_NS tb_candidate_offer.system.rc_rsp_status;
wire actual_rc_rsp_valid;
reg expected_rc_rsp_valid;
initial expected_rc_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.rc_rsp_valid;
always @(tb_candidate_offer.system.rc_rsp_valid) expected_rc_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.rc_rsp_valid;
wire [3:0] actual_rc_slots;
reg [3:0] expected_rc_slots;
initial expected_rc_slots <= #SHIFT_NS tb_candidate_offer.system.rc_slots;
always @(tb_candidate_offer.system.rc_slots) expected_rc_slots <= #SHIFT_NS tb_candidate_offer.system.rc_slots;
reg [31:0] drive_recover_checkpoint;
initial drive_recover_checkpoint <= #SHIFT_NS tb_candidate_offer.system.recover_checkpoint;
always @(tb_candidate_offer.system.recover_checkpoint) drive_recover_checkpoint <= #SHIFT_NS tb_candidate_offer.system.recover_checkpoint;
reg [31:0] drive_recover_cookie;
initial drive_recover_cookie <= #SHIFT_NS tb_candidate_offer.system.recover_cookie;
always @(tb_candidate_offer.system.recover_cookie) drive_recover_cookie <= #SHIFT_NS tb_candidate_offer.system.recover_cookie;
reg [63:0] drive_recover_design;
initial drive_recover_design <= #SHIFT_NS tb_candidate_offer.system.recover_design;
always @(tb_candidate_offer.system.recover_design) drive_recover_design <= #SHIFT_NS tb_candidate_offer.system.recover_design;
reg [3:0] drive_recover_price;
initial drive_recover_price <= #SHIFT_NS tb_candidate_offer.system.recover_price;
always @(tb_candidate_offer.system.recover_price) drive_recover_price <= #SHIFT_NS tb_candidate_offer.system.recover_price;
reg [1:0] drive_recover_query;
initial drive_recover_query <= #SHIFT_NS tb_candidate_offer.system.recover_query;
always @(tb_candidate_offer.system.recover_query) drive_recover_query <= #SHIFT_NS tb_candidate_offer.system.recover_query;
reg [31:0] drive_recover_version;
initial drive_recover_version <= #SHIFT_NS tb_candidate_offer.system.recover_version;
always @(tb_candidate_offer.system.recover_version) drive_recover_version <= #SHIFT_NS tb_candidate_offer.system.recover_version;
wire actual_rst;
reg expected_rst;
initial expected_rst <= #SHIFT_NS tb_candidate_offer.system.rst;
always @(tb_candidate_offer.system.rst) expected_rst <= #SHIFT_NS tb_candidate_offer.system.rst;
reg [31:0] drive_snapshot_checkpoint;
initial drive_snapshot_checkpoint <= #SHIFT_NS tb_candidate_offer.system.snapshot_checkpoint;
always @(tb_candidate_offer.system.snapshot_checkpoint) drive_snapshot_checkpoint <= #SHIFT_NS tb_candidate_offer.system.snapshot_checkpoint;
reg [31:0] drive_snapshot_cookie;
initial drive_snapshot_cookie <= #SHIFT_NS tb_candidate_offer.system.snapshot_cookie;
always @(tb_candidate_offer.system.snapshot_cookie) drive_snapshot_cookie <= #SHIFT_NS tb_candidate_offer.system.snapshot_cookie;
reg [31:0] drive_snapshot_count;
initial drive_snapshot_count <= #SHIFT_NS tb_candidate_offer.system.snapshot_count;
always @(tb_candidate_offer.system.snapshot_count) drive_snapshot_count <= #SHIFT_NS tb_candidate_offer.system.snapshot_count;
reg [63:0] drive_snapshot_design;
initial drive_snapshot_design <= #SHIFT_NS tb_candidate_offer.system.snapshot_design;
always @(tb_candidate_offer.system.snapshot_design) drive_snapshot_design <= #SHIFT_NS tb_candidate_offer.system.snapshot_design;
reg [31:0] drive_snapshot_nodes;
initial drive_snapshot_nodes <= #SHIFT_NS tb_candidate_offer.system.snapshot_nodes;
always @(tb_candidate_offer.system.snapshot_nodes) drive_snapshot_nodes <= #SHIFT_NS tb_candidate_offer.system.snapshot_nodes;
reg [31:0] drive_snapshot_probe;
initial drive_snapshot_probe <= #SHIFT_NS tb_candidate_offer.system.snapshot_probe;
always @(tb_candidate_offer.system.snapshot_probe) drive_snapshot_probe <= #SHIFT_NS tb_candidate_offer.system.snapshot_probe;
wire actual_t_configured;
reg expected_t_configured;
initial expected_t_configured <= #SHIFT_NS tb_candidate_offer.system.t_configured;
always @(tb_candidate_offer.system.t_configured) expected_t_configured <= #SHIFT_NS tb_candidate_offer.system.t_configured;
wire [63:0] actual_t_m_araddr;
reg [63:0] expected_t_m_araddr;
initial expected_t_m_araddr <= #SHIFT_NS tb_candidate_offer.system.t_m_araddr;
always @(tb_candidate_offer.system.t_m_araddr) expected_t_m_araddr <= #SHIFT_NS tb_candidate_offer.system.t_m_araddr;
wire [1:0] actual_t_m_arburst;
reg [1:0] expected_t_m_arburst;
initial expected_t_m_arburst <= #SHIFT_NS tb_candidate_offer.system.t_m_arburst;
always @(tb_candidate_offer.system.t_m_arburst) expected_t_m_arburst <= #SHIFT_NS tb_candidate_offer.system.t_m_arburst;
wire [3:0] actual_t_m_arid;
reg [3:0] expected_t_m_arid;
initial expected_t_m_arid <= #SHIFT_NS tb_candidate_offer.system.t_m_arid;
always @(tb_candidate_offer.system.t_m_arid) expected_t_m_arid <= #SHIFT_NS tb_candidate_offer.system.t_m_arid;
wire [7:0] actual_t_m_arlen;
reg [7:0] expected_t_m_arlen;
initial expected_t_m_arlen <= #SHIFT_NS tb_candidate_offer.system.t_m_arlen;
always @(tb_candidate_offer.system.t_m_arlen) expected_t_m_arlen <= #SHIFT_NS tb_candidate_offer.system.t_m_arlen;
reg drive_t_m_arready;
initial drive_t_m_arready <= #SHIFT_NS tb_candidate_offer.system.t_m_arready;
always @(tb_candidate_offer.system.t_m_arready) drive_t_m_arready <= #SHIFT_NS tb_candidate_offer.system.t_m_arready;
wire [2:0] actual_t_m_arsize;
reg [2:0] expected_t_m_arsize;
initial expected_t_m_arsize <= #SHIFT_NS tb_candidate_offer.system.t_m_arsize;
always @(tb_candidate_offer.system.t_m_arsize) expected_t_m_arsize <= #SHIFT_NS tb_candidate_offer.system.t_m_arsize;
wire actual_t_m_arvalid;
reg expected_t_m_arvalid;
initial expected_t_m_arvalid <= #SHIFT_NS tb_candidate_offer.system.t_m_arvalid;
always @(tb_candidate_offer.system.t_m_arvalid) expected_t_m_arvalid <= #SHIFT_NS tb_candidate_offer.system.t_m_arvalid;
reg [511:0] drive_t_m_rdata;
initial drive_t_m_rdata <= #SHIFT_NS tb_candidate_offer.system.t_m_rdata;
always @(tb_candidate_offer.system.t_m_rdata) drive_t_m_rdata <= #SHIFT_NS tb_candidate_offer.system.t_m_rdata;
reg [3:0] drive_t_m_rid;
initial drive_t_m_rid <= #SHIFT_NS tb_candidate_offer.system.t_m_rid;
always @(tb_candidate_offer.system.t_m_rid) drive_t_m_rid <= #SHIFT_NS tb_candidate_offer.system.t_m_rid;
reg drive_t_m_rlast;
initial drive_t_m_rlast <= #SHIFT_NS tb_candidate_offer.system.t_m_rlast;
always @(tb_candidate_offer.system.t_m_rlast) drive_t_m_rlast <= #SHIFT_NS tb_candidate_offer.system.t_m_rlast;
wire actual_t_m_rready;
reg expected_t_m_rready;
initial expected_t_m_rready <= #SHIFT_NS tb_candidate_offer.system.t_m_rready;
always @(tb_candidate_offer.system.t_m_rready) expected_t_m_rready <= #SHIFT_NS tb_candidate_offer.system.t_m_rready;
reg [1:0] drive_t_m_rresp;
initial drive_t_m_rresp <= #SHIFT_NS tb_candidate_offer.system.t_m_rresp;
always @(tb_candidate_offer.system.t_m_rresp) drive_t_m_rresp <= #SHIFT_NS tb_candidate_offer.system.t_m_rresp;
reg drive_t_m_rvalid;
initial drive_t_m_rvalid <= #SHIFT_NS tb_candidate_offer.system.t_m_rvalid;
always @(tb_candidate_offer.system.t_m_rvalid) drive_t_m_rvalid <= #SHIFT_NS tb_candidate_offer.system.t_m_rvalid;
reg drive_test_route_abort;
initial drive_test_route_abort <= #SHIFT_NS tb_candidate_offer.system.test_route_abort;
always @(tb_candidate_offer.system.test_route_abort) drive_test_route_abort <= #SHIFT_NS tb_candidate_offer.system.test_route_abort;
reg drive_test_route_version_flip;
initial drive_test_route_version_flip <= #SHIFT_NS tb_candidate_offer.system.test_route_version_flip;
always @(tb_candidate_offer.system.test_route_version_flip) drive_test_route_version_flip <= #SHIFT_NS tb_candidate_offer.system.test_route_version_flip;
wire actual_ss_start_ready;
reg expected_ss_start_ready;
initial expected_ss_start_ready <= #SHIFT_NS tb_candidate_offer.system.ss_start_ready;
always @(tb_candidate_offer.system.ss_start_ready) expected_ss_start_ready <= #SHIFT_NS tb_candidate_offer.system.ss_start_ready;
wire actual_ss_rsp_valid;
reg expected_ss_rsp_valid;
initial expected_ss_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.ss_rsp_valid;
always @(tb_candidate_offer.system.ss_rsp_valid) expected_ss_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.ss_rsp_valid;
wire [3:0] actual_ss_rsp_status;
reg [3:0] expected_ss_rsp_status;
initial expected_ss_rsp_status <= #SHIFT_NS tb_candidate_offer.system.ss_rsp_status;
always @(tb_candidate_offer.system.ss_rsp_status) expected_ss_rsp_status <= #SHIFT_NS tb_candidate_offer.system.ss_rsp_status;
wire [31:0] actual_ss_rsp_cookie;
reg [31:0] expected_ss_rsp_cookie;
initial expected_ss_rsp_cookie <= #SHIFT_NS tb_candidate_offer.system.ss_rsp_cookie;
always @(tb_candidate_offer.system.ss_rsp_cookie) expected_ss_rsp_cookie <= #SHIFT_NS tb_candidate_offer.system.ss_rsp_cookie;
wire [31:0] actual_ss_polls;
reg [31:0] expected_ss_polls;
initial expected_ss_polls <= #SHIFT_NS tb_candidate_offer.system.ss_polls;
always @(tb_candidate_offer.system.ss_polls) expected_ss_polls <= #SHIFT_NS tb_candidate_offer.system.ss_polls;
wire [31:0] actual_ss_expands;
reg [31:0] expected_ss_expands;
initial expected_ss_expands <= #SHIFT_NS tb_candidate_offer.system.ss_expands;
always @(tb_candidate_offer.system.ss_expands) expected_ss_expands <= #SHIFT_NS tb_candidate_offer.system.ss_expands;
wire [31:0] actual_ss_candidates;
reg [31:0] expected_ss_candidates;
initial expected_ss_candidates <= #SHIFT_NS tb_candidate_offer.system.ss_candidates;
always @(tb_candidate_offer.system.ss_candidates) expected_ss_candidates <= #SHIFT_NS tb_candidate_offer.system.ss_candidates;
wire [31:0] actual_ss_result_node;
reg [31:0] expected_ss_result_node;
initial expected_ss_result_node <= #SHIFT_NS tb_candidate_offer.system.ss_result_node;
always @(tb_candidate_offer.system.ss_result_node) expected_ss_result_node <= #SHIFT_NS tb_candidate_offer.system.ss_result_node;
wire [31:0] actual_ss_result_key;
reg [31:0] expected_ss_result_key;
initial expected_ss_result_key <= #SHIFT_NS tb_candidate_offer.system.ss_result_key;
always @(tb_candidate_offer.system.ss_result_key) expected_ss_result_key <= #SHIFT_NS tb_candidate_offer.system.ss_result_key;
wire actual_ss_busy;
reg expected_ss_busy;
initial expected_ss_busy <= #SHIFT_NS tb_candidate_offer.system.ss_busy;
always @(tb_candidate_offer.system.ss_busy) expected_ss_busy <= #SHIFT_NS tb_candidate_offer.system.ss_busy;
wire actual_ss_fault;
reg expected_ss_fault;
initial expected_ss_fault <= #SHIFT_NS tb_candidate_offer.system.ss_fault;
always @(tb_candidate_offer.system.ss_fault) expected_ss_fault <= #SHIFT_NS tb_candidate_offer.system.ss_fault;
wire [3:0] actual_ss_phase;
reg [3:0] expected_ss_phase;
initial expected_ss_phase <= #SHIFT_NS tb_candidate_offer.system.ss_phase;
always @(tb_candidate_offer.system.ss_phase) expected_ss_phase <= #SHIFT_NS tb_candidate_offer.system.ss_phase;
wire actual_ss_poll_event;
reg expected_ss_poll_event;
initial expected_ss_poll_event <= #SHIFT_NS tb_candidate_offer.system.ss_poll_event;
always @(tb_candidate_offer.system.ss_poll_event) expected_ss_poll_event <= #SHIFT_NS tb_candidate_offer.system.ss_poll_event;
wire [31:0] actual_ss_poll_node;
reg [31:0] expected_ss_poll_node;
initial expected_ss_poll_node <= #SHIFT_NS tb_candidate_offer.system.ss_poll_node;
always @(tb_candidate_offer.system.ss_poll_node) expected_ss_poll_node <= #SHIFT_NS tb_candidate_offer.system.ss_poll_node;
wire [31:0] actual_ss_poll_key;
reg [31:0] expected_ss_poll_key;
initial expected_ss_poll_key <= #SHIFT_NS tb_candidate_offer.system.ss_poll_key;
always @(tb_candidate_offer.system.ss_poll_key) expected_ss_poll_key <= #SHIFT_NS tb_candidate_offer.system.ss_poll_key;
wire [31:0] actual_ss_poll_size;
reg [31:0] expected_ss_poll_size;
initial expected_ss_poll_size <= #SHIFT_NS tb_candidate_offer.system.ss_poll_size;
always @(tb_candidate_offer.system.ss_poll_size) expected_ss_poll_size <= #SHIFT_NS tb_candidate_offer.system.ss_poll_size;
reg drive_qc_cmd_valid;
initial drive_qc_cmd_valid <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_valid;
always @(tb_candidate_offer.system.qc_cmd_valid) drive_qc_cmd_valid <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_valid;
wire actual_qc_cmd_ready;
reg expected_qc_cmd_ready;
initial expected_qc_cmd_ready <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_ready;
always @(tb_candidate_offer.system.qc_cmd_ready) expected_qc_cmd_ready <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_ready;
reg [1:0] drive_qc_cmd_slot;
initial drive_qc_cmd_slot <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_slot;
always @(tb_candidate_offer.system.qc_cmd_slot) drive_qc_cmd_slot <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_slot;
reg [31:0] drive_qc_cmd_cookie;
initial drive_qc_cmd_cookie <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_cookie;
always @(tb_candidate_offer.system.qc_cmd_cookie) drive_qc_cmd_cookie <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_cookie;
reg [31:0] drive_qc_cmd_route_cookie;
initial drive_qc_cmd_route_cookie <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_route_cookie;
always @(tb_candidate_offer.system.qc_cmd_route_cookie) drive_qc_cmd_route_cookie <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_route_cookie;
reg [31:0] drive_qc_cmd_source;
initial drive_qc_cmd_source <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_source;
always @(tb_candidate_offer.system.qc_cmd_source) drive_qc_cmd_source <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_source;
reg [31:0] drive_qc_cmd_key;
initial drive_qc_cmd_key <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_key;
always @(tb_candidate_offer.system.qc_cmd_key) drive_qc_cmd_key <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_key;
reg [31:0] drive_qc_cmd_nodes;
initial drive_qc_cmd_nodes <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_nodes;
always @(tb_candidate_offer.system.qc_cmd_nodes) drive_qc_cmd_nodes <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_nodes;
reg [31:0] drive_qc_cmd_max_polls;
initial drive_qc_cmd_max_polls <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_max_polls;
always @(tb_candidate_offer.system.qc_cmd_max_polls) drive_qc_cmd_max_polls <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_max_polls;
reg [31:0] drive_qc_cmd_poll_cookie;
initial drive_qc_cmd_poll_cookie <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_poll_cookie;
always @(tb_candidate_offer.system.qc_cmd_poll_cookie) drive_qc_cmd_poll_cookie <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_poll_cookie;
reg [63:0] drive_qc_cmd_design;
initial drive_qc_cmd_design <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_design;
always @(tb_candidate_offer.system.qc_cmd_design) drive_qc_cmd_design <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_design;
reg [1:0] drive_qc_cmd_query;
initial drive_qc_cmd_query <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_query;
always @(tb_candidate_offer.system.qc_cmd_query) drive_qc_cmd_query <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_query;
reg [3:0] drive_qc_cmd_price;
initial drive_qc_cmd_price <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_price;
always @(tb_candidate_offer.system.qc_cmd_price) drive_qc_cmd_price <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_price;
reg [447:0] drive_qc_cmd_expand;
initial drive_qc_cmd_expand <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_expand;
always @(tb_candidate_offer.system.qc_cmd_expand) drive_qc_cmd_expand <= #SHIFT_NS tb_candidate_offer.system.qc_cmd_expand;
wire actual_qc_rsp_valid;
reg expected_qc_rsp_valid;
initial expected_qc_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.qc_rsp_valid;
always @(tb_candidate_offer.system.qc_rsp_valid) expected_qc_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.qc_rsp_valid;
reg drive_qc_rsp_ready;
initial drive_qc_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.qc_rsp_ready;
always @(tb_candidate_offer.system.qc_rsp_ready) drive_qc_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.qc_rsp_ready;
wire [3:0] actual_qc_rsp_status;
reg [3:0] expected_qc_rsp_status;
initial expected_qc_rsp_status <= #SHIFT_NS tb_candidate_offer.system.qc_rsp_status;
always @(tb_candidate_offer.system.qc_rsp_status) expected_qc_rsp_status <= #SHIFT_NS tb_candidate_offer.system.qc_rsp_status;
wire [3:0] actual_qc_rsp_detail;
reg [3:0] expected_qc_rsp_detail;
initial expected_qc_rsp_detail <= #SHIFT_NS tb_candidate_offer.system.qc_rsp_detail;
always @(tb_candidate_offer.system.qc_rsp_detail) expected_qc_rsp_detail <= #SHIFT_NS tb_candidate_offer.system.qc_rsp_detail;
wire [31:0] actual_qc_rsp_cookie;
reg [31:0] expected_qc_rsp_cookie;
initial expected_qc_rsp_cookie <= #SHIFT_NS tb_candidate_offer.system.qc_rsp_cookie;
always @(tb_candidate_offer.system.qc_rsp_cookie) expected_qc_rsp_cookie <= #SHIFT_NS tb_candidate_offer.system.qc_rsp_cookie;
wire [31:0] actual_qc_rsp_nodes;
reg [31:0] expected_qc_rsp_nodes;
initial expected_qc_rsp_nodes <= #SHIFT_NS tb_candidate_offer.system.qc_rsp_nodes;
always @(tb_candidate_offer.system.qc_rsp_nodes) expected_qc_rsp_nodes <= #SHIFT_NS tb_candidate_offer.system.qc_rsp_nodes;
wire [31:0] actual_qc_rsp_acked;
reg [31:0] expected_qc_rsp_acked;
initial expected_qc_rsp_acked <= #SHIFT_NS tb_candidate_offer.system.qc_rsp_acked;
always @(tb_candidate_offer.system.qc_rsp_acked) expected_qc_rsp_acked <= #SHIFT_NS tb_candidate_offer.system.qc_rsp_acked;
wire actual_qc_rsp_committed;
reg expected_qc_rsp_committed;
initial expected_qc_rsp_committed <= #SHIFT_NS tb_candidate_offer.system.qc_rsp_committed;
always @(tb_candidate_offer.system.qc_rsp_committed) expected_qc_rsp_committed <= #SHIFT_NS tb_candidate_offer.system.qc_rsp_committed;
reg drive_qc_abort;
initial drive_qc_abort <= #SHIFT_NS tb_candidate_offer.system.qc_abort;
always @(tb_candidate_offer.system.qc_abort) drive_qc_abort <= #SHIFT_NS tb_candidate_offer.system.qc_abort;
wire actual_qc_busy;
reg expected_qc_busy;
initial expected_qc_busy <= #SHIFT_NS tb_candidate_offer.system.qc_busy;
always @(tb_candidate_offer.system.qc_busy) expected_qc_busy <= #SHIFT_NS tb_candidate_offer.system.qc_busy;
wire actual_qc_fault;
reg expected_qc_fault;
initial expected_qc_fault <= #SHIFT_NS tb_candidate_offer.system.qc_fault;
always @(tb_candidate_offer.system.qc_fault) expected_qc_fault <= #SHIFT_NS tb_candidate_offer.system.qc_fault;
wire [3:0] actual_qc_phase;
reg [3:0] expected_qc_phase;
initial expected_qc_phase <= #SHIFT_NS tb_candidate_offer.system.qc_phase;
always @(tb_candidate_offer.system.qc_phase) expected_qc_phase <= #SHIFT_NS tb_candidate_offer.system.qc_phase;
wire actual_qc_prepared_event;
reg expected_qc_prepared_event;
initial expected_qc_prepared_event <= #SHIFT_NS tb_candidate_offer.system.qc_prepared_event;
always @(tb_candidate_offer.system.qc_prepared_event) expected_qc_prepared_event <= #SHIFT_NS tb_candidate_offer.system.qc_prepared_event;
wire [31:0] actual_qc_prepare_acked;
reg [31:0] expected_qc_prepare_acked;
initial expected_qc_prepare_acked <= #SHIFT_NS tb_candidate_offer.system.qc_prepare_acked;
always @(tb_candidate_offer.system.qc_prepare_acked) expected_qc_prepare_acked <= #SHIFT_NS tb_candidate_offer.system.qc_prepare_acked;
wire [31:0] actual_qc_cleanup_acked;
reg [31:0] expected_qc_cleanup_acked;
initial expected_qc_cleanup_acked <= #SHIFT_NS tb_candidate_offer.system.qc_cleanup_acked;
always @(tb_candidate_offer.system.qc_cleanup_acked) expected_qc_cleanup_acked <= #SHIFT_NS tb_candidate_offer.system.qc_cleanup_acked;
reg drive_scan_valid;
initial drive_scan_valid <= #SHIFT_NS tb_candidate_offer.system.scan_valid;
always @(tb_candidate_offer.system.scan_valid) drive_scan_valid <= #SHIFT_NS tb_candidate_offer.system.scan_valid;
wire actual_scan_ready;
reg expected_scan_ready;
initial expected_scan_ready <= #SHIFT_NS tb_candidate_offer.system.scan_ready;
always @(tb_candidate_offer.system.scan_ready) expected_scan_ready <= #SHIFT_NS tb_candidate_offer.system.scan_ready;
reg drive_scan_permit;
initial drive_scan_permit <= #SHIFT_NS tb_candidate_offer.system.scan_permit;
always @(tb_candidate_offer.system.scan_permit) drive_scan_permit <= #SHIFT_NS tb_candidate_offer.system.scan_permit;
reg [13:0] drive_scan_frame;
initial drive_scan_frame <= #SHIFT_NS tb_candidate_offer.system.scan_frame;
always @(tb_candidate_offer.system.scan_frame) drive_scan_frame <= #SHIFT_NS tb_candidate_offer.system.scan_frame;
wire actual_scan_rsp_valid;
reg expected_scan_rsp_valid;
initial expected_scan_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.scan_rsp_valid;
always @(tb_candidate_offer.system.scan_rsp_valid) expected_scan_rsp_valid <= #SHIFT_NS tb_candidate_offer.system.scan_rsp_valid;
reg drive_scan_rsp_ready;
initial drive_scan_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.scan_rsp_ready;
always @(tb_candidate_offer.system.scan_rsp_ready) drive_scan_rsp_ready <= #SHIFT_NS tb_candidate_offer.system.scan_rsp_ready;
wire [2:0] actual_scan_status;
reg [2:0] expected_scan_status;
initial expected_scan_status <= #SHIFT_NS tb_candidate_offer.system.scan_status;
always @(tb_candidate_offer.system.scan_status) expected_scan_status <= #SHIFT_NS tb_candidate_offer.system.scan_status;
wire [13:0] actual_scan_result_frame;
reg [13:0] expected_scan_result_frame;
initial expected_scan_result_frame <= #SHIFT_NS tb_candidate_offer.system.scan_result_frame;
always @(tb_candidate_offer.system.scan_result_frame) expected_scan_result_frame <= #SHIFT_NS tb_candidate_offer.system.scan_result_frame;
wire [26:0] actual_scan_owner;
reg [26:0] expected_scan_owner;
initial expected_scan_owner <= #SHIFT_NS tb_candidate_offer.system.scan_owner;
always @(tb_candidate_offer.system.scan_owner) expected_scan_owner <= #SHIFT_NS tb_candidate_offer.system.scan_owner;
wire actual_scan_published;
reg expected_scan_published;
initial expected_scan_published <= #SHIFT_NS tb_candidate_offer.system.scan_published;
always @(tb_candidate_offer.system.scan_published) expected_scan_published <= #SHIFT_NS tb_candidate_offer.system.scan_published;
reg [31:0] drive_snapshot_label_crc;
initial drive_snapshot_label_crc <= #SHIFT_NS tb_candidate_offer.system.snapshot_label_crc;
always @(tb_candidate_offer.system.snapshot_label_crc) drive_snapshot_label_crc <= #SHIFT_NS tb_candidate_offer.system.snapshot_label_crc;
wire [31:0] actual_lr_source_crc;
reg [31:0] expected_lr_source_crc;
initial expected_lr_source_crc <= #SHIFT_NS tb_candidate_offer.system.lr_source_crc;
always @(tb_candidate_offer.system.lr_source_crc) expected_lr_source_crc <= #SHIFT_NS tb_candidate_offer.system.lr_source_crc;
`SHADOW_NETLIST_TOP shadow_dut (
 .baseline_retired(drive_baseline_retired),
 .restore_seed_enable(drive_restore_seed_enable),
 .baseline_permit(drive_baseline_permit),
 .baseline_epoch(drive_baseline_epoch),
 .baseline_req_valid(actual_baseline_req_valid),
 .baseline_req_ready(drive_baseline_req_ready),
 .baseline_req_node(actual_baseline_req_node),
 .baseline_req_epoch(actual_baseline_req_epoch),
 .baseline_rsp_valid(drive_baseline_rsp_valid),
 .baseline_rsp_ready(actual_baseline_rsp_ready),
 .baseline_rsp_status(drive_baseline_rsp_status),
 .baseline_rsp_node(drive_baseline_rsp_node),
 .baseline_rsp_epoch(drive_baseline_rsp_epoch),
 .baseline_rsp_payload(drive_baseline_rsp_payload),
 .wm_enable(drive_wm_enable),
 .wm_source_version(drive_wm_source_version),
 .wm_source_query(drive_wm_source_query),
 .wm_source_price(drive_wm_source_price),
 .wm_path_crc(drive_wm_path_crc),
 .wm_query_crc(drive_wm_query_crc),
 .wm_owned(actual_wm_owned),
 .wm_fault(actual_wm_fault),
 .wm_joined(actual_wm_joined),
 .wm_receipts(actual_wm_receipts),
 .ap_valid(drive_ap_valid),
 .ap_rsp_ready(drive_ap_rsp_ready),
 .ap_ready(actual_ap_ready),
 .ap_rsp_valid(actual_ap_rsp_valid),
 .ap_design(drive_ap_design),
 .ap_generation(drive_ap_generation),
 .ap_checkpoint(drive_ap_checkpoint),
 .ap_node(drive_ap_node),
 .ap_net(drive_ap_net),
 .ap_cookie(drive_ap_cookie),
 .ap_rsp_design(actual_ap_rsp_design),
 .ap_rsp_generation(actual_ap_rsp_generation),
 .ap_rsp_checkpoint(actual_ap_rsp_checkpoint),
 .ap_rsp_cookie(actual_ap_rsp_cookie),
 .ap_refs(actual_ap_refs),
 .ap_occ(actual_ap_occ),
 .ap_status(actual_ap_status),
 .jp_start(drive_jp_start),
 .jp_start_ready(actual_jp_start_ready),
 .jp_commit(drive_jp_commit),
 .jp_commit_ready(actual_jp_commit_ready),
 .jp_cancel(drive_jp_cancel),
 .jp_cancel_ready(actual_jp_cancel_ready),
 .jp_owned(actual_jp_owned),
 .jp_done(actual_jp_done),
 .jp_done_ready(drive_jp_done_ready),
 .jp_result(actual_jp_result),
 .jp_manifest_ready(drive_jp_manifest_ready),
 .jp_generation(drive_jp_generation),
 .jp_design(drive_jp_design),
 .jp_checkpoint(drive_jp_checkpoint),
 .jp_version(drive_jp_version),
 .jp_query(drive_jp_query),
 .jp_price(drive_jp_price),
 .jp_load(drive_jp_load),
 .jp_ack(drive_jp_ack),
 .jp_ready(actual_jp_ready),
 .jp_reply(actual_jp_reply),
 .jp_status(actual_jp_status),
 .jp_authority_stage(drive_jp_authority_stage),
 .boot_required(drive_boot_required),
 .boot_cfg_valid(drive_boot_cfg_valid),
 .boot_cfg_ready(actual_boot_cfg_ready),
 .boot_design(drive_boot_design),
 .boot_generation(drive_boot_generation),
 .boot_checkpoint(drive_boot_checkpoint),
 .boot_version(drive_boot_version),
 .boot_nodes(drive_boot_nodes),
 .boot_label_count(drive_boot_label_count),
 .boot_label_crc(drive_boot_label_crc),
 .boot_path_crc(drive_boot_path_crc),
 .boot_query_crc(drive_boot_query_crc),
 .boot_query(drive_boot_query),
 .boot_slots(drive_boot_slots),
 .boot_price(drive_boot_price),
 .boot_payload(drive_boot_payload),
 .boot_pending(actual_boot_pending),
 .boot_rsp_valid(actual_boot_rsp_valid),
 .boot_rsp_ready(drive_boot_rsp_ready),
 .boot_status(actual_boot_status),
 .boot_verify_valid(drive_boot_verify_valid),
 .boot_verify_ready(actual_boot_verify_ready),
 .boot_verified_count(actual_boot_verified_count),
 .boot_verify_status(actual_boot_verify_status),
 .boot_receipts(actual_boot_receipts),
 .boot_config_receipts(actual_boot_config_receipts),
 .qc_cp_generation(drive_qc_cp_generation),
 .qc_cp_valid(drive_qc_cp_valid),
 .qc_cp_restore(drive_qc_cp_restore),
 .qc_cp_rsp_ready(drive_qc_cp_rsp_ready),
 .qc_cp_s_valid(drive_qc_cp_s_valid),
 .qc_cp_s_last(drive_qc_cp_s_last),
 .qc_cp_m_ready(drive_qc_cp_m_ready),
 .qc_cp_test_reset(drive_qc_cp_test_reset),
 .qc_cp_ready(actual_qc_cp_ready),
 .qc_cp_busy(actual_qc_cp_busy),
 .qc_cp_rsp_valid(actual_qc_cp_rsp_valid),
 .qc_cp_s_ready(actual_qc_cp_s_ready),
 .qc_cp_m_valid(actual_qc_cp_m_valid),
 .qc_cp_m_last(actual_qc_cp_m_last),
 .qc_restore_pending(actual_qc_restore_pending),
 .qc_cp_expected_crc(drive_qc_cp_expected_crc),
 .qc_cp_s_index(drive_qc_cp_s_index),
 .qc_cp_s_data(drive_qc_cp_s_data),
 .qc_cp_crc(actual_qc_cp_crc),
 .qc_cp_m_index(actual_qc_cp_m_index),
 .qc_cp_m_data(actual_qc_cp_m_data),
 .qc_cp_status(actual_qc_cp_status),
 .as_cfg_valid(drive_as_cfg_valid),
 .as_cfg_ready(actual_as_cfg_ready),
 .as_cfg_design(drive_as_cfg_design),
 .as_cfg_generation(drive_as_cfg_generation),
 .as_cfg_primary(drive_as_cfg_primary),
 .as_cfg_pool(drive_as_cfg_pool),
 .as_cfg_allocator(drive_as_cfg_allocator),
 .as_cfg_checkpoint(drive_as_cfg_checkpoint),
 .as_cfg_nodes(drive_as_cfg_nodes),
 .as_cfg_nets(drive_as_cfg_nets),
 .as_cfg_capacity(drive_as_cfg_capacity),
 .as_configured(actual_as_configured),
 .as_bound_design(actual_as_bound_design),
 .as_bound_generation(actual_as_bound_generation),
 .as_bound_checkpoint(actual_as_bound_checkpoint),
 .as_m_araddr(actual_as_m_araddr),
 .as_m_arlen(actual_as_m_arlen),
 .as_m_arsize(actual_as_m_arsize),
 .as_m_arburst(actual_as_m_arburst),
 .as_m_arid(actual_as_m_arid),
 .as_m_arvalid(actual_as_m_arvalid),
 .as_m_arready(drive_as_m_arready),
 .as_m_rdata(drive_as_m_rdata),
 .as_m_rid(drive_as_m_rid),
 .as_m_rresp(drive_as_m_rresp),
 .as_m_rlast(drive_as_m_rlast),
 .as_m_rvalid(drive_as_m_rvalid),
 .as_m_rready(actual_as_m_rready),
 .as_m_awaddr(actual_as_m_awaddr),
 .as_m_awlen(actual_as_m_awlen),
 .as_m_awsize(actual_as_m_awsize),
 .as_m_awburst(actual_as_m_awburst),
 .as_m_awid(actual_as_m_awid),
 .as_m_awvalid(actual_as_m_awvalid),
 .as_m_awready(drive_as_m_awready),
 .as_m_wdata(actual_as_m_wdata),
 .as_m_wstrb(actual_as_m_wstrb),
 .as_m_wlast(actual_as_m_wlast),
 .as_m_wvalid(actual_as_m_wvalid),
 .as_m_wready(drive_as_m_wready),
 .as_m_bid(drive_as_m_bid),
 .as_m_bresp(drive_as_m_bresp),
 .as_m_bvalid(drive_as_m_bvalid),
 .as_m_bready(actual_as_m_bready),
 .as_cfg_rsp_valid(actual_as_cfg_rsp_valid),
 .as_cfg_rsp_ready(drive_as_cfg_rsp_ready),
 .as_cfg_status(actual_as_cfg_status),
 .as_busy(actual_as_busy),
 .as_fault(actual_as_fault),
 .as_drained(actual_as_drained),
 .as_retired(actual_as_retired),
 .as_rsp_generation(actual_as_rsp_generation),
 .cp_valid(drive_cp_valid),
 .cp_restore(drive_cp_restore),
 .cp_ready(actual_cp_ready),
 .cp_busy(actual_cp_busy),
 .cp_rsp_valid(actual_cp_rsp_valid),
 .cp_rsp_ready(drive_cp_rsp_ready),
 .cp_status(actual_cp_status),
 .cp_crc(actual_cp_crc),
 .cp_design(drive_cp_design),
 .cp_nodes(drive_cp_nodes),
 .cp_nets(drive_cp_nets),
 .cp_expected_crc(drive_cp_expected_crc),
 .cp_s_valid(drive_cp_s_valid),
 .cp_s_ready(actual_cp_s_ready),
 .cp_s_index(drive_cp_s_index),
 .cp_s_data(drive_cp_s_data),
 .cp_s_last(drive_cp_s_last),
 .cp_m_valid(actual_cp_m_valid),
 .cp_m_ready(drive_cp_m_ready),
 .cp_m_index(actual_cp_m_index),
 .cp_m_data(actual_cp_m_data),
 .cp_m_last(actual_cp_m_last),
 .cp_test_reset(drive_cp_test_reset),
 .pc_route_retired(actual_pc_route_retired),
 .pc_acquire_valid(drive_pc_acquire_valid),
 .pc_acquire_ready(actual_pc_acquire_ready),
 .pc_owned(actual_pc_owned),
 .pc_release_valid(drive_pc_release_valid),
 .pc_release_ready(actual_pc_release_ready),
 .abort(drive_abort),
 .busy(actual_busy),
 .cc_busy(actual_cc_busy),
 .cc_fault(actual_cc_fault),
 .cf_fault(actual_cf_fault),
 .clk(drive_clk),
 .cost_lease(actual_cost_lease),
 .cs_busy(actual_cs_busy),
 .cs_configured(actual_cs_configured),
 .cs_design_id(actual_cs_design_id),
 .cs_editing(actual_cs_editing),
 .cs_fault(actual_cs_fault),
 .cs_m_araddr(actual_cs_m_araddr),
 .cs_m_arburst(actual_cs_m_arburst),
 .cs_m_arid(actual_cs_m_arid),
 .cs_m_arlen(actual_cs_m_arlen),
 .cs_m_arready(drive_cs_m_arready),
 .cs_m_arsize(actual_cs_m_arsize),
 .cs_m_arvalid(actual_cs_m_arvalid),
 .cs_m_awaddr(actual_cs_m_awaddr),
 .cs_m_awburst(actual_cs_m_awburst),
 .cs_m_awid(actual_cs_m_awid),
 .cs_m_awlen(actual_cs_m_awlen),
 .cs_m_awready(drive_cs_m_awready),
 .cs_m_awsize(actual_cs_m_awsize),
 .cs_m_awvalid(actual_cs_m_awvalid),
 .cs_m_bid(drive_cs_m_bid),
 .cs_m_bready(actual_cs_m_bready),
 .cs_m_bresp(drive_cs_m_bresp),
 .cs_m_bvalid(drive_cs_m_bvalid),
 .cs_m_rdata(drive_cs_m_rdata),
 .cs_m_rid(drive_cs_m_rid),
 .cs_m_rlast(drive_cs_m_rlast),
 .cs_m_rready(actual_cs_m_rready),
 .cs_m_rresp(drive_cs_m_rresp),
 .cs_m_rvalid(drive_cs_m_rvalid),
 .cs_m_wdata(actual_cs_m_wdata),
 .cs_m_wlast(actual_cs_m_wlast),
 .cs_m_wready(drive_cs_m_wready),
 .cs_m_wstrb(actual_cs_m_wstrb),
 .cs_m_wvalid(actual_cs_m_wvalid),
 .cs_published_version(actual_cs_published_version),
 .cs_ready_for_query(actual_cs_ready_for_query),
 .d_configured(actual_d_configured),
 .d_m_araddr(actual_d_m_araddr),
 .d_m_arburst(actual_d_m_arburst),
 .d_m_arid(actual_d_m_arid),
 .d_m_arlen(actual_d_m_arlen),
 .d_m_arready(drive_d_m_arready),
 .d_m_arsize(actual_d_m_arsize),
 .d_m_arvalid(actual_d_m_arvalid),
 .d_m_awaddr(actual_d_m_awaddr),
 .d_m_awburst(actual_d_m_awburst),
 .d_m_awid(actual_d_m_awid),
 .d_m_awlen(actual_d_m_awlen),
 .d_m_awready(drive_d_m_awready),
 .d_m_awsize(actual_d_m_awsize),
 .d_m_awvalid(actual_d_m_awvalid),
 .d_m_bid(drive_d_m_bid),
 .d_m_bready(actual_d_m_bready),
 .d_m_bresp(drive_d_m_bresp),
 .d_m_bvalid(drive_d_m_bvalid),
 .d_m_rdata(drive_d_m_rdata),
 .d_m_rid(drive_d_m_rid),
 .d_m_rlast(drive_d_m_rlast),
 .d_m_rready(actual_d_m_rready),
 .d_m_rresp(drive_d_m_rresp),
 .d_m_rvalid(drive_d_m_rvalid),
 .d_m_wdata(actual_d_m_wdata),
 .d_m_wlast(actual_d_m_wlast),
 .d_m_wready(drive_d_m_wready),
 .d_m_wstrb(actual_d_m_wstrb),
 .d_m_wvalid(actual_d_m_wvalid),
 .design_id(drive_design_id),
 .f_all_drained(actual_f_all_drained),
 .f_backend_idle(actual_f_backend_idle),
 .f_fault(actual_f_fault),
 .f_normal_retired(actual_f_normal_retired),
 .f_phase(actual_f_phase),
 .f_recovery_owned(actual_f_recovery_owned),
 .f_route_payload(drive_f_route_payload),
 .f_sp(drive_f_sp),
 .f_sr(actual_f_sr),
 .f_srp(actual_f_srp),
 .f_srr(drive_f_srr),
 .f_srv(actual_f_srv),
 .f_sv(drive_f_sv),
 .fault(actual_fault),
 .g_configured(actual_g_configured),
 .g_m_araddr(actual_g_m_araddr),
 .g_m_arburst(actual_g_m_arburst),
 .g_m_arid(actual_g_m_arid),
 .g_m_arlen(actual_g_m_arlen),
 .g_m_arready(drive_g_m_arready),
 .g_m_arsize(actual_g_m_arsize),
 .g_m_arvalid(actual_g_m_arvalid),
 .g_m_rdata(drive_g_m_rdata),
 .g_m_rid(drive_g_m_rid),
 .g_m_rlast(drive_g_m_rlast),
 .g_m_rready(actual_g_m_rready),
 .g_m_rresp(drive_g_m_rresp),
 .g_m_rvalid(drive_g_m_rvalid),
 .k_a_checkpoint(actual_k_a_checkpoint),
 .k_a_cookie(actual_k_a_cookie),
 .k_a_design(actual_k_a_design),
 .k_a_net(actual_k_a_net),
 .k_a_node(actual_k_a_node),
 .k_a_occ(actual_k_a_occ),
 .k_a_ready(actual_k_a_ready),
 .k_a_refs(actual_k_a_refs),
 .k_a_rsp_checkpoint(actual_k_a_rsp_checkpoint),
 .k_a_rsp_cookie(actual_k_a_rsp_cookie),
 .k_a_rsp_design(actual_k_a_rsp_design),
 .k_a_rsp_ready(actual_k_a_rsp_ready),
 .k_a_rsp_valid(actual_k_a_rsp_valid),
 .k_a_status(actual_k_a_status),
 .k_a_valid(actual_k_a_valid),
 .k_busy(actual_k_busy),
 .k_cold_rst(drive_k_cold_rst),
 .k_corrected(actual_k_corrected),
 .k_count(actual_k_count),
 .k_fault(actual_k_fault),
 .k_full(actual_k_full),
 .k_permit(actual_k_permit),
 .k_rec_ready(actual_k_rec_ready),
 .k_rec_valid(drive_k_rec_valid),
 .k_rsp_cookie(actual_k_rsp_cookie),
 .k_rsp_ready(drive_k_rsp_ready),
 .k_rsp_status(actual_k_rsp_status),
 .k_rsp_valid(actual_k_rsp_valid),
 .k_saved_checkpoint(actual_k_saved_checkpoint),
 .k_saved_design(actual_k_saved_design),
 .k_target_reset(actual_k_target_reset),
 .lr_fault(actual_lr_fault),
 .lr_rsp_status(actual_lr_rsp_status),
 .lr_s_cookie(drive_lr_s_cookie),
 .lr_s_last(drive_lr_s_last),
 .lr_s_node(drive_lr_s_node),
 .lr_s_payload(drive_lr_s_payload),
 .lr_s_ready(actual_lr_s_ready),
 .lr_s_valid(drive_lr_s_valid),
 .lr_verified(actual_lr_verified),
 .lr_written(actual_lr_written),
 .operation_pending(actual_operation_pending),
 .out_action(actual_out_action),
 .out_attrs(actual_out_attrs),
 .out_bits(actual_out_bits),
 .out_commit_acked(actual_out_commit_acked),
 .out_commit_payload(actual_out_commit_payload),
 .out_commit_status(actual_out_commit_status),
 .out_commit_valid(actual_out_commit_valid),
 .out_config(actual_out_config),
 .out_connection(actual_out_connection),
 .out_cookie(actual_out_cookie),
 .out_cost_geometry(actual_out_cost_geometry),
 .out_cost_geometry_result(actual_out_cost_geometry_result),
 .out_cost_packet(actual_out_cost_packet),
 .out_cost_status(actual_out_cost_status),
 .out_cost_valid(actual_out_cost_valid),
 .out_cost_words(actual_out_cost_words),
 .out_node(actual_out_node),
 .out_offer_before(actual_out_offer_before),
 .out_offer_key(actual_out_offer_key),
 .out_offer_node(actual_out_offer_node),
 .out_offer_size(actual_out_offer_size),
 .out_offer_status(actual_out_offer_status),
 .out_offer_valid(actual_out_offer_valid),
 .out_params(actual_out_params),
 .out_params_valid(actual_out_params_valid),
 .out_position(actual_out_position),
 .out_post_attrs(actual_out_post_attrs),
 .out_post_distance(actual_out_post_distance),
 .out_post_prev_read(actual_out_post_prev_read),
 .out_post_status(actual_out_post_status),
 .out_post_upstream(actual_out_post_upstream),
 .out_post_valid(actual_out_post_valid),
 .out_post_x(actual_out_post_x),
 .out_post_y(actual_out_post_y),
 .out_prep_count(actual_out_prep_count),
 .out_prep_history(actual_out_prep_history),
 .out_prep_net_data(actual_out_prep_net_data),
 .out_prep_occupancy(actual_out_prep_occupancy),
 .out_prep_price_index(actual_out_prep_price_index),
 .out_prep_price_value(actual_out_prep_price_value),
 .out_prep_status(actual_out_prep_status),
 .out_prep_valid(actual_out_prep_valid),
 .out_profile_revision(actual_out_profile_revision),
 .out_ready(drive_out_ready),
 .out_sequence(actual_out_sequence),
 .out_services(actual_out_services),
 .out_steps(actual_out_steps),
 .out_valid(actual_out_valid),
 .owner_configured(actual_owner_configured),
 .owner_m_araddr(actual_owner_m_araddr),
 .owner_m_arburst(actual_owner_m_arburst),
 .owner_m_arid(actual_owner_m_arid),
 .owner_m_arlen(actual_owner_m_arlen),
 .owner_m_arready(drive_owner_m_arready),
 .owner_m_arsize(actual_owner_m_arsize),
 .owner_m_arvalid(actual_owner_m_arvalid),
 .owner_m_awaddr(actual_owner_m_awaddr),
 .owner_m_awburst(actual_owner_m_awburst),
 .owner_m_awid(actual_owner_m_awid),
 .owner_m_awlen(actual_owner_m_awlen),
 .owner_m_awready(drive_owner_m_awready),
 .owner_m_awsize(actual_owner_m_awsize),
 .owner_m_awvalid(actual_owner_m_awvalid),
 .owner_m_bid(drive_owner_m_bid),
 .owner_m_bready(actual_owner_m_bready),
 .owner_m_bresp(drive_owner_m_bresp),
 .owner_m_bvalid(drive_owner_m_bvalid),
 .owner_m_rdata(drive_owner_m_rdata),
 .owner_m_rid(drive_owner_m_rid),
 .owner_m_rlast(drive_owner_m_rlast),
 .owner_m_rready(actual_owner_m_rready),
 .owner_m_rresp(drive_owner_m_rresp),
 .owner_m_rvalid(drive_owner_m_rvalid),
 .owner_m_wdata(actual_owner_m_wdata),
 .owner_m_wlast(actual_owner_m_wlast),
 .owner_m_wready(drive_owner_m_wready),
 .owner_m_wstrb(actual_owner_m_wstrb),
 .owner_m_wvalid(actual_owner_m_wvalid),
 .p_active(actual_p_active),
 .p_active_price(actual_p_active_price),
 .p_active_query(actual_p_active_query),
 .p_m_araddr(actual_p_m_araddr),
 .p_m_arburst(actual_p_m_arburst),
 .p_m_arid(actual_p_m_arid),
 .p_m_arlen(actual_p_m_arlen),
 .p_m_arready(drive_p_m_arready),
 .p_m_arsize(actual_p_m_arsize),
 .p_m_arvalid(actual_p_m_arvalid),
 .p_m_awaddr(actual_p_m_awaddr),
 .p_m_awburst(actual_p_m_awburst),
 .p_m_awid(actual_p_m_awid),
 .p_m_awlen(actual_p_m_awlen),
 .p_m_awready(drive_p_m_awready),
 .p_m_awsize(actual_p_m_awsize),
 .p_m_awvalid(actual_p_m_awvalid),
 .p_m_bid(drive_p_m_bid),
 .p_m_bready(actual_p_m_bready),
 .p_m_bresp(drive_p_m_bresp),
 .p_m_bvalid(drive_p_m_bvalid),
 .p_m_rdata(drive_p_m_rdata),
 .p_m_rid(drive_p_m_rid),
 .p_m_rlast(drive_p_m_rlast),
 .p_m_rready(actual_p_m_rready),
 .p_m_rresp(drive_p_m_rresp),
 .p_m_rvalid(drive_p_m_rvalid),
 .p_m_wdata(actual_p_m_wdata),
 .p_m_wlast(actual_p_m_wlast),
 .p_m_wready(drive_p_m_wready),
 .p_m_wstrb(actual_p_m_wstrb),
 .p_m_wvalid(actual_p_m_wvalid),
 .q_busy(actual_q_busy),
 .q_configured(actual_q_configured),
 .q_fault(actual_q_fault),
 .q_m_araddr(actual_q_m_araddr),
 .q_m_arburst(actual_q_m_arburst),
 .q_m_arid(actual_q_m_arid),
 .q_m_arlen(actual_q_m_arlen),
 .q_m_arready(drive_q_m_arready),
 .q_m_arsize(actual_q_m_arsize),
 .q_m_arvalid(actual_q_m_arvalid),
 .q_m_rdata(drive_q_m_rdata),
 .q_m_rid(drive_q_m_rid),
 .q_m_rlast(drive_q_m_rlast),
 .q_m_rready(actual_q_m_rready),
 .q_m_rresp(drive_q_m_rresp),
 .q_m_rvalid(drive_q_m_rvalid),
 .query_ready(actual_query_ready),
 .query_version(actual_query_version),
 .rc_block(actual_rc_block),
 .rc_busy(actual_rc_busy),
 .rc_fault(actual_rc_fault),
 .rc_req_ready(actual_rc_req_ready),
 .rc_req_valid(drive_rc_req_valid),
 .rc_rsp_acked(actual_rc_rsp_acked),
 .rc_rsp_cookie(actual_rc_rsp_cookie),
 .rc_rsp_nodes(actual_rc_rsp_nodes),
 .rc_rsp_ready(drive_rc_rsp_ready),
 .rc_rsp_status(actual_rc_rsp_status),
 .rc_rsp_valid(actual_rc_rsp_valid),
 .rc_slots(actual_rc_slots),
 .recover_checkpoint(drive_recover_checkpoint),
 .recover_cookie(drive_recover_cookie),
 .recover_design(drive_recover_design),
 .recover_price(drive_recover_price),
 .recover_query(drive_recover_query),
 .recover_version(drive_recover_version),
 .rst(actual_rst),
 .snapshot_checkpoint(drive_snapshot_checkpoint),
 .snapshot_cookie(drive_snapshot_cookie),
 .snapshot_count(drive_snapshot_count),
 .snapshot_design(drive_snapshot_design),
 .snapshot_nodes(drive_snapshot_nodes),
 .snapshot_probe(drive_snapshot_probe),
 .t_configured(actual_t_configured),
 .t_m_araddr(actual_t_m_araddr),
 .t_m_arburst(actual_t_m_arburst),
 .t_m_arid(actual_t_m_arid),
 .t_m_arlen(actual_t_m_arlen),
 .t_m_arready(drive_t_m_arready),
 .t_m_arsize(actual_t_m_arsize),
 .t_m_arvalid(actual_t_m_arvalid),
 .t_m_rdata(drive_t_m_rdata),
 .t_m_rid(drive_t_m_rid),
 .t_m_rlast(drive_t_m_rlast),
 .t_m_rready(actual_t_m_rready),
 .t_m_rresp(drive_t_m_rresp),
 .t_m_rvalid(drive_t_m_rvalid),
 .test_route_abort(drive_test_route_abort),
 .test_route_version_flip(drive_test_route_version_flip),
 .ss_start_ready(actual_ss_start_ready),
 .ss_rsp_valid(actual_ss_rsp_valid),
 .ss_rsp_status(actual_ss_rsp_status),
 .ss_rsp_cookie(actual_ss_rsp_cookie),
 .ss_polls(actual_ss_polls),
 .ss_expands(actual_ss_expands),
 .ss_candidates(actual_ss_candidates),
 .ss_result_node(actual_ss_result_node),
 .ss_result_key(actual_ss_result_key),
 .ss_busy(actual_ss_busy),
 .ss_fault(actual_ss_fault),
 .ss_phase(actual_ss_phase),
 .ss_poll_event(actual_ss_poll_event),
 .ss_poll_node(actual_ss_poll_node),
 .ss_poll_key(actual_ss_poll_key),
 .ss_poll_size(actual_ss_poll_size),
 .qc_cmd_valid(drive_qc_cmd_valid),
 .qc_cmd_ready(actual_qc_cmd_ready),
 .qc_cmd_slot(drive_qc_cmd_slot),
 .qc_cmd_cookie(drive_qc_cmd_cookie),
 .qc_cmd_route_cookie(drive_qc_cmd_route_cookie),
 .qc_cmd_source(drive_qc_cmd_source),
 .qc_cmd_key(drive_qc_cmd_key),
 .qc_cmd_nodes(drive_qc_cmd_nodes),
 .qc_cmd_max_polls(drive_qc_cmd_max_polls),
 .qc_cmd_poll_cookie(drive_qc_cmd_poll_cookie),
 .qc_cmd_design(drive_qc_cmd_design),
 .qc_cmd_query(drive_qc_cmd_query),
 .qc_cmd_price(drive_qc_cmd_price),
 .qc_cmd_expand(drive_qc_cmd_expand),
 .qc_rsp_valid(actual_qc_rsp_valid),
 .qc_rsp_ready(drive_qc_rsp_ready),
 .qc_rsp_status(actual_qc_rsp_status),
 .qc_rsp_detail(actual_qc_rsp_detail),
 .qc_rsp_cookie(actual_qc_rsp_cookie),
 .qc_rsp_nodes(actual_qc_rsp_nodes),
 .qc_rsp_acked(actual_qc_rsp_acked),
 .qc_rsp_committed(actual_qc_rsp_committed),
 .qc_abort(drive_qc_abort),
 .qc_busy(actual_qc_busy),
 .qc_fault(actual_qc_fault),
 .qc_phase(actual_qc_phase),
 .qc_prepared_event(actual_qc_prepared_event),
 .qc_prepare_acked(actual_qc_prepare_acked),
 .qc_cleanup_acked(actual_qc_cleanup_acked),
 .scan_valid(drive_scan_valid),
 .scan_ready(actual_scan_ready),
 .scan_permit(drive_scan_permit),
 .scan_frame(drive_scan_frame),
 .scan_rsp_valid(actual_scan_rsp_valid),
 .scan_rsp_ready(drive_scan_rsp_ready),
 .scan_status(actual_scan_status),
 .scan_result_frame(actual_scan_result_frame),
 .scan_owner(actual_scan_owner),
 .scan_published(actual_scan_published),
 .snapshot_label_crc(drive_snapshot_label_crc),
 .lr_source_crc(actual_lr_source_crc)
);
always @(posedge drive_clk) begin
 if(drive_k_cold_rst===1'b1)reset_edges=reset_edges+1;
 else if(drive_k_cold_rst===1'b0&&reset_edges>=5)armed=1;
end
always @(posedge drive_clk or negedge drive_clk) begin
 #1;
 if(armed)begin
  checks=checks+1;last_checked=$time;
  if(actual_baseline_req_valid!==expected_baseline_req_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=baseline_req_valid time=%0t actual=%h expected=%h",$time,actual_baseline_req_valid,expected_baseline_req_valid);
  if(actual_baseline_req_node!==expected_baseline_req_node)
   $fatal(1,"FULL_SHADOW_MISMATCH port=baseline_req_node time=%0t actual=%h expected=%h",$time,actual_baseline_req_node,expected_baseline_req_node);
  if(actual_baseline_req_epoch!==expected_baseline_req_epoch)
   $fatal(1,"FULL_SHADOW_MISMATCH port=baseline_req_epoch time=%0t actual=%h expected=%h",$time,actual_baseline_req_epoch,expected_baseline_req_epoch);
  if(actual_baseline_rsp_ready!==expected_baseline_rsp_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=baseline_rsp_ready time=%0t actual=%h expected=%h",$time,actual_baseline_rsp_ready,expected_baseline_rsp_ready);
  if(actual_wm_owned!==expected_wm_owned)
   $fatal(1,"FULL_SHADOW_MISMATCH port=wm_owned time=%0t actual=%h expected=%h",$time,actual_wm_owned,expected_wm_owned);
  if(actual_wm_fault!==expected_wm_fault)
   $fatal(1,"FULL_SHADOW_MISMATCH port=wm_fault time=%0t actual=%h expected=%h",$time,actual_wm_fault,expected_wm_fault);
  if(actual_wm_joined!==expected_wm_joined)
   $fatal(1,"FULL_SHADOW_MISMATCH port=wm_joined time=%0t actual=%h expected=%h",$time,actual_wm_joined,expected_wm_joined);
  if(actual_wm_receipts!==expected_wm_receipts)
   $fatal(1,"FULL_SHADOW_MISMATCH port=wm_receipts time=%0t actual=%h expected=%h",$time,actual_wm_receipts,expected_wm_receipts);
  if(actual_ap_ready!==expected_ap_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ap_ready time=%0t actual=%h expected=%h",$time,actual_ap_ready,expected_ap_ready);
  if(actual_ap_rsp_valid!==expected_ap_rsp_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ap_rsp_valid time=%0t actual=%h expected=%h",$time,actual_ap_rsp_valid,expected_ap_rsp_valid);
  if(actual_ap_rsp_design!==expected_ap_rsp_design)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ap_rsp_design time=%0t actual=%h expected=%h",$time,actual_ap_rsp_design,expected_ap_rsp_design);
  if(actual_ap_rsp_generation!==expected_ap_rsp_generation)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ap_rsp_generation time=%0t actual=%h expected=%h",$time,actual_ap_rsp_generation,expected_ap_rsp_generation);
  if(actual_ap_rsp_checkpoint!==expected_ap_rsp_checkpoint)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ap_rsp_checkpoint time=%0t actual=%h expected=%h",$time,actual_ap_rsp_checkpoint,expected_ap_rsp_checkpoint);
  if(actual_ap_rsp_cookie!==expected_ap_rsp_cookie)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ap_rsp_cookie time=%0t actual=%h expected=%h",$time,actual_ap_rsp_cookie,expected_ap_rsp_cookie);
  if(actual_ap_refs!==expected_ap_refs)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ap_refs time=%0t actual=%h expected=%h",$time,actual_ap_refs,expected_ap_refs);
  if(actual_ap_occ!==expected_ap_occ)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ap_occ time=%0t actual=%h expected=%h",$time,actual_ap_occ,expected_ap_occ);
  if(actual_ap_status!==expected_ap_status)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ap_status time=%0t actual=%h expected=%h",$time,actual_ap_status,expected_ap_status);
  if(actual_jp_start_ready!==expected_jp_start_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=jp_start_ready time=%0t actual=%h expected=%h",$time,actual_jp_start_ready,expected_jp_start_ready);
  if(actual_jp_commit_ready!==expected_jp_commit_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=jp_commit_ready time=%0t actual=%h expected=%h",$time,actual_jp_commit_ready,expected_jp_commit_ready);
  if(actual_jp_cancel_ready!==expected_jp_cancel_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=jp_cancel_ready time=%0t actual=%h expected=%h",$time,actual_jp_cancel_ready,expected_jp_cancel_ready);
  if(actual_jp_owned!==expected_jp_owned)
   $fatal(1,"FULL_SHADOW_MISMATCH port=jp_owned time=%0t actual=%h expected=%h",$time,actual_jp_owned,expected_jp_owned);
  if(actual_jp_done!==expected_jp_done)
   $fatal(1,"FULL_SHADOW_MISMATCH port=jp_done time=%0t actual=%h expected=%h",$time,actual_jp_done,expected_jp_done);
  if(actual_jp_result!==expected_jp_result)
   $fatal(1,"FULL_SHADOW_MISMATCH port=jp_result time=%0t actual=%h expected=%h",$time,actual_jp_result,expected_jp_result);
  if(actual_jp_ready!==expected_jp_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=jp_ready time=%0t actual=%h expected=%h",$time,actual_jp_ready,expected_jp_ready);
  if(actual_jp_reply!==expected_jp_reply)
   $fatal(1,"FULL_SHADOW_MISMATCH port=jp_reply time=%0t actual=%h expected=%h",$time,actual_jp_reply,expected_jp_reply);
  if(actual_jp_status!==expected_jp_status)
   $fatal(1,"FULL_SHADOW_MISMATCH port=jp_status time=%0t actual=%h expected=%h",$time,actual_jp_status,expected_jp_status);
  if(actual_boot_cfg_ready!==expected_boot_cfg_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=boot_cfg_ready time=%0t actual=%h expected=%h",$time,actual_boot_cfg_ready,expected_boot_cfg_ready);
  if(actual_boot_pending!==expected_boot_pending)
   $fatal(1,"FULL_SHADOW_MISMATCH port=boot_pending time=%0t actual=%h expected=%h",$time,actual_boot_pending,expected_boot_pending);
  if(actual_boot_rsp_valid!==expected_boot_rsp_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=boot_rsp_valid time=%0t actual=%h expected=%h",$time,actual_boot_rsp_valid,expected_boot_rsp_valid);
  if(actual_boot_status!==expected_boot_status)
   $fatal(1,"FULL_SHADOW_MISMATCH port=boot_status time=%0t actual=%h expected=%h",$time,actual_boot_status,expected_boot_status);
  if(actual_boot_verify_ready!==expected_boot_verify_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=boot_verify_ready time=%0t actual=%h expected=%h",$time,actual_boot_verify_ready,expected_boot_verify_ready);
  if(actual_boot_verified_count!==expected_boot_verified_count)
   $fatal(1,"FULL_SHADOW_MISMATCH port=boot_verified_count time=%0t actual=%h expected=%h",$time,actual_boot_verified_count,expected_boot_verified_count);
  if(actual_boot_verify_status!==expected_boot_verify_status)
   $fatal(1,"FULL_SHADOW_MISMATCH port=boot_verify_status time=%0t actual=%h expected=%h",$time,actual_boot_verify_status,expected_boot_verify_status);
  if(actual_boot_receipts!==expected_boot_receipts)
   $fatal(1,"FULL_SHADOW_MISMATCH port=boot_receipts time=%0t actual=%h expected=%h",$time,actual_boot_receipts,expected_boot_receipts);
  if(actual_boot_config_receipts!==expected_boot_config_receipts)
   $fatal(1,"FULL_SHADOW_MISMATCH port=boot_config_receipts time=%0t actual=%h expected=%h",$time,actual_boot_config_receipts,expected_boot_config_receipts);
  if(actual_qc_cp_ready!==expected_qc_cp_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_cp_ready time=%0t actual=%h expected=%h",$time,actual_qc_cp_ready,expected_qc_cp_ready);
  if(actual_qc_cp_busy!==expected_qc_cp_busy)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_cp_busy time=%0t actual=%h expected=%h",$time,actual_qc_cp_busy,expected_qc_cp_busy);
  if(actual_qc_cp_rsp_valid!==expected_qc_cp_rsp_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_cp_rsp_valid time=%0t actual=%h expected=%h",$time,actual_qc_cp_rsp_valid,expected_qc_cp_rsp_valid);
  if(actual_qc_cp_s_ready!==expected_qc_cp_s_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_cp_s_ready time=%0t actual=%h expected=%h",$time,actual_qc_cp_s_ready,expected_qc_cp_s_ready);
  if(actual_qc_cp_m_valid!==expected_qc_cp_m_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_cp_m_valid time=%0t actual=%h expected=%h",$time,actual_qc_cp_m_valid,expected_qc_cp_m_valid);
  if(actual_qc_cp_m_last!==expected_qc_cp_m_last)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_cp_m_last time=%0t actual=%h expected=%h",$time,actual_qc_cp_m_last,expected_qc_cp_m_last);
  if(actual_qc_restore_pending!==expected_qc_restore_pending)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_restore_pending time=%0t actual=%h expected=%h",$time,actual_qc_restore_pending,expected_qc_restore_pending);
  if(actual_qc_cp_crc!==expected_qc_cp_crc)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_cp_crc time=%0t actual=%h expected=%h",$time,actual_qc_cp_crc,expected_qc_cp_crc);
  if(actual_qc_cp_m_index!==expected_qc_cp_m_index)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_cp_m_index time=%0t actual=%h expected=%h",$time,actual_qc_cp_m_index,expected_qc_cp_m_index);
  if(actual_qc_cp_m_data!==expected_qc_cp_m_data)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_cp_m_data time=%0t actual=%h expected=%h",$time,actual_qc_cp_m_data,expected_qc_cp_m_data);
  if(actual_qc_cp_status!==expected_qc_cp_status)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_cp_status time=%0t actual=%h expected=%h",$time,actual_qc_cp_status,expected_qc_cp_status);
  if(actual_as_cfg_ready!==expected_as_cfg_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_cfg_ready time=%0t actual=%h expected=%h",$time,actual_as_cfg_ready,expected_as_cfg_ready);
  if(actual_as_configured!==expected_as_configured)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_configured time=%0t actual=%h expected=%h",$time,actual_as_configured,expected_as_configured);
  if(actual_as_bound_design!==expected_as_bound_design)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_bound_design time=%0t actual=%h expected=%h",$time,actual_as_bound_design,expected_as_bound_design);
  if(actual_as_bound_generation!==expected_as_bound_generation)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_bound_generation time=%0t actual=%h expected=%h",$time,actual_as_bound_generation,expected_as_bound_generation);
  if(actual_as_bound_checkpoint!==expected_as_bound_checkpoint)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_bound_checkpoint time=%0t actual=%h expected=%h",$time,actual_as_bound_checkpoint,expected_as_bound_checkpoint);
  if(actual_as_m_araddr!==expected_as_m_araddr)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_m_araddr time=%0t actual=%h expected=%h",$time,actual_as_m_araddr,expected_as_m_araddr);
  if(actual_as_m_arlen!==expected_as_m_arlen)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_m_arlen time=%0t actual=%h expected=%h",$time,actual_as_m_arlen,expected_as_m_arlen);
  if(actual_as_m_arsize!==expected_as_m_arsize)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_m_arsize time=%0t actual=%h expected=%h",$time,actual_as_m_arsize,expected_as_m_arsize);
  if(actual_as_m_arburst!==expected_as_m_arburst)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_m_arburst time=%0t actual=%h expected=%h",$time,actual_as_m_arburst,expected_as_m_arburst);
  if(actual_as_m_arid!==expected_as_m_arid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_m_arid time=%0t actual=%h expected=%h",$time,actual_as_m_arid,expected_as_m_arid);
  if(actual_as_m_arvalid!==expected_as_m_arvalid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_m_arvalid time=%0t actual=%h expected=%h",$time,actual_as_m_arvalid,expected_as_m_arvalid);
  if(actual_as_m_rready!==expected_as_m_rready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_m_rready time=%0t actual=%h expected=%h",$time,actual_as_m_rready,expected_as_m_rready);
  if(actual_as_m_awaddr!==expected_as_m_awaddr)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_m_awaddr time=%0t actual=%h expected=%h",$time,actual_as_m_awaddr,expected_as_m_awaddr);
  if(actual_as_m_awlen!==expected_as_m_awlen)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_m_awlen time=%0t actual=%h expected=%h",$time,actual_as_m_awlen,expected_as_m_awlen);
  if(actual_as_m_awsize!==expected_as_m_awsize)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_m_awsize time=%0t actual=%h expected=%h",$time,actual_as_m_awsize,expected_as_m_awsize);
  if(actual_as_m_awburst!==expected_as_m_awburst)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_m_awburst time=%0t actual=%h expected=%h",$time,actual_as_m_awburst,expected_as_m_awburst);
  if(actual_as_m_awid!==expected_as_m_awid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_m_awid time=%0t actual=%h expected=%h",$time,actual_as_m_awid,expected_as_m_awid);
  if(actual_as_m_awvalid!==expected_as_m_awvalid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_m_awvalid time=%0t actual=%h expected=%h",$time,actual_as_m_awvalid,expected_as_m_awvalid);
  if(actual_as_m_wdata!==expected_as_m_wdata)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_m_wdata time=%0t actual=%h expected=%h",$time,actual_as_m_wdata,expected_as_m_wdata);
  if(actual_as_m_wstrb!==expected_as_m_wstrb)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_m_wstrb time=%0t actual=%h expected=%h",$time,actual_as_m_wstrb,expected_as_m_wstrb);
  if(actual_as_m_wlast!==expected_as_m_wlast)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_m_wlast time=%0t actual=%h expected=%h",$time,actual_as_m_wlast,expected_as_m_wlast);
  if(actual_as_m_wvalid!==expected_as_m_wvalid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_m_wvalid time=%0t actual=%h expected=%h",$time,actual_as_m_wvalid,expected_as_m_wvalid);
  if(actual_as_m_bready!==expected_as_m_bready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_m_bready time=%0t actual=%h expected=%h",$time,actual_as_m_bready,expected_as_m_bready);
  if(actual_as_cfg_rsp_valid!==expected_as_cfg_rsp_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_cfg_rsp_valid time=%0t actual=%h expected=%h",$time,actual_as_cfg_rsp_valid,expected_as_cfg_rsp_valid);
  if(actual_as_cfg_status!==expected_as_cfg_status)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_cfg_status time=%0t actual=%h expected=%h",$time,actual_as_cfg_status,expected_as_cfg_status);
  if(actual_as_busy!==expected_as_busy)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_busy time=%0t actual=%h expected=%h",$time,actual_as_busy,expected_as_busy);
  if(actual_as_fault!==expected_as_fault)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_fault time=%0t actual=%h expected=%h",$time,actual_as_fault,expected_as_fault);
  if(actual_as_drained!==expected_as_drained)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_drained time=%0t actual=%h expected=%h",$time,actual_as_drained,expected_as_drained);
  if(actual_as_retired!==expected_as_retired)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_retired time=%0t actual=%h expected=%h",$time,actual_as_retired,expected_as_retired);
  if(actual_as_rsp_generation!==expected_as_rsp_generation)
   $fatal(1,"FULL_SHADOW_MISMATCH port=as_rsp_generation time=%0t actual=%h expected=%h",$time,actual_as_rsp_generation,expected_as_rsp_generation);
  if(actual_cp_ready!==expected_cp_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cp_ready time=%0t actual=%h expected=%h",$time,actual_cp_ready,expected_cp_ready);
  if(actual_cp_busy!==expected_cp_busy)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cp_busy time=%0t actual=%h expected=%h",$time,actual_cp_busy,expected_cp_busy);
  if(actual_cp_rsp_valid!==expected_cp_rsp_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cp_rsp_valid time=%0t actual=%h expected=%h",$time,actual_cp_rsp_valid,expected_cp_rsp_valid);
  if(actual_cp_status!==expected_cp_status)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cp_status time=%0t actual=%h expected=%h",$time,actual_cp_status,expected_cp_status);
  if(actual_cp_crc!==expected_cp_crc)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cp_crc time=%0t actual=%h expected=%h",$time,actual_cp_crc,expected_cp_crc);
  if(actual_cp_s_ready!==expected_cp_s_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cp_s_ready time=%0t actual=%h expected=%h",$time,actual_cp_s_ready,expected_cp_s_ready);
  if(actual_cp_m_valid!==expected_cp_m_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cp_m_valid time=%0t actual=%h expected=%h",$time,actual_cp_m_valid,expected_cp_m_valid);
  if(actual_cp_m_index!==expected_cp_m_index)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cp_m_index time=%0t actual=%h expected=%h",$time,actual_cp_m_index,expected_cp_m_index);
  if(actual_cp_m_data!==expected_cp_m_data)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cp_m_data time=%0t actual=%h expected=%h",$time,actual_cp_m_data,expected_cp_m_data);
  if(actual_cp_m_last!==expected_cp_m_last)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cp_m_last time=%0t actual=%h expected=%h",$time,actual_cp_m_last,expected_cp_m_last);
  if(actual_pc_route_retired!==expected_pc_route_retired)
   $fatal(1,"FULL_SHADOW_MISMATCH port=pc_route_retired time=%0t actual=%h expected=%h",$time,actual_pc_route_retired,expected_pc_route_retired);
  if(actual_pc_acquire_ready!==expected_pc_acquire_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=pc_acquire_ready time=%0t actual=%h expected=%h",$time,actual_pc_acquire_ready,expected_pc_acquire_ready);
  if(actual_pc_owned!==expected_pc_owned)
   $fatal(1,"FULL_SHADOW_MISMATCH port=pc_owned time=%0t actual=%h expected=%h",$time,actual_pc_owned,expected_pc_owned);
  if(actual_pc_release_ready!==expected_pc_release_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=pc_release_ready time=%0t actual=%h expected=%h",$time,actual_pc_release_ready,expected_pc_release_ready);
  if(actual_busy!==expected_busy)
   $fatal(1,"FULL_SHADOW_MISMATCH port=busy time=%0t actual=%h expected=%h",$time,actual_busy,expected_busy);
  if(actual_cc_busy!==expected_cc_busy)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cc_busy time=%0t actual=%h expected=%h",$time,actual_cc_busy,expected_cc_busy);
  if(actual_cc_fault!==expected_cc_fault)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cc_fault time=%0t actual=%h expected=%h",$time,actual_cc_fault,expected_cc_fault);
  if(actual_cf_fault!==expected_cf_fault)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cf_fault time=%0t actual=%h expected=%h",$time,actual_cf_fault,expected_cf_fault);
  if(actual_cost_lease!==expected_cost_lease)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cost_lease time=%0t actual=%h expected=%h",$time,actual_cost_lease,expected_cost_lease);
  if(actual_cs_busy!==expected_cs_busy)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_busy time=%0t actual=%h expected=%h",$time,actual_cs_busy,expected_cs_busy);
  if(actual_cs_configured!==expected_cs_configured)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_configured time=%0t actual=%h expected=%h",$time,actual_cs_configured,expected_cs_configured);
  if(actual_cs_design_id!==expected_cs_design_id)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_design_id time=%0t actual=%h expected=%h",$time,actual_cs_design_id,expected_cs_design_id);
  if(actual_cs_editing!==expected_cs_editing)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_editing time=%0t actual=%h expected=%h",$time,actual_cs_editing,expected_cs_editing);
  if(actual_cs_fault!==expected_cs_fault)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_fault time=%0t actual=%h expected=%h",$time,actual_cs_fault,expected_cs_fault);
  if(actual_cs_m_araddr!==expected_cs_m_araddr)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_m_araddr time=%0t actual=%h expected=%h",$time,actual_cs_m_araddr,expected_cs_m_araddr);
  if(actual_cs_m_arburst!==expected_cs_m_arburst)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_m_arburst time=%0t actual=%h expected=%h",$time,actual_cs_m_arburst,expected_cs_m_arburst);
  if(actual_cs_m_arid!==expected_cs_m_arid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_m_arid time=%0t actual=%h expected=%h",$time,actual_cs_m_arid,expected_cs_m_arid);
  if(actual_cs_m_arlen!==expected_cs_m_arlen)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_m_arlen time=%0t actual=%h expected=%h",$time,actual_cs_m_arlen,expected_cs_m_arlen);
  if(actual_cs_m_arsize!==expected_cs_m_arsize)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_m_arsize time=%0t actual=%h expected=%h",$time,actual_cs_m_arsize,expected_cs_m_arsize);
  if(actual_cs_m_arvalid!==expected_cs_m_arvalid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_m_arvalid time=%0t actual=%h expected=%h",$time,actual_cs_m_arvalid,expected_cs_m_arvalid);
  if(actual_cs_m_awaddr!==expected_cs_m_awaddr)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_m_awaddr time=%0t actual=%h expected=%h",$time,actual_cs_m_awaddr,expected_cs_m_awaddr);
  if(actual_cs_m_awburst!==expected_cs_m_awburst)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_m_awburst time=%0t actual=%h expected=%h",$time,actual_cs_m_awburst,expected_cs_m_awburst);
  if(actual_cs_m_awid!==expected_cs_m_awid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_m_awid time=%0t actual=%h expected=%h",$time,actual_cs_m_awid,expected_cs_m_awid);
  if(actual_cs_m_awlen!==expected_cs_m_awlen)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_m_awlen time=%0t actual=%h expected=%h",$time,actual_cs_m_awlen,expected_cs_m_awlen);
  if(actual_cs_m_awsize!==expected_cs_m_awsize)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_m_awsize time=%0t actual=%h expected=%h",$time,actual_cs_m_awsize,expected_cs_m_awsize);
  if(actual_cs_m_awvalid!==expected_cs_m_awvalid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_m_awvalid time=%0t actual=%h expected=%h",$time,actual_cs_m_awvalid,expected_cs_m_awvalid);
  if(actual_cs_m_bready!==expected_cs_m_bready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_m_bready time=%0t actual=%h expected=%h",$time,actual_cs_m_bready,expected_cs_m_bready);
  if(actual_cs_m_rready!==expected_cs_m_rready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_m_rready time=%0t actual=%h expected=%h",$time,actual_cs_m_rready,expected_cs_m_rready);
  if(actual_cs_m_wdata!==expected_cs_m_wdata)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_m_wdata time=%0t actual=%h expected=%h",$time,actual_cs_m_wdata,expected_cs_m_wdata);
  if(actual_cs_m_wlast!==expected_cs_m_wlast)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_m_wlast time=%0t actual=%h expected=%h",$time,actual_cs_m_wlast,expected_cs_m_wlast);
  if(actual_cs_m_wstrb!==expected_cs_m_wstrb)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_m_wstrb time=%0t actual=%h expected=%h",$time,actual_cs_m_wstrb,expected_cs_m_wstrb);
  if(actual_cs_m_wvalid!==expected_cs_m_wvalid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_m_wvalid time=%0t actual=%h expected=%h",$time,actual_cs_m_wvalid,expected_cs_m_wvalid);
  if(actual_cs_published_version!==expected_cs_published_version)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_published_version time=%0t actual=%h expected=%h",$time,actual_cs_published_version,expected_cs_published_version);
  if(actual_cs_ready_for_query!==expected_cs_ready_for_query)
   $fatal(1,"FULL_SHADOW_MISMATCH port=cs_ready_for_query time=%0t actual=%h expected=%h",$time,actual_cs_ready_for_query,expected_cs_ready_for_query);
  if(actual_d_configured!==expected_d_configured)
   $fatal(1,"FULL_SHADOW_MISMATCH port=d_configured time=%0t actual=%h expected=%h",$time,actual_d_configured,expected_d_configured);
  if(actual_d_m_araddr!==expected_d_m_araddr)
   $fatal(1,"FULL_SHADOW_MISMATCH port=d_m_araddr time=%0t actual=%h expected=%h",$time,actual_d_m_araddr,expected_d_m_araddr);
  if(actual_d_m_arburst!==expected_d_m_arburst)
   $fatal(1,"FULL_SHADOW_MISMATCH port=d_m_arburst time=%0t actual=%h expected=%h",$time,actual_d_m_arburst,expected_d_m_arburst);
  if(actual_d_m_arid!==expected_d_m_arid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=d_m_arid time=%0t actual=%h expected=%h",$time,actual_d_m_arid,expected_d_m_arid);
  if(actual_d_m_arlen!==expected_d_m_arlen)
   $fatal(1,"FULL_SHADOW_MISMATCH port=d_m_arlen time=%0t actual=%h expected=%h",$time,actual_d_m_arlen,expected_d_m_arlen);
  if(actual_d_m_arsize!==expected_d_m_arsize)
   $fatal(1,"FULL_SHADOW_MISMATCH port=d_m_arsize time=%0t actual=%h expected=%h",$time,actual_d_m_arsize,expected_d_m_arsize);
  if(actual_d_m_arvalid!==expected_d_m_arvalid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=d_m_arvalid time=%0t actual=%h expected=%h",$time,actual_d_m_arvalid,expected_d_m_arvalid);
  if(actual_d_m_awaddr!==expected_d_m_awaddr)
   $fatal(1,"FULL_SHADOW_MISMATCH port=d_m_awaddr time=%0t actual=%h expected=%h",$time,actual_d_m_awaddr,expected_d_m_awaddr);
  if(actual_d_m_awburst!==expected_d_m_awburst)
   $fatal(1,"FULL_SHADOW_MISMATCH port=d_m_awburst time=%0t actual=%h expected=%h",$time,actual_d_m_awburst,expected_d_m_awburst);
  if(actual_d_m_awid!==expected_d_m_awid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=d_m_awid time=%0t actual=%h expected=%h",$time,actual_d_m_awid,expected_d_m_awid);
  if(actual_d_m_awlen!==expected_d_m_awlen)
   $fatal(1,"FULL_SHADOW_MISMATCH port=d_m_awlen time=%0t actual=%h expected=%h",$time,actual_d_m_awlen,expected_d_m_awlen);
  if(actual_d_m_awsize!==expected_d_m_awsize)
   $fatal(1,"FULL_SHADOW_MISMATCH port=d_m_awsize time=%0t actual=%h expected=%h",$time,actual_d_m_awsize,expected_d_m_awsize);
  if(actual_d_m_awvalid!==expected_d_m_awvalid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=d_m_awvalid time=%0t actual=%h expected=%h",$time,actual_d_m_awvalid,expected_d_m_awvalid);
  if(actual_d_m_bready!==expected_d_m_bready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=d_m_bready time=%0t actual=%h expected=%h",$time,actual_d_m_bready,expected_d_m_bready);
  if(actual_d_m_rready!==expected_d_m_rready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=d_m_rready time=%0t actual=%h expected=%h",$time,actual_d_m_rready,expected_d_m_rready);
  if(actual_d_m_wdata!==expected_d_m_wdata)
   $fatal(1,"FULL_SHADOW_MISMATCH port=d_m_wdata time=%0t actual=%h expected=%h",$time,actual_d_m_wdata,expected_d_m_wdata);
  if(actual_d_m_wlast!==expected_d_m_wlast)
   $fatal(1,"FULL_SHADOW_MISMATCH port=d_m_wlast time=%0t actual=%h expected=%h",$time,actual_d_m_wlast,expected_d_m_wlast);
  if(actual_d_m_wstrb!==expected_d_m_wstrb)
   $fatal(1,"FULL_SHADOW_MISMATCH port=d_m_wstrb time=%0t actual=%h expected=%h",$time,actual_d_m_wstrb,expected_d_m_wstrb);
  if(actual_d_m_wvalid!==expected_d_m_wvalid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=d_m_wvalid time=%0t actual=%h expected=%h",$time,actual_d_m_wvalid,expected_d_m_wvalid);
  if(actual_f_all_drained!==expected_f_all_drained)
   $fatal(1,"FULL_SHADOW_MISMATCH port=f_all_drained time=%0t actual=%h expected=%h",$time,actual_f_all_drained,expected_f_all_drained);
  if(actual_f_backend_idle!==expected_f_backend_idle)
   $fatal(1,"FULL_SHADOW_MISMATCH port=f_backend_idle time=%0t actual=%h expected=%h",$time,actual_f_backend_idle,expected_f_backend_idle);
  if(actual_f_fault!==expected_f_fault)
   $fatal(1,"FULL_SHADOW_MISMATCH port=f_fault time=%0t actual=%h expected=%h",$time,actual_f_fault,expected_f_fault);
  if(actual_f_normal_retired!==expected_f_normal_retired)
   $fatal(1,"FULL_SHADOW_MISMATCH port=f_normal_retired time=%0t actual=%h expected=%h",$time,actual_f_normal_retired,expected_f_normal_retired);
  if(actual_f_phase!==expected_f_phase)
   $fatal(1,"FULL_SHADOW_MISMATCH port=f_phase time=%0t actual=%h expected=%h",$time,actual_f_phase,expected_f_phase);
  if(actual_f_recovery_owned!==expected_f_recovery_owned)
   $fatal(1,"FULL_SHADOW_MISMATCH port=f_recovery_owned time=%0t actual=%h expected=%h",$time,actual_f_recovery_owned,expected_f_recovery_owned);
  if(actual_f_sr!==expected_f_sr)
   $fatal(1,"FULL_SHADOW_MISMATCH port=f_sr time=%0t actual=%h expected=%h",$time,actual_f_sr,expected_f_sr);
  if(actual_f_srp!==expected_f_srp)
   $fatal(1,"FULL_SHADOW_MISMATCH port=f_srp time=%0t actual=%h expected=%h",$time,actual_f_srp,expected_f_srp);
  if(actual_f_srv!==expected_f_srv)
   $fatal(1,"FULL_SHADOW_MISMATCH port=f_srv time=%0t actual=%h expected=%h",$time,actual_f_srv,expected_f_srv);
  if(actual_fault!==expected_fault)
   $fatal(1,"FULL_SHADOW_MISMATCH port=fault time=%0t actual=%h expected=%h",$time,actual_fault,expected_fault);
  if(actual_g_configured!==expected_g_configured)
   $fatal(1,"FULL_SHADOW_MISMATCH port=g_configured time=%0t actual=%h expected=%h",$time,actual_g_configured,expected_g_configured);
  if(actual_g_m_araddr!==expected_g_m_araddr)
   $fatal(1,"FULL_SHADOW_MISMATCH port=g_m_araddr time=%0t actual=%h expected=%h",$time,actual_g_m_araddr,expected_g_m_araddr);
  if(actual_g_m_arburst!==expected_g_m_arburst)
   $fatal(1,"FULL_SHADOW_MISMATCH port=g_m_arburst time=%0t actual=%h expected=%h",$time,actual_g_m_arburst,expected_g_m_arburst);
  if(actual_g_m_arid!==expected_g_m_arid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=g_m_arid time=%0t actual=%h expected=%h",$time,actual_g_m_arid,expected_g_m_arid);
  if(actual_g_m_arlen!==expected_g_m_arlen)
   $fatal(1,"FULL_SHADOW_MISMATCH port=g_m_arlen time=%0t actual=%h expected=%h",$time,actual_g_m_arlen,expected_g_m_arlen);
  if(actual_g_m_arsize!==expected_g_m_arsize)
   $fatal(1,"FULL_SHADOW_MISMATCH port=g_m_arsize time=%0t actual=%h expected=%h",$time,actual_g_m_arsize,expected_g_m_arsize);
  if(actual_g_m_arvalid!==expected_g_m_arvalid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=g_m_arvalid time=%0t actual=%h expected=%h",$time,actual_g_m_arvalid,expected_g_m_arvalid);
  if(actual_g_m_rready!==expected_g_m_rready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=g_m_rready time=%0t actual=%h expected=%h",$time,actual_g_m_rready,expected_g_m_rready);
  if(actual_k_a_checkpoint!==expected_k_a_checkpoint)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_a_checkpoint time=%0t actual=%h expected=%h",$time,actual_k_a_checkpoint,expected_k_a_checkpoint);
  if(actual_k_a_cookie!==expected_k_a_cookie)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_a_cookie time=%0t actual=%h expected=%h",$time,actual_k_a_cookie,expected_k_a_cookie);
  if(actual_k_a_design!==expected_k_a_design)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_a_design time=%0t actual=%h expected=%h",$time,actual_k_a_design,expected_k_a_design);
  if(actual_k_a_net!==expected_k_a_net)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_a_net time=%0t actual=%h expected=%h",$time,actual_k_a_net,expected_k_a_net);
  if(actual_k_a_node!==expected_k_a_node)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_a_node time=%0t actual=%h expected=%h",$time,actual_k_a_node,expected_k_a_node);
  if(actual_k_a_occ!==expected_k_a_occ)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_a_occ time=%0t actual=%h expected=%h",$time,actual_k_a_occ,expected_k_a_occ);
  if(actual_k_a_ready!==expected_k_a_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_a_ready time=%0t actual=%h expected=%h",$time,actual_k_a_ready,expected_k_a_ready);
  if(actual_k_a_refs!==expected_k_a_refs)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_a_refs time=%0t actual=%h expected=%h",$time,actual_k_a_refs,expected_k_a_refs);
  if(actual_k_a_rsp_checkpoint!==expected_k_a_rsp_checkpoint)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_a_rsp_checkpoint time=%0t actual=%h expected=%h",$time,actual_k_a_rsp_checkpoint,expected_k_a_rsp_checkpoint);
  if(actual_k_a_rsp_cookie!==expected_k_a_rsp_cookie)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_a_rsp_cookie time=%0t actual=%h expected=%h",$time,actual_k_a_rsp_cookie,expected_k_a_rsp_cookie);
  if(actual_k_a_rsp_design!==expected_k_a_rsp_design)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_a_rsp_design time=%0t actual=%h expected=%h",$time,actual_k_a_rsp_design,expected_k_a_rsp_design);
  if(actual_k_a_rsp_ready!==expected_k_a_rsp_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_a_rsp_ready time=%0t actual=%h expected=%h",$time,actual_k_a_rsp_ready,expected_k_a_rsp_ready);
  if(actual_k_a_rsp_valid!==expected_k_a_rsp_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_a_rsp_valid time=%0t actual=%h expected=%h",$time,actual_k_a_rsp_valid,expected_k_a_rsp_valid);
  if(actual_k_a_status!==expected_k_a_status)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_a_status time=%0t actual=%h expected=%h",$time,actual_k_a_status,expected_k_a_status);
  if(actual_k_a_valid!==expected_k_a_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_a_valid time=%0t actual=%h expected=%h",$time,actual_k_a_valid,expected_k_a_valid);
  if(actual_k_busy!==expected_k_busy)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_busy time=%0t actual=%h expected=%h",$time,actual_k_busy,expected_k_busy);
  if(actual_k_corrected!==expected_k_corrected)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_corrected time=%0t actual=%h expected=%h",$time,actual_k_corrected,expected_k_corrected);
  if(actual_k_count!==expected_k_count)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_count time=%0t actual=%h expected=%h",$time,actual_k_count,expected_k_count);
  if(actual_k_fault!==expected_k_fault)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_fault time=%0t actual=%h expected=%h",$time,actual_k_fault,expected_k_fault);
  if(actual_k_full!==expected_k_full)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_full time=%0t actual=%h expected=%h",$time,actual_k_full,expected_k_full);
  if(actual_k_permit!==expected_k_permit)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_permit time=%0t actual=%h expected=%h",$time,actual_k_permit,expected_k_permit);
  if(actual_k_rec_ready!==expected_k_rec_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_rec_ready time=%0t actual=%h expected=%h",$time,actual_k_rec_ready,expected_k_rec_ready);
  if(actual_k_rsp_cookie!==expected_k_rsp_cookie)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_rsp_cookie time=%0t actual=%h expected=%h",$time,actual_k_rsp_cookie,expected_k_rsp_cookie);
  if(actual_k_rsp_status!==expected_k_rsp_status)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_rsp_status time=%0t actual=%h expected=%h",$time,actual_k_rsp_status,expected_k_rsp_status);
  if(actual_k_rsp_valid!==expected_k_rsp_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_rsp_valid time=%0t actual=%h expected=%h",$time,actual_k_rsp_valid,expected_k_rsp_valid);
  if(actual_k_saved_checkpoint!==expected_k_saved_checkpoint)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_saved_checkpoint time=%0t actual=%h expected=%h",$time,actual_k_saved_checkpoint,expected_k_saved_checkpoint);
  if(actual_k_saved_design!==expected_k_saved_design)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_saved_design time=%0t actual=%h expected=%h",$time,actual_k_saved_design,expected_k_saved_design);
  if(actual_k_target_reset!==expected_k_target_reset)
   $fatal(1,"FULL_SHADOW_MISMATCH port=k_target_reset time=%0t actual=%h expected=%h",$time,actual_k_target_reset,expected_k_target_reset);
  if(actual_lr_fault!==expected_lr_fault)
   $fatal(1,"FULL_SHADOW_MISMATCH port=lr_fault time=%0t actual=%h expected=%h",$time,actual_lr_fault,expected_lr_fault);
  if(actual_lr_rsp_status!==expected_lr_rsp_status)
   $fatal(1,"FULL_SHADOW_MISMATCH port=lr_rsp_status time=%0t actual=%h expected=%h",$time,actual_lr_rsp_status,expected_lr_rsp_status);
  if(actual_lr_s_ready!==expected_lr_s_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=lr_s_ready time=%0t actual=%h expected=%h",$time,actual_lr_s_ready,expected_lr_s_ready);
  if(actual_lr_verified!==expected_lr_verified)
   $fatal(1,"FULL_SHADOW_MISMATCH port=lr_verified time=%0t actual=%h expected=%h",$time,actual_lr_verified,expected_lr_verified);
  if(actual_lr_written!==expected_lr_written)
   $fatal(1,"FULL_SHADOW_MISMATCH port=lr_written time=%0t actual=%h expected=%h",$time,actual_lr_written,expected_lr_written);
  if(actual_operation_pending!==expected_operation_pending)
   $fatal(1,"FULL_SHADOW_MISMATCH port=operation_pending time=%0t actual=%h expected=%h",$time,actual_operation_pending,expected_operation_pending);
  if(actual_out_action!==expected_out_action)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_action time=%0t actual=%h expected=%h",$time,actual_out_action,expected_out_action);
  if(actual_out_attrs!==expected_out_attrs)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_attrs time=%0t actual=%h expected=%h",$time,actual_out_attrs,expected_out_attrs);
  if(actual_out_bits!==expected_out_bits)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_bits time=%0t actual=%h expected=%h",$time,actual_out_bits,expected_out_bits);
  if(actual_out_commit_acked!==expected_out_commit_acked)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_commit_acked time=%0t actual=%h expected=%h",$time,actual_out_commit_acked,expected_out_commit_acked);
  if(actual_out_commit_payload!==expected_out_commit_payload)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_commit_payload time=%0t actual=%h expected=%h",$time,actual_out_commit_payload,expected_out_commit_payload);
  if(actual_out_commit_status!==expected_out_commit_status)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_commit_status time=%0t actual=%h expected=%h",$time,actual_out_commit_status,expected_out_commit_status);
  if(actual_out_commit_valid!==expected_out_commit_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_commit_valid time=%0t actual=%h expected=%h",$time,actual_out_commit_valid,expected_out_commit_valid);
  if(actual_out_config!==expected_out_config)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_config time=%0t actual=%h expected=%h",$time,actual_out_config,expected_out_config);
  if(actual_out_connection!==expected_out_connection)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_connection time=%0t actual=%h expected=%h",$time,actual_out_connection,expected_out_connection);
  if(actual_out_cookie!==expected_out_cookie)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_cookie time=%0t actual=%h expected=%h",$time,actual_out_cookie,expected_out_cookie);
  if(actual_out_cost_geometry!==expected_out_cost_geometry)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_cost_geometry time=%0t actual=%h expected=%h",$time,actual_out_cost_geometry,expected_out_cost_geometry);
  if(actual_out_cost_geometry_result!==expected_out_cost_geometry_result)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_cost_geometry_result time=%0t actual=%h expected=%h",$time,actual_out_cost_geometry_result,expected_out_cost_geometry_result);
  if(actual_out_cost_packet!==expected_out_cost_packet)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_cost_packet time=%0t actual=%h expected=%h",$time,actual_out_cost_packet,expected_out_cost_packet);
  if(actual_out_cost_status!==expected_out_cost_status)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_cost_status time=%0t actual=%h expected=%h",$time,actual_out_cost_status,expected_out_cost_status);
  if(actual_out_cost_valid!==expected_out_cost_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_cost_valid time=%0t actual=%h expected=%h",$time,actual_out_cost_valid,expected_out_cost_valid);
  if(actual_out_cost_words!==expected_out_cost_words)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_cost_words time=%0t actual=%h expected=%h",$time,actual_out_cost_words,expected_out_cost_words);
  if(actual_out_node!==expected_out_node)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_node time=%0t actual=%h expected=%h",$time,actual_out_node,expected_out_node);
  if(actual_out_offer_before!==expected_out_offer_before)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_offer_before time=%0t actual=%h expected=%h",$time,actual_out_offer_before,expected_out_offer_before);
  if(actual_out_offer_key!==expected_out_offer_key)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_offer_key time=%0t actual=%h expected=%h",$time,actual_out_offer_key,expected_out_offer_key);
  if(actual_out_offer_node!==expected_out_offer_node)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_offer_node time=%0t actual=%h expected=%h",$time,actual_out_offer_node,expected_out_offer_node);
  if(actual_out_offer_size!==expected_out_offer_size)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_offer_size time=%0t actual=%h expected=%h",$time,actual_out_offer_size,expected_out_offer_size);
  if(actual_out_offer_status!==expected_out_offer_status)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_offer_status time=%0t actual=%h expected=%h",$time,actual_out_offer_status,expected_out_offer_status);
  if(actual_out_offer_valid!==expected_out_offer_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_offer_valid time=%0t actual=%h expected=%h",$time,actual_out_offer_valid,expected_out_offer_valid);
  if(actual_out_params!==expected_out_params)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_params time=%0t actual=%h expected=%h",$time,actual_out_params,expected_out_params);
  if(actual_out_params_valid!==expected_out_params_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_params_valid time=%0t actual=%h expected=%h",$time,actual_out_params_valid,expected_out_params_valid);
  if(actual_out_position!==expected_out_position)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_position time=%0t actual=%h expected=%h",$time,actual_out_position,expected_out_position);
  if(actual_out_post_attrs!==expected_out_post_attrs)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_post_attrs time=%0t actual=%h expected=%h",$time,actual_out_post_attrs,expected_out_post_attrs);
  if(actual_out_post_distance!==expected_out_post_distance)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_post_distance time=%0t actual=%h expected=%h",$time,actual_out_post_distance,expected_out_post_distance);
  if(actual_out_post_prev_read!==expected_out_post_prev_read)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_post_prev_read time=%0t actual=%h expected=%h",$time,actual_out_post_prev_read,expected_out_post_prev_read);
  if(actual_out_post_status!==expected_out_post_status)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_post_status time=%0t actual=%h expected=%h",$time,actual_out_post_status,expected_out_post_status);
  if(actual_out_post_upstream!==expected_out_post_upstream)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_post_upstream time=%0t actual=%h expected=%h",$time,actual_out_post_upstream,expected_out_post_upstream);
  if(actual_out_post_valid!==expected_out_post_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_post_valid time=%0t actual=%h expected=%h",$time,actual_out_post_valid,expected_out_post_valid);
  if(actual_out_post_x!==expected_out_post_x)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_post_x time=%0t actual=%h expected=%h",$time,actual_out_post_x,expected_out_post_x);
  if(actual_out_post_y!==expected_out_post_y)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_post_y time=%0t actual=%h expected=%h",$time,actual_out_post_y,expected_out_post_y);
  if(actual_out_prep_count!==expected_out_prep_count)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_prep_count time=%0t actual=%h expected=%h",$time,actual_out_prep_count,expected_out_prep_count);
  if(actual_out_prep_history!==expected_out_prep_history)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_prep_history time=%0t actual=%h expected=%h",$time,actual_out_prep_history,expected_out_prep_history);
  if(actual_out_prep_net_data!==expected_out_prep_net_data)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_prep_net_data time=%0t actual=%h expected=%h",$time,actual_out_prep_net_data,expected_out_prep_net_data);
  if(actual_out_prep_occupancy!==expected_out_prep_occupancy)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_prep_occupancy time=%0t actual=%h expected=%h",$time,actual_out_prep_occupancy,expected_out_prep_occupancy);
  if(actual_out_prep_price_index!==expected_out_prep_price_index)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_prep_price_index time=%0t actual=%h expected=%h",$time,actual_out_prep_price_index,expected_out_prep_price_index);
  if(actual_out_prep_price_value!==expected_out_prep_price_value)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_prep_price_value time=%0t actual=%h expected=%h",$time,actual_out_prep_price_value,expected_out_prep_price_value);
  if(actual_out_prep_status!==expected_out_prep_status)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_prep_status time=%0t actual=%h expected=%h",$time,actual_out_prep_status,expected_out_prep_status);
  if(actual_out_prep_valid!==expected_out_prep_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_prep_valid time=%0t actual=%h expected=%h",$time,actual_out_prep_valid,expected_out_prep_valid);
  if(actual_out_profile_revision!==expected_out_profile_revision)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_profile_revision time=%0t actual=%h expected=%h",$time,actual_out_profile_revision,expected_out_profile_revision);
  if(actual_out_sequence!==expected_out_sequence)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_sequence time=%0t actual=%h expected=%h",$time,actual_out_sequence,expected_out_sequence);
  if(actual_out_services!==expected_out_services)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_services time=%0t actual=%h expected=%h",$time,actual_out_services,expected_out_services);
  if(actual_out_steps!==expected_out_steps)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_steps time=%0t actual=%h expected=%h",$time,actual_out_steps,expected_out_steps);
  if(actual_out_valid!==expected_out_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=out_valid time=%0t actual=%h expected=%h",$time,actual_out_valid,expected_out_valid);
  if(actual_owner_configured!==expected_owner_configured)
   $fatal(1,"FULL_SHADOW_MISMATCH port=owner_configured time=%0t actual=%h expected=%h",$time,actual_owner_configured,expected_owner_configured);
  if(actual_owner_m_araddr!==expected_owner_m_araddr)
   $fatal(1,"FULL_SHADOW_MISMATCH port=owner_m_araddr time=%0t actual=%h expected=%h",$time,actual_owner_m_araddr,expected_owner_m_araddr);
  if(actual_owner_m_arburst!==expected_owner_m_arburst)
   $fatal(1,"FULL_SHADOW_MISMATCH port=owner_m_arburst time=%0t actual=%h expected=%h",$time,actual_owner_m_arburst,expected_owner_m_arburst);
  if(actual_owner_m_arid!==expected_owner_m_arid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=owner_m_arid time=%0t actual=%h expected=%h",$time,actual_owner_m_arid,expected_owner_m_arid);
  if(actual_owner_m_arlen!==expected_owner_m_arlen)
   $fatal(1,"FULL_SHADOW_MISMATCH port=owner_m_arlen time=%0t actual=%h expected=%h",$time,actual_owner_m_arlen,expected_owner_m_arlen);
  if(actual_owner_m_arsize!==expected_owner_m_arsize)
   $fatal(1,"FULL_SHADOW_MISMATCH port=owner_m_arsize time=%0t actual=%h expected=%h",$time,actual_owner_m_arsize,expected_owner_m_arsize);
  if(actual_owner_m_arvalid!==expected_owner_m_arvalid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=owner_m_arvalid time=%0t actual=%h expected=%h",$time,actual_owner_m_arvalid,expected_owner_m_arvalid);
  if(actual_owner_m_awaddr!==expected_owner_m_awaddr)
   $fatal(1,"FULL_SHADOW_MISMATCH port=owner_m_awaddr time=%0t actual=%h expected=%h",$time,actual_owner_m_awaddr,expected_owner_m_awaddr);
  if(actual_owner_m_awburst!==expected_owner_m_awburst)
   $fatal(1,"FULL_SHADOW_MISMATCH port=owner_m_awburst time=%0t actual=%h expected=%h",$time,actual_owner_m_awburst,expected_owner_m_awburst);
  if(actual_owner_m_awid!==expected_owner_m_awid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=owner_m_awid time=%0t actual=%h expected=%h",$time,actual_owner_m_awid,expected_owner_m_awid);
  if(actual_owner_m_awlen!==expected_owner_m_awlen)
   $fatal(1,"FULL_SHADOW_MISMATCH port=owner_m_awlen time=%0t actual=%h expected=%h",$time,actual_owner_m_awlen,expected_owner_m_awlen);
  if(actual_owner_m_awsize!==expected_owner_m_awsize)
   $fatal(1,"FULL_SHADOW_MISMATCH port=owner_m_awsize time=%0t actual=%h expected=%h",$time,actual_owner_m_awsize,expected_owner_m_awsize);
  if(actual_owner_m_awvalid!==expected_owner_m_awvalid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=owner_m_awvalid time=%0t actual=%h expected=%h",$time,actual_owner_m_awvalid,expected_owner_m_awvalid);
  if(actual_owner_m_bready!==expected_owner_m_bready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=owner_m_bready time=%0t actual=%h expected=%h",$time,actual_owner_m_bready,expected_owner_m_bready);
  if(actual_owner_m_rready!==expected_owner_m_rready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=owner_m_rready time=%0t actual=%h expected=%h",$time,actual_owner_m_rready,expected_owner_m_rready);
  if(actual_owner_m_wdata!==expected_owner_m_wdata)
   $fatal(1,"FULL_SHADOW_MISMATCH port=owner_m_wdata time=%0t actual=%h expected=%h",$time,actual_owner_m_wdata,expected_owner_m_wdata);
  if(actual_owner_m_wlast!==expected_owner_m_wlast)
   $fatal(1,"FULL_SHADOW_MISMATCH port=owner_m_wlast time=%0t actual=%h expected=%h",$time,actual_owner_m_wlast,expected_owner_m_wlast);
  if(actual_owner_m_wstrb!==expected_owner_m_wstrb)
   $fatal(1,"FULL_SHADOW_MISMATCH port=owner_m_wstrb time=%0t actual=%h expected=%h",$time,actual_owner_m_wstrb,expected_owner_m_wstrb);
  if(actual_owner_m_wvalid!==expected_owner_m_wvalid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=owner_m_wvalid time=%0t actual=%h expected=%h",$time,actual_owner_m_wvalid,expected_owner_m_wvalid);
  if(actual_p_active!==expected_p_active)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_active time=%0t actual=%h expected=%h",$time,actual_p_active,expected_p_active);
  if(actual_p_active_price!==expected_p_active_price)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_active_price time=%0t actual=%h expected=%h",$time,actual_p_active_price,expected_p_active_price);
  if(actual_p_active_query!==expected_p_active_query)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_active_query time=%0t actual=%h expected=%h",$time,actual_p_active_query,expected_p_active_query);
  if(actual_p_m_araddr!==expected_p_m_araddr)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_m_araddr time=%0t actual=%h expected=%h",$time,actual_p_m_araddr,expected_p_m_araddr);
  if(actual_p_m_arburst!==expected_p_m_arburst)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_m_arburst time=%0t actual=%h expected=%h",$time,actual_p_m_arburst,expected_p_m_arburst);
  if(actual_p_m_arid!==expected_p_m_arid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_m_arid time=%0t actual=%h expected=%h",$time,actual_p_m_arid,expected_p_m_arid);
  if(actual_p_m_arlen!==expected_p_m_arlen)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_m_arlen time=%0t actual=%h expected=%h",$time,actual_p_m_arlen,expected_p_m_arlen);
  if(actual_p_m_arsize!==expected_p_m_arsize)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_m_arsize time=%0t actual=%h expected=%h",$time,actual_p_m_arsize,expected_p_m_arsize);
  if(actual_p_m_arvalid!==expected_p_m_arvalid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_m_arvalid time=%0t actual=%h expected=%h",$time,actual_p_m_arvalid,expected_p_m_arvalid);
  if(actual_p_m_awaddr!==expected_p_m_awaddr)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_m_awaddr time=%0t actual=%h expected=%h",$time,actual_p_m_awaddr,expected_p_m_awaddr);
  if(actual_p_m_awburst!==expected_p_m_awburst)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_m_awburst time=%0t actual=%h expected=%h",$time,actual_p_m_awburst,expected_p_m_awburst);
  if(actual_p_m_awid!==expected_p_m_awid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_m_awid time=%0t actual=%h expected=%h",$time,actual_p_m_awid,expected_p_m_awid);
  if(actual_p_m_awlen!==expected_p_m_awlen)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_m_awlen time=%0t actual=%h expected=%h",$time,actual_p_m_awlen,expected_p_m_awlen);
  if(actual_p_m_awsize!==expected_p_m_awsize)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_m_awsize time=%0t actual=%h expected=%h",$time,actual_p_m_awsize,expected_p_m_awsize);
  if(actual_p_m_awvalid!==expected_p_m_awvalid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_m_awvalid time=%0t actual=%h expected=%h",$time,actual_p_m_awvalid,expected_p_m_awvalid);
  if(actual_p_m_bready!==expected_p_m_bready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_m_bready time=%0t actual=%h expected=%h",$time,actual_p_m_bready,expected_p_m_bready);
  if(actual_p_m_rready!==expected_p_m_rready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_m_rready time=%0t actual=%h expected=%h",$time,actual_p_m_rready,expected_p_m_rready);
  if(actual_p_m_wdata!==expected_p_m_wdata)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_m_wdata time=%0t actual=%h expected=%h",$time,actual_p_m_wdata,expected_p_m_wdata);
  if(actual_p_m_wlast!==expected_p_m_wlast)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_m_wlast time=%0t actual=%h expected=%h",$time,actual_p_m_wlast,expected_p_m_wlast);
  if(actual_p_m_wstrb!==expected_p_m_wstrb)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_m_wstrb time=%0t actual=%h expected=%h",$time,actual_p_m_wstrb,expected_p_m_wstrb);
  if(actual_p_m_wvalid!==expected_p_m_wvalid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=p_m_wvalid time=%0t actual=%h expected=%h",$time,actual_p_m_wvalid,expected_p_m_wvalid);
  if(actual_q_busy!==expected_q_busy)
   $fatal(1,"FULL_SHADOW_MISMATCH port=q_busy time=%0t actual=%h expected=%h",$time,actual_q_busy,expected_q_busy);
  if(actual_q_configured!==expected_q_configured)
   $fatal(1,"FULL_SHADOW_MISMATCH port=q_configured time=%0t actual=%h expected=%h",$time,actual_q_configured,expected_q_configured);
  if(actual_q_fault!==expected_q_fault)
   $fatal(1,"FULL_SHADOW_MISMATCH port=q_fault time=%0t actual=%h expected=%h",$time,actual_q_fault,expected_q_fault);
  if(actual_q_m_araddr!==expected_q_m_araddr)
   $fatal(1,"FULL_SHADOW_MISMATCH port=q_m_araddr time=%0t actual=%h expected=%h",$time,actual_q_m_araddr,expected_q_m_araddr);
  if(actual_q_m_arburst!==expected_q_m_arburst)
   $fatal(1,"FULL_SHADOW_MISMATCH port=q_m_arburst time=%0t actual=%h expected=%h",$time,actual_q_m_arburst,expected_q_m_arburst);
  if(actual_q_m_arid!==expected_q_m_arid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=q_m_arid time=%0t actual=%h expected=%h",$time,actual_q_m_arid,expected_q_m_arid);
  if(actual_q_m_arlen!==expected_q_m_arlen)
   $fatal(1,"FULL_SHADOW_MISMATCH port=q_m_arlen time=%0t actual=%h expected=%h",$time,actual_q_m_arlen,expected_q_m_arlen);
  if(actual_q_m_arsize!==expected_q_m_arsize)
   $fatal(1,"FULL_SHADOW_MISMATCH port=q_m_arsize time=%0t actual=%h expected=%h",$time,actual_q_m_arsize,expected_q_m_arsize);
  if(actual_q_m_arvalid!==expected_q_m_arvalid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=q_m_arvalid time=%0t actual=%h expected=%h",$time,actual_q_m_arvalid,expected_q_m_arvalid);
  if(actual_q_m_rready!==expected_q_m_rready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=q_m_rready time=%0t actual=%h expected=%h",$time,actual_q_m_rready,expected_q_m_rready);
  if(actual_query_ready!==expected_query_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=query_ready time=%0t actual=%h expected=%h",$time,actual_query_ready,expected_query_ready);
  if(actual_query_version!==expected_query_version)
   $fatal(1,"FULL_SHADOW_MISMATCH port=query_version time=%0t actual=%h expected=%h",$time,actual_query_version,expected_query_version);
  if(actual_rc_block!==expected_rc_block)
   $fatal(1,"FULL_SHADOW_MISMATCH port=rc_block time=%0t actual=%h expected=%h",$time,actual_rc_block,expected_rc_block);
  if(actual_rc_busy!==expected_rc_busy)
   $fatal(1,"FULL_SHADOW_MISMATCH port=rc_busy time=%0t actual=%h expected=%h",$time,actual_rc_busy,expected_rc_busy);
  if(actual_rc_fault!==expected_rc_fault)
   $fatal(1,"FULL_SHADOW_MISMATCH port=rc_fault time=%0t actual=%h expected=%h",$time,actual_rc_fault,expected_rc_fault);
  if(actual_rc_req_ready!==expected_rc_req_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=rc_req_ready time=%0t actual=%h expected=%h",$time,actual_rc_req_ready,expected_rc_req_ready);
  if(actual_rc_rsp_acked!==expected_rc_rsp_acked)
   $fatal(1,"FULL_SHADOW_MISMATCH port=rc_rsp_acked time=%0t actual=%h expected=%h",$time,actual_rc_rsp_acked,expected_rc_rsp_acked);
  if(actual_rc_rsp_cookie!==expected_rc_rsp_cookie)
   $fatal(1,"FULL_SHADOW_MISMATCH port=rc_rsp_cookie time=%0t actual=%h expected=%h",$time,actual_rc_rsp_cookie,expected_rc_rsp_cookie);
  if(actual_rc_rsp_nodes!==expected_rc_rsp_nodes)
   $fatal(1,"FULL_SHADOW_MISMATCH port=rc_rsp_nodes time=%0t actual=%h expected=%h",$time,actual_rc_rsp_nodes,expected_rc_rsp_nodes);
  if(actual_rc_rsp_status!==expected_rc_rsp_status)
   $fatal(1,"FULL_SHADOW_MISMATCH port=rc_rsp_status time=%0t actual=%h expected=%h",$time,actual_rc_rsp_status,expected_rc_rsp_status);
  if(actual_rc_rsp_valid!==expected_rc_rsp_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=rc_rsp_valid time=%0t actual=%h expected=%h",$time,actual_rc_rsp_valid,expected_rc_rsp_valid);
  if(actual_rc_slots!==expected_rc_slots)
   $fatal(1,"FULL_SHADOW_MISMATCH port=rc_slots time=%0t actual=%h expected=%h",$time,actual_rc_slots,expected_rc_slots);
  if(actual_rst!==expected_rst)
   $fatal(1,"FULL_SHADOW_MISMATCH port=rst time=%0t actual=%h expected=%h",$time,actual_rst,expected_rst);
  if(actual_t_configured!==expected_t_configured)
   $fatal(1,"FULL_SHADOW_MISMATCH port=t_configured time=%0t actual=%h expected=%h",$time,actual_t_configured,expected_t_configured);
  if(actual_t_m_araddr!==expected_t_m_araddr)
   $fatal(1,"FULL_SHADOW_MISMATCH port=t_m_araddr time=%0t actual=%h expected=%h",$time,actual_t_m_araddr,expected_t_m_araddr);
  if(actual_t_m_arburst!==expected_t_m_arburst)
   $fatal(1,"FULL_SHADOW_MISMATCH port=t_m_arburst time=%0t actual=%h expected=%h",$time,actual_t_m_arburst,expected_t_m_arburst);
  if(actual_t_m_arid!==expected_t_m_arid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=t_m_arid time=%0t actual=%h expected=%h",$time,actual_t_m_arid,expected_t_m_arid);
  if(actual_t_m_arlen!==expected_t_m_arlen)
   $fatal(1,"FULL_SHADOW_MISMATCH port=t_m_arlen time=%0t actual=%h expected=%h",$time,actual_t_m_arlen,expected_t_m_arlen);
  if(actual_t_m_arsize!==expected_t_m_arsize)
   $fatal(1,"FULL_SHADOW_MISMATCH port=t_m_arsize time=%0t actual=%h expected=%h",$time,actual_t_m_arsize,expected_t_m_arsize);
  if(actual_t_m_arvalid!==expected_t_m_arvalid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=t_m_arvalid time=%0t actual=%h expected=%h",$time,actual_t_m_arvalid,expected_t_m_arvalid);
  if(actual_t_m_rready!==expected_t_m_rready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=t_m_rready time=%0t actual=%h expected=%h",$time,actual_t_m_rready,expected_t_m_rready);
  if(actual_ss_start_ready!==expected_ss_start_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ss_start_ready time=%0t actual=%h expected=%h",$time,actual_ss_start_ready,expected_ss_start_ready);
  if(actual_ss_rsp_valid!==expected_ss_rsp_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ss_rsp_valid time=%0t actual=%h expected=%h",$time,actual_ss_rsp_valid,expected_ss_rsp_valid);
  if(actual_ss_rsp_status!==expected_ss_rsp_status)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ss_rsp_status time=%0t actual=%h expected=%h",$time,actual_ss_rsp_status,expected_ss_rsp_status);
  if(actual_ss_rsp_cookie!==expected_ss_rsp_cookie)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ss_rsp_cookie time=%0t actual=%h expected=%h",$time,actual_ss_rsp_cookie,expected_ss_rsp_cookie);
  if(actual_ss_polls!==expected_ss_polls)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ss_polls time=%0t actual=%h expected=%h",$time,actual_ss_polls,expected_ss_polls);
  if(actual_ss_expands!==expected_ss_expands)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ss_expands time=%0t actual=%h expected=%h",$time,actual_ss_expands,expected_ss_expands);
  if(actual_ss_candidates!==expected_ss_candidates)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ss_candidates time=%0t actual=%h expected=%h",$time,actual_ss_candidates,expected_ss_candidates);
  if(actual_ss_result_node!==expected_ss_result_node)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ss_result_node time=%0t actual=%h expected=%h",$time,actual_ss_result_node,expected_ss_result_node);
  if(actual_ss_result_key!==expected_ss_result_key)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ss_result_key time=%0t actual=%h expected=%h",$time,actual_ss_result_key,expected_ss_result_key);
  if(actual_ss_busy!==expected_ss_busy)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ss_busy time=%0t actual=%h expected=%h",$time,actual_ss_busy,expected_ss_busy);
  if(actual_ss_fault!==expected_ss_fault)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ss_fault time=%0t actual=%h expected=%h",$time,actual_ss_fault,expected_ss_fault);
  if(actual_ss_phase!==expected_ss_phase)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ss_phase time=%0t actual=%h expected=%h",$time,actual_ss_phase,expected_ss_phase);
  if(actual_ss_poll_event!==expected_ss_poll_event)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ss_poll_event time=%0t actual=%h expected=%h",$time,actual_ss_poll_event,expected_ss_poll_event);
  if(actual_ss_poll_node!==expected_ss_poll_node)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ss_poll_node time=%0t actual=%h expected=%h",$time,actual_ss_poll_node,expected_ss_poll_node);
  if(actual_ss_poll_key!==expected_ss_poll_key)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ss_poll_key time=%0t actual=%h expected=%h",$time,actual_ss_poll_key,expected_ss_poll_key);
  if(actual_ss_poll_size!==expected_ss_poll_size)
   $fatal(1,"FULL_SHADOW_MISMATCH port=ss_poll_size time=%0t actual=%h expected=%h",$time,actual_ss_poll_size,expected_ss_poll_size);
  if(actual_qc_cmd_ready!==expected_qc_cmd_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_cmd_ready time=%0t actual=%h expected=%h",$time,actual_qc_cmd_ready,expected_qc_cmd_ready);
  if(actual_qc_rsp_valid!==expected_qc_rsp_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_rsp_valid time=%0t actual=%h expected=%h",$time,actual_qc_rsp_valid,expected_qc_rsp_valid);
  if(actual_qc_rsp_status!==expected_qc_rsp_status)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_rsp_status time=%0t actual=%h expected=%h",$time,actual_qc_rsp_status,expected_qc_rsp_status);
  if(actual_qc_rsp_detail!==expected_qc_rsp_detail)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_rsp_detail time=%0t actual=%h expected=%h",$time,actual_qc_rsp_detail,expected_qc_rsp_detail);
  if(actual_qc_rsp_cookie!==expected_qc_rsp_cookie)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_rsp_cookie time=%0t actual=%h expected=%h",$time,actual_qc_rsp_cookie,expected_qc_rsp_cookie);
  if(actual_qc_rsp_nodes!==expected_qc_rsp_nodes)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_rsp_nodes time=%0t actual=%h expected=%h",$time,actual_qc_rsp_nodes,expected_qc_rsp_nodes);
  if(actual_qc_rsp_acked!==expected_qc_rsp_acked)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_rsp_acked time=%0t actual=%h expected=%h",$time,actual_qc_rsp_acked,expected_qc_rsp_acked);
  if(actual_qc_rsp_committed!==expected_qc_rsp_committed)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_rsp_committed time=%0t actual=%h expected=%h",$time,actual_qc_rsp_committed,expected_qc_rsp_committed);
  if(actual_qc_busy!==expected_qc_busy)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_busy time=%0t actual=%h expected=%h",$time,actual_qc_busy,expected_qc_busy);
  if(actual_qc_fault!==expected_qc_fault)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_fault time=%0t actual=%h expected=%h",$time,actual_qc_fault,expected_qc_fault);
  if(actual_qc_phase!==expected_qc_phase)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_phase time=%0t actual=%h expected=%h",$time,actual_qc_phase,expected_qc_phase);
  if(actual_qc_prepared_event!==expected_qc_prepared_event)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_prepared_event time=%0t actual=%h expected=%h",$time,actual_qc_prepared_event,expected_qc_prepared_event);
  if(actual_qc_prepare_acked!==expected_qc_prepare_acked)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_prepare_acked time=%0t actual=%h expected=%h",$time,actual_qc_prepare_acked,expected_qc_prepare_acked);
  if(actual_qc_cleanup_acked!==expected_qc_cleanup_acked)
   $fatal(1,"FULL_SHADOW_MISMATCH port=qc_cleanup_acked time=%0t actual=%h expected=%h",$time,actual_qc_cleanup_acked,expected_qc_cleanup_acked);
  if(actual_scan_ready!==expected_scan_ready)
   $fatal(1,"FULL_SHADOW_MISMATCH port=scan_ready time=%0t actual=%h expected=%h",$time,actual_scan_ready,expected_scan_ready);
  if(actual_scan_rsp_valid!==expected_scan_rsp_valid)
   $fatal(1,"FULL_SHADOW_MISMATCH port=scan_rsp_valid time=%0t actual=%h expected=%h",$time,actual_scan_rsp_valid,expected_scan_rsp_valid);
  if(actual_scan_status!==expected_scan_status)
   $fatal(1,"FULL_SHADOW_MISMATCH port=scan_status time=%0t actual=%h expected=%h",$time,actual_scan_status,expected_scan_status);
  if(actual_scan_result_frame!==expected_scan_result_frame)
   $fatal(1,"FULL_SHADOW_MISMATCH port=scan_result_frame time=%0t actual=%h expected=%h",$time,actual_scan_result_frame,expected_scan_result_frame);
  if(actual_scan_owner!==expected_scan_owner)
   $fatal(1,"FULL_SHADOW_MISMATCH port=scan_owner time=%0t actual=%h expected=%h",$time,actual_scan_owner,expected_scan_owner);
  if(actual_scan_published!==expected_scan_published)
   $fatal(1,"FULL_SHADOW_MISMATCH port=scan_published time=%0t actual=%h expected=%h",$time,actual_scan_published,expected_scan_published);
  if(actual_lr_source_crc!==expected_lr_source_crc)
   $fatal(1,"FULL_SHADOW_MISMATCH port=lr_source_crc time=%0t actual=%h expected=%h",$time,actual_lr_source_crc,expected_lr_source_crc);
 end
end
// Call only at the original normal terminal point, before $finish.
task finish_and_check;
time original_end;
begin
 original_end=$time;
 #(SHIFT_NS+2);
 if(!armed||reset_edges<5||checks==0||last_checked<original_end+SHIFT_NS-5)
  $fatal(1,"FULL_SHADOW_INCOMPLETE reset=%0d checks=%0d last=%0t end=%0t",reset_edges,checks,last_checked,original_end);
 $display("FULL_SHADOW_PASS outputs=346 bits=14384 checks=%0d reset_edges=%0d original_end=%0t last_checked=%0t",checks,reset_edges,original_end,last_checked);
end endtask
initial begin #100000000; $fatal(1,"FULL_SHADOW_WATCHDOG"); end
endmodule
`default_nettype wire
