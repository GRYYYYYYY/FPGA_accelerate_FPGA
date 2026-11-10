`timescale 1ns/1ps
// Behavioral contract for the UNMODIFIED installed2022.2 BUFCE primitives.
// This is zero-SDF primitive testing, not timing signoff or a device tie-off proof.
module clock_semantics_case #(
  parameter integer ID=0, LEAF=0, ASYNC=0, INV_CE=0, INV_I=0
)(output reg done=0);
  reg ce=INV_CE, i=INV_I;
  wire o;
  integer checks=0;
  generate if (LEAF) begin
    BUFCE_LEAF #(.CE_TYPE(ASYNC ? "ASYNC" : "SYNC"),
                 .IS_CE_INVERTED(INV_CE), .IS_I_INVERTED(INV_I)) dut(.CE(ce), .I(i), .O(o));
  end else begin
    BUFCE_ROW #(.CE_TYPE(ASYNC ? "ASYNC" : "SYNC"),
                .IS_CE_INVERTED(INV_CE), .IS_I_INVERTED(INV_I)) dut(.CE(ce), .I(i), .O(o));
  end endgenerate

  task automatic sample(input integer phase, input logic expected);
    #5;
    if (o !== expected) $fatal(1,"CLOCK_FAIL id=%0d phase=%0d i=%b ce=%b expected=%b actual=%b",ID,phase,i,ce,expected,o);
    checks=checks+1;
    $display("CLOCK_SAMPLE id=%0d phase=%0d i=%b ce=%b expected=%b actual=%b",ID,phase,i,ce,expected,o);
  endtask

  initial begin
    #150; // Installed glbl releases GSR at100ns; input/attribute initialization has settled.
    i=INV_I; ce=INV_CE; sample(0,0);
    ce=1^INV_CE; sample(1,0);           // Enable can update while effective I=0.
    i=1^INV_I; sample(2,1);            // Both gate modes pass effective I.
    ce=INV_CE; sample(3,ASYNC ? 0:1);  // SYNC must retain high-phase enable state.
    i=INV_I; sample(4,0);
    i=1^INV_I; sample(5,0);            // Disabled clock remains blocked.
    ce=1^INV_CE; sample(6,ASYNC ? 1:0);// CE-as-data follows only in ASYNC at I=1.
    i=INV_I; sample(7,0);
    i=1^INV_I; sample(8,1);
    i=INV_I; ce=INV_CE; sample(9,0);
    ce=1'bz; sample(10,0);             // Library Z default is a simulation rule only.
    i=1^INV_I; sample(11,1);
    if (checks != 12) $fatal(1,"Incomplete clock case");
    $display("CLOCK_CASE_PASS id=%0d leaf=%0d async=%0d inv_ce=%0d inv_i=%0d checks=%0d",ID,LEAF,ASYNC,INV_CE,INV_I,checks);
    done=1;
  end
endmodule

module tb_clock_primitive_semantics;
  wire [15:0] done;
  generate
    for(genvar leaf=0;leaf<2;leaf=leaf+1) begin:g_leaf
      for(genvar mode=0;mode<2;mode=mode+1) begin:g_mode
        for(genvar ceinv=0;ceinv<2;ceinv=ceinv+1) begin:g_ceinv
          for(genvar iinv=0;iinv<2;iinv=iinv+1) begin:g_iinv
            localparam integer ID=leaf*8+mode*4+ceinv*2+iinv;
            clock_semantics_case #(.ID(ID),.LEAF(leaf),.ASYNC(mode),.INV_CE(ceinv),.INV_I(iinv)) checked(.done(done[ID]));
          end
        end
      end
    end
  endgenerate
  initial begin
    wait (&done);
    $display("TEST_PASS clock_primitive_semantics cases=16 samples=192");
    $finish;
  end
  initial begin
    #1000;
    $fatal(1,"CLOCK_TIMEOUT done=%h",done);
  end
endmodule
