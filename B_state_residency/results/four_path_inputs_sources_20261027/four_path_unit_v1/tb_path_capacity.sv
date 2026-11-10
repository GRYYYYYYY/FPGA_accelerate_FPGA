`timescale 1ns/1ps
`default_nettype none
module tb_path_capacity;
 localparam N=4,WORDS=156;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,abort=0,active=1,lease=1;
 reg[1:0]active_query=0;reg[3:0]active_price=6;reg[31:0]active_version=6;reg[63:0]active_design=64'h123456789abcdef0;
 reg req_valid=0,req_op=0,rsp_ready=0;reg[1:0]req_slot=0;wire req_ready,rsp_valid,busy,fault;
 reg[31:0]req_cookie=0,req_source=66893,req_sink=6954,req_net=26422,req_sequence=180330;
 wire[3:0]rsp_status;wire[31:0]rsp_cookie,rsp_nodes,rsp_acked;wire[N-1:0]slot_valid;
 wire l_valid,l_rsp_ready,o_valid,o_rsp_ready;reg l_ready=0,l_rsp_valid=0,l_present=1,o_ready=0,o_rsp_valid=0;
 wire[31:0]l_node,o_node,o_net,o_cookie;wire[2:0]o_op;reg[3:0]l_status=0,o_status=0;reg[159:0]l_payload=0;reg[31:0]o_rsp_cookie=0;
 reg cp_valid=0,cp_restore=0,cp_safe=1,cp_rsp_ready=0,cp_s_valid=0,cp_s_last=0,cp_m_ready=0;
 wire cp_ready,cp_busy,cp_rsp_valid,cp_s_ready,cp_m_valid,cp_m_last;
 reg[63:0]cp_design=64'h123456789abcdef0;reg[31:0]cp_nodes=9089009,cp_nets=27960,cp_expected_crc=0,cp_s_index=0,cp_s_data=0;
 wire[3:0]cp_status;wire[31:0]cp_crc,cp_m_index,cp_m_data;
 route_commit_controller #(.PATH_SLOTS(N),.MAX_PATH(32),.MAX_CYCLES(4096))dut(.*);
 reg[31:0]saved[0:WORDS-1],pristine[0:WORDS-1],exported[0:WORDS-1];
 reg[31:0]label_nodes[0:4];reg[159:0]labels[0:4];
 reg[31:0]owner_nodes[0:4];integer refs[0:4];
 integer trace,fd,rc,checks=0,cp_id=0,qid=0,ticks=0,lwait=0,owait=0,nlabels=0,nowners=0,at;
 string file_path;
 reg held_l=0,held_o=0;reg[31:0]old_l;reg[98:0]old_o;
 task ck(input bit pass,input string why);begin checks=checks+1;if(!pass)$fatal(1,"path capacity check%0d %s",checks,why);end endtask
 function automatic[31:0]crc_image;reg[31:0]v;begin
  v=32'hffffffff;for(integer i=0;i<WORDS;i=i+1)begin v=v^saved[i];repeat(32)v=v[0]?(v>>1)^32'hedb88320:v>>1;end crc_image=~v;
 end endfunction
 task reset_paths;begin
  @(negedge clk);rst=1;req_valid=0;rsp_ready=0;cp_valid=0;cp_s_valid=0;cp_m_ready=0;cp_rsp_ready=0;cp_safe=1;
  repeat(3)@(negedge clk);rst=0;repeat(2)@(negedge clk);$fdisplay(trace,"RESET %0d %0d",cp_id,qid);
 end endtask
 task cp_start(input bit restore);begin
  @(negedge clk);cp_restore=restore;cp_valid=1;
  do @(posedge clk);while(!cp_ready);@(negedge clk);cp_valid=0;
 end endtask
 task cp_finish(input integer wanted);reg[35:0]hold;begin
  wait(cp_rsp_valid);@(negedge clk);ck(cp_status==wanted,"checkpoint status");hold={cp_status,cp_crc};
  repeat(5)begin @(negedge clk);ck(cp_rsp_valid&&cp_busy&&!req_ready&&{cp_status,cp_crc}===hold,"held checkpoint reply");end
  $fdisplay(trace,"D %0d %0d %08h %0d",cp_id,cp_status,cp_crc,slot_valid);
  cp_rsp_ready=1;@(negedge clk);cp_rsp_ready=0;cp_id=cp_id+1;repeat(2)@(negedge clk);
 end endtask
 task load_image(input integer mode,input integer wanted);begin
  cp_expected_crc=crc_image()^(mode==1);cp_start(1);
  for(integer i=0;i<WORDS;i=i+1)begin
   @(negedge clk);cp_s_valid=1;cp_s_index=i;cp_s_data=saved[i];cp_s_last=i==WORDS-1||(mode==2&&i==116);
   do @(posedge clk);while(!cp_s_ready);@(negedge clk);cp_s_valid=0;
   if(mode==2&&i==116)break;
   if(mode==3&&i==124)begin cp_safe=0;break;end
  end
  cp_finish(wanted);cp_safe=1;
 end endtask
 task save_image;reg[64:0]hold;reg[31:0]sum;begin
  cp_start(0);sum=32'hffffffff;
  for(integer i=0;i<WORDS;i=i+1)begin
   wait(cp_m_valid);@(negedge clk);hold={cp_m_last,cp_m_index,cp_m_data};
   repeat(2)begin @(negedge clk);ck(cp_m_valid&&{cp_m_last,cp_m_index,cp_m_data}===hold&&!req_ready,"held export word");end
   ck(cp_m_index==i&&cp_m_last==(i==WORDS-1),"export framing");exported[i]=cp_m_data;
   sum=sum^cp_m_data;repeat(32)sum=sum[0]?(sum>>1)^32'hedb88320:sum>>1;
   cp_m_ready=1;@(negedge clk);cp_m_ready=0;
  end
  cp_finish(0);ck(cp_crc==~sum,"native export CRC");
 end endtask
 task send(input bit op,input integer slot,input integer sink,input integer wanted,input integer acked);reg[99:0]hold;begin
  @(negedge clk);qid=qid+1;req_cookie=32'habc00000+qid;req_op=op;req_slot=slot;req_sink=sink;req_valid=1;
  do @(posedge clk);while(!req_ready);@(negedge clk);req_valid=0;
  wait(rsp_valid);@(negedge clk);ck(rsp_status==wanted&&rsp_cookie==req_cookie&&rsp_acked==acked,"route reply");
  ck(!l_valid&&!o_valid&&!l_rsp_valid&&!o_rsp_valid&&!lwait&&!owait,"backend retirement");
  hold={rsp_status,rsp_cookie,rsp_nodes,rsp_acked};
  repeat(5)begin @(negedge clk);ck(rsp_valid&&!req_ready&&{rsp_status,rsp_cookie,rsp_nodes,rsp_acked}===hold,"held route reply");end
  $fdisplay(trace,"R %0d %0d %0d %0d %0d",qid,rsp_status,rsp_nodes,rsp_acked,slot_valid);
  rsp_ready=1;@(negedge clk);rsp_ready=0;repeat(2)@(negedge clk);
 end endtask
 always @(posedge clk)begin
  ticks=ticks+1;if(ticks>100000)$fatal(1,"path watchdog cp=%0d state=%0d",cp_id,dut.state);
  if(rst)begin l_ready<=0;o_ready<=0;l_rsp_valid<=0;o_rsp_valid<=0;lwait<=0;owait<=0;held_l<=0;held_o<=0;end
  else begin
   l_ready<=ticks%4==0;o_ready<=ticks%5==0;
   if(held_l&&(!l_valid||l_node!==old_l))$fatal(1,"label changed under backpressure");
   if(held_o&&(!o_valid||{o_op,o_node,o_net,o_cookie}!==old_o))$fatal(1,"owner changed under backpressure");
   held_l<=l_valid&&!l_ready;old_l<=l_node;held_o<=o_valid&&!o_ready;old_o<={o_op,o_node,o_net,o_cookie};
   if(l_valid&&l_ready)begin
    if(lwait||l_rsp_valid)$fatal(1,"label overlap");at=-1;
    for(integer i=0;i<5;i=i+1)if(label_nodes[i]==l_node)at=i;
    if(at<0)$fatal(1,"unexpected label %0d",l_node);
    l_payload<=labels[at];lwait<=3;nlabels=nlabels+1;$fdisplay(trace,"L %0d %0d %040h",qid,l_node,labels[at]);
   end
   if(lwait>0)begin lwait<=lwait-1;if(lwait==1)l_rsp_valid<=1;end
   if(l_rsp_valid&&l_rsp_ready)l_rsp_valid<=0;
   if(o_valid&&o_ready)begin
    if(owait||o_rsp_valid)$fatal(1,"owner overlap");at=-1;
    for(integer i=0;i<5;i=i+1)if(owner_nodes[i]==o_node)at=i;
    if(at<0||o_net!=26422||(o_op!=1&&o_op!=2)||o_cookie!=req_cookie)$fatal(1,"owner request");
    if(o_op==2&&refs[at]==0)$fatal(1,"owner underflow");
    $fdisplay(trace,"O %0d %0d %0d %0d %0d",qid,o_op,o_node,refs[at],refs[at]+(o_op==1?1:-1));
    refs[at]=refs[at]+(o_op==1?1:-1);nowners=nowners+1;owait<=3;o_rsp_cookie<=o_cookie;
   end
   if(owait>0)begin owait<=owait-1;if(owait==1)o_rsp_valid<=1;end
   if(o_rsp_valid&&o_rsp_ready)o_rsp_valid<=0;
   if(req_valid&&req_ready)$fdisplay(trace,"Q %0d %0d %0d %08h %0d %0d",qid,req_op,req_slot,req_cookie,req_sink,req_sequence);
   if(cp_valid&&cp_ready)$fdisplay(trace,"C %0d %0d %08h",cp_id,cp_restore,cp_expected_crc);
   if(cp_s_valid&&cp_s_ready)$fdisplay(trace,"I %0d %0d %08h %0d",cp_id,cp_s_index,cp_s_data,cp_s_last);
   if(cp_m_valid&&cp_m_ready)$fdisplay(trace,"E %0d %0d %08h %0d",cp_id,cp_m_index,cp_m_data,cp_m_last);
  end
 end
 initial begin
  if(!$value$plusargs("events=%s",file_path))$fatal(1,"events");trace=$fopen(file_path,"w");
  if(!$value$plusargs("image=%s",file_path))$fatal(1,"image");fd=$fopen(file_path,"r");
  for(integer i=0;i<WORDS;i=i+1)begin rc=$fscanf(fd,"%h",saved[i]);if(rc!=1)$fatal(1,"image format");pristine[i]=saved[i];end $fclose(fd);
  if(!$value$plusargs("labels=%s",file_path))$fatal(1,"labels");fd=$fopen(file_path,"r");
  for(integer i=0;i<5;i=i+1)begin rc=$fscanf(fd,"%d %h",label_nodes[i],labels[i]);if(rc!=2)$fatal(1,"label format");end $fclose(fd);
  owner_nodes[0]=339193;owner_nodes[1]=990179;owner_nodes[2]=558358;owner_nodes[3]=265324;refs[0]=1;refs[1]=2;refs[2]=4;refs[3]=5;owner_nodes[4]=990178;refs[4]=1;
  reset_paths;load_image(0,0);ck(slot_valid==15&&nowners==0,"metadata registration does not add owner refs");save_image;
  for(integer i=0;i<WORDS;i=i+1)ck(exported[i]==pristine[i],"four slot canonical image");
  send(0,3,6954,1,0);send(1,3,151354,1,0);
  ck(!fault&&slot_valid==15&&nlabels==0&&nowners==0,"occupied slot and wrong identity reject without traffic");
  load_image(1,1);ck(slot_valid==15,"bad CRC keeps live slots");
  saved[125]=saved[124];load_image(0,1);ck(slot_valid==15,"last slot duplicate keeps live slots");saved[125]=pristine[125];
  saved[118]=33;load_image(0,1);ck(slot_valid==15,"last slot invalid length");saved[118]=pristine[118];
  saved[122]=0;load_image(0,1);ck(slot_valid==15,"last slot invalid design");saved[122]=pristine[122];
  load_image(2,1);ck(slot_valid==15,"old three slot length rejected");
  load_image(3,2);ck(slot_valid==15&&!fault,"partial fourth slot cancellation is atomic");
  send(1,3,6954,0,3);ck(slot_valid==7&&refs[0]==1&&refs[1]==2&&refs[2]==3&&refs[3]==4&&refs[4]==0,"native fourth old path ripup");save_image;
  for(integer i=0;i<WORDS;i=i+1)ck(exported[i]==(i<117?pristine[i]:0),"unused last slot serialized zero");
  send(0,3,6954,0,3);ck(slot_valid==15&&nlabels==5&&refs[0]==1&&refs[1]==2&&refs[2]==4&&refs[3]==5&&refs[4]==1,"real CPU q4 backtrace commit");save_image;
  for(integer i=0;i<WORDS;i=i+1)ck(exported[i]==pristine[i],"four paths preserved after q3");
  reset_paths;ck(slot_valid==0&&refs[1]==2,"controller-only reset preserves owner backend");load_image(0,0);save_image;
  for(integer i=0;i<WORDS;i=i+1)ck(exported[i]==pristine[i],"restored four slot image");
  send(1,1,67922,0,3);ck(slot_valid==13,"q2 ripup retains q1/q3/q4");
  send(1,2,151354,0,3);ck(slot_valid==9,"q3 ripup retains q1/q4");
  send(1,3,6954,0,3);ck(slot_valid==1,"q4 ripup retains q1");
  send(1,0,204279,0,3);ck(slot_valid==0&&nlabels==5,"saved paths ripup without label reads");save_image;
  for(integer i=0;i<WORDS;i=i+1)ck(exported[i]==0,"empty canonical image");
  ck(refs[0]==0&&refs[1]==0&&refs[2]==0&&refs[3]==1&&refs[4]==0&&nowners==18,"underlying owner references retained");
  $fdisplay(trace,"FINAL %0d %0d %0d %0d %0d %0d %0d",nlabels,nowners,refs[0],refs[1],refs[2],refs[3],refs[4]);
  $display("PATH_CAPACITY_PASS checks=%0d cp=%0d routes=%0d",checks,cp_id,qid);$fclose(trace);$finish;
 end
endmodule
`default_nettype wire
