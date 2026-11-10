// Placed-netlist workload around the unchanged RouterAcc cost_calculator.
// This is a routing integration workload, not the graph-compression accelerator.
module routeracc_cost_registered (
    input wire clk, reset, valid,
    input wire [47:0] per_x, per_y,
    input wire [17:0] per_z,
    input wire [7:0] end_x, end_y, cen_x, cen_y,
    input wire [2:0] end_z, cen_z,
    input wire [13:0] cen_g,
    output reg [95:0] f_out,
    output reg [83:0] g_out,
    output reg valid_out
);
    wire clk_global;
    BUFG clock_buffer(.I(clk), .O(clk_global));
    reg reset_q, valid_q;
    reg [47:0] px_q, py_q;
    reg [17:0] pz_q;
    reg [7:0] ex_q, ey_q, cx_q, cy_q;
    reg [2:0] ez_q, cz_q;
    reg [13:0] cg_q;
    wire [95:0] f;
    wire [83:0] g;
    wire cost_valid;
    always @(posedge clk_global) begin
        reset_q <= reset; valid_q <= valid;
        px_q <= per_x; py_q <= per_y; pz_q <= per_z;
        ex_q <= end_x; ey_q <= end_y; ez_q <= end_z;
        cx_q <= cen_x; cy_q <= cen_y; cz_q <= cen_z;
        cg_q <= cen_g;
        f_out <= f; g_out <= g; valid_out <= cost_valid;
    end
    cost_calculator #(.DIMENSION(6), .X_DW(8), .Y_DW(8), .Z_DW(3),
        .H_DW(14), .G_DW(14), .F_DW(16)) original_cost (
        .f_val(f), .g_val(g), .cost_vld(cost_valid),
        .per_x(px_q), .per_y(py_q), .per_z(pz_q),
        .end_x(ex_q), .end_y(ey_q), .end_z(ez_q),
        .cen_x(cx_q), .cen_y(cy_q), .cen_z(cz_q), .cen_g_val(cg_q),
        .din_vld(valid_q), .clk(clk_global), .reset(reset_q)
    );
endmodule
