`timescale 1ns/1ps
// Observes actual native exports. No payload RAM, persistence, or source data substitution.
module export_manifest #(parameter integer PATH_SLOTS=2,MAX_PATH=32)(
 input wire clk,rst,lease,arm,abort,source_write,published,
 input wire[63:0]active_design,target_generation,selected_design,selected_generation,
 input wire[31:0]target_checkpoint,active_version,active_sequence,selected_checkpoint,selected_version,
 input wire[1:0]active_query,selected_query,input wire[3:0]active_price,selected_price,input wire[PATH_SLOTS-1:0]active_slots,
 input wire owner_manifest,label_manifest,
 input wire label_accept,label_restore,label_done,input wire[1:0]label_query,input wire[3:0]label_price,label_status,
 input wire[31:0]label_count,label_crc,
 input wire path_accept,path_restore,path_done,path_word,input wire[3:0]path_status,
 input wire[31:0]path_index,path_data,path_crc,input wire path_last,
 input wire query_accept,query_restore,query_done,query_word,input wire[3:0]query_status,
 input wire[31:0]query_index,query_data,query_crc,input wire query_last,
 output reg owned,fault,output reg[2:0]receipts,
 output reg[31:0]saved_label_count,saved_label_crc,saved_path_crc,saved_query_crc,
 output wire manifest_ready
);
 reg[63:0]bound_design,generation;reg[31:0]checkpoint,version,sequence_floor;reg[1:0]query_epoch;reg[PATH_SLOTS-1:0]slots;reg[3:0]price;
 reg lp,pp,qp;reg[31:0]pn,qn,pc,qc;
 localparam PATH_STRIDE=7+MAX_PATH,PATH_WORDS=PATH_SLOTS*PATH_STRIDE;
 wire[31:0]path_slot=pn/PATH_STRIDE,path_field=pn%PATH_STRIDE;
 function automatic[31:0]fold(input[31:0]prev,value);reg[31:0]v;begin
  v=prev^value;for(integer b=0;b<32;b=b+1)v=v[0]?(v>>1)^32'hedb88320:v>>1;fold=v;
 end endfunction
 wire context_ok=active_design==bound_design&&active_version==version&&active_query==query_epoch&&active_price==price&&active_sequence==sequence_floor&&active_slots==slots;
 assign manifest_ready=owned&&!fault&&lease&&!abort&&!source_write&&context_ok&&receipts==7&&owner_manifest&&label_manifest&&
  selected_design==bound_design&&selected_generation==generation&&selected_checkpoint==checkpoint&&selected_version==version&&selected_query==query_epoch&&selected_price==price;
 always @(posedge clk)begin
  if(rst)begin
   owned<=0;fault<=0;receipts<=0;lp<=0;pp<=0;qp<=0;pn<=0;qn<=0;pc<=32'hffffffff;qc<=32'hffffffff;
   bound_design<=0;generation<=0;checkpoint<=0;version<=0;sequence_floor<=0;query_epoch<=0;price<=0;slots<=0;
   saved_label_count<=0;saved_label_crc<=0;saved_path_crc<=0;saved_query_crc<=0;
  end else begin
   if(arm)begin
    if(owned||!lease||abort||source_write)fault<=1;
    else begin
     owned<=1;fault<=0;receipts<=0;lp<=0;pp<=0;qp<=0;pn<=0;qn<=0;pc<=32'hffffffff;qc<=32'hffffffff;
     bound_design<=active_design;generation<=target_generation;checkpoint<=target_checkpoint;version<=active_version;
     sequence_floor<=active_sequence;query_epoch<=active_query;price<=active_price;slots<=active_slots;
    end
   end
   if(owned)begin
    if(!lease||abort||source_write||!context_ok)begin fault<=1;receipts<=0;end
    if(label_accept)begin
     if(lp||receipts[0]||label_restore||label_query!=query_epoch||label_price!=price)fault<=1;
     else lp<=1;
    end
    if(label_done)begin
     lp<=0;if(!lp||label_status!=0||label_count==0)fault<=1;
     else begin receipts[0]<=1;saved_label_count<=label_count;saved_label_crc<=label_crc;end
    end
    if(path_accept)begin if(pp||receipts[1]||path_restore)fault<=1;else pp<=1;end
    if(path_word)begin
     if(!pp||path_index!=pn||pn>=PATH_WORDS||path_last!=(pn==PATH_WORDS-1))fault<=1;
     if(path_slot<PATH_SLOTS)begin
      if((path_field==0&&path_data!={31'd0,slots[path_slot]})||
         (path_field==1&&slots[path_slot]&&(path_data==0||path_data>MAX_PATH))||
         (path_field==5&&slots[path_slot]&&path_data!=bound_design[31:0])||
         (path_field==6&&slots[path_slot]&&path_data!=bound_design[63:32]))fault<=1;
     end
     pc<=fold(pc,path_data);pn<=pn+1;
    end
    if(path_done)begin
     pp<=0;if(!pp||path_status!=0||pn!=PATH_WORDS||path_crc!=~pc)fault<=1;
     else begin receipts[1]<=1;saved_path_crc<=path_crc;end
    end
    if(query_accept)begin if(qp||receipts[2]||query_restore)fault<=1;else qp<=1;end
    if(query_word)begin
     if(!qp||query_index!=qn||qn>=10||query_last!=(qn==9))fault<=1;
     case(qn)
      0:if(query_data!=32'h51435031)fault<=1;
      1:if(query_data!=1)fault<=1;
      2:if(query_data!=bound_design[31:0])fault<=1;
      3:if(query_data!=bound_design[63:32])fault<=1;
      4:if(query_data!=generation[31:0])fault<=1;
      5:if(query_data!=generation[63:32])fault<=1;
      6:if(query_data!=version)fault<=1;
      7:if(query_data!={25'd0,1'b1,price,query_epoch})fault<=1;
      8:if(query_data!=sequence_floor)fault<=1;
      9:if(query_data!=0)fault<=1;
     endcase
     qc<=fold(qc,query_data);qn<=qn+1;
    end
    if(query_done)begin
     qp<=0;if(!qp||query_status!=0||qn!=10||query_crc!=~qc)fault<=1;
     else begin receipts[2]<=1;saved_query_crc<=query_crc;end
    end
    if(published)begin if(!manifest_ready)fault<=1;owned<=0;end
   end
  end
 end
endmodule
