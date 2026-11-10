"""One-record query State cache; original guards, response and drain preserved."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def derive(s):
 changes=[]
 def rep(a,b):
  nonlocal s
  assert s.count(a)==1,a;s=s.replace(a,b,1);changes.append((a,b))
 rep(' localparam IDLE=0,AR=1,R=2;', ''' // State-table contents are immutable while configured; query labels are not cached here.
 reg cache_valid;
 reg [511:0] cache_data;
 reg [31:0] cache_connection,cache_net,cache_sink,cache_cross,cache_version,cache_revision;
 reg [63:0] cache_design;
 reg [1:0] cache_query;reg [3:0] cache_price;
 wire cache_hit=cache_valid&&req_connection==cache_connection&&req_net==cache_net&&req_sink==cache_sink&&req_cross==cache_cross&&req_version==cache_version&&revision==cache_revision&&req_design==cache_design&&req_query==cache_query&&req_price==cache_price;
 localparam IDLE=0,AR=1,R=2;''')
 rep('  if(rst)begin state<=IDLE;', '  if(rst)begin cache_valid<=0;cache_data<=0;cache_connection<=0;cache_net<=0;cache_sink<=0;cache_cross<=0;cache_version<=0;cache_revision<=0;cache_design<=0;cache_query<=0;cache_price<=0;state<=IDLE;')
 rep('  end else begin\n   if(cfg_rsp_valid', '''  end else begin
   // decision_lock is deliberately absent: it drops between parent expansions.
   // An inactive query, changed full context or fault always revokes reuse.
   if(!query_active||!configured||fail_now||stopped||active_query!=cache_query||active_price!=cache_price||active_version!=cache_version||active_design!=cache_design||revision!=cache_revision)cache_valid<=0;
   if(cfg_rsp_valid''')
 rep('     else begin context_owned<=1;m_araddr<=base+({32\'b0,req_connection}<<6);state<=AR;end', '''     else if(cache_hit)begin context_owned<=1;reply(0,cache_data);end
     else begin context_owned<=1;m_araddr<=base+({32'b0,req_connection}<<6);state<=AR;end''')
 rep('if(!response_sent&&!fail_now&&!stopped)reply(0,m_rdata);', '''if(!response_sent&&!fail_now&&!stopped)begin
      reply(0,m_rdata);cache_valid<=1;cache_data<=m_rdata;cache_connection<=rsp_connection;cache_net<=rsp_net;cache_sink<=rsp_sink;cache_cross<=rsp_cross;cache_version<=rsp_version;cache_revision<=rsp_revision;cache_design<=rsp_design;cache_query<=rsp_query;cache_price<=rsp_price;
     end ''')
 return s,changes
if __name__=='__main__':
 s,c=derive((ROOT/'hardware/variants/connection_state_v1/connection_state_reader.sv').read_text());Path(__file__).with_name('connection_state_reader.sv').write_text(s)
