`timescale 1ns/1ps
// Independent byte-file AXI memory; three address windows, bursts <=3 beats.
module axi_file_memory #(parameter integer ADDR_BITS=64,READ_ONLY=0,MAX_BEATS=3,parameter TAG="memory")(
 input wire clk,rst,input wire[63:0]base0,base1,base2,size0,size1,size2,
 input wire[ADDR_BITS-1:0]araddr,input wire[7:0]arlen,input wire[2:0]arsize,input wire[1:0]arburst,input wire[3:0]arid,input wire arvalid,output wire arready,
 output reg[511:0]rdata,output reg[3:0]rid,output reg[1:0]rresp,output reg rlast,rvalid,input wire rready,
 input wire[ADDR_BITS-1:0]awaddr,input wire[7:0]awlen,input wire[2:0]awsize,input wire[1:0]awburst,input wire[3:0]awid,input wire awvalid,output wire awready,
 input wire[511:0]wdata,input wire[63:0]wstrb,input wire wlast,wvalid,output wire wready,
 output reg[3:0]bid,output reg[1:0]bresp,output reg bvalid,input wire bready,
 input wire inject_r,inject_b,
 output integer reads=0,writes=0,rbeats=0,wbeats=0,bresponses=0
);
 reg[31:0]rng=32'hc7aa4813;reg rp=0,wp=0,wend=0;integer rdpos=0,rdlen=0,wrlen=0,wrcount=0,delay_r=0,delay_b=0;
 reg[63:0]rdaddr,wraddr;reg[511:0]wqueue[0:2];reg[63:0]squeue[0:2];
 integer fd[0:2],logfd,rc,k,j,file_id,relative,nread;
 reg[7:0]bytes[0:63];reg[511:0]data;string path,path1,path2,logpath;
 assign arready=!rst&&!rp&&!rvalid&&rng[2:0]!=0;
 assign awready=!rst&&!READ_ONLY&&!wp&&!bvalid&&rng[5:3]<4;
 assign wready=!rst&&!READ_ONLY&&!wend&&!bvalid&&rng[8:6]>2;
 task decode(input[63:0]address);
  begin
   if(address>=base0&&address<base0+size0)begin file_id=0;relative=address-base0;end
   else if(size1!=0&&address>=base1&&address<base1+size1)begin file_id=1;relative=address-base1;end
   else if(size2!=0&&address>=base2&&address<base2+size2)begin file_id=2;relative=address-base2;end
   else $fatal(1,"%s range %h",TAG,address);
  end
 endtask
 initial begin
  if(!$value$plusargs({TAG,"0=%s"},path)||!$value$plusargs({TAG,"log=%s"},logpath))$fatal(1,"%s paths",TAG);
  fd[0]=$fopen(path,READ_ONLY?"rb":"r+b");fd[1]=0;fd[2]=0;
  if($value$plusargs({TAG,"1=%s"},path1))fd[1]=$fopen(path1,"rb");
  if($value$plusargs({TAG,"2=%s"},path2))fd[2]=$fopen(path2,"rb");
  logfd=$fopen(logpath,"w");if(!fd[0]||!logfd)$fatal(1,"%s open",TAG);
 end
 always @(posedge clk)begin
  rng<={rng[30:0],rng[31]^rng[21]^rng[1]^rng[0]};
  if(rst)begin rp<=0;wp<=0;wend<=0;rvalid<=0;bvalid<=0;wrcount<=0;delay_b<=0;delay_r<=0;rdpos<=0;rdata<=0;rid<=0;rresp<=0;rlast<=0;bid<=0;bresp<=0;end
  else begin
   if(arvalid&&arready)begin
    if(arlen>=MAX_BEATS||arsize!=6||arburst!=1||arid!=0||araddr[5:0]!=0||({1'b0,araddr[11:0]}+(arlen+1)*64)>4096)$fatal(1,"%s AR shape",TAG);
    decode(araddr);rdaddr<=araddr;rdlen<=arlen+1;rdpos<=0;rp<=1;delay_r<=rng[12:9];reads=reads+1;$fdisplay(logfd,"A %h %0d",araddr,arlen+1);
   end
   if(rp&&!rvalid)begin
    if(delay_r!=0)delay_r<=delay_r-1;
    else begin
     decode(rdaddr+rdpos*64);for(k=0;k<64;k=k+1)bytes[k]=0;
     rc=$fseek(fd[file_id],relative,0);if(rc!=0)$fatal(1,"seek R");nread=$fread(bytes,fd[file_id]);if(nread<=0)$fatal(1,"read missing bytes");
     data=0;for(k=0;k<64;k=k+1)data[k*8+:8]=bytes[k];
     rdata<=data;rid<=0;rresp<=inject_r?2:0;rlast<=rdpos==rdlen-1;rvalid<=1;
    end
   end
   if(rvalid&&rready)begin
    $fdisplay(logfd,"R %h %0128h %0d",rdaddr+rdpos*64,rdata,rresp);rbeats=rbeats+1;rvalid<=0;
    if(rdpos==rdlen-1)rp<=0;else begin rdpos<=rdpos+1;delay_r<=rng[12:9];end
   end
   if(awvalid&&awready)begin
    if(awlen>=MAX_BEATS||awsize!=6||awburst!=1||awid!=0||awaddr[5:0]!=0||({1'b0,awaddr[11:0]}+(awlen+1)*64)>4096)$fatal(1,"%s AW shape",TAG);
    decode(awaddr);wraddr<=awaddr;wrlen<=awlen+1;wp<=1;writes=writes+1;
   end
   if(wvalid&&wready)begin
    if(wrcount>=MAX_BEATS)$fatal(1,"%s W count",TAG);wqueue[wrcount]<=wdata;squeue[wrcount]<=wstrb;wrcount<=wrcount+1;wbeats=wbeats+1;
    if(wlast)wend<=1;
   end
   if(wp&&wend&&!bvalid)begin
    if(wrcount!=wrlen)$fatal(1,"%s AW/W lengths",TAG);
    if(delay_b<7)delay_b<=delay_b+1;
    else begin
     for(j=0;j<wrcount;j=j+1)begin
      decode(wraddr+j*64);
      for(k=0;k<64;k=k+1)if(squeue[j][k])begin rc=$fseek(fd[file_id],relative+k,0);if(rc!=0)$fatal(1,"seek W");$fwrite(fd[file_id],"%c",wqueue[j][k*8+:8]);end
      $fflush(fd[file_id]);$fdisplay(logfd,"W %h %016h %0128h",wraddr+j*64,squeue[j],wqueue[j]);
     end
     bvalid<=1;bid<=0;bresp<=inject_b?2:0;
    end
   end
   if(bvalid&&bready)begin $fdisplay(logfd,"B %0d",bresp);bresponses=bresponses+1;wp<=0;wend<=0;bvalid<=0;wrcount<=0;delay_b<=0;end
   $fflush(logfd);
  end
 end
endmodule
