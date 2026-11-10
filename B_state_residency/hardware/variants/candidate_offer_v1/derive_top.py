from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def derive(s):
 s=s.replace('module candidate_commit_engine','module candidate_offer_engine',1)
 ports='''output wire out_offer_valid,output wire [3:0] out_offer_status,output wire [31:0] out_offer_key,out_offer_node,out_offer_before,out_offer_size,
output wire [31:0] seed_rsp_key,seed_rsp_id,
'''
 s=s.replace('output wire out_commit_valid,',ports+'output wire out_commit_valid,',1)
 decl='''wire offer_busy,offer_fault,offer_ready,offer_req_valid;reg offer_started;
wire [31:0] offer_cookie,offer_version,offer_backend_status;wire [1:0] offer_query;wire [3:0] offer_price;wire [63:0] offer_design;
wire of_valid,of_ready,of_rsp_valid,of_rsp_ready;wire [31:0] of_key,of_id,of_cookie,of_version,of_rsp_status,of_rsp_cookie,of_rsp_size,of_rsp_version;wire [63:0] of_design,of_rsp_design;wire [1:0] of_query,of_rsp_query;wire [3:0] of_price,of_rsp_price;
wire offer_identity_error;
'''
 s=s.replace('wire k_reply_error=',decl+'wire k_reply_error=',1)
 s=s.replace('||commit_busy','||commit_busy||offer_busy')
 s=s.replace('out_cost_valid&&out_commit_valid));','out_cost_valid&&out_commit_valid&&(out_action==2||(out_offer_valid&&out_offer_status==0))));',1)
 s=s.replace('assign fault=','assign fault=offer_fault||offer_identity_error||',1)
 s=s.replace('if(k_reply_error||commit_fault', 'if(offer_fault||offer_identity_error||k_reply_error||commit_fault',1)
 s=s.replace('query_frontier frontier(','''query_frontier_offer frontier(
 .design_id(design_id),.offer_valid(of_valid),.offer_ready(of_ready),.offer_key(of_key),.offer_id(of_id),.offer_cookie(of_cookie),.offer_version(of_version),.offer_design(of_design),.offer_query(of_query),.offer_price(of_price),
 .offer_rsp_valid(of_rsp_valid),.offer_rsp_ready(of_rsp_ready),.offer_rsp_status(of_rsp_status),.offer_rsp_cookie(of_rsp_cookie),.offer_rsp_size(of_rsp_size),.offer_rsp_version(of_rsp_version),.offer_rsp_design(of_rsp_design),.offer_rsp_query(of_rsp_query),.offer_rsp_price(of_rsp_price),.seed_rsp_key(seed_rsp_key),.seed_rsp_id(seed_rsp_id),''',1)
 logic='''assign offer_identity_error=out_offer_valid&&(offer_cookie!=out_sequence||out_offer_node!=out_node||out_offer_key!=out_cost_words[159:128]||offer_query!=p_active_query||offer_price!=p_active_price||offer_version!=query_version||offer_design!=design_id);
assign offer_req_valid=!fault&&q_meta_valid&&raw_seen&&raw_out_valid&&out_action==1&&out_cost_valid&&out_cost_status==0&&out_commit_valid&&out_commit_status==0&&out_commit_acked==7&&!offer_started;
always @(posedge clk)begin
 if(rst)offer_started<=0;
 else if(raw_out_valid&&raw_out_ready)offer_started<=0;
 else if(offer_req_valid&&offer_ready)offer_started<=1;
end
cost_offer offer_inputs(.clk(clk),.rst(rst),.abort(abort||fence_stopped),.active(p_active),.decision_lock(operation_pending),.active_query(p_active_query),.active_price(p_active_price),.active_version(query_version),.active_design(design_id),
 .req_valid(offer_req_valid),.req_ready(offer_ready),.req_cookie(out_sequence),.req_node(out_node),.req_key(out_cost_words[159:128]),.req_before(frontier_size),
 .rsp_valid(out_offer_valid),.rsp_ready(raw_out_valid&&raw_out_ready&&out_action==1),.rsp_status(out_offer_status),.rsp_cookie(offer_cookie),.rsp_node(out_offer_node),.rsp_key(out_offer_key),.rsp_before(out_offer_before),.rsp_size(out_offer_size),.rsp_version(offer_version),.rsp_backend_status(offer_backend_status),.rsp_query(offer_query),.rsp_price(offer_price),.rsp_design(offer_design),.busy(offer_busy),.fault(offer_fault),
 .f_valid(of_valid),.f_ready(of_ready),.f_key(of_key),.f_id(of_id),.f_cookie(of_cookie),.f_version(of_version),.f_design(of_design),.f_query(of_query),.f_price(of_price),
 .f_rsp_valid(of_rsp_valid),.f_rsp_ready(of_rsp_ready),.f_rsp_status(of_rsp_status),.f_rsp_cookie(of_rsp_cookie),.f_rsp_size(of_rsp_size),.f_rsp_version(of_rsp_version),.f_rsp_design(of_rsp_design),.f_rsp_query(of_rsp_query),.f_rsp_price(of_rsp_price));
'''
 s=s.replace('assign all_configured=',logic+'assign all_configured=',1)
 return s
if __name__=='__main__':Path(__file__).with_name('candidate_offer_engine.sv').write_text(derive((ROOT/'hardware/variants/candidate_commit_v2/candidate_commit_engine.sv').read_text()))
