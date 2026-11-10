`timescale 1ns/1ps
// Captures an entire real expander operation before exposing children.
// The enclosing query owner must fence host/config mutations while depth!=0.
module expansion_capture #(parameter integer DEPTH=64,CAPACITY=256)(
 input wire clk,rst,abort,
 input wire expand_valid,output wire expand_ready,
 input wire[31:0]expand_cookie,expand_parent,expand_prune,expand_has_laguna,
 input wire[511:0]expand_context,output wire[511:0]out_context,
 output wire out_valid,input wire out_ready,output wire[31:0]out_node,out_position,out_sequence,output wire[255:0]out_attrs,
 output wire result_valid,input wire result_ready,output wire[3:0]result_status,
 output wire[31:0]result_detail,result_cookie,result_count,result_raw_count,result_mask,output wire result_hit,
 output wire busy,output wire fault,output wire[31:0]depth,
 output wire e_expand_valid,input wire e_expand_ready,output wire[31:0]e_expand_cookie,e_expand_parent,e_expand_prune,e_expand_has_laguna,
 input wire e_out_valid,output wire e_out_ready,input wire[31:0]e_out_node,e_out_position,e_out_sequence,input wire[255:0]e_out_attrs,
 input wire e_result_valid,output wire e_result_ready,input wire[3:0]e_result_status,
 input wire[31:0]e_result_detail,e_result_cookie,e_result_count,e_result_raw_count,e_result_mask,input wire e_result_hit
);
 reg[1:0]state; // 0 quiescent; 1 exposed request; 2 physical operation
 reg[31:0]cookie,parent,prune,laguna,received;
 reg[164:0]results[0:DEPTH-1];
 reg protocol_fault,result_offered;
 wire begin_ready,capturing,frame_fault,frame_valid,frame_done,pop_ready;
 wire[3:0]frame_error;wire[351:0]item_record;
 wire accept=expand_valid&&expand_ready;
 wire unexpected=(e_out_valid||e_result_valid)&&state!=2;
 wire bad_child=e_out_valid&&state==2&&e_out_sequence!=received;
 wire bad_result=e_result_valid&&state==2&&(e_result_cookie!=cookie||e_result_count!=received);
 assign fault=frame_fault||protocol_fault;
 assign busy=depth!=0||state!=0||fault;
 assign expand_ready=begin_ready&&state==0&&!result_ready&&!result_offered;
 wire finish=e_result_valid&&state==2;
 children_frames #(.DEPTH(DEPTH),.CAPACITY(CAPACITY),.CONTEXT_BITS(512)) frames(
 .clk(clk),.rst(rst),.abort(abort||protocol_fault||bad_child||bad_result||unexpected),
 .begin_valid(expand_valid&&state==0&&!result_ready&&!result_offered),.begin_ready(begin_ready),.begin_context(expand_context),
 .child_valid(e_out_valid&&state==2),.child_ready(e_out_ready),.child_record({e_out_node,e_out_position,e_out_sequence,e_out_attrs}),
 .finish_valid(finish),.finish_ready(e_result_ready),.finish_status(e_result_status),.finish_count(e_result_count),
 .capture_active(capturing),.fault(frame_fault),.error_code(frame_error),.depth(depth),
 .frame_valid(frame_valid),.frame_context(out_context),.item_valid(out_valid),.item_ready(out_ready),.item_record(item_record),
 // pop_ready already qualifies frame_done. Supplying the independent
 // consumer intent avoids frame_done -> pop_valid -> begin_ready -> push
 // -> frame_done feedback; the actual pop handshake is unchanged.
 .frame_done(frame_done),.pop_valid(result_ready&&state==0&&(fault||!expand_valid||result_offered)),.pop_ready(pop_ready));
 assign {out_node,out_position,out_sequence,out_attrs}=item_record;
 assign result_valid=frame_done&&state==0&&(fault||!expand_valid||result_offered);
 wire[164:0] saved_result=depth!=0?results[depth-1]:165'b0;
 wire[164:0] corrected_result={((fault&&saved_result[164:161]==0)?4'd4:saved_result[164:161]),saved_result[160:0]};
 reg[164:0] offered_result;
 assign {result_status,result_detail,result_cookie,result_count,result_raw_count,result_mask,result_hit}=result_offered?offered_result:corrected_result;
 always @(posedge clk)begin
  if(rst)offered_result<=0;
  else if(result_valid&&!result_offered)offered_result<=corrected_result;
 end
 assign e_expand_valid=!rst&&state==1;
 assign e_expand_cookie=cookie;assign e_expand_parent=parent;assign e_expand_prune=prune;assign e_expand_has_laguna=laguna;
 always @(posedge clk)begin
  if(rst)begin state<=0;cookie<=0;parent<=0;prune<=0;laguna<=0;received<=0;protocol_fault<=0;result_offered<=0;end
  else begin
   if(result_valid)result_offered<=!result_ready;
   if(accept)begin
    cookie<=expand_cookie;parent<=expand_parent;prune<=expand_prune;laguna<=expand_has_laguna;received<=0;
    if(depth<DEPTH)begin state<=1;results[depth]<={4'd4,32'd0,expand_cookie,32'd0,32'd0,32'd0,1'b0};end
   end
   if(e_expand_valid&&e_expand_ready)state<=2;
   if(e_out_valid&&e_out_ready)received<=received+1;
   if(e_result_valid&&e_result_ready)begin
    results[depth-1]<={e_result_status,e_result_detail,cookie,e_result_count,e_result_raw_count,e_result_mask,e_result_hit};state<=0;
   end
   if(unexpected||bad_child||bad_result)protocol_fault<=1;
  end
 end
endmodule
