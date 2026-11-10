from pathlib import Path
import importlib.util,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('parser',HERE.parent/'coordinate_v1/generate_top.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser);ports=parser.ports
paths={
 'g':HERE.parent/'graph_reader_v1/graph_static_reader.sv','d':HERE.parent/'design_store_v3/design_state_store.sv',
 'b':HERE.parent/'children_engine_v2/children_build_engine.sv','p':HERE.parent/'auto_pager_v1/paged_exclusion_engine.sv',
 'e':HERE.parent/'expansion_v1/expansion_controller.sv','m':HERE.parent/'metadata_v1/metadata_controller.sv',
 'a':HERE.parent/'access_service_v1/access_service.sv','s':HERE.parent/'access_fabric_v3/access_dispatch.sv',
 'c':HERE.parent/'coordinate_v1/coordinate_controller.sv','t':HERE.parent/'coordinate_v1/geometry_table_reader.sv',
 'o':HERE.parent/'owner_bridge_v1/owner_bridge.sv','u':HERE.parent/'owner_axi_v1/owner_state_store.sv',
 'k':HERE/'candidate_controller.sv'}
def bits(width):
 if not width:return 1
 high,low=map(int,width.strip('[]').split(':'));return high-low+1
def main():
 ps={pre:ports(path)for pre,path in paths.items()};ext={'clk':('input',''),'rst':('input',''),'abort':('input','')};wires={};con={};lines=[]
 def wire(name,width):
  if name not in ext:
   if name in wires:assert wires[name]==width,(name,wires[name],width)
   wires[name]=width
 for pre in ps:
  con[pre]={}
  for n,(direction,width)in ps[pre].items():
   expression=False;sig=pre+'_'+n
   if n in ['clk','rst']:sig=n
   elif pre in ['g','d','p','t','u']:
    if pre=='u':
     if n=='abort':sig='abort||stopped';expression=True
     elif n.startswith(('req_','rsp_'))or n=='fault':sig='o_b_'+n
     elif n=='busy':sig='u_busy'
    if n.startswith('m_')or(pre in ['g','d','t','u']and(n.startswith('cfg_')or n=='configured')):
     sig=('owner_'if pre=='u'else pre+'_')+n;ext[sig]=(direction,width)
    elif pre=='p'and n.startswith('ctrl_'):
     sig='p_'+n
     ext['host_'+n]=(direction,width)
    elif pre=='p'and n.startswith('io_'):sig='p_'+n
    elif pre=='p'and n in ['active','active_query','active_price']:sig='p_'+n;ext[sig]=(direction,width)
   elif pre=='b':sig='b_'+n
   elif pre=='e':
    if n.startswith(('b_','p_','d_claim_')):sig=n
    elif n in ['g_fault','d_fault']:sig=n+'||arb_'+n[0]+'_fault';expression=True
    elif n=='p_fault':sig='p_fault||arb_io_fault';expression=True
    elif n=='configuration_fault':sig='expansion_external_fault'
    elif n=='enable':sig='can_start'
    else:sig='e_'+n
   elif pre in ['m','a','s','c','o']:
    if n=='abort':sig='abort||stopped';expression=True
    elif n in ['active','active_query','active_price']:sig='p_'+n
    elif n=='enable':sig='operation_pending'
    elif pre=='m'and n=='claim_active':sig='d_claim_active'
    elif pre in ['m','c']and n=='nodes':sig='held_g_nodes'
    elif pre=='c'and n in ['table_rows','table_columns']:sig='held_t_'+n[6:]
    elif pre in ['m','c']and n=='g_fault':sig='g_fault||arb_g_fault';expression=True
    elif pre=='m'and n=='d_fault':sig='d_fault||arb_d_fault';expression=True
    elif pre=='c'and n=='p_fault':sig='p_fault||arb_io_fault';expression=True
    elif pre=='a'and n.startswith('svc_'):sig='s_'+('req_'+n[4:]if not n.startswith('svc_rsp_')else n[4:]);sig={'s_req_valid':'s_req_valid','s_req_ready':'s_req_ready','s_req_fault':'s_fault'}.get(sig,sig)
    elif pre=='s'and n.startswith(('c_','o_')):sig=n
    elif pre=='c'and n.startswith('t_'):sig=n
    elif pre=='o'and n.startswith('s_'):sig='o_'+n[2:]
    elif pre=='o'and n.startswith('h_'):sig='host_owner_'+n[2:];ext[sig]=(direction,width)
    elif pre=='o'and n=='decision_lock':sig='operation_pending'
    else:sig=pre+'_'+n
   elif pre=='k':
    if n in ['abort','active','active_query','active_price']:sig=n if n=='abort'else'p_'+n
    elif n=='nodes':sig='held_g_nodes'
    elif n=='enable':sig='can_start'
    elif n=='subsystem_fault':sig='subsystem_fault'
    elif n.startswith(('e_','m_','a_')):sig=n
    elif n in ['operation_pending','stopped']:sig=n
    else:sig=n;ext[sig]=(direction,width)
   if sig not in ['clk','rst','abort']and not expression:wire(sig,width)
   con[pre][n]=sig
 # Explicit connections whose names intentionally differ from service packet fields.
 con['a']['svc_valid']='s_req_valid';con['a']['svc_ready']='s_req_ready';con['a']['svc_fault']='s_fault'
 for pre in ['g','d','t','u']:
  for n in ps[pre]:
   if n.startswith('cfg_')or n=='configured':
    if pre!='u':continue
    # Owner configuration is already immutable after success; no operation can
    # start until its response retires. Still gate initial cfg against host work.
    if n=='cfg_valid':con[pre][n]='owner_cfg_valid&&!operation_pending&&!o_host_pending'
    elif n=='cfg_ready':con[pre][n]='owner_raw_cfg_ready';wire('owner_raw_cfg_ready','')
 for n,v in ps['d'].items():
  if n.startswith(('req_','rsp_')):ext['host_design_'+n]=v
 for n,v in ps['p'].items():
  if n.startswith('io_'):ext['host_'+n]=v
 ext['fault']=('output','');ext['busy']=('output','')
 for n in ['operation_pending','stopped','can_start','subsystem_fault','expansion_external_fault','configuration_fault','host_label_pending','host_design_pending','permit_label','permit_design']:
  if n in ['host_label_pending','host_design_pending']:continue
  wire(n,'')
 for n in ['held_g_nodes','held_d_nodes','held_owner_nodes','held_t_rows','held_t_columns']:wire(n,'[31:0]')
 # Declarations for the three shared request/response arbiters.
 def arb(name,clients,backend,req_fields,rsp_fields):
  rw=sum(bits(ps[backend][n][1])for n in req_fields);sw=sum(bits(ps[backend][n][1])for n in rsp_fields);nc=len(clients)
  for suffix,width in [('c_req_valid',f'[{nc-1}:0]'),('c_req_ready',f'[{nc-1}:0]'),('c_rsp_valid',f'[{nc-1}:0]'),('c_rsp_ready',f'[{nc-1}:0]'),('c_req_data',f'[{nc*rw-1}:0]'),('c_rsp_data',f'[{nc*sw-1}:0]'),('b_req_data',f'[{rw-1}:0]'),('b_rsp_data',f'[{sw-1}:0]'),('fault',''),('busy','')]:wire('arb_'+name+'_'+suffix,width)
  stem='arb_'+name
  for i,client in enumerate(clients):
   def cname(field):return client+'_'+field
   for field in req_fields+rsp_fields:wire(cname(field),ps[backend][field][1])
   for field in ['req_valid','req_ready','rsp_valid','rsp_ready']:wire(cname(field),'')
   lines.extend([f' assign {stem}_c_req_valid[{i}]={cname("req_valid")};',f' assign {cname("req_ready")}={stem}_c_req_ready[{i}];',f' assign {stem}_c_req_data[{i*rw}+:{rw}]={{'+','.join(cname(n)for n in req_fields)+'};',f' assign {cname("rsp_valid")}={stem}_c_rsp_valid[{i}];',f' assign {stem}_c_rsp_ready[{i}]={cname("rsp_ready")};',f' assign {{'+','.join(cname(n)for n in rsp_fields)+f'}}={stem}_c_rsp_data[{i*sw}+:{sw}];'])
  lines.extend([' assign {'+','.join(backend+'_'+n for n in req_fields)+'}='+stem+'_b_req_data;',' assign '+stem+'_b_rsp_data={'+','.join(backend+'_'+n for n in rsp_fields)+'};'])
  args={'clk':'clk','rst':'rst',**{n:stem+'_'+n for n in ['c_req_valid','c_req_ready','c_req_data','c_rsp_valid','c_rsp_ready','c_rsp_data','b_req_data','b_rsp_data','fault','busy']},'b_req_valid':backend+'_req_valid','b_req_ready':backend+'_req_ready','b_rsp_valid':backend+'_rsp_valid','b_rsp_ready':backend+'_rsp_ready'}
  lines.append(f' service_arbiter #(.CLIENTS({nc}),.REQUEST_BITS({rw}),.RESPONSE_BITS({sw})){name}_arb(\n'+',\n'.join('.'+n+'('+v+')'for n,v in args.items())+'\n);')
 arb('g',['e_g','m_g','c_g'],'g',['req_op','req_cookie','req_node','req_index'],['rsp_status','rsp_cookie','rsp_parent','rsp_index','rsp_node','rsp_start','rsp_count','rsp_attrs'])
 arb('d',['e_d','m_d','h_d'],'d',['req_op','req_cookie','req_owner','req_node','req_arg'],['rsp_status','rsp_cookie','rsp_flags','rsp_count','rsp_mask'])
 # Pager IO uses legacy valid/node/value/field names rather than req_*.
 io_req=['write','node','value','field'];io_rsp=['status','payload','present'];rw=68;sw=165
 for suffix,width in [('c_req_valid','[2:0]'),('c_req_ready','[2:0]'),('c_rsp_valid','[2:0]'),('c_rsp_ready','[2:0]'),('c_req_data','[203:0]'),('c_rsp_data','[494:0]'),('b_req_data','[67:0]'),('b_rsp_data','[164:0]'),('fault',''),('busy','')]:wire('arb_io_'+suffix,width)
 for i,client in enumerate(['c_p_io','s_l','h_io']):
  for field,width in [('valid',''),('ready',''),('write',''),('node','[31:0]'),('value','[31:0]'),('field','[2:0]'),('rsp_valid',''),('rsp_ready',''),('status','[3:0]'),('payload','[159:0]'),('present','')]:wire(client+'_'+field,width)
  # All clients use status/payload/present without rsp_ qualifiers.
  rnames=[client+'_'+n for n in io_rsp]
  lines.extend([f' assign arb_io_c_req_valid[{i}]={client}_valid;',f' assign {client}_ready=arb_io_c_req_ready[{i}];',f' assign arb_io_c_req_data[{i*rw}+:{rw}]={{'+','.join(client+'_'+n for n in io_req)+'};',f' assign {client}_rsp_valid=arb_io_c_rsp_valid[{i}];',f' assign arb_io_c_rsp_ready[{i}]={client}_rsp_ready;',f' assign {{'+','.join(rnames)+f'}}=arb_io_c_rsp_data[{i*sw}+:{sw}];'])
 lines+=[' assign {p_io_write,p_io_node,p_io_value,p_io_field}=arb_io_b_req_data;',' assign arb_io_b_rsp_data={p_io_status,p_io_payload,p_io_present};']
 args={'clk':'clk','rst':'rst',**{n:'arb_io_'+n for n in ['c_req_valid','c_req_ready','c_req_data','c_rsp_valid','c_rsp_ready','c_rsp_data','b_req_data','b_rsp_data','fault','busy']},'b_req_valid':'p_io_valid','b_req_ready':'p_io_ready','b_rsp_valid':'p_io_rsp_valid','b_rsp_ready':'p_io_rsp_ready'}
 lines.append(' service_arbiter #(.CLIENTS(3),.REQUEST_BITS(68),.RESPONSE_BITS(165))io_arb(\n'+',\n'.join('.'+n+'('+v+')'for n,v in args.items())+'\n);')
 # The coordinate controller's IO response names include no rsp_ prefix except valid/ready.
 for n in ['status','payload','present']:con['c']['p_io_'+n]='c_p_io_'+n
 # Host design and label clients are accepted only outside a complete operation.
 for n in ['req_op','req_cookie','req_owner','req_node','req_arg']:lines.append(' assign h_d_'+n+'=host_design_'+n+';')
 lines+=[' assign h_d_req_valid=host_design_req_valid&&permit_design;',' assign host_design_req_ready=h_d_req_ready&&permit_design;',' assign host_design_rsp_valid=h_d_rsp_valid;',' assign h_d_rsp_ready=host_design_rsp_ready;']
 for n in ['rsp_status','rsp_cookie','rsp_flags','rsp_count','rsp_mask']:lines.append(' assign host_design_'+n+'=h_d_'+n+';')
 lines+=[' assign h_io_valid=host_io_valid&&permit_label&&!host_ctrl_valid;',' assign host_io_ready=h_io_ready&&permit_label&&!host_ctrl_valid;',' assign host_io_rsp_valid=h_io_rsp_valid;',' assign h_io_rsp_ready=host_io_rsp_ready;']
 for n in io_req:lines.append(' assign h_io_'+n+'=host_io_'+n+';')
 for n in io_rsp:lines.append(' assign host_io_'+('rsp_valid'if n=='valid'else n)+'=h_io_'+n+';')
 for n,(direction,width)in ps['p'].items():
  if n.startswith('ctrl_'):
   if n=='ctrl_valid':lines.append(' assign p_ctrl_valid=host_ctrl_valid&&permit_label;')
   elif n=='ctrl_ready':lines.append(' assign host_ctrl_ready=p_ctrl_ready&&permit_label;')
   elif direction=='input':lines.append(' assign p_'+n+'=host_'+n+';')
   else:lines.append(' assign host_'+n+'=p_'+n+';')
  elif n in ['dispatch_enable','execute_enable','fence_service_enable','ack_receive_enable']:lines.append(' assign p_'+n+'=1;')
 reg_names=['held_g_nodes','held_d_nodes','held_owner_nodes','held_t_rows','held_t_columns']
 decl=[' reg[31:0]'+','.join(reg_names)+';',' reg host_label_pending,host_design_pending;']
 for n in reg_names:wires.pop(n)
 lines+=[' assign owner_cfg_ready=owner_raw_cfg_ready&&!operation_pending&&!o_host_pending;',
 ' assign configuration_fault=g_configured&&d_configured&&owner_configured&&(held_g_nodes!=held_d_nodes||held_g_nodes!=held_owner_nodes);',
 ' assign expansion_external_fault=configuration_fault||stopped||abort||m_fault||a_fault||s_fault||c_fault||o_fault||o_b_fault||t_fault||arb_g_fault||arb_d_fault||arb_io_fault;',
 ' assign subsystem_fault=e_fault||b_fault||g_fault||d_fault||p_fault||expansion_external_fault;',
 ' assign fault=subsystem_fault||stopped;',
 ' assign busy=operation_pending||host_label_pending||host_design_pending||o_host_pending;',
 ' assign permit_label=!rst&&!fault&&!operation_pending&&!host_label_pending;',
 ' assign permit_design=!rst&&!fault&&!operation_pending&&!host_design_pending;',
 ' assign can_start=g_configured&&d_configured&&t_configured&&owner_configured&&p_active&&!configuration_fault&&!operation_pending&&!host_label_pending&&!host_design_pending&&!o_host_pending&&!host_ctrl_valid&&!host_io_valid&&!host_design_req_valid&&!host_owner_req_valid&&!g_cfg_rsp_valid&&!d_cfg_rsp_valid&&!t_cfg_rsp_valid&&!owner_cfg_rsp_valid&&!g_cfg_valid&&!d_cfg_valid&&!t_cfg_valid&&!owner_cfg_valid&&!d_claim_active;',
 ' always @(posedge clk)begin',
 '  if(rst)begin held_g_nodes<=0;held_d_nodes<=0;held_owner_nodes<=0;held_t_rows<=0;held_t_columns<=0;host_label_pending<=0;host_design_pending<=0;end',
 '  else begin',
 '   if(g_cfg_valid&&g_cfg_ready)held_g_nodes<=g_cfg_nodes;',
 '   if(d_cfg_valid&&d_cfg_ready)held_d_nodes<=d_cfg_nodes;',
 '   if(owner_cfg_valid&&owner_cfg_ready)held_owner_nodes<=owner_cfg_nodes;',
 '   if(t_cfg_valid&&t_cfg_ready)begin held_t_rows<=t_cfg_rows;held_t_columns<=t_cfg_columns;end',
 '   if((host_ctrl_valid&&host_ctrl_ready)||(host_io_valid&&host_io_ready))host_label_pending<=1;',
 '   if((host_ctrl_rsp_valid&&host_ctrl_rsp_ready)||(host_io_rsp_valid&&host_io_rsp_ready))host_label_pending<=0;',
 '   if(host_design_req_valid&&host_design_req_ready)host_design_pending<=1;',
 '   if(host_design_rsp_valid&&host_design_rsp_ready)host_design_pending<=0;',
 '  end',
 ' end']
 modules={'g':'graph_static_reader','d':'design_state_store','p':'paged_exclusion_engine #(.SLOTS(SLOTS),.TX_BITS(TX_BITS),.GEN_BITS(GEN_BITS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),.PROBE_LIMIT(PROBE_LIMIT),.EPOCH_BITS(EPOCH_BITS))','b':'children_build_engine','e':'expansion_controller #(.TOKEN_BITS(TOKEN_BITS),.OWNER_BITS(OWNER_BITS))','m':'metadata_controller #(.TOKEN_BITS(TOKEN_BITS))','a':'access_service #(.TOKEN_BITS(TOKEN_BITS))','s':'access_dispatch #(.MAX_CYCLES((1<<HASH_BITS)+262144))','c':'coordinate_controller #(.TOKEN_BITS(TOKEN_BITS),.MAX_CYCLES((1<<HASH_BITS)+262144))','t':'geometry_table_reader','o':'owner_bridge','u':'owner_state_store','k':'candidate_controller #(.MAX_CYCLES(MAX_CYCLES))'}
 # Remove declaration aliases that were replaced with shared service nets.
 declared=[' wire '+width+' '+n+';'for n,width in wires.items()if n not in ext]
 text=['`timescale 1ns/1ps','module candidate_engine #(parameter integer SLOTS=32,TX_BITS=16,GEN_BITS=16,FRAMES=163840,INDEX_BITS=18,HASH_BITS=18,PROBE_LIMIT=64,EPOCH_BITS=16,TOKEN_BITS=32,OWNER_BITS=32,MAX_CYCLES=33554432)(', ',\n'.join(' '+d+' wire '+w+' '+n for n,(d,w)in ext.items()),');']+decl+declared+lines
 for pre,module in modules.items():text.append(' '+module+' '+{'e':'expansion','m':'metadata','a':'access','s':'dispatch','c':'coordinates','u':'owner_store','o':'owners','k':'controller'}.get(pre,pre)+'(\n'+',\n'.join('.'+n+'('+v+')'for n,v in con[pre].items())+'\n);')
 text.append('endmodule');(HERE/'candidate_engine.sv').write_text('\n'.join(text)+'\n')
if __name__=='__main__':main()
