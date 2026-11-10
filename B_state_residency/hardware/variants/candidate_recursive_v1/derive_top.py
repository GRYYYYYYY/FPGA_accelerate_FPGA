from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def derive(s):
 s=s.replace('module candidate_capture_engine #','module candidate_recursive_engine #',1).replace('candidate_capture_query_core #','candidate_recursive_query_core #',1)
 old='reg prep_started,raw_seen,post_started;reg [31:0] held_net,held_parent;';assert old in s
 s=s.replace(old,'reg prep_started,raw_seen,post_started;reg [31:0] held_net;wire[31:0]held_parent,held_root_cookie;',1)
 s=s.replace('held_parent<=0;','',1).replace('held_parent<=expand_parent;','',1)
 s=s.replace(' core(\n',' core(\n.current_parent(held_parent),.current_root_cookie(held_root_cookie),\n',1)
 assert '.current_parent(held_parent)'in s
 return s
if __name__=='__main__':
 p=Path(__file__).parent;(p/'candidate_recursive_engine.sv').write_text(derive((ROOT/'hardware/variants/candidate_capture_v1/candidate_capture_engine.sv').read_text()))
