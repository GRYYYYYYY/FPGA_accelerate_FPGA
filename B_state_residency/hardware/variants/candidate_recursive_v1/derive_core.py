from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def derive(s):
 s=s.replace('module candidate_capture_query_core #','module candidate_recursive_query_core #',1)
 s=s.replace(' input wire [31:0] frame_version,',' output wire[31:0] current_parent,current_root_cookie,\n input wire [31:0] frame_version,',1)
 s=s.replace('wire[511:0]captured_context;', 'wire[511:0]captured_context,controller_expand_context;',1)
 old=".expand_context({26'b0,p_active_query,p_active_price,frame_version,frame_design,expand_cookie,expand_parent,expand_prune,expand_has_laguna,expand_sink,expand_net,expand_sequence,expand_flags,expand_xmin,expand_xmax,expand_ymin,expand_ymax})"
 assert old in s;s=s.replace(old,'.expand_context(controller_expand_context)',1)
 s=s.replace('candidate_controller #(.MAX_CYCLES(MAX_CYCLES)) controller(', '''recursive_candidate_controller #(.MAX_CYCLES(MAX_CYCLES)) controller(
.active_version(frame_version),.active_design(frame_design),.e_context(captured_context),.e_depth(capture_depth),.e_expand_context(controller_expand_context),.out_parent(current_parent),.out_root_cookie(current_root_cookie),''',1)
 assert 'recursive_candidate_controller #' in s
 return s
if __name__=='__main__':
 p=Path(__file__).parent;(p/'candidate_recursive_query_core.sv').write_text(derive((ROOT/'hardware/variants/candidate_capture_v1/candidate_capture_query_core.sv').read_text()))
