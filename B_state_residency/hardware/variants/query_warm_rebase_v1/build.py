"""Preserve original image CRC while importing ledger into recovery context."""
from pathlib import Path
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/checkpoint_commit_v6/sources/query_lifecycle.sv')
def rep(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def make():
 s=BASE.read_text().replace('parameter integer MAX_CYCLES=8388608','parameter integer MAX_CYCLES=8388608,ENABLE_REBASE=0')
 s=rep(s,' input wire clk,rst,abort', ''' input wire cp_rebase,cp_rebase_permit,input wire[31:0]cp_source_version,input wire[1:0]cp_source_query,input wire[3:0]cp_source_price,
 input wire clk,rst,abort''')
 s=rep(s,' wire cp_drift=', ''' reg cp_rebasing;reg[31:0]cp_src_version;reg[1:0]cp_src_query;reg[3:0]cp_src_price;
 wire want_rebase=(ENABLE_REBASE!=0)&&cp_rebase;
 wire[31:0]cp_image_version=cp_rebasing?cp_src_version:cp_ctx_version;
 wire[1:0]cp_image_query=cp_rebasing?cp_src_query:cp_ctx_query;
 wire[3:0]cp_image_price=cp_rebasing?cp_src_price:cp_ctx_price;
 wire cp_drift=(cp_rebasing&&!cp_rebase_permit)||''')
 s=rep(s,'cp_stage[6]!=cp_ctx_version','cp_stage[6]!=cp_image_version')
 s=rep(s,'cp_stage[7][1:0]!=cp_ctx_query','cp_stage[7][1:0]!=cp_image_query')
 s=rep(s,'cp_stage[7][5:2]!=cp_ctx_price','cp_stage[7][5:2]!=cp_image_price')
 s=rep(s,"cp_state<=CP_IDLE;cp_pos<=0;", "cp_rebasing<=0;cp_src_version<=0;cp_src_query<=0;cp_src_price<=0;cp_state<=CP_IDLE;cp_pos<=0;")
 s=rep(s,'     cp_ctx_design<=active_design;', '     cp_rebasing<=want_rebase&&cp_restore;cp_src_version<=cp_source_version;cp_src_query<=cp_source_query;cp_src_price<=cp_source_price;\n     cp_ctx_design<=active_design;')
 s=rep(s,'if(active_design==0||active_generation==0||active_version==0)', 'if(active_design==0||active_generation==0||active_version==0||(want_rebase&&(!cp_restore||!cp_rebase_permit||cp_source_version==0||cp_source_version>=active_version||cp_source_price!=cp_source_version[3:0]||active_price!=active_version[3:0])))')
 # Source packet and source CRC are never rewritten. Publication already uses cp_ctx_*.
 (HERE/'query_lifecycle.sv').write_text(s)
if __name__=='__main__':make()
