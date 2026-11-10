module udev_route_probe_v1(input clk, input reset, input [7:0] data, output reg [7:0] q);
  always @(posedge clk) begin
    if (reset) q <= 8'h00;
    else q <= q + data;
  end
endmodule
