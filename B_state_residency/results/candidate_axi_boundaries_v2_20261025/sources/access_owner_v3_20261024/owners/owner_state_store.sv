`timescale 1ns/1ps
// Exclusive owner of primary/pool/allocator backing. No query-lifecycle clear.
module owner_state_store #(parameter integer MAX_CYCLES=1048576)(
 input wire clk,rst,abort,
 input wire cfg_valid,output wire cfg_ready,
 input wire[63:0]cfg_primary,cfg_pool,cfg_allocator,input wire[31:0]cfg_nodes,cfg_capacity,
 output reg cfg_rsp_valid,input wire cfg_rsp_ready,output reg[2:0]cfg_status,output reg configured,
 input wire req_valid,output wire req_ready,input wire[2:0]req_op,input wire[31:0]req_cookie,req_node,req_net,
 output reg rsp_valid,input wire rsp_ready,output reg[3:0]rsp_status,
 output reg[31:0]rsp_cookie,rsp_count,rsp_occupancy,output reg rsp_will_overuse,
 output wire fault,busy,
 output reg[63:0]m_araddr,output wire[7:0]m_arlen,output wire[2:0]m_arsize,output wire[1:0]m_arburst,output wire[3:0]m_arid,
 output wire m_arvalid,input wire m_arready,input wire[511:0]m_rdata,input wire[3:0]m_rid,input wire[1:0]m_rresp,input wire m_rlast,m_rvalid,output wire m_rready,
 output reg[63:0]m_awaddr,output wire[7:0]m_awlen,output wire[2:0]m_awsize,output wire[1:0]m_awburst,output wire[3:0]m_awid,
 output wire m_awvalid,input wire m_awready,output reg[511:0]m_wdata,output reg[63:0]m_wstrb,output wire m_wlast,m_wvalid,input wire m_wready,
 input wire[3:0]m_bid,input wire[1:0]m_bresp,input wire m_bvalid,output wire m_bready
);
 localparam IDLE=0,AR=1,R=2,META=3,PRIMARY=4,WALK=5,WALK_RECORD=6,INNER=7,PLAN=8,ALLOC=9,WRITE_START=10,WRITE=11,B=12;
 reg[3:0]state,continuation;
 reg stopped,inflight,aw_done,w_done;
 reg[31:0]elapsed,nodes,capacity,node,key,op,ptr,previous,hops,found,found_previous,inner_remaining;
 reg[63:0]primary_base,pool_base,allocator_base;
 reg[1:0]read_lane;
 reg[127:0]read_value,primary_record,meta_record,previous_record,found_record,found_previous_record,head_record,outer_record;
 reg[63:0]write_addresses[0:3];reg[127:0]write_records[0:3];
 integer write_count,write_index;
 reg[31:0]selected_entry;
 reg allocate_free;
 // Blocking temporaries used only while constructing a complete write plan.
 reg[127:0]a,t,u,v;
 reg[31:0]count,occ,refs,entry;
 integer k;
 wire unexpected_r=m_rvalid&&state!=R&&!(state==AR&&m_arready);
 wire unexpected_b=m_bvalid&&state!=B&&!(state==WRITE&&(aw_done||m_awready)&&(w_done||m_wready));
 wire timed_out=inflight&&!rsp_valid&&!stopped&&elapsed>=MAX_CYCLES-1;
 wire stop_now=abort||unexpected_r||unexpected_b||timed_out;
 assign fault=!rst&&(stopped||stop_now);
 assign busy=!rst&&(inflight||rsp_valid||state!=IDLE);
 assign cfg_ready=!rst&&!fault&&!configured&&!cfg_rsp_valid&&!inflight&&!rsp_valid&&state==IDLE;
 assign req_ready=!rst&&!fault&&!cfg_rsp_valid&&!inflight&&!rsp_valid&&state==IDLE&&!(cfg_valid&&cfg_ready);
 // Do not withdraw AXI VALID on fault: drain the already issued transaction.
 assign m_arvalid=!rst&&state==AR;
 assign m_rready=!rst&&state==R;
 assign m_awvalid=!rst&&state==WRITE&&!aw_done;
 assign m_wvalid=!rst&&state==WRITE&&!w_done;
 assign m_bready=!rst&&state==B;
 assign m_arlen=0;assign m_awlen=0;assign m_arsize=6;assign m_awsize=6;
 assign m_arburst=1;assign m_awburst=1;assign m_arid=0;assign m_awid=0;assign m_wlast=1;
 wire[64:0]primary_bytes=({33'b0,cfg_nodes}*65'd16+65'd63)&~65'd63;
 wire[64:0]pool_bytes=({33'b0,cfg_capacity}*65'd16+65'd63)&~65'd63;
 wire[64:0]primary_last={1'b0,cfg_primary}+primary_bytes-1'b1;
 wire[64:0]pool_last={1'b0,cfg_pool}+pool_bytes-1'b1;
 wire[64:0]allocator_last={1'b0,cfg_allocator}+65'd63;
 wire overlaps_pa=({1'b0,cfg_primary}<=allocator_last)&&({1'b0,cfg_allocator}<=primary_last);
 wire overlaps_po=cfg_capacity!=0&&({1'b0,cfg_primary}<=pool_last)&&({1'b0,cfg_pool}<=primary_last);
 wire overlaps_oa=cfg_capacity!=0&&({1'b0,cfg_pool}<=allocator_last)&&({1'b0,cfg_allocator}<=pool_last);
 wire cfg_bad=cfg_nodes==0||cfg_primary[5:0]!=0||cfg_pool[5:0]!=0||cfg_allocator[5:0]!=0||primary_last[64]||allocator_last[64]||(cfg_capacity!=0&&pool_last[64])||overlaps_pa||overlaps_po||overlaps_oa;
 function[63:0]primary_address(input[31:0]id);primary_address=primary_base+({32'b0,id}<<4);endfunction
 function[63:0]pool_address(input[31:0]plus_one);pool_address=pool_base+({32'b0,plus_one-32'd1}<<4);endfunction
 task read_record(input[63:0]address,input[3:0]next_state);
  begin m_araddr<={address[63:6],6'b0};read_lane<=address[5:4];continuation<=next_state;state<=AR;end
 endtask
 task respond(input[3:0]status);
  begin rsp_status<=status;rsp_valid<=1;state<=IDLE;end
 endtask
 task poison(input[3:0]status);
  begin
   stopped<=1;
   if(inflight&&!rsp_valid)begin rsp_status<=status;rsp_valid<=1;end
  end
 endtask
 task bad_structure;
  begin poison(6);state<=IDLE;end
 endtask
 task append_write(input[63:0]address,input[127:0]value);
  begin write_addresses[write_count]<=address;write_records[write_count]<=value;write_count=write_count+1;end
 endtask
 task start_writes;
  begin write_index<=0;state<=WRITE_START;end
 endtask
 task result_values(input[31:0]new_count,input[31:0]new_occ);
  begin rsp_count<=new_count;rsp_occupancy<=new_occ;rsp_will_overuse<=new_occ>1||(new_occ==1&&new_count==0);end
 endtask
 task advance_walk(input[127:0]value);
  begin previous<=ptr;previous_record<=value;ptr<=value[95:64];hops<=hops+1'b1;state<=WALK;end
 endtask
 wire[31:0]r_net=read_value[31:0],r_refs=read_value[63:32],r_next=read_value[95:64];
 wire bad_active=read_value[127:96]!=0||r_net==0||r_net>32'h80000000||r_refs==0||r_refs>65535||r_net==primary_record[31:0];
 always @(posedge clk)begin
  if(rst)begin
   state<=IDLE;continuation<=IDLE;stopped<=0;inflight<=0;aw_done<=0;w_done<=0;
   elapsed<=0;nodes<=0;capacity<=0;node<=0;key<=0;op<=0;ptr<=0;previous<=0;hops<=0;found<=0;found_previous<=0;inner_remaining<=0;
   primary_base<=0;pool_base<=0;allocator_base<=0;read_lane<=0;read_value<=0;primary_record<=0;meta_record<=0;
   previous_record<=0;found_record<=0;found_previous_record<=0;head_record<=0;outer_record<=0;
   write_count=0;write_index<=0;selected_entry<=0;allocate_free<=0;
   cfg_rsp_valid<=0;cfg_status<=0;configured<=0;rsp_valid<=0;rsp_status<=0;rsp_cookie<=0;rsp_count<=0;rsp_occupancy<=0;rsp_will_overuse<=0;
   m_araddr<=0;m_awaddr<=0;m_wdata<=0;m_wstrb<=0;
   for(k=0;k<4;k=k+1)begin write_addresses[k]<=0;write_records[k]<=0;end
  end else begin
   if(cfg_rsp_valid&&cfg_rsp_ready)cfg_rsp_valid<=0;
   if(rsp_valid&&rsp_ready)begin rsp_valid<=0;inflight<=0;end
   if(inflight&&!rsp_valid&&!stopped)elapsed<=elapsed+1'b1;
   if(cfg_valid&&cfg_ready)begin
    cfg_rsp_valid<=1;cfg_status<=cfg_bad?1:0;
    if(!cfg_bad)begin configured<=1;primary_base<=cfg_primary;pool_base<=cfg_pool;allocator_base<=cfg_allocator;nodes<=cfg_nodes;capacity<=cfg_capacity;end
   end
   case(state)
    IDLE:if(req_valid&&req_ready)begin
     inflight<=1;elapsed<=0;rsp_cookie<=req_cookie;rsp_count<=0;rsp_occupancy<=0;rsp_will_overuse<=0;
     node<=req_node;key<=req_net+1'b1;op<={29'b0,req_op};write_count=0;
     if(!configured)respond(13);
     else if(req_op>2)respond(7);
     else if(req_node>=nodes||req_net[31])respond(1);
     else read_record(allocator_base,META);
    end
    AR:if(m_arready)state<=R;
    R:if(m_rvalid)begin
     if(stopped||stop_now)state<=IDLE;
     else if(m_rid!=0||m_rresp!=0||!m_rlast)begin poison(9);state<=IDLE;end
     else begin read_value<=m_rdata[read_lane*128+:128];state<=continuation;end
    end
    META:begin
     if(read_value[127:96]!=0||read_value[31:0]>capacity||read_value[63:32]>read_value[31:0]||read_value[95:64]>read_value[31:0])bad_structure;
     else begin meta_record<=read_value;read_record(primary_address(node),PRIMARY);end
    end
    PRIMARY:begin
     if(read_value[127:96]!=0||(r_net==0?(read_value!=0):(r_net>32'h80000000||read_value[47:32]==0||read_value[63:48]==0)))bad_structure;
     else begin
      primary_record<=read_value;ptr<=r_next;previous<=0;previous_record<=0;hops<=0;found<=0;found_previous<=0;head_record<=0;found_record<=0;found_previous_record<=0;state<=WALK;
     end
    end
    WALK:begin
     if(ptr==0)begin
      if({16'b0,primary_record[63:48]}!=hops+(primary_record[31:0]!=0)||hops>meta_record[95:64])bad_structure;
      else state<=PLAN;
     end else if(ptr>meta_record[31:0]||hops>=capacity||hops>={16'b0,primary_record[63:48]})bad_structure;
     else read_record(pool_address(ptr),WALK_RECORD);
    end
    WALK_RECORD:begin
     if(bad_active)bad_structure;
     else begin
      if(hops==0)head_record<=read_value;
      if(r_net==key)begin found<=ptr;found_record<=read_value;found_previous<=previous;found_previous_record<=previous_record;end
      if(hops==0)advance_walk(read_value);
      else begin outer_record<=read_value;inner_remaining<=hops;read_record(pool_address(primary_record[95:64]),INNER);end
     end
    end
    INNER:begin
     if(bad_active||r_net==outer_record[31:0])bad_structure;
     else if(inner_remaining==1)advance_walk(outer_record);
     else if(r_next==0||r_next>meta_record[31:0])bad_structure;
     else begin inner_remaining<=inner_remaining-1'b1;read_record(pool_address(r_next),INNER);end
    end
    PLAN:begin
     a=primary_record;refs={16'b0,a[47:32]};occ={16'b0,a[63:48]};
     count=a[31:0]==key?refs:found!=0?found_record[63:32]:0;
     result_values(count,occ);write_count=0;
     if(op==0)respond(0);
     else if(op==1)begin
      if(count==65535)respond(3);
      else if(count!=0)begin
       if(a[31:0]==key)begin a[47:32]=refs+1;append_write(primary_address(node),a);end
       else begin t=found_record;t[63:32]=count+1;append_write(pool_address(found),t);end
       result_values(count+1,occ);start_writes;
      end else if(occ==65535)respond(4);
      else if(a[31:0]==0)begin append_write(primary_address(node),{32'b0,32'b0,32'h00010001,key});result_values(1,1);start_writes;end
      else begin
       allocate_free<=meta_record[63:32]!=0;
       entry=meta_record[63:32]!=0?meta_record[63:32]:meta_record[31:0]+1;
       if(meta_record[63:32]==0&&meta_record[31:0]==capacity)respond(5);
       else begin selected_entry<=entry;read_record(pool_address(entry),ALLOC);end
      end
     end else if(count==0)respond(2);
     else if(a[31:0]==key)begin
      if(refs>1)begin a[47:32]=refs-1;append_write(primary_address(node),a);result_values(count-1,occ);start_writes;end
      else if(a[95:64]==0)begin append_write(primary_address(node),128'b0);result_values(0,0);start_writes;end
      else if(meta_record[95:64]==0)bad_structure;
      else begin
       t=meta_record;t[63:32]=a[95:64];t[95:64]=t[95:64]-1;
       append_write(pool_address(a[95:64]),{32'b0,meta_record[63:32],64'b0});append_write(allocator_base,t);
       u=head_record;u[63:48]=occ-1;append_write(primary_address(node),u);
       result_values(0,occ-1);start_writes;
      end
     end else if(count>1)begin
      t=found_record;t[63:32]=count-1;append_write(pool_address(found),t);result_values(count-1,occ);start_writes;
     end else if(meta_record[95:64]==0)bad_structure;
     else begin
      if(found_previous!=0)begin u=found_previous_record;u[95:64]=found_record[95:64];append_write(pool_address(found_previous),u);end
      else a[95:64]=found_record[95:64];
      append_write(pool_address(found),{32'b0,meta_record[63:32],64'b0});
      a[63:48]=occ-1;append_write(primary_address(node),a);
      t=meta_record;t[63:32]=found;t[95:64]=t[95:64]-1;append_write(allocator_base,t);
      result_values(0,occ-1);start_writes;
     end
    end
    ALLOC:begin
     if(allocate_free?(r_net!=0||r_refs!=0||read_value[127:96]!=0||r_next>meta_record[31:0]||r_next==selected_entry):(read_value!=0))bad_structure;
     else begin
      a=primary_record;t=meta_record;occ={16'b0,a[63:48]};
      if(allocate_free)t[63:32]=r_next;else t[31:0]=selected_entry;
      t[95:64]=t[95:64]+1;
      append_write(pool_address(selected_entry),{32'b0,a[95:64],32'd1,key});
      a[95:64]=selected_entry;a[63:48]=occ+1;
      append_write(primary_address(node),a);append_write(allocator_base,t);
      result_values(1,occ+1);start_writes;
     end
    end
    WRITE_START:begin
     m_awaddr<={write_addresses[write_index][63:6],6'b0};
     m_wdata<=({384'b0,write_records[write_index]}<<(write_addresses[write_index][5:4]*128));
     m_wstrb<=64'hffff<<(write_addresses[write_index][5:4]*16);aw_done<=0;w_done<=0;state<=WRITE;
    end
    WRITE:begin
     if(m_awready)aw_done<=1;if(m_wready)w_done<=1;
     if((aw_done||m_awready)&&(w_done||m_wready))state<=B;
    end
    B:if(m_bvalid)begin
     if(stopped||stop_now)state<=IDLE;
     else if(m_bid!=0||m_bresp!=0)begin poison(9);state<=IDLE;end
     else if(write_index+1==write_count)respond(0);
     else begin write_index<=write_index+1;state<=WRITE_START;end
    end
    default:begin poison(10);state<=IDLE;end
   endcase
   if(stop_now)begin
    poison(abort?12:timed_out?11:10);
    if(state!=AR&&state!=R&&state!=WRITE&&state!=B)state<=IDLE;
   end else if(stopped&&state!=AR&&state!=R&&state!=WRITE&&state!=B)state<=IDLE;
  end
 end
endmodule
