`timescale 1ns/1ps
module boot_restore_gate(
 input wire clk,cold_rst,work_rst,required,
 input wire cfg_valid,output wire cfg_ready,input wire[63:0]cfg_design,cfg_generation,
 input wire[31:0]cfg_checkpoint,cfg_version,cfg_nodes,cfg_label_count,cfg_label_crc,cfg_path_crc,cfg_query_crc,
 input wire[1:0]cfg_query,cfg_slots,input wire[3:0]cfg_price,input wire[2303:0]cfg_payload,
 output wire pending,admin_allowed,done_held,output wire rsp_valid,input wire rsp_ready,output wire[3:0]rsp_status,
 output wire[4:0]receipts,output wire[7:0]config_receipts,
 input wire verify_valid,output wire verify_ready,output reg[31:0]verified_count,output reg[3:0]verify_status,
 input wire[15:0]sv,sr,srv,srr,input wire[38911:0]sp,input wire[4095:0]rp,
 input wire owner_configured,authority_configured,input wire[63:0]authority_design,authority_generation,input wire[31:0]authority_checkpoint,
 input wire providers_configured,active,input wire[63:0]active_design,input wire[31:0]active_version,published_version,
 input wire[1:0]active_query,route_slots,input wire[3:0]active_price,input wire recovery_permit,input wire[63:0]recovery_design,input wire[31:0]recovery_checkpoint,
 input wire path_accept,path_restore,path_done,input wire[3:0]path_status,input wire[31:0]path_crc,
 input wire query_accept,query_restore,query_done,input wire[3:0]query_status,input wire[31:0]query_crc,
 input wire retired,lease_owned
);
 localparam RUN=0,WAIT_CFG=1,RESTORE=2,BAD_CFG=3,DONE=4;
 reg[2:0]state;reg[63:0]bound_design,generation;reg[31:0]checkpoint,version,nodes,label_count,label_crc,wanted_path_crc,wanted_query_crc;
 reg[1:0]query,slots;reg[3:0]price;reg[2303:0]descriptor;
 reg[7:0]configured;reg cfg_owned,cfg_match;reg[3:0]cfg_lane;
 reg labels_ok,path_ok,query_ok,path_importing,query_importing,verifying,read_owned;
 reg[31:0]crc,last_node,read_node;
 wire reset=cold_rst||work_rst;
 wire owner_ok=authority_configured&&owner_configured&&authority_design==bound_design&&authority_generation==generation&&authority_checkpoint==checkpoint;
 wire context_ok=providers_configured&&active&&active_design==bound_design&&active_version==version&&published_version==version&&active_query==query&&active_price==price&&recovery_permit&&recovery_design==bound_design&&recovery_checkpoint==checkpoint;
 assign pending=state!=RUN;
 assign admin_allowed=!reset&&state==RESTORE;
 assign done_held=state==DONE||state==BAD_CFG;
 assign cfg_ready=!reset&&state==WAIT_CFG;
 assign rsp_valid=!reset&&(state==DONE||state==BAD_CFG);
 assign rsp_status=state==BAD_CFG?4'd1:4'd0;
 assign receipts={query_ok,path_ok,labels_ok,context_ok&&(&configured),owner_ok};
 assign config_receipts=configured;
 assign verify_ready=!reset&&state==RESTORE&&!verifying&&!read_owned&&context_ok&&(&configured)&&owner_ok;
 function automatic[31:0]word_crc(input[31:0]old_crc,w);reg[31:0]v;begin v=old_crc^w;for(integer k=0;k<32;k=k+1)v=v[0]?(v>>1)^32'hedb88320:v>>1;word_crc=v;end endfunction
 function automatic[31:0]row_crc(input[31:0]old_crc,input[191:0]row);reg[31:0]v;begin v=old_crc;for(integer k=0;k<6;k=k+1)v=word_crc(v,row[32*k+:32]);row_crc=v;end endfunction
 wire[15:0]requests=sv&sr;
 wire invalidating=|(requests&16'hc07f);
 wire label_write=requests[8]&&sp[19456];
 wire read_request=requests[8]&&!sp[19456]&&sp[19521+:3]==0;
 wire read_reply=srv[8]&&srr[8];
 wire[31:0]next_crc=row_crc(crc,{rp[2053+:160],read_node});
 integer i;
 always @(posedge clk)begin
  if(cold_rst)begin
   state<=required?WAIT_CFG:RUN;bound_design<=0;generation<=0;checkpoint<=0;version<=0;nodes<=0;label_count<=0;label_crc<=0;wanted_path_crc<=0;wanted_query_crc<=0;query<=0;slots<=0;price<=0;descriptor<=0;
   configured<=0;cfg_owned<=0;cfg_match<=0;cfg_lane<=0;labels_ok<=0;path_ok<=0;query_ok<=0;path_importing<=0;query_importing<=0;verifying<=0;read_owned<=0;verified_count<=0;verify_status<=0;crc<=32'hffffffff;last_node<=0;read_node<=0;
  end else if(work_rst&&state!=RUN)begin
   // A work reset during bootstrap invalidates every receipt; never opens RUN.
   state<=WAIT_CFG;configured<=0;cfg_owned<=0;labels_ok<=0;path_ok<=0;query_ok<=0;path_importing<=0;query_importing<=0;verifying<=0;read_owned<=0;verified_count<=0;
  end else if(!work_rst)begin
   case(state)
    WAIT_CFG:if(cfg_valid&&cfg_ready)begin
     if(cfg_design==0||cfg_generation==0||cfg_checkpoint==0||cfg_version==0||cfg_nodes==0||cfg_label_count>cfg_nodes||cfg_price!=cfg_version[3:0]||(cfg_label_count==0&&cfg_label_crc!=0))state<=BAD_CFG;
     else begin
      bound_design<=cfg_design;generation<=cfg_generation;checkpoint<=cfg_checkpoint;version<=cfg_version;nodes<=cfg_nodes;label_count<=cfg_label_count;label_crc<=cfg_label_crc;wanted_path_crc<=cfg_path_crc;wanted_query_crc<=cfg_query_crc;query<=cfg_query;slots<=cfg_slots;price<=cfg_price;descriptor<=cfg_payload;
      configured<=0;labels_ok<=cfg_label_count==0;path_ok<=0;query_ok<=0;state<=RESTORE;
     end
    end
    BAD_CFG:if(rsp_ready)state<=WAIT_CFG;
    RESTORE:begin
     // All six endpoint configurations, coordinator config and saved descriptor
     // must be real successful front-end transactions matching this descriptor.
     for(i=0;i<16;i=i+1)begin
      if(requests[i]&&(i<6||i==14||i==15))begin
       cfg_owned<=1;cfg_lane<=i;configured[i<6?i:i==15?6:7]<=0;
       if(i<6)cfg_match<=sp[i*2432+:384]==descriptor[i*384+:384]&&sp[i*2432+384+:2048]==0;
       else if(i==14)cfg_match<=sp[34048]&&sp[34049+:64]==bound_design&&sp[34113+:32]==checkpoint&&sp[34145+:32]==version&&sp[34177+:2]==query&&sp[34179+:4]==price&&sp[34183+:2297]==0;
       else cfg_match<=sp[36480+:2304]==descriptor&&sp[38784+:64]==bound_design&&sp[38848+:32]==checkpoint&&sp[38880]&&sp[38881+:31]==0;
      end
     end
     if(cfg_owned&&srv[cfg_lane]&&srr[cfg_lane])begin
      cfg_owned<=0;configured[cfg_lane<6?cfg_lane:cfg_lane==15?6:7]<=cfg_match&&(cfg_lane>=14?rp[cfg_lane*256+:1]==0:rp[cfg_lane*256+:3]==0);
     end
     if(invalidating)begin labels_ok<=label_count==0;path_ok<=0;query_ok<=0;verifying<=0;verified_count<=0;end
     if(label_write)begin labels_ok<=0;verifying<=0;verified_count<=0;end
     if(verify_valid&&verify_ready)begin
      verifying<=label_count!=0;read_owned<=0;verified_count<=0;verify_status<=0;crc<=32'hffffffff;last_node<=0;labels_ok<=label_count==0;
     end
     if(verifying&&read_request)begin read_owned<=1;read_node<=sp[19457+:32];end
     if(verifying&&read_owned&&read_reply)begin
      read_owned<=0;
      if(rp[2048+:4]!=0||!rp[2052]||read_node>=nodes||(verified_count!=0&&read_node<=last_node))begin verifying<=0;labels_ok<=0;verify_status<=1;end
      else begin
       last_node<=read_node;crc<=next_crc;verified_count<=verified_count+1;
       if(verified_count+1==label_count)begin verifying<=0;labels_ok<=~next_crc==label_crc;verify_status<=~next_crc==label_crc?0:2;end
      end
     end
     if(path_accept)begin path_importing<=path_restore;if(path_restore)path_ok<=0;end
     if(path_done&&path_importing)begin path_importing<=0;path_ok<=path_status==0&&path_crc==wanted_path_crc&&route_slots==slots;end
     if(query_accept)begin query_importing<=query_restore;if(query_restore)query_ok<=0;end
     if(query_done&&query_importing)begin query_importing<=0;query_ok<=query_status==0&&query_crc==wanted_query_crc;end
     // Mutations have final priority over concurrent completion replies.
     // In-flight imports started before mutation must not earn fresh receipts.
     if(invalidating||label_write)begin
      labels_ok<=!label_write&&label_count==0;path_ok<=0;query_ok<=0;
      path_importing<=0;query_importing<=0;verifying<=0;read_owned<=0;verified_count<=0;
     end
     if((&receipts)&&retired&&lease_owned&&!cfg_owned&&!read_owned&&!verifying&&!invalidating&&!label_write)state<=DONE;
    end
    DONE:if(rsp_ready)state<=RUN;
    default:begin end
   endcase
  end
 end
endmodule
