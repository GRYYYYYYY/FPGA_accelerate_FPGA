from pathlib import Path
import re
p=Path(__file__).parent
s=(p/'postprev_inputs.sv').read_text();header=s[s.index(')(\n')+3:s.index('\n);')]
ports=[];decl=[]
for direction,width,names in re.findall(r'(input|output)\s+(?:wire|reg)\s*(\[[^]]+\])?\s*(.*?)(?=input|output|\Z)',header,re.S):
 for name in re.split(r'[\s,]+',names.strip(' ,\n')):
  if not name:continue
  ports.append(name);decl.append(('reg ' if direction=='input' else 'wire ')+(width+' 'if width else '')+name+('=0'if direction=='input'else'')+';')
body=r'''
reg[159:0] mem[0:15];reg present[0:15];
integer i,checks=0,parent_reads=0,prev_writes=0,clears=0,before_reads,serial=0,phase=0;
reg lp=0;reg[31:0]ln,lv;reg lw;reg[2:0]lf;reg hold_label=0;reg[3:0]label_error=0,coord_error=0;reg[31:0]clear_error=0;
reg[159:0] merged;reg[31:0] expected_up;integer expected_status;
always #5 clk=~clk;
always @(posedge clk)begin
 if(rst)begin f_rsp_valid<=0;l_rsp_valid<=0;c_rsp_valid<=0;lp<=0;end
 else begin
  if(f_rsp_valid&&f_rsp_ready)f_rsp_valid<=0;
  if(f_req_valid&&f_req_ready)begin clears<=clears+1;f_rsp_valid<=1;f_rsp_status<=clear_error;f_rsp_cookie<=f_req_cookie;f_rsp_query<=f_req_query;f_rsp_price<=f_req_price;f_rsp_size<=0;end
  if(l_rsp_valid&&l_rsp_ready)l_rsp_valid<=0;
  if(l_valid&&l_ready)begin
   if(lp||l_rsp_valid)$fatal(1,"label overlap");lp<=1;ln<=l_node;lv<=l_value;lw<=l_write;lf<=l_field;
   if(l_write)prev_writes<=prev_writes+1;else parent_reads<=parent_reads+1;
  end
  if(lp&&!hold_label)begin
   lp<=0;merged=present[ln]?mem[ln]:0;
   if(lw)begin if(lf!=2)$fatal(1,"wrong field");merged[95:64]=lv;mem[ln]<=merged;present[ln]<=1;end
   l_rsp_valid<=1;l_status<=label_error;l_payload<=merged;l_present<=lw||present[ln];
  end
  if(c_rsp_valid&&c_rsp_ready)c_rsp_valid<=0;
  if(c_req_valid&&c_req_ready)begin
   c_rsp_valid<=1;c_rsp_status<=coord_error;c_rsp_cookie<=c_req_cookie;c_rsp_node<=c_req_node;c_rsp_query<=c_req_query;c_rsp_price<=c_req_price;c_rsp_op<=0;c_rsp_y<=3;c_rsp_attrs<=0;c_rsp_attrs[127:112]<=2;c_rsp_prev_read<=1;c_rsp_label_prev<=mem[c_req_node][95:64];
  end
 end
end
task tick;begin @(posedge clk);#1;end endtask
task setup;begin
 @(negedge clk);rst=1;abort=0;req_valid=0;rsp_ready=0;active=0;decision_lock=0;hold_label=0;label_error=0;coord_error=0;clear_error=0;
 repeat(4)tick();@(negedge clk);rst=0;active=1;decision_lock=1;active_query=1;active_price=3;active_version=32'h10003;active_design=64'h123456789abcdef0;
 f_req_ready=1;l_ready=1;c_req_ready=1;
 for(i=0;i<16;i=i+1)begin mem[i]=0;mem[i][95:64]=32'hffffffff;present[i]=1;end
 mem[0][63:32]=32'h3f800000;mem[1][63:32]=32'h40000000;
 repeat(3)tick();
end endtask
task issue(input integer parent,child,early);begin
 @(negedge clk);serial=serial+1;req_cookie=serial;req_parent=parent;req_child=child;req_early=early;req_centers=0;req_valid=1;
 do @(posedge clk);while(!req_ready);#1;@(negedge clk);req_valid=0;
end endtask
task finish(input integer code,input[31:0]up,input integer delta);reg[31:0]hu,hx,hy,hd;begin
 wait(rsp_valid);@(negedge clk);
 if(rsp_status!=code||rsp_cookie!=serial||rsp_parent!=req_parent||rsp_child!=req_child)$fatal(1,"reply identity code=%0d expected=%0d",rsp_status,code);
 if(parent_reads-before_reads!=delta)$fatal(1,"parent read count phase=%0d actual=%0d expected=%0d",phase,parent_reads-before_reads,delta);
 if(code==0&&(rsp_upstream!==up||rsp_x!=2||rsp_y!=3||rsp_distance!==32'h40a00000))$fatal(1,"wrong result phase=%0d up=%h expected=%h",phase,rsp_upstream,up);
 hu=rsp_upstream;hx=rsp_x;hy=rsp_y;hd=rsp_distance;
 repeat(4)begin tick();if(!rsp_valid||rsp_upstream!==hu||rsp_x!==hx||rsp_y!==hy||rsp_distance!==hd||req_ready)$fatal(1,"reply hold");end
 @(negedge clk);rsp_ready=1;tick();@(negedge clk);rsp_ready=0;repeat(2)tick();checks=checks+1;
 $display("CHECK %0d %0d %0d %08h %0d",phase,code,delta,up,parent_reads);
end endtask
task run(input integer parent,child,early,input[31:0]up,input integer delta);begin phase=phase+1;before_reads=parent_reads;issue(parent,child,early);finish(0,up,delta);end endtask
initial begin
 setup();run(0,2,0,32'h3f800000,1);mem[2][63:32]=32'h40000000;run(0,3,0,32'h3f800000,0);
 // A legitimate host write is possible only outside this decision lease.
 decision_lock=0;repeat(2)tick();mem[0][63:32]=32'h40400000;decision_lock=1;run(0,4,0,32'h40400000,1);
 run(1,5,0,32'h40000000,1);run(0,6,0,32'h40400000,1);
 active_version=active_version+65536;run(0,2,0,32'h40400000,1);
 active_price=active_price+1;run(0,3,0,32'h40400000,1);
 active_query=active_query+1;run(0,4,0,32'h40400000,1);
 active_design=active_design^64'h100000000;run(0,5,0,32'h40400000,1);
 active=0;repeat(2)tick();active=1;run(0,6,0,32'h40400000,1);
 run(0,0,0,32'h40400000,1);mem[0][63:32]=32'h40800000;
 run(0,0,0,32'h40800000,1);mem[0][63:32]=32'h40a00000;
 run(0,2,0,32'h40a00000,1);run(0,3,1,32'h40a00000,0);if(clears!=1)$fatal(1,"EARLY CLEAR omitted");
 present[7]=0;run(7,8,0,0,1);present[7]=1;mem[7][63:32]=32'h41100000;run(7,9,0,32'h41100000,1);
 // Prev-write error on a warm hit must stop before any cached response is used.
 phase=phase+1;before_reads=parent_reads;label_error=2;issue(7,10,0);finish(2,0,0);if(!fault||req_ready)$fatal(1,"write error did not stop");
 setup();phase=phase+1;before_reads=parent_reads;hold_label=1;issue(0,2,0);repeat(1100)tick();if(!fault||req_ready||!busy)$fatal(1,"timeout lease");hold_label=0;finish(2,0,0);
 setup();phase=phase+1;before_reads=parent_reads;hold_label=1;issue(0,2,0);repeat(3)tick();abort=1;tick();abort=0;hold_label=0;finish(2,0,0);if(!fault)$fatal(1,"abort");
 setup();run(0,2,0,32'h3f800000,1);
 phase=phase+1;before_reads=parent_reads;issue(0,3,0);wait(rsp_valid);active_version=active_version+65536;tick();if(!fault||rsp_status!=0||rsp_upstream!==32'h3f800000)$fatal(1,"late drift response");finish(0,32'h3f800000,0);
 if(checks!=21)$fatal(1,"check total=%0d",checks);
 $display("PARENT_UPSTREAM_BOUNDS_PASS checks=%0d parent_reads=%0d prev_writes=%0d clears=%0d",checks,parent_reads,prev_writes,clears);$finish;
end
initial begin #10000000;$fatal(1,"watchdog phase=%0d",phase);end
'''
(p/'tb_parent_bounds.sv').write_text('`timescale 1ns/1ps\nmodule tb_parent_bounds;\n'+'\n'.join(decl)+'\npostprev_inputs #(.MAX_CYCLES(1024))dut(.*);\n'+body+'\nendmodule\n')
