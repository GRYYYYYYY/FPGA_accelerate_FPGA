from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def derive(s):
 s=s.replace('module candidate_postprev_engine','module candidate_params_engine',1)
 ports='''input wire [31:0] expand_connection,
input wire q_cfg_valid,output wire q_cfg_ready,input wire [63:0] q_cfg_base,q_cfg_design,
input wire [31:0] q_cfg_connections,q_cfg_nodes,q_cfg_nets,q_cfg_revision,
output wire q_cfg_rsp_valid,input wire q_cfg_rsp_ready,output wire [2:0] q_cfg_status,output wire q_configured,
output wire out_params_valid,output wire [511:0] out_params,output wire [31:0] out_connection,out_profile_revision,
output wire q_busy,q_fault,
output wire [63:0] q_m_araddr,output wire [7:0] q_m_arlen,output wire [2:0] q_m_arsize,output wire [1:0] q_m_arburst,output wire [3:0] q_m_arid,
output wire q_m_arvalid,input wire q_m_arready,input wire [511:0] q_m_rdata,input wire [3:0] q_m_rid,input wire [1:0] q_m_rresp,input wire q_m_rlast,q_m_rvalid,output wire q_m_rready,
'''
 s=s.replace('output wire out_post_valid',ports+'output wire out_post_valid',1)
 decl='''wire q_req_ready,q_rsp_valid,q_cfg_raw_ready,raw_result_valid,raw_result_ready;
wire [3:0] q_rsp_status;wire [511:0] q_rsp_data;
wire [31:0] q_rsp_cookie,q_rsp_connection,q_rsp_net,q_rsp_sink,q_rsp_cross,q_rsp_version,q_rsp_revision;
wire [1:0] q_rsp_query;wire [3:0] q_rsp_price;wire [63:0] q_rsp_design,q_design;
wire [31:0] q_nodes,q_nets,q_connections,q_revision;
reg q_pending,q_meta_valid,q_stopped;reg [511:0] q_meta;
reg [31:0] q_cookie,q_connection,q_net,q_sink,q_cross,q_version,q_profile,cost_nets;
reg [1:0] q_query;reg [3:0] q_price;reg [63:0] q_design_held;
wire q_lease=q_pending||q_busy;
wire q_identity_error;
'''
 s=s.replace('wire raw_cs_req_valid,raw_cs_req_ready;',decl+'wire raw_cs_req_valid,raw_cs_req_ready;',1)
 s=s.replace('assign post_req_valid=','assign post_req_valid=q_meta_valid&&',1).replace('assign out_valid=','assign out_valid=q_meta_valid&&',1)
 s=s.replace('cost_lease||cc_busy||prefetch_busy||post_busy;','cost_lease||cc_busy||prefetch_busy||post_busy||q_lease;',1)
 s=s.replace('!(cc_busy||prefetch_busy||post_busy)','!(cc_busy||prefetch_busy||post_busy||q_lease)')
 s=s.replace('assign all_configured=g_configured','assign all_configured=q_configured&&!q_cfg_rsp_valid&&g_configured',1)
 s=s.replace('assign configuration_fault=','assign configuration_fault=(q_configured&&g_configured&&cs_configured&&(q_nodes!=g_nodes||q_nets!=cost_nets||q_design!=design_id))||',1)
 s=s.replace('assign fault=','assign fault=q_fault||q_stopped||q_identity_error||',1)
 s=s.replace('if(post_fault||post_identity_error||frontier_fault','if(q_fault||q_stopped||q_identity_error||post_fault||post_identity_error||frontier_fault',1)
 s=s.replace('.result_valid(result_valid)','.result_valid(raw_result_valid)',1).replace('.result_ready(result_ready)','.result_ready(raw_result_ready)',1)
 logic='''assign q_cfg_ready=q_cfg_raw_ready&&!state_lease&&!fault;
assign out_params_valid=q_meta_valid&&operation_pending;
assign out_params=q_meta;assign out_connection=q_connection;assign out_profile_revision=q_profile;
assign result_valid=raw_result_valid&&q_meta_valid;
assign raw_result_ready=result_ready&&q_meta_valid;
assign q_identity_error=q_meta_valid&&operation_pending&&(!p_active||p_active_query!=q_query||p_active_price!=q_price||query_version!=q_version||design_id!=q_design_held);
always @(posedge clk)begin
 if(rst)begin q_pending<=0;q_meta_valid<=0;q_stopped<=0;q_meta<=0;q_cookie<=0;q_connection<=0;q_net<=0;q_sink<=0;q_cross<=0;q_version<=0;q_profile<=0;q_query<=0;q_price<=0;q_design_held<=0;cost_nets<=0;end
 else begin
  if(cs_cfg_valid&&cs_cfg_ready)cost_nets<=cs_cfg_net_count;
  if(q_pending&&q_req_ready)q_pending<=0;
  if(expand_valid&&expand_ready)begin
   q_pending<=1;q_meta_valid<=0;q_cookie<=expand_cookie;q_connection<=expand_connection;q_net<=expand_net;q_sink<=expand_sink;q_cross<=expand_flags&32'h18;
   q_version<=query_version;q_query<=p_active_query;q_price<=p_active_price;q_design_held<=design_id;q_profile<=q_revision;
  end
  if(q_rsp_valid)begin
   if(q_rsp_status!=0||q_rsp_cookie!=q_cookie||q_rsp_connection!=q_connection||q_rsp_net!=q_net||q_rsp_sink!=q_sink||q_rsp_cross!=q_cross||q_rsp_query!=q_query||q_rsp_price!=q_price||q_rsp_version!=q_version||q_rsp_design!=q_design_held||q_rsp_revision!=q_profile)q_stopped<=1;
   else begin q_meta<=q_rsp_data;q_meta_valid<=1;end
  end
 end
end
connection_state_reader #(.MAX_CYCLES(MAX_CYCLES)) params_reader(
 .clk(clk),.rst(rst),.abort(abort||fence_stopped),
 .cfg_valid(q_cfg_valid&&!state_lease&&!fault),.cfg_ready(q_cfg_raw_ready),.cfg_base(q_cfg_base),.cfg_design(q_cfg_design),.cfg_connections(q_cfg_connections),.cfg_nodes(q_cfg_nodes),.cfg_nets(q_cfg_nets),.cfg_revision(q_cfg_revision),.cfg_rsp_valid(q_cfg_rsp_valid),.cfg_rsp_ready(q_cfg_rsp_ready),.cfg_status(q_cfg_status),.configured(q_configured),.design_id(q_design),.nodes(q_nodes),.nets(q_nets),.connections(q_connections),.revision(q_revision),
 .query_active(p_active),.decision_lock(operation_pending),.active_query(p_active_query),.active_price(p_active_price),.active_version(query_version),.active_design(design_id),
 .req_valid(q_pending),.req_ready(q_req_ready),.req_cookie(q_cookie),.req_connection(q_connection),.req_net(q_net),.req_sink(q_sink),.req_cross(q_cross),.req_version(q_version),.req_query(q_query),.req_price(q_price),.req_design(q_design_held),
 .rsp_valid(q_rsp_valid),.rsp_ready(1'b1),.rsp_status(q_rsp_status),.rsp_cookie(q_rsp_cookie),.rsp_connection(q_rsp_connection),.rsp_net(q_rsp_net),.rsp_sink(q_rsp_sink),.rsp_cross(q_rsp_cross),.rsp_version(q_rsp_version),.rsp_revision(q_rsp_revision),.rsp_query(q_rsp_query),.rsp_price(q_rsp_price),.rsp_design(q_rsp_design),.rsp_data(q_rsp_data),.busy(q_busy),.fault(q_fault),
 .m_araddr(q_m_araddr),.m_arlen(q_m_arlen),.m_arsize(q_m_arsize),.m_arburst(q_m_arburst),.m_arid(q_m_arid),.m_arvalid(q_m_arvalid),.m_arready(q_m_arready),.m_rdata(q_m_rdata),.m_rid(q_m_rid),.m_rresp(q_m_rresp),.m_rlast(q_m_rlast),.m_rvalid(q_m_rvalid),.m_rready(q_m_rready));
'''
 s=s.replace('assign all_configured=',logic+'assign all_configured=',1)
 return s
if __name__=='__main__':
 p=Path(__file__).parent;p.joinpath('candidate_params_engine.sv').write_text(derive((ROOT/'hardware/variants/candidate_postprev_v1/candidate_postprev_engine.sv').read_text()))
