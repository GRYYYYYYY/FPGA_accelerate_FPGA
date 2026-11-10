`timescale 1ns/1ps
module label_snapshot_checkpoint_adapter #(parameter integer FRAMES=16384,INDEX_BITS=14)(
 input wire clk,rst,lease,source_drained,cmd_valid,output wire cmd_ready,
 input wire[1:0]cmd_query,input wire[3:0]cmd_price,input wire[31:0]cmd_nodes,cmd_cookie,
 output wire busy,rsp_valid,input wire rsp_ready,output wire[3:0]status,output wire[31:0]rsp_cookie,record_count,record_crc,page_count,
 output wire receipt_valid,
 output wire scan_valid,input wire scan_ready,output wire[INDEX_BITS-1:0]scan_frame,
 input wire scan_rsp_valid,output wire scan_rsp_ready,input wire[2:0]scan_status,input wire[INDEX_BITS-1:0]scan_result_frame,input wire[26:0]scan_owner,input wire scan_published,
 output wire[31:0]m_araddr,output wire m_arvalid,input wire m_arready,
 input wire[511:0]m_rdata,input wire[3:0]m_rid,input wire[1:0]m_rresp,input wire m_rlast,m_rvalid,output wire m_rready,
 output wire record_valid,input wire record_ready,output wire[31:0]record_node,output wire[159:0]record_payload,
 input wire host_release_valid,root_release_ready,output wire host_release_ready,root_release_valid,manifest_ready
);
 wire owned=busy||cmd_valid;
 assign host_release_ready=root_release_ready&&!owned;
 assign root_release_valid=host_release_valid&&!owned;
 assign manifest_ready=receipt_valid&&!owned;
 label_snapshot_reader #(.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS)) engine(.*);
endmodule
