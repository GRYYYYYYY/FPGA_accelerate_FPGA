from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def make():
 s=(ROOT/'hardware/variants/continuous_query_v1/tb_continuous_query.sv').read_text()
 s=s.replace('integer query_index,next_node,path_steps;','integer query_index,next_node,path_steps;\nreg[31:0]saved1[0:31],saved2[0:31];integer count1=0,count2=0,stage_no,pi,pj,expected_refs,probe_node;')
 s=s.replace('   route_node=next_node;path_steps=path_steps+1;','   route_node=next_node;path_steps=path_steps+1;\n   if(route_node!=65185)begin saved1[count1]=route_node;count1=count1+1;end')
 pos=s.index('initial begin\n trace=$fopen')
 tasks=r'''
task owner_op(input integer op,input[31:0]node,input integer want_refs,input integer want_occ);begin
 @(negedge clk);host_owner_req_op=op;host_owner_req_cookie=32'he0000000+node;host_owner_req_node=node;host_owner_req_net=2717;host_owner_req_valid=1;
 do @(posedge clk);while(!host_owner_req_ready);@(negedge clk);host_owner_req_valid=0;
 wait(host_owner_rsp_valid);@(negedge clk);
 if(host_owner_rsp_status||host_owner_rsp_cookie!=32'he0000000+node||host_owner_rsp_count!=want_refs||host_owner_rsp_occupancy!=want_occ)$fatal(1,"owner stage=%0d op=%0d node=%0d refs=%0d occ=%0d expected=%0d %0d",stage_no,op,node,host_owner_rsp_count,host_owner_rsp_occupancy,want_refs,want_occ);
 $fdisplay(trace,"SO %0d %0d %0d %0d %0d %0d",cycles,stage_no,op,node,host_owner_rsp_count,host_owner_rsp_occupancy);
 host_owner_rsp_ready=1;@(negedge clk);host_owner_rsp_ready=0;
end endtask
function integer in_first(input[31:0]node);integer k;begin in_first=0;for(k=0;k<count1;k=k+1)if(saved1[k]==node)in_first=1;end endfunction
function integer in_second(input[31:0]node);integer k;begin in_second=0;for(k=0;k<count2;k=k+1)if(saved2[k]==node)in_second=1;end endfunction
task probe_owners;integer k,node,refs;begin
 for(k=0;k<count1+count2;k=k+1)begin
  node=k<count1?saved1[k]:saved2[k-count1];
  refs=stage_no==0?in_first(node):stage_no==1?in_first(node)+in_second(node):stage_no==2?in_second(node):0;
  owner_op(0,node,refs,refs!=0);
 end
 $fdisplay(trace,"ST %0d %0d",cycles,stage_no);
end endtask
'''
 s=s[:pos]+tasks+s[pos:]
 needle=' control(1);control(2);'
 extra=r'''
 // Save second actual path before any future search can overwrite prev.
 route_node=128009;path_steps=0;
 while(route_node!=65185)begin
  label_read(route_node);next_node=host_record[95:64];
  $fdisplay(trace,"B2 %0d %0d %0d",cycles,route_node,next_node);
  if(next_node==32'hffffffff||path_steps>32)$fatal(1,"q2 backtrace chain");
  route_node=next_node;path_steps=path_steps+1;
  if(route_node!=65185)begin saved2[count2]=route_node;count2=count2+1;end
 end
 if(count1!=6||count2!=6||path_steps!=7)$fatal(1,"saved paths");
 stage_no=0;probe_owners;
 stage_no=1;
 for(pi=0;pi<count2;pi=pi+1)owner_op(1,saved2[pi],1+in_first(saved2[pi]),1);
 probe_owners;
 stage_no=2;
 for(pi=0;pi<count1;pi=pi+1)owner_op(2,saved1[pi],in_second(saved1[pi]),in_second(saved1[pi])!=0);
 probe_owners;
 stage_no=3;
 for(pi=0;pi<count2;pi=pi+1)owner_op(2,saved2[pi],0,0);
 probe_owners;
'''
 assert needle in s;s=s.replace(needle,extra+needle,1);return s
if __name__=='__main__':(Path(__file__).parent/'tb_shared_ripup.sv').write_text(make())
