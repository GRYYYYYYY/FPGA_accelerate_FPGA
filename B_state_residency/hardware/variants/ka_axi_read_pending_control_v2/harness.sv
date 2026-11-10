module ka_axi_read_pending_control(input wire clk);
(* anyseq *) reg rst, arvalid, rready, hold_r;
wire [7:0] arlen=0;
localparam READ_DELAY=0;
reg [31:0] rng=32'hc7aa4813;
reg rp=0, rvalid, rlast, read_pending;
integer rdlen=0, rdpos=0, delay_r=0;
wire arready;
assign arready=!rst&&!rp&&!rvalid&&rng[2:0]!=0;
wire m_arvalid=arvalid,m_arready=arready,m_rvalid=rvalid,m_rready=rready,m_rlast=rlast;
 always @(posedge clk)begin
  if(rst)read_pending<=0;
  else begin
   if(m_arvalid&&m_arready)read_pending<=1;
   if(m_rvalid&&m_rready&&m_rlast)read_pending<=0;
  end
 end

always @(posedge clk) begin
 rng<={rng[30:0],rng[31]^rng[21]^rng[1]^rng[0]};
 if(rst) begin rp<=0;rvalid<=0;rlast<=0;rdpos<=0;delay_r<=0;end
 else begin
  if(arvalid&&arready)begin rdlen<=arlen+1;rdpos<=0;rp<=1;delay_r<=rng[12:9]+READ_DELAY; end
  if(rp&&!rvalid)begin
   if(hold_r===1'b1)begin end
   else if(delay_r!=0)delay_r<=delay_r-1;
   else begin rlast<=rdpos==rdlen-1;rvalid<=1; end
  end
  if(rvalid&&rready)begin
   rvalid<=0;
   if(rdpos==rdlen-1)rp<=0;else begin rdpos<=rdpos+1;delay_r<=rng[12:9];end
  end
 end
end
reg past_valid=0;
initial assume(rst);
always @(posedge clk) begin
 past_valid<=1;
 if(past_valid && !rst) begin
  assert(rp==read_pending);
  if(rp) assert(rdlen==1 && rdpos==0);
  if(rvalid) assert(rp && rlast);
  if(!read_pending) assert(!rvalid);
 end
 cover(past_valid && !rst && rvalid && rready && read_pending);
 cover(past_valid && !rst && $past(!rst && rvalid && rready) && !read_pending && !rvalid);
end
endmodule
