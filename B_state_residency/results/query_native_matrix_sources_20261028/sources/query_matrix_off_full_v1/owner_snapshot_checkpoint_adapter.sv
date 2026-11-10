`timescale 1ns/1ps
// Cumulative dirty-line snapshot relative to an externally cloned immutable baseline.
// Single outstanding source writer; addresses are captured from actual AW handshakes.
module owner_snapshot_checkpoint_adapter #(parameter integer MAX_DIRTY=64)(
 input wire clk,rst,lease,source_drained,
 input wire obs_awvalid,obs_awready,input wire[63:0]obs_awaddr,input wire[7:0]obs_awlen,
 input wire obs_bvalid,obs_bready,input wire[1:0]obs_bresp,
 input wire cmd_valid,output wire cmd_ready,input wire[63:0]source_base,destination_base,span_bytes,input wire[31:0]cmd_cookie,
 output wire busy,rsp_valid,input wire rsp_ready,output wire[3:0]status,output wire[31:0]rsp_cookie,
 output wire receipt_valid,output wire[31:0]dirty_count,verified_count,
 output wire[63:0]m_araddr,output wire m_arvalid,input wire m_arready,
 input wire[511:0]m_rdata,input wire[3:0]m_rid,input wire[1:0]m_rresp,input wire m_rlast,m_rvalid,output wire m_rready,
 output wire[63:0]m_awaddr,output wire m_awvalid,input wire m_awready,
 output wire[511:0]m_wdata,output wire m_wvalid,input wire m_wready,
 input wire[3:0]m_bid,input wire[1:0]m_bresp,input wire m_bvalid,output wire m_bready,
 input wire host_release_valid,root_release_ready,
 output wire host_release_ready,root_release_valid,manifest_ready
);
 wire snapshot_owned=busy||cmd_valid;
 assign host_release_ready=root_release_ready&&!snapshot_owned;
 assign root_release_valid=host_release_valid&&!snapshot_owned;
 assign manifest_ready=receipt_valid&&!snapshot_owned;
 incremental_owner_snapshot #(.MAX_DIRTY(MAX_DIRTY)) engine(.*);
endmodule
