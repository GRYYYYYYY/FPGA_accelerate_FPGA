`timescale 1ns/1ps
// Cumulative dirty-line snapshot relative to an externally cloned immutable baseline.
// Single outstanding source writer; addresses are captured from actual AW handshakes.
module cumulative_owner_snapshot #(parameter integer MAX_DIRTY=64)(
 input wire clk,rst,lease,source_drained,source_healthy,source_protocol_ok,
 input wire[1:0]cmd_op, // 0 bind once before source writes; 1 clear data error only; 2 copy
 input wire[63:0]cmd_design,cmd_baseline,cmd_generation,cmd_checkpoint,
 input wire[63:0]bank0_base,bank1_base,active_destination,active_generation,
 input wire[3:0]obs_bid,obs_awid,input wire[2:0]obs_awsize,input wire[1:0]obs_awburst,
 output reg bound,data_error,coverage_error,
 output reg[63:0]generation_floor,checkpoint_floor,
 output reg[63:0]receipt_design,receipt_baseline,receipt_generation,receipt_checkpoint,receipt_destination,
 input wire[63:0]publish_design,publish_baseline,publish_generation,publish_checkpoint,publish_destination,
 output wire manifest_ready,release_blocked,
 input wire obs_awvalid,obs_awready,input wire[63:0]obs_awaddr,input wire[7:0]obs_awlen,
 input wire obs_bvalid,obs_bready,input wire[1:0]obs_bresp,
 input wire cmd_valid,output wire cmd_ready,input wire[63:0]source_base,destination_base,span_bytes,input wire[31:0]cmd_cookie,
 output wire busy,rsp_valid,input wire rsp_ready,output reg[3:0]status,output reg[31:0]rsp_cookie,
 output reg receipt_valid,output reg[31:0]dirty_count,verified_count,
 output wire[63:0]m_araddr,output wire m_arvalid,input wire m_arready,
 input wire[511:0]m_rdata,input wire[3:0]m_rid,input wire[1:0]m_rresp,input wire m_rlast,m_rvalid,output wire m_rready,
 output wire[63:0]m_awaddr,output wire m_awvalid,input wire m_awready,
 output wire[511:0]m_wdata,output wire m_wvalid,input wire m_wready,
 input wire[3:0]m_bid,input wire[1:0]m_bresp,input wire m_bvalid,output wire m_bready
);
 localparam IDLE=0,SELECT=1,READ_AR=2,READ_R=3,WRITE_SEND=4,WRITE_B=5,VERIFY_AR=6,VERIFY_R=7,DONE=8;
 reg[3:0]state;reg[63:0]dirty[0:MAX_DIRTY-1];reg[63:0]scan_address,src,dst,span,src_address,dst_address;
 reg[8:0]scan_left;reg pending,stopped,aw_sent,w_sent;reg[31:0]count,index;reg[511:0]buffer;
 wire aw_event=obs_awvalid&&obs_awready,b_event=obs_bvalid&&obs_bready;
 wire active=state!=IDLE&&state!=DONE;
 reg[63:0]bound_design,bound_baseline,bound_src,bound_span,bound_bank0,bound_bank1;
 reg[63:0]copy_active_destination,copy_active_generation;
 wire tracking_fault=data_error||coverage_error;
 wire unsafe_source=!lease||!source_drained||!source_healthy||!source_protocol_ok||aw_event||b_event;
 wire identity_changed=active_destination!=copy_active_destination||active_generation!=copy_active_generation;
 wire stop_now=unsafe_source||tracking_fault||identity_changed;
 wire[64:0]aw_end={1'b0,obs_awaddr}+(({57'd0,obs_awlen}+65'd1)<<6);
 wire[64:0]bound_end={1'b0,bound_src}+{1'b0,bound_span};
 wire[64:0]bank0_end={1'b0,bank0_base}+{1'b0,span_bytes};
 wire[64:0]bank1_end={1'b0,bank1_base}+{1'b0,span_bytes};
 wire context_matches=cmd_design==bound_design&&cmd_baseline==bound_baseline&&source_base==bound_src&&span_bytes==bound_span&&bank0_base==bound_bank0&&bank1_base==bound_bank1;
 assign release_blocked=busy||cmd_valid;
 assign manifest_ready=receipt_valid&&!release_blocked&&!unsafe_source&&!tracking_fault&&bound&&
    publish_design==receipt_design&&publish_baseline==receipt_baseline&&publish_generation==receipt_generation&&
    publish_checkpoint==receipt_checkpoint&&publish_destination==receipt_destination&&
    receipt_destination!=active_destination&&receipt_generation>active_generation;
 wire[64:0]src_end={1'b0,source_base}+{1'b0,span_bytes};
 wire[64:0]dst_end={1'b0,destination_base}+{1'b0,span_bytes};
 integer i;reg found;
 assign busy=state!=IDLE;assign rsp_valid=state==DONE;
 assign cmd_ready=state==IDLE&&scan_left==0&&!pending;
 assign m_araddr=state==VERIFY_AR?dst_address:src_address;
 assign m_arvalid=state==READ_AR||state==VERIFY_AR;
 assign m_rready=state==READ_R||state==VERIFY_R;
 assign m_awaddr=dst_address;assign m_awvalid=state==WRITE_SEND&&!aw_sent;
 assign m_wdata=buffer;assign m_wvalid=state==WRITE_SEND&&!w_sent;
 assign m_bready=state==WRITE_B;
 always @(posedge clk)begin
  if(rst)begin
   scan_left<=0;scan_address<=0;pending<=0;data_error<=0;coverage_error<=0;dirty_count<=0;
   bound<=0;generation_floor<=0;checkpoint_floor<=0;
   bound_design<=0;bound_baseline<=0;bound_src<=0;bound_span<=0;bound_bank0<=0;bound_bank1<=0;
   copy_active_destination<=0;copy_active_generation<=0;
   receipt_design<=0;receipt_baseline<=0;receipt_generation<=0;receipt_checkpoint<=0;receipt_destination<=0;
   state<=IDLE;status<=0;rsp_cookie<=0;receipt_valid<=0;verified_count<=0;
   stopped<=0;aw_sent<=0;w_sent<=0;count<=0;index<=0;src<=0;dst<=0;span<=0;src_address<=0;dst_address<=0;buffer<=0;
  end else begin
   if(b_event)begin
    pending<=0;
    if(!pending||obs_bid!=0)begin coverage_error<=1;receipt_valid<=0;end
    if(obs_bresp!=0)begin data_error<=1;receipt_valid<=0;end
   end
   if(!source_protocol_ok)begin coverage_error<=1;receipt_valid<=0;end
   if(!lease||!source_healthy||!source_drained)receipt_valid<=0;
   if(aw_event)begin
    pending<=1;receipt_valid<=0;
    if(!bound||(pending&&!b_event)||scan_left!=0||obs_awaddr[5:0]!=0||obs_awid!=0||obs_awsize!=6||obs_awburst!=1||
      aw_end[64]||obs_awaddr<bound_src||aw_end>bound_end||({1'b0,obs_awaddr[11:0]}+(({57'd0,obs_awlen}+65'd1)<<6))>4096)coverage_error<=1;
    else begin scan_address<=obs_awaddr;scan_left<={1'b0,obs_awlen}+1'b1;end
   end
   if(scan_left!=0)begin
    found=0;for(i=0;i<MAX_DIRTY;i=i+1)if(i<dirty_count&&dirty[i]==scan_address)found=1;
    if(!found)begin
     if(dirty_count==MAX_DIRTY)begin coverage_error<=1;receipt_valid<=0;end
     else begin dirty[dirty_count]<=scan_address;dirty_count<=dirty_count+1;end
    end
    scan_address<=scan_address+64;scan_left<=scan_left-1;
   end
   if(active&&stop_now)stopped<=1;
   case(state)
    IDLE:if(cmd_valid&&cmd_ready)begin
     rsp_cookie<=cmd_cookie;receipt_valid<=0;status<=0;verified_count<=0;stopped<=0;index<=0;
     state<=DONE;
     if(unsafe_source)status<=1;
     else if(coverage_error)status<=3;
     else if(cmd_op==0)begin
      if(bound||dirty_count!=0||cmd_design==0||cmd_baseline==0||active_generation==0||
        span_bytes==0||source_base[5:0]!=0||bank0_base[5:0]!=0||bank1_base[5:0]!=0||span_bytes[5:0]!=0||
        src_end[64]||bank0_end[64]||bank1_end[64]||
        ({1'b0,source_base}<bank0_end&&{1'b0,bank0_base}<src_end)||
        ({1'b0,source_base}<bank1_end&&{1'b0,bank1_base}<src_end)||
        ({1'b0,bank0_base}<bank1_end&&{1'b0,bank1_base}<bank0_end))status<=4;
      else begin
       bound<=1;bound_design<=cmd_design;bound_baseline<=cmd_baseline;bound_src<=source_base;bound_span<=span_bytes;
       bound_bank0<=bank0_base;bound_bank1<=bank1_base;generation_floor<=active_generation;checkpoint_floor<=cmd_checkpoint;
      end
     end else if(!bound||!context_matches)status<=4;
     else if(cmd_op==1)begin data_error<=0;end
     else if(cmd_op!=2)status<=4;
     else if(data_error)status<=3;
     else if(cmd_generation<=generation_floor||cmd_generation<=active_generation||cmd_checkpoint<=checkpoint_floor)status<=9;
     else if((destination_base!=bound_bank0&&destination_base!=bound_bank1)||destination_base==active_destination)status<=4;
     else begin
      generation_floor<=cmd_generation;checkpoint_floor<=cmd_checkpoint;
      receipt_design<=bound_design;receipt_baseline<=bound_baseline;receipt_generation<=cmd_generation;
      receipt_checkpoint<=cmd_checkpoint;receipt_destination<=destination_base;
      copy_active_destination<=active_destination;copy_active_generation<=active_generation;
      src<=bound_src;dst<=destination_base;span<=bound_span;count<=dirty_count;state<=SELECT;
     end
    end
    SELECT:begin
     if(stopped||stop_now)begin status<=2;state<=DONE;end
     else if(index==count)begin receipt_valid<=1;state<=DONE;end
     else if(dirty[index]<src||dirty[index]-src>=span)begin status<=4;state<=DONE;end
     else begin src_address<=dirty[index];dst_address<=dst+(dirty[index]-src);state<=READ_AR;end
    end
    READ_AR:if(m_arready)state<=READ_R;
    READ_R:if(m_rvalid)begin
     if(m_rresp!=0||m_rid!=0||!m_rlast)begin status<=5;state<=DONE;end
     else if(stopped||stop_now)begin status<=2;state<=DONE;end
     else begin buffer<=m_rdata;aw_sent<=0;w_sent<=0;state<=WRITE_SEND;end
    end
    WRITE_SEND:begin
     if(m_awvalid&&m_awready)aw_sent<=1;
     if(m_wvalid&&m_wready)w_sent<=1;
     if((aw_sent||m_awready)&&(w_sent||m_wready))state<=WRITE_B;
    end
    WRITE_B:if(m_bvalid)begin
     if(m_bresp!=0||m_bid!=0)begin status<=6;state<=DONE;end
     else if(stopped||stop_now)begin status<=2;state<=DONE;end
     else state<=VERIFY_AR;
    end
    VERIFY_AR:if(m_arready)state<=VERIFY_R;
    VERIFY_R:if(m_rvalid)begin
     if(m_rresp!=0||m_rid!=0||!m_rlast||m_rdata!==buffer)begin status<=7;state<=DONE;end
     else if(stopped||stop_now)begin status<=2;state<=DONE;end
     else begin verified_count<=verified_count+1;index<=index+1;state<=SELECT;end
    end
    DONE:if(rsp_ready)state<=IDLE;
    default:begin status<=8;receipt_valid<=0;state<=DONE;end
   endcase
   if(aw_event||b_event||!lease||!source_drained||!source_healthy||!source_protocol_ok||tracking_fault)
    receipt_valid<=0;
  end
 end
endmodule
