`timescale 1ns/1ps
module tb_watchdog_width;
  reg old_seen=0, sized_seen=0;
  localparam time CORRECT_DELAY=64'd500000000000;
  initial begin
    #500000000000;
    if($time!==64'd1783793664)$fatal(1,"old truncation not reproduced");
    old_seen=1;$display("OLD_DELAY_REPRODUCED ns=%0d",$time);
  end
  initial begin
    #(64'd500000000000);
    if($time!==CORRECT_DELAY || !old_seen)$fatal(1,"sized delay incorrect");
    sized_seen=1;$display("SIZED_DELAY_PASS ns=%0d",$time);
  end
  initial begin
    #(CORRECT_DELAY);#1;
    if(!sized_seen || $time!==64'd500000000001)$fatal(1,"time parameter incorrect");
    $display("TEST_PASS watchdog_width");$finish;
  end
endmodule
