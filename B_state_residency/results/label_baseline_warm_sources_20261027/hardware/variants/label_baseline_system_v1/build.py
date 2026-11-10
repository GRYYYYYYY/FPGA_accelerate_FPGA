from pathlib import Path
import re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=Path('/tmp/B_state_residency_offer_20261025/label_source_crc_full_v2/sources')
CHAIN=[('query_residency_system.sv','search_residency_system'),('search_residency_system.sv','residency_system'),('residency_system.sv','candidate_recursive_engine'),('priced/candidate_recursive_engine.sv','candidate_recursive_query_core'),('priced/candidate_recursive_query_core.sv','paged_exclusion_engine'),('expansion_20261024/pager/pager/paged_exclusion_engine.sv','resident_page_manager')]
PORTS='''input wire baseline_permit,input wire[63:0]baseline_epoch,
output wire baseline_req_valid,input wire baseline_req_ready,
output wire[31:0]baseline_req_node,output wire[63:0]baseline_req_epoch,
input wire baseline_rsp_valid,output wire baseline_rsp_ready,
input wire[3:0]baseline_rsp_status,input wire[31:0]baseline_rsp_node,
input wire[63:0]baseline_rsp_epoch,input wire[159:0]baseline_rsp_payload,
'''
NAMES=['baseline_permit','baseline_epoch','baseline_req_valid','baseline_req_ready','baseline_req_node','baseline_req_epoch','baseline_rsp_valid','baseline_rsp_ready','baseline_rsp_status','baseline_rsp_node','baseline_rsp_epoch','baseline_rsp_payload']
def balanced(s,i):
 assert s[i]=='(';d=1;j=i+1
 while d:d+=(s[j]=='(')-(s[j]==')');j+=1
 return j

def make():
 result={}
 for name,child in CHAIN:
  s=(BASE/name).read_text();s=s.replace('#(', '#(parameter integer ENABLE_BASELINE=0,',1)
  i=s.index(')(')+2;s=s[:i]+'\n'+PORTS+s[i:]
  m=re.search(r'\b'+child+r'\s*#\(',s);assert m
  i=m.end();s=s[:i]+'.ENABLE_BASELINE(ENABLE_BASELINE),'+s[i:]
  j=balanced(s,m.end()-1);j=s.index('(',j)+1
  s=s[:j]+''.join('.'+n+'('+n+'),'for n in NAMES)+s[j:]
  result[name]=s
 result['expansion_20261024/pager/pager/resident_page_manager.sv']=(ROOT/'hardware/variants/label_baseline_miss_v1/resident_page_manager.sv').read_text()
 return result
if __name__=='__main__':
 for n,s in make().items():
  p=HERE/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
