// Simulation-only checks around an unchanged generated HLS AXI memory model.
// The model indexes cells by floor(byte_address / 2**AxSIZE); validate that
// exact index domain, including narrow/unaligned requests, before forwarding.
module a_axi_model_rebase_guard_v1 #(
    parameter [63:0] BASE = 64'd4096,
    parameter [63:0] DEPTH = 64'd1,
    parameter integer DATA_BITS = 64,
    parameter NAME = "axi"
)(
    input clk,
    input awvalid, awready,
    input [63:0] awaddr,
    input [7:0] awlen,
    input [2:0] awsize,
    input [1:0] awburst,
    input arvalid, arready,
    input [63:0] araddr,
    input [7:0] arlen,
    input [2:0] arsize,
    input [1:0] arburst
);
localparam [64:0] MAX_ADDRESS = 65'h0ffffffffffffffff;
initial begin
    if (BASE == 0 || BASE[11:0] != 0 || DEPTH == 0 ||
        !(DATA_BITS == 32 || DATA_BITS == 64 || DATA_BITS == 128 ||
          DATA_BITS == 256 || DATA_BITS == 512) ||
        ({1'b0, BASE} + {1'b0, DEPTH} * (DATA_BITS/8) - 1) > MAX_ADDRESS)
        $fatal(1, "A_REBASE_CONFIGURATION %s", NAME);
end
task automatic check_request;
    input [63:0] address;
    input [7:0] length;
    input [2:0] size;
    input [1:0] burst;
    input write_request;
    reg [64:0] offset, last_index, last_byte;
    begin
        if ((^{address, length, size, burst}) === 1'bx)
            $fatal(1, "A_REBASE_UNKNOWN %s write=%b", NAME, write_request);
        if (address < BASE)
            $fatal(1, "A_REBASE_BELOW_BASE %s write=%b", NAME, write_request);
        if (burst != 0 && burst != 1)
            $fatal(1, "A_REBASE_BURST %s write=%b", NAME, write_request);
        if ((65'd1 << size) > DATA_BITS/8)
            $fatal(1, "A_REBASE_SIZE %s write=%b", NAME, write_request);
        offset = {1'b0, address} - {1'b0, BASE};
        last_index = offset >> size;
        if (burst == 1) last_index = last_index + {57'd0, length};
        if (last_index >= {1'b0, DEPTH})
            $fatal(1, "A_REBASE_MODEL_RANGE %s write=%b", NAME, write_request);
        last_byte = ((last_index + 1) << size) - 1;
        if ({1'b0, BASE} + last_byte > MAX_ADDRESS)
            $fatal(1, "A_REBASE_OVERFLOW %s write=%b", NAME, write_request);
        if ((offset >> 12) != (last_byte >> 12))
            $fatal(1, "A_REBASE_4K %s write=%b", NAME, write_request);
    end
endtask
always @(posedge clk) begin
    if (awvalid === 1'b1 && awready === 1'b1)
        check_request(awaddr, awlen, awsize, awburst, 1'b1);
    if (arvalid === 1'b1 && arready === 1'b1)
        check_request(araddr, arlen, arsize, arburst, 1'b0);
end
endmodule
