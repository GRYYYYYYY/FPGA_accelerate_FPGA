"""Reuse original stimuli; compare both banks and an old-tree stage reference."""
from pathlib import Path
import importlib.util


def build(root, mode, suite):
    root = Path(root)
    spec = importlib.util.spec_from_file_location('original_path_tb', root/'hardware/variants/route_path_write_v1/build_tb.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    # All three modes retain the previously tested path factoring.
    text, marker = helper.build(root, 'factored', suite)
    assert mode in ['baseline', 'default', 'factored']
    if mode == 'factored':
        old = 'route_commit_controller #('
        assert text.count(old) == 1
        text = text.replace(old, 'route_commit_controller #(.FACTORED_STAGE_WRITES(1),')
    text = text.replace('ROUTE_PATH_OVERLAP_PASS', 'ROUTE_STAGE_OVERLAP_PASS')
    marker = marker.replace('ROUTE_PATH_OVERLAP_PASS', 'ROUTE_STAGE_OVERLAP_PASS')
    words = 32 if suite == 'checkpoint32' else 8
    stride = 7 + words
    declarations = f'''
 integer stage_fd,stage_cycle=0,stage_checked=0,stage_captures=0,stage_imports=0;
 reg stage_seen=0;string stage_path;
 reg[31:0]stage_previous[0:{2*stride-1}],stage_expected[0:{2*stride-1}];
'''
    text = text.replace('module tb_route_commit;', 'module tb_route_commit;\n'+declarations)
    monitor = '''
 initial begin
  if(!$value$plusargs("stage_events=%s",stage_path))$fatal(1,"stage events path");
  stage_fd=$fopen(stage_path,"w");if(!stage_fd)$fatal(1,"stage events open");
 end
 // Original control branches, with no dependency on new sw_* event signals.
 always @(posedge clk)begin
  if(dut.rst)begin end
  else begin
   case(dut.cp_state)
    0:if(dut.cp_valid&&dut.cp_ready)begin
     if(dut.cp_design!=dut.active_design||dut.cp_nodes==0||dut.cp_nets==0)begin end
     else if(dut.cp_restore)begin end
     else begin
      stage_captures=stage_captures+1;
      for(integer ss=0;ss<2;ss=ss+1)begin
       stage_expected[ss*STRIDE]<=dut.slot_valid[ss]?1:0;
       stage_expected[ss*STRIDE+1]<=dut.slot_valid[ss]?dut.sizes[ss]:0;
       stage_expected[ss*STRIDE+2]<=dut.slot_valid[ss]?dut.nets[ss]:0;
       stage_expected[ss*STRIDE+3]<=dut.slot_valid[ss]?dut.sources[ss]:0;
       stage_expected[ss*STRIDE+4]<=dut.slot_valid[ss]?dut.sinks[ss]:0;
       stage_expected[ss*STRIDE+5]<=dut.slot_valid[ss]?dut.designs[ss][31:0]:0;
       stage_expected[ss*STRIDE+6]<=dut.slot_valid[ss]?dut.designs[ss][63:32]:0;
       for(integer ww=0;ww<WORDS;ww=ww+1)
        stage_expected[ss*STRIDE+7+ww]<=dut.slot_valid[ss]&&ww<dut.sizes[ss]?dut.path[ss][ww]:0;
      end
     end
    end
    2:if(dut.cp_failed||dut.abort||dut.fault||dut.cp_drift)begin end
     else if(dut.cp_s_valid&&dut.cp_s_ready)begin
      if(dut.cp_s_index!=dut.cp_pos||dut.cp_s_last!=(dut.cp_pos+1==TOTAL))begin end
      else begin stage_expected[dut.cp_pos]<=dut.cp_s_data;stage_imports=stage_imports+1;end
     end
    default:begin end
   endcase
  end
  #1;
  for(integer cc=0;cc<TOTAL;cc=cc+1)
   if(dut.cp_stage[cc]!==stage_expected[cc])$fatal(1,"old-tree stage mismatch cycle=%0d word=%0d got=%08h expected=%08h",stage_checked,cc,dut.cp_stage[cc],stage_expected[cc]);
  stage_checked=stage_checked+1;
 end
 always @(negedge clk)begin
  stage_cycle=stage_cycle+1;
  for(integer ww=0;ww<TOTAL;ww=ww+1)begin
   if(!stage_seen||dut.cp_stage[ww]!==stage_previous[ww])
    $fdisplay(stage_fd,"STAGE %0d %0d %08h",stage_cycle,ww,dut.cp_stage[ww]);
   stage_previous[ww]=dut.cp_stage[ww];
  end
  stage_seen=1;$fflush(stage_fd);
 end
'''.replace('STRIDE', str(stride)).replace('WORDS', str(words)).replace('TOTAL', str(2*stride))
    assert text.count('\nendmodule') == 1 and text.count('$finish;') == 1
    text = text.replace('\nendmodule', monitor+'\nendmodule')
    text = text.replace('$finish;', '$display("ROUTE_STAGE_BANK_PASS checked=%0d captures=%0d imports=%0d",stage_checked,stage_captures,stage_imports);$finish;')
    return text, marker
