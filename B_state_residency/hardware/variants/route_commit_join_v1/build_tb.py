from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def make():
 s=(ROOT/'hardware/variants/shared_ripup_v1/tb_shared_ripup.sv').read_text();connections={}
 # Map both complete host services through the synthesizable adapter.
 lm={'valid':'valid','ready':'ready','write':'write','node':'node','value':'value','field':'field','rsp_valid':'rsp_valid','rsp_ready':'rsp_ready','status':'status','present':'present','payload':'payload'}
 om={'req_valid':'valid','req_ready':'ready','req_op':'op','req_node':'node','req_net':'net','req_cookie':'cookie','rsp_valid':'rsp_valid','rsp_ready':'rsp_ready','rsp_status':'status','rsp_cookie':'rsp_cookie','rsp_count':'count','rsp_occupancy':'occupancy','rsp_will_overuse':'will_overuse'}
 decl='reg rc_req_valid=0,rc_req_op=0,rc_req_slot=0,rc_rsp_ready=0;reg[31:0]rc_req_cookie=0,rc_req_sink=0,rc_req_sequence=0;wire rc_req_ready,rc_rsp_valid,rc_block,rc_fault,rc_busy;wire[3:0]rc_rsp_status;wire[31:0]rc_rsp_cookie,rc_rsp_nodes,rc_rsp_acked;wire[1:0]rc_slots;\n'
 def wire(name,width=1):return 'wire '+(f'[{width-1}:0] 'if width>1 else '')+name+';\n'
 widths={'node':32,'value':32,'field':3,'status':4,'payload':160,'op':3,'net':32,'cookie':32,'rsp_cookie':32,'count':32,'occupancy':32}
 binds=[]
 for prefix,mapping,tag in [('host_io_',lm,'l'),('host_owner_',om,'o')]:
  for old,new in mapping.items():
   name=prefix+old;b='b_'+tag+'_'+new;connections[name]=b;decl+=wire(b,widths.get(new,1));binds.append(f'.h_{tag}_{new}({name})');binds.append(f'.b_{tag}_{new}({b})')
 # Every non-service admission/config entry is fenced bidirectionally.
 pairs=[('host_ctrl_valid','host_ctrl_ready'),('host_design_req_valid','host_design_req_ready'),('expand_valid','expand_ready'),('seed_valid','seed_ready')]+[(p+'_cfg_valid',p+'_cfg_ready')for p in ['q','g','d','t','owner','cs']]
 for valid,ready in pairs:
  connections[valid]=f'({valid}&&!rc_block)';raw='raw_'+ready;connections[ready]=raw;decl+=wire(raw)+f'assign {ready}=!rc_block&&{raw};\n'
  # ready formerly a wire, remains externally gated.
 valid_inputs=[v for v,_ in pairs]+['host_io_valid','host_owner_req_valid']
 pending=['b_l_rsp_valid','b_o_rsp_valid','host_ctrl_rsp_valid','host_design_rsp_valid','seed_rsp_valid','result_valid']+[p+'_cfg_rsp_valid'for p in ['q','g','d','t','owner','cs']]
 admit='!busy&&'+ '&&'.join('!'+x for x in valid_inputs+pending)
 decl+='route_commit_host_adapter #(.MAX_PATH(32)) route_join(.clk(clk),.rst(rst),.abort(1\'b0),.active(p_active),.admit('+admit+'),.active_query(p_active_query),.active_price(p_active_price),.active_version(query_version),.active_design(design_id),.req_valid(rc_req_valid),.req_ready(rc_req_ready),.req_op(rc_req_op),.req_slot(rc_req_slot),.req_cookie(rc_req_cookie),.req_source(32\'d65185),.req_sink(rc_req_sink),.req_net(32\'d2717),.req_sequence(rc_req_sequence),.rsp_valid(rc_rsp_valid),.rsp_ready(rc_rsp_ready),.rsp_status(rc_rsp_status),.rsp_cookie(rc_rsp_cookie),.rsp_nodes(rc_rsp_nodes),.rsp_acked(rc_rsp_acked),.busy(rc_busy),.fault(rc_fault),.block_external(rc_block),.slot_valid(rc_slots),'+','.join(binds)+');\n'
 needle='candidate_recursive_engine #(.SLOTS(SLOTS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS))dut(.*);';assert needle in s
 s=s.replace(needle,decl+needle.replace('(.*);','('+','.join('.'+k+'('+v+')'for k,v in connections.items())+',.*);'))
 # Observers save only the nodes actually issued by the new controller.
 observer='''
reg[31:0]rc_read_node;integer route_commands=0;
always @(posedge clk)if(!rst)begin
 if(rc_block)begin
'''+''.join(f' if({v}&&{r})$fatal(1,"route fence {v}");\n'for v,r in pairs)+'''
 end
 if(route_join.l_valid&&route_join.l_ready)begin rc_read_node<=route_join.l_node;$fdisplay(trace,"RL %0d %0d %0d",cycles,rc_req_slot,route_join.l_node);end
 if(route_join.l_rsp_valid&&route_join.l_rsp_ready)$fdisplay(trace,"RA %0d %0d %0d %040h",cycles,rc_req_slot,rc_read_node,b_l_payload);
 if(route_join.o_valid&&route_join.o_ready)begin
  $fdisplay(trace,"RO %0d %0d %0d %0d",cycles,rc_req_slot,route_join.o_op,route_join.o_node);
  if(route_join.o_op==1)begin
   if(rc_req_slot==0)begin saved1[count1]<=route_join.o_node;count1<=count1+1;end
   else begin saved2[count2]<=route_join.o_node;count2<=count2+1;end
  end
 end
 if(route_join.o_rsp_valid&&route_join.o_rsp_ready)$fdisplay(trace,"RB %0d %0d %0d %0d %0d",cycles,rc_req_slot,b_o_status,b_o_count,b_o_occupancy);
end
'''
 a=s.index('initial begin\n trace=$fopen')
 task='''
task route_command(input integer op,slot,sink,sequence_id);begin
 @(negedge clk);rc_req_op=op;rc_req_slot=slot;rc_req_sink=sink;rc_req_sequence=sequence_id;rc_req_cookie=32'hf0000000+route_commands;rc_req_valid=1;
 do @(posedge clk);while(!rc_req_ready);@(negedge clk);rc_req_valid=0;
'''+''.join(f' {v}=1;\n'for v in valid_inputs)+'''
 wait(rc_rsp_valid);@(negedge clk);
 if(rc_rsp_status||rc_rsp_cookie!=32'hf0000000+route_commands||rc_rsp_nodes!=6||rc_rsp_acked!=6||rc_fault)$fatal(1,"route controller result");
 repeat(5)begin @(negedge clk);if(!rc_rsp_valid||!rc_block||host_io_ready||host_owner_req_ready)$fatal(1,"route response fence");end
 $fdisplay(trace,"RC %0d %0d %0d %0d %0d",cycles,op,slot,rc_rsp_nodes,rc_rsp_acked);
'''+''.join(f' {v}=0;\n'for v in valid_inputs)+'''
 rc_rsp_ready=1;@(negedge clk);rc_rsp_ready=0;wait(!rc_block);@(negedge clk);route_commands=route_commands+1;
end endtask
'''
 s=s[:a]+observer+task+s[a:]
 a=s.index('  // Read actual prev links;');b=s.index('  label_write(150697',a);s=s[:a]+'  route_command(0,0,150697,1);\n'+s[b:]
 a=s.index(' // Save second actual path');b=s.index(' control(1);control(2);',a)
 s=s[:a]+''' stage_no=0;probe_owners;
 stage_no=1;route_command(0,1,128009,2);probe_owners;
 stage_no=2;route_command(1,0,150697,1);probe_owners;
 stage_no=3;route_command(1,1,128009,2);probe_owners;
 if(rc_slots!=0||count1!=6||count2!=6||route_commands!=4||rc_fault)$fatal(1,"route final state");
'''+s[b:]
 return s
if __name__=='__main__':(Path(__file__).parent/'tb_route_join.sv').write_text(make())
