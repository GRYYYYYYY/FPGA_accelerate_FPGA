from pathlib import Path
s=Path('hardware/variants/candidate_prefetch_v1/candidate_prefetch_query_core.sv').read_text().replace('module candidate_prefetch_query_core #(','module candidate_postprev_query_core #(',1)
ports=''' input wire post_l_valid,output wire post_l_ready,input wire post_l_write,
 input wire [31:0] post_l_node,post_l_value,input wire [2:0] post_l_field,
 output wire post_l_rsp_valid,input wire post_l_rsp_ready,output wire [3:0] post_l_status,output wire [159:0] post_l_payload,output wire post_l_present,
 input wire post_c_req_valid,output wire post_c_req_ready,input wire [31:0] post_c_req_cookie,post_c_req_node,
 input wire [1:0] post_c_req_query,input wire [3:0] post_c_req_price,
 output wire post_c_rsp_valid,input wire post_c_rsp_ready,output wire [3:0] post_c_rsp_status,
 output wire [31:0] post_c_rsp_cookie,post_c_rsp_node,post_c_rsp_y,post_c_rsp_label_prev,
 output wire [255:0] post_c_rsp_attrs,output wire [1:0] post_c_rsp_op,post_c_rsp_query,output wire [3:0] post_c_rsp_price,output wire post_c_rsp_prev_read,
'''
s=s.replace(' input wire p_o_req_valid,',ports+' input wire p_o_req_valid,',1)
for name in ['req_valid','req_ready','rsp_valid','rsp_ready']:s=s.replace('wire [2:0] arb_io_c_'+name,'wire [3:0] arb_io_c_'+name)
s=s.replace('wire [203:0] arb_io_c_req_data','wire [271:0] arb_io_c_req_data').replace('wire [494:0] arb_io_c_rsp_data','wire [659:0] arb_io_c_rsp_data')
s=s.replace(' assign {p_io_write,p_io_node,p_io_value,p_io_field}', ''' assign arb_io_c_req_valid[3]=post_l_valid;
 assign post_l_ready=arb_io_c_req_ready[3];
 assign arb_io_c_req_data[204+:68]={post_l_write,post_l_node,post_l_value,post_l_field};
 assign post_l_rsp_valid=arb_io_c_rsp_valid[3];
 assign arb_io_c_rsp_ready[3]=post_l_rsp_ready;
 assign {post_l_status,post_l_payload,post_l_present}=arb_io_c_rsp_data[495+:165];
 assign {p_io_write,p_io_node,p_io_value,p_io_field}''',1)
s=s.replace('service_arbiter #(.CLIENTS(3),.REQUEST_BITS(68),.RESPONSE_BITS(165))io_arb','service_arbiter #(.CLIENTS(4),.REQUEST_BITS(68),.RESPONSE_BITS(165))io_arb')
reqfields=[('op',2),('query',2),('price',4),('cookie',32),('node',32)]
rspfields=[('status',4),('op',2),('query',2),('price',4),('cookie',32),('node',32),('y',32),('slr',32),('next',32),('prev_column',32),('label_prev',32),('north',1),('prev_read',1),('prev_present',1),('attrs',256)]
assert sum(w for _,w in rspfields)==495
logic=' wire pc_arb_fault,pc_arb_busy;\n'
for direction,fields in [('req',reqfields),('rsp',rspfields)]:
 logic+=f' wire mc_{direction}_valid,mc_{direction}_ready;\n'
 for name,width in fields:logic+=f' wire [{width-1}:0] mc_{direction}_{name};\n'
for name in ['slr','next','prev_column']:logic+=f' wire [31:0] post_c_rsp_{name};\n'
logic+=' wire post_c_rsp_north,post_c_rsp_prev_present;\n'
logic+=' wire [1:0] pc_rv,pc_rr,pc_sv,pc_sr;wire [143:0] pc_rd;wire [989:0] pc_sd;wire [71:0] pc_bd;wire [494:0] pc_bs;\n'
logic+=' assign pc_rv={post_c_req_valid,c_req_valid};assign {post_c_req_ready,c_req_ready}=pc_rr;\n'
logic+=' assign pc_rd[0+:72]={'+','.join('c_req_'+n for n,_ in reqfields)+'};\n'
logic+=" assign pc_rd[72+:72]={2'd0,post_c_req_query,post_c_req_price,post_c_req_cookie,post_c_req_node};\n"
logic+=' assign {post_c_rsp_valid,c_rsp_valid}=pc_sv;assign pc_sr={post_c_rsp_ready,c_rsp_ready};\n'
for index,prefix in enumerate(['c_rsp_','post_c_rsp_']):logic+=' assign {'+','.join(prefix+n for n,_ in rspfields)+f'}}=pc_sd[{index*495}+:495];\n'
logic+=' assign {'+','.join('mc_req_'+n for n,_ in reqfields)+'}=pc_bd;\n'
logic+=' assign pc_bs={'+','.join('mc_rsp_'+n for n,_ in rspfields)+'};\n'
logic+=''' service_arbiter #(.CLIENTS(2),.REQUEST_BITS(72),.RESPONSE_BITS(495))post_coordinate_arb(
 .clk(clk),.rst(rst),.c_req_valid(pc_rv),.c_req_ready(pc_rr),.c_req_data(pc_rd),.c_rsp_valid(pc_sv),.c_rsp_ready(pc_sr),.c_rsp_data(pc_sd),
 .b_req_valid(mc_req_valid),.b_req_ready(mc_req_ready),.b_req_data(pc_bd),.b_rsp_valid(mc_rsp_valid),.b_rsp_ready(mc_rsp_ready),.b_rsp_data(pc_bs),.busy(pc_arb_busy),.fault(pc_arb_fault));
'''
a=s.index(' coordinate_controller #');b=s.index('\n);',a)+3;part=s[a:b]
for direction,fields in [('req',reqfields),('rsp',rspfields)]:
 for name,_ in [('valid',1),('ready',1)]+fields:part=part.replace('('+f'c_{direction}_{name}'+')','('+f'mc_{direction}_{name}'+')')
s=s[:a]+logic+part+s[b:]
# Fault declaration before use; other declarations above instance are already in scope.
s=s.replace(' wire  c_fault;',' wire  c_fault;\n wire pc_arb_fault,pc_arb_busy;',1).replace(' wire pc_arb_fault,pc_arb_busy;\n wire mc_req_valid',' wire mc_req_valid',1)
s=s.replace('||c_fault||','||c_fault||pc_arb_fault||')
Path('hardware/variants/candidate_postprev_v1/candidate_postprev_query_core.sv').write_text(s)
