from pathlib import Path
import re
HERE=Path(__file__).resolve().parent
BASE=Path('/tmp/B_state_residency_offer_20261025/label_source_crc_full_v2/sources/expansion_20261024/pager/backend')
def ports(s):
 h=s.split(')(\n',1)[1].split('\n);',1)[0]
 for m in re.finditer(r'(input|output)\s+(?:wire|reg)\s*(\[[^]]+\])?\s*([^;]*?)(?=\binput\b|\boutput\b|$)',h,re.S):
  for n in m[3].strip().rstrip(',').split(','):
   n=n.strip()
   if n:yield m[1],m[2]or'',n

def make():
 decl={};initial=[]
 driven=lambda n:n.startswith('native_rsp_')or n in ['native_cmd_ready','native_fault','baseline_req_ready']or n.startswith('baseline_rsp_')and n!='baseline_rsp_ready'
 for dr,w,n in ports((HERE/'resident_page_manager.sv').read_text()):
  reg=dr=='input'and not driven(n)
  decl[n]=('reg'if reg else'wire')+' '+w+' '+n+';'
  if reg:initial.append(n+'=0;')
 ep=[]
 for dr,w,n in ports((BASE/'memory_scratch_endpoint_small_staticcodec.sv').read_text()):
  alias='native_'+n if n.startswith(('cmd_','rsp_'))else'backend_fault'if n=='fault'else n
  ep.append('.'+n+'('+alias+')')
  if alias not in decl:
   w=w.replace('GENERATION_BITS','16').replace('TAG_BITS','2').replace('INDEX_BITS','4').replace('TX_BITS','16')
   reg=dr=='input'and not n.startswith('m_');decl[alias]=('reg'if reg else'wire')+' '+w+' '+alias+';'
   if reg:initial.append(alias+'=0;')
 decl['injected_fault']='reg injected_fault=0;assign native_fault=backend_fault||injected_fault;'
 s='''`timescale 1ns/1ps
module tb_baseline_miss;
localparam TX_BITS=16;
`ifdef SINGLE
localparam SLOTS=1;
`else
localparam SLOTS=32;
`endif
'''+ '\n'.join(decl.values())+'''
initial clk=0;always #5 clk=~clk;
resident_page_manager #(.SLOTS(SLOTS),.ENABLE_BASELINE(1)) dut(.*);
memory_scratch_endpoint_small_staticcodec #(.FRAMES(16),.INDEX_BITS(4),.HASH_BITS(4),.PROBE_LIMIT(16)) endpoint('''+','.join(ep)+''');
wire[63:0]ba;wire[7:0]bl;wire[2:0]bz;wire[1:0]bb;wire[3:0]bi;wire bv,by,brv,brr,brlast;wire[511:0]bd;wire[3:0]brid;wire[1:0]bresp;
reg cv=0,cr=0;wire cy,crv,bidle,configured;wire[3:0]cs;reg inj=0;
label_baseline_reader reader(.clk(clk),.rst(rst),.cfg_valid(cv),.cfg_ready(cy),.cfg_permit(1'b1),.cfg_base(64'hb000000000),.cfg_epoch(64'h300010003),.cfg_count(32'd9089009),.cfg_rsp_valid(crv),.cfg_rsp_ready(cr),.cfg_status(cs),.req_valid(baseline_req_valid),.req_ready(baseline_req_ready),.req_node(baseline_req_node),.req_epoch(baseline_req_epoch),.rsp_valid(baseline_rsp_valid),.rsp_ready(baseline_rsp_ready),.rsp_status(baseline_rsp_status),.rsp_node(baseline_rsp_node),.rsp_epoch(baseline_rsp_epoch),.rsp_payload(baseline_rsp_payload),.idle(bidle),.configured(configured),.araddr(ba),.arlen(bl),.arsize(bz),.arburst(bb),.arid(bi),.arvalid(bv),.arready(by),.rdata(bd),.rid(brid),.rresp(bresp),.rlast(brlast),.rvalid(brv),.rready(brr));
axi_file_memory #(.READ_ONLY(1),.TAG("baseline")) bmem(.clk(clk),.rst(rst),.base0(64'hb000000000),.size0(64'd290848320),.base1(64'b0),.size1(64'b0),.base2(64'b0),.size2(64'b0),.araddr(ba),.arlen(bl),.arsize(bz),.arburst(bb),.arid(bi),.arvalid(bv),.arready(by),.rdata(bd),.rid(brid),.rresp(bresp),.rlast(brlast),.rvalid(brv),.rready(brr),.awaddr(64'b0),.awlen(8'b0),.awsize(3'd6),.awburst(2'd1),.awid(4'b0),.awvalid(1'b0),.wdata(512'b0),.wstrb(64'b0),.wlast(1'b0),.wvalid(1'b0),.bready(1'b1),.inject_r(inj),.inject_b(1'b0));
axi_file_memory #(.ADDR_BITS(32),.TAG("pages")) pmem(.clk(clk),.rst(rst),.base0(64'b0),.size0(64'd3072),.base1(64'b0),.size1(64'b0),.base2(64'b0),.size2(64'b0),.araddr(m_araddr),.arlen(m_arlen),.arsize(m_arsize),.arburst(m_arburst),.arid(m_arid),.arvalid(m_arvalid),.arready(m_arready),.rdata(m_rdata),.rid(m_rid),.rresp(m_rresp),.rlast(m_rlast),.rvalid(m_rvalid),.rready(m_rready),.awaddr(m_awaddr),.awlen(m_awlen),.awsize(m_awsize),.awburst(m_awburst),.awid(m_awid),.awvalid(m_awvalid),.awready(m_awready),.wdata(m_wdata),.wstrb(m_wstrb),.wlast(m_wlast),.wvalid(m_wvalid),.wready(m_wready),.bid(m_bid),.bresp(m_bresp),.bvalid(m_bvalid),.bready(m_bready),.inject_r(1'b0),.inject_b(1'b0));
integer tf,fd,rc,node,checks=0,misses=0,phase=0;reg[159:0]v0,v1,v8,want;string path,trace;
task check(input bit ok);begin checks=checks+1;if(!ok)$fatal(1,"miss check%0d phase%0d",checks,phase);end endtask
always @(posedge clk)if(!rst)begin
 if(native_cmd_valid&&native_cmd_ready)$fdisplay(tf,"N %0d %0d %0d %0d %0d %h",native_cmd_op,native_cmd_slot,native_cmd_page,native_cmd_offset,native_cmd_field,native_cmd_value);
 if(native_rsp_valid&&native_rsp_ready)$fdisplay(tf,"R %0d %0d %040h",native_rsp_status,native_rsp_present,native_rsp_payload);
 if(baseline_req_valid&&baseline_req_ready)begin misses=misses+1;$fdisplay(tf,"MISS %0d %h",baseline_req_node,baseline_req_epoch);end
 if(baseline_rsp_valid&&baseline_rsp_ready)$fdisplay(tf,"BASE %0d %0d %040h",baseline_rsp_node,baseline_rsp_status,baseline_rsp_payload);
end
task control(input integer op,status);begin
 @(negedge clk);ctrl_op=op;ctrl_valid=1;do @(posedge clk);while(!ctrl_ready);
 @(negedge clk);ctrl_valid=0;wait(ctrl_rsp_valid);#1;check(ctrl_status==status);
 repeat(3)begin @(posedge clk);#1;check(ctrl_rsp_valid&&ctrl_status==status);end
 @(negedge clk);ctrl_rsp_ready=1;@(posedge clk);@(negedge clk);ctrl_rsp_ready=0;
 $fdisplay(tf,"CTRL %0d %0d",op,status);
end endtask
task io(input integer n,wr,fi,input[31:0]val,input integer status,input[159:0]want);begin
 @(negedge clk);io_node=n;io_write=wr;io_field=fi;io_value=val;io_valid=1;
 do @(posedge clk);while(!io_ready);
 @(negedge clk);io_valid=0;io_node=32'hffffffff;io_value=0;
 wait(io_rsp_valid);#1;check(io_status==status&&io_payload==want&&(status!=0||io_present));
 repeat(4)begin @(posedge clk);#1;check(io_rsp_valid&&io_status==status&&io_payload==want);end
 $fdisplay(tf,"IO %0d %0d %0d %h %0d %040h",n,wr,fi,val,status,io_payload);
 @(negedge clk);io_rsp_ready=1;@(posedge clk);@(negedge clk);io_rsp_ready=0;
end endtask
task client(input integer n,input[159:0]want);begin
 @(negedge clk);resolve_page=n>>3;resolve_token=1;resolve_generation=1;resolve_phase=1;resolve_query=1;resolve_price=3;resolve_valid=1;
 do @(posedge clk);while(!resolve_ready);
 @(negedge clk);resolve_valid=0;wait(map_valid);#1;check(map_status==0);
 client_cmd_slot=map_slot;client_cmd_page=map_page;client_cmd_generation=map_binding_generation;client_cmd_query=1;client_cmd_price=3;client_cmd_op=2;client_cmd_field=2;client_cmd_offset=n%8;client_cmd_value=0;
 @(negedge clk);map_ready=1;@(posedge clk);@(negedge clk);map_ready=0;client_cmd_valid=1;
 do @(posedge clk);while(!client_cmd_ready);
 @(negedge clk);client_cmd_valid=0;wait(client_rsp_valid);#1;check(client_rsp_status==0&&client_rsp_present&&client_rsp_payload==want);
 repeat(5)begin @(posedge clk);#1;check(client_rsp_valid&&client_rsp_payload==want&&!idle&&!io_ready);end
 $fdisplay(tf,"CLIENT %0d %040h",n,client_rsp_payload);
 @(negedge clk);client_rsp_ready=1;@(posedge clk);@(negedge clk);client_rsp_ready=0;
end endtask
initial begin
'''+ '\n'.join(initial)+'''
 rst=1;client_quiescent=1;dispatch_enable=1;execute_enable=1;fence_service_enable=1;ack_receive_enable=1;
 baseline_epoch=64'h300010003;baseline_permit=1;ctrl_query=1;ctrl_price=3;io_query=1;io_price=3;
 if(!$value$plusargs("vectors=%s",path)||!$value$plusargs("trace=%s",trace))$fatal(1,"paths");
 fd=$fopen(path,"r");tf=$fopen(trace,"w");rc=$fscanf(fd,"%h %h %h",v0,v1,v8);check(rc==3);
 repeat(5)@(posedge clk);@(negedge clk);rst=0;cv=1;do @(posedge clk);while(!cy);@(negedge clk);cv=0;wait(crv);#1;check(cs==0);@(negedge clk);cr=1;@(posedge clk);@(negedge clk);cr=0;
 baseline_permit=0;control(0,1);check(!active);baseline_permit=1;control(0,0);baseline_epoch=77;
 phase=1;io(0,0,2,0,0,v0);check(misses==1);control(1,0);check(snapshot_clean);io(0,0,2,0,0,v0);check(misses==1);
 phase=2;want=v1;want[127:96]=32'h2c067;io(1,1,3,32'h2c067,0,want);check(misses==2);io(1,0,2,0,0,want);check(misses==2);
 phase=3;control(1,0);check(snapshot_clean);io(0,0,2,0,0,v0);io(1,0,2,0,0,want);check(misses==2);
 phase=4;client(8,v8);check(misses==3);control(1,0);check(snapshot_clean);client(8,v8);check(misses==3);
 phase=5;
`ifdef FAULT_DRAIN
 fork
  begin wait(bv&&by);@(negedge clk);injected_fault=1;end
  begin io(16,0,2,0,10,0);end
 join
 check(bidle);
`else
 inj=1;io(16,0,2,0,10,0);inj=0;
`endif
 check(fault&&misses==4&&!io_ready&&!snapshot_clean);
 $fdisplay(tf,"PASS %0d %0d",checks,misses);$fclose(tf);$display("BASELINE_MISS_PASS checks=%0d misses=%0d",checks,misses);$finish;
end
initial begin #3000000;$fatal(1,"miss watchdog phase%0d",phase);end
endmodule
'''
 return s
if __name__=='__main__':(HERE/'tb_miss.sv').write_text(make())
