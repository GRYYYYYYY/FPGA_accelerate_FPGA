"""Reuse parent upstream only under the existing exclusive decision lease."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def derive(s):
 changes=[]
 def rep(a,b):
  nonlocal s
  assert s.count(a)==1,a;s=s.replace(a,b,1);changes.append((a,b))
 rep(' localparam IDLE=0,FS=1,', ''' // Valid only while the exclusive decision lease remains asserted.
 // The only concurrent cost writer targets req_child. Self aliases never fill/hit.
 reg cache_valid;reg [31:0] cache_parent,cache_upstream,cache_version;
 reg [63:0] cache_design;reg [1:0] cache_query;reg [3:0] cache_price;
 wire cache_hit=cache_valid&&cache_parent==rsp_parent&&rsp_child!=rsp_parent&&cache_query==rsp_query&&cache_price==rsp_price&&cache_version==rsp_version&&cache_design==rsp_design;
 localparam IDLE=0,FS=1,''')
 rep('  if(rst)begin state<=IDLE;', '  if(rst)begin cache_valid<=0;cache_parent<=0;cache_upstream<=0;cache_version<=0;cache_design<=0;cache_query<=0;cache_price<=0;state<=IDLE;')
 rep('  else begin\n   if(owned', '''  else begin
   if(!active||!decision_lock||fail_now||stopped||active_query!=cache_query||active_price!=cache_price||active_version!=cache_version||active_design!=cache_design)cache_valid<=0;
   if(req_valid&&req_ready&&(req_parent!=cache_parent||req_child==cache_parent))cache_valid<=0;
   if(owned''')
 rep('    WW:if(l_rsp_valid)begin if(fault)fail(2);else state<=LS;end', '''    WW:if(l_rsp_valid)begin if(fault)fail(2);else if(cache_hit)begin rsp_upstream<=cache_upstream;state<=CS;end else state<=LS;end''')
 rep('else begin rsp_upstream<=l_payload[63:32];state<=CS;end end', '''else begin rsp_upstream<=l_payload[63:32];state<=CS;
      if(l_present&&rsp_parent!=rsp_child)begin cache_valid<=1;cache_parent<=rsp_parent;cache_upstream<=l_payload[63:32];cache_query<=rsp_query;cache_price<=rsp_price;cache_version<=rsp_version;cache_design<=rsp_design;end else cache_valid<=0;
     end end''')
 return s,changes
if __name__=='__main__':
 s,c=derive((ROOT/'hardware/variants/candidate_postprev_v1/postprev_inputs.sv').read_text());Path(__file__).with_name('postprev_inputs.sv').write_text(s)
