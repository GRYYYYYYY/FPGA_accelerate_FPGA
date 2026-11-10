`timescale 1ns/1ps
module tb_response_fallthrough_fence_debug;
 small_endpoint_checkpoint_stream_v3_test #(.SMALL(1)) test();
 always @(posedge test.clk)begin
  if(!test.rst && test.dut.q_valid && test.dut.q_receive && test.active_op==11)
   $display("FINISH_DEBUG state=%0d status=%0d active=%0d ack=%0d sealed=%0d req=%0d work=%0d rsp=%0d fence_req=%0d fence_ack=%0d leases=%h",test.dut.state,test.dut.q_status,test.dut.pages.fence_active,test.dut.pages.acknowledged,test.dut.pages.peer_sealed,test.dut.pages.request_count,test.dut.pages.work_count,test.dut.pages.response_count,test.dut.pages.fence_request_count,test.dut.pages.fence_ack_count,test.dut.pages.leases);
 end
endmodule
