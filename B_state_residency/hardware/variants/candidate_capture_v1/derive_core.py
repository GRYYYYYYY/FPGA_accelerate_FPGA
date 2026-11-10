"""Insert sealed static children replay before existing metadata/access controller."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
FIELDS=['expand_valid','expand_ready','expand_cookie','expand_parent','expand_prune','expand_has_laguna','out_valid','out_ready','out_node','out_position','out_sequence','out_attrs','result_valid','result_ready','result_status','result_detail','result_cookie','result_count','result_raw_count','result_mask','result_hit']
def derive(s):
 s=s.replace('module candidate_commit_query_core #','module candidate_capture_query_core #',1)
 s=s.replace(' input wire commit_l_valid,',' input wire [31:0] frame_version,input wire [63:0] frame_design,\n input wire commit_l_valid,',1)
 a=s.index(' expansion_controller #');b=s.index('\n);',a)+3;old=s[a:b];new=old
 for n in FIELDS:new=new.replace('.'+n+'(e_'+n+')','.'+n+'(ce_'+n+')')
 assert '.enable(can_start)'in new
 new=new.replace('.enable(can_start)', '.enable(operation_pending&&!capture_fault&&!configuration_fault)')
 s=s[:a]+new+s[b:]
 s=s.replace('assign subsystem_fault=e_fault||','assign subsystem_fault=capture_fault||e_fault||',1)
 declarations=[]
 for n in FIELDS:
  width='[255:0] 'if n=='out_attrs'else '[3:0] 'if n=='result_status'else '[31:0] 'if n not in ['expand_valid','expand_ready','out_valid','out_ready','result_valid','result_ready','result_hit']else ''
  declarations.append(' wire '+width+'ce_'+n+';')
 context='{26\'b0,p_active_query,p_active_price,frame_version,frame_design,expand_cookie,expand_parent,expand_prune,expand_has_laguna,expand_sink,expand_net,expand_sequence,expand_flags,expand_xmin,expand_xmax,expand_ymin,expand_ymax}'
 add='\n'.join(declarations)+'''\n wire capture_fault,capture_busy;wire[31:0]capture_depth;wire[511:0]captured_context;
 expansion_capture #(.DEPTH(4),.CAPACITY(32)) child_capture(
 .clk(clk),.rst(rst),.abort(abort),.expand_context('''+context+'''),.out_context(captured_context),
 .busy(capture_busy),.fault(capture_fault),.depth(capture_depth),
'''+',\n'.join('.'+n+'(e_'+n+')'for n in FIELDS)+',\n'+',\n'.join('.e_'+n+'(ce_'+n+')'for n in FIELDS)+');\n'
 s=s.replace(' wire  e_busy;',add+' wire  e_busy;',1)
 return s
if __name__=='__main__':
 p=Path(__file__).parent;(p/'candidate_capture_query_core.sv').write_text(derive((ROOT/'hardware/variants/candidate_commit_v1/candidate_commit_query_core.sv').read_text()))
