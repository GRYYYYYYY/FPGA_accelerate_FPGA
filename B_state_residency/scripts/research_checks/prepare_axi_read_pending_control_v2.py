"""Explicit source-reviewed control projection of current single-beat fixture."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');S=B/'stage_static_cp_shadow_system_v6/sources';p=B/'ka_axi_read_pending_control_v2';assert not p.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=(S/'axi_file_memory.sv').read_text();r=(S/'checkpoint_authority_reader.sv').read_text();tb=(S/'tb_query_fault.sv').read_text()
fragments=['assign arready=!rst&&!rp&&!rvalid&&rng[2:0]!=0;',"rng<={rng[30:0],rng[31]^rng[21]^rng[1]^rng[0]};",'rdlen<=arlen+1;rdpos<=0;rp<=1;delay_r<=rng[12:9]+READ_DELAY;','if(hold_r===1\'b1)begin end','else if(delay_r!=0)delay_r<=delay_r-1;','rlast<=rdpos==rdlen-1;rvalid<=1;','if(rdpos==rdlen-1)rp<=0;else begin rdpos<=rdpos+1;delay_r<=rng[12:9];end']
for f in fragments:assert f in m
block=r[r.index(' always @(posedge clk)begin\n  if(rst)read_pending<=0;'):r.index(' always @(posedge clk)begin\n  if(rst)begin')]
assert 'if(m_arvalid&&m_arready)read_pending<=1;' in block and 'if(m_rvalid&&m_rready&&m_rlast)read_pending<=0;' in block
assert 'READ_ONLY(1),.MAX_BEATS(1),.TAG("snapshot")) authority_memory' in tb
store=S/'access_owner_v3_20261024/owners/owner_state_store.sv';assert 'assign m_arlen=0;' in store.read_text()
text='''module ka_axi_read_pending_control(input wire clk);
(* anyseq *) reg rst, arvalid, rready, hold_r;
wire [7:0] arlen=0;
localparam READ_DELAY=0;
reg [31:0] rng=32'hc7aa4813;
reg rp=0, rvalid, rlast, read_pending;
integer rdlen=0, rdpos=0, delay_r=0;
wire arready;
'''+fragments[0]+'''
wire m_arvalid=arvalid,m_arready=arready,m_rvalid=rvalid,m_rready=rready,m_rlast=rlast;
'''+block+'''
always @(posedge clk) begin
 '''+fragments[1]+'''
 if(rst) begin rp<=0;rvalid<=0;rlast<=0;rdpos<=0;delay_r<=0;end
 else begin
  if(arvalid&&arready)begin '''+fragments[2]+''' end
  if(rp&&!rvalid)begin
   '''+fragments[3]+'''
   '''+fragments[4]+'''
   else begin '''+fragments[5]+''' end
  end
  if(rvalid&&rready)begin
   rvalid<=0;
   '''+fragments[6]+'''
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
'''
p.mkdir();(p/'harness.sv').write_text(text);(R/'hardware/variants/ka_axi_read_pending_control_v2/harness.sv').write_text(text)
receipt={'status':'prepared_source_reviewed_control_projection_not_full_rtl','source_sha256':{str(x):sha(x) for x in [S/'axi_file_memory.sv',S/'checkpoint_authority_reader.sv',S/'tb_query_fault.sv',store]},'checked_memory_fragments':fragments,'reader_process':block,'harness_sha256':sha(p/'harness.sv'),'limits':['Explicit control projection, not automatic full file equivalence. File I/O, data/status and fatal shape checks removed; legal arlen=0 bound to actual store and MAX_BEATS1 fixture.','Only one reader sharing reset with memory; private bank reset and mux not represented.','Not arbitrary AXI environment or full-system gate acceptance.'],'full_system_functional_netlist_validated':False,'physical_gate_open':False};(p/'projection.json').write_text(json.dumps(receipt,indent=2)+'\n');print(p)
