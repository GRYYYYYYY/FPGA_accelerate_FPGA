from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=ROOT/'hardware/variants/label_baseline_system_v1'
DEEP=['priced/candidate_recursive_engine.sv','priced/candidate_recursive_query_core.sv','expansion_20261024/pager/pager/paged_exclusion_engine.sv']
MANAGER='expansion_20261024/pager/pager/resident_page_manager.sv'
def make():
 out={}
 for name in DEEP:
  s=(BASE/name).read_text().replace('input wire baseline_permit,','input wire baseline_raw_probe,\ninput wire baseline_permit,',1)
  s=s.replace('.baseline_permit(baseline_permit),','.baseline_raw_probe(baseline_raw_probe),.baseline_permit(baseline_permit),',1);out[name]=s
 s=(BASE/MANAGER).read_text().replace('input wire baseline_permit,','input wire baseline_raw_probe,\ninput wire baseline_permit,',1)
 s=s.replace('reg writing;', 'reg raw_probe;reg writing;')
 s=s.replace('if(ENABLE_BASELINE)probe_access', 'if(ENABLE_BASELINE&&!raw_probe)probe_access')
 s=s.replace('writing<=0;\n', 'writing<=0;raw_probe<=0;\n',1)
 s=s.replace('writing<=io_write;', 'raw_probe<=ENABLE_BASELINE&&baseline_raw_probe;writing<=io_write;',1)
 s=s.replace('else if(io_node[31:24]!=0', 'else if(ENABLE_BASELINE&&baseline_raw_probe&&io_write)begin io_status<=3;state<=IO_REPLY;end\n                        else if(io_node[31:24]!=0',1)
 s=s.replace('offset<=client_cmd_offset;field<=client_cmd_field;writing<=0;', 'offset<=client_cmd_offset;field<=client_cmd_field;writing<=0;raw_probe<=0;',1)
 out[MANAGER]=s
 leaf=(ROOT/'hardware/variants/label_source_crc_v1/label_restore_controller.sv').read_text()
 leaf=leaf.replace('input wire clk,rst,', 'output wire l_probe,\n input wire clk,rst,',1)
 # PS issues the physical-empty check; PW keeps provenance until the reply is consumed.
 at=leaf.index(' assign start_ready=');leaf=leaf[:at]+' assign l_probe=!rst&&(state==PS||state==PW);\n'+leaf[at:]
 out['label_restore_controller.sv']=leaf
 s=(ROOT/'hardware/variants/label_baseline_fence_v1/residency_system.sv').read_text()
 s=s.replace('wire lr_busy;', 'wire lr_busy;wire lr_l_probe;\nwire baseline_raw_probe=ENABLE_BASELINE&&f_recovery_owned&&k_labels_valid&&lr_l_probe;',1)
 s=s.replace('.baseline_permit(baseline_permit),','.baseline_raw_probe(baseline_raw_probe),.baseline_permit(baseline_permit),',1)
 marker='))label_restore(';assert marker in s;s=s.replace(marker,marker+'.l_probe(lr_l_probe),',1)
 out['residency_system.sv']=s
 return out
if __name__=='__main__':
 for n,s in make().items():
  p=HERE/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
