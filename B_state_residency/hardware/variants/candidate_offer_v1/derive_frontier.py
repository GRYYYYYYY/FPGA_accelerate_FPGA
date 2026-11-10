from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def derive(s):
 s=s.replace('module query_frontier(','module query_frontier_offer(',1)
 ports=''' input wire [63:0] design_id,
 input wire offer_valid,output wire offer_ready,input wire [31:0] offer_key,offer_id,offer_cookie,offer_version,input wire [63:0] offer_design,input wire [1:0] offer_query,input wire [3:0] offer_price,
 output wire offer_rsp_valid,input wire offer_rsp_ready,output wire [31:0] offer_rsp_status,offer_rsp_cookie,offer_rsp_size,offer_rsp_version,output wire [63:0] offer_rsp_design,output wire [1:0] offer_rsp_query,output wire [3:0] offer_rsp_price,
 output wire [31:0] seed_rsp_key,seed_rsp_id,
'''
 s=s.replace(' input wire clk,rst,',ports+' input wire clk,rst,',1)
 s=s.replace('reg [1:0] control;', 'reg [63:0] held_design,owned_offer_design;reg [31:0] owned_offer_version;reg offer_pending;\n reg [1:0] control;',1)
 s=s.replace('wire [2:0] rv,rr,sv,sr;wire [401:0] rd;wire [497:0] sd;', 'wire [3:0] rv,rr,sv,sr;wire [535:0] rd;wire [663:0] sd;',1)
 s=s.replace('held_version==version;', 'held_version==version&&held_design==design_id;',1)
 s=s.replace('held_version!=version);', 'held_version!=version||held_design!=design_id);',1)
 s=s.replace('control!=0||arb_busy||fs_busy||fault', 'control!=0||arb_busy||fs_busy||offer_pending||fault',1)
 s=s.replace('(seed_op==1||seed_op==3)', '(seed_op==1||seed_op==2||seed_op==3)',1)
 s=s.replace(' assign {fs_req_op,', ''' assign seed_rsp_key=seed_key_out;assign seed_rsp_id=seed_id_out;
 wire offer_permit=matching&&decision_lock&&!closing&&control==0&&offer_version==version&&offer_design==design_id&&offer_query==query_id&&offer_price==price&&!fault;
 assign rv[3]=offer_valid&&offer_permit;assign offer_ready=rr[3]&&offer_permit;
 assign rd[402+:134]={32'd1,offer_key,offer_id,offer_cookie,offer_query,offer_price};
 wire [31:0] offer_unused_key,offer_unused_id;
 assign offer_rsp_valid=sv[3];assign sr[3]=offer_rsp_ready;
 assign {offer_rsp_status,offer_unused_key,offer_unused_id,offer_rsp_size,offer_rsp_cookie,offer_rsp_query,offer_rsp_price}=sd[498+:166];
 assign offer_rsp_version=owned_offer_version;assign offer_rsp_design=owned_offer_design;
 always @(posedge clk)begin
  if(rst)begin offer_pending<=0;owned_offer_version<=0;owned_offer_design<=0;end
  else begin
   if(sv[3]&&sr[3])offer_pending<=0;
   if(rv[3]&&rr[3])begin offer_pending<=1;owned_offer_version<=offer_version;owned_offer_design<=offer_design;end
  end
 end
 assign {fs_req_op,''',1)
 s=s.replace('.CLIENTS(3),.REQUEST_BITS(134)', '.CLIENTS(4),.REQUEST_BITS(134)',1)
 s=s.replace('held_version<=0;end','held_version<=0;held_design<=0;end',1)
 s=s.replace('held_version<=version;control<=1;', 'held_version<=version;held_design<=design_id;control<=1;',1)
 return s
if __name__=='__main__':Path(__file__).with_name('query_frontier_offer.sv').write_text(derive((ROOT/'hardware/variants/candidate_postprev_v1/query_frontier.sv').read_text()))
