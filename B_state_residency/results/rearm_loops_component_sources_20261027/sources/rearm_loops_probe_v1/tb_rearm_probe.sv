`timescale 1ns/1ps
module tb_rearm_probe;
 tb_rearm_loop t();
 always #500 $display("DBG t=%0t ks=%0d ls=%0d cfg=%b/%b/%b rec=%b/%b lbl=%b/%b/%b lr=%b/%b/%h safe=%b nr=%b fault=%b started=%b",$time,t.dut.k.state,t.dut.l.state,t.k_cfg_valid,t.k_cfg_ready,t.k_cfg_rsp_valid,t.k_recover_valid,t.k_recover_ready,t.k_labels_valid,t.l_start_offer,t.l_start_ready,t.l_rsp_valid,t.l_rsp_ready,t.l_rsp_status,t.external_safe,t.external_normal_retired,t.k_fault,t.started);
 initial begin #10000;$display("PROBE_DONE");$finish;end
endmodule
