"""Preserve route/CP tests and observe every changed path word and its cycle."""
from pathlib import Path
import importlib.util


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build(root, mode, suite):
    root = Path(root)
    if suite == 'checkpoint32':
        helper = load(root/'hardware/variants/route_checkpoint_v1/build_tb.py', 'original_cp32_builder')
        text = helper.make(32)
        text = text.replace('module tb_route_commit;', 'module tb_route_commit;\n wire idle_fault;')
        marker = 'ROUTE_CHECKPOINT_PASS'
        words = 32
    else:
        helper = load(root/'hardware/variants/route_label_exclusion_v2/build_tb.py', 'preserved_route_tb')
        assert suite in ['route', 'checkpoint', 'generic_overlap']
        text, marker = helper.build(root, 'baseline', suite)
        words = 8
        if suite == 'generic_overlap':
            text = text.replace('ROUTE_LABEL_OVERLAP_PASS', 'ROUTE_PATH_OVERLAP_PASS')
            marker = 'ROUTE_PATH_OVERLAP_PASS'
    assert mode in ['baseline', 'default', 'factored']
    if mode == 'factored':
        old = 'route_commit_controller #('
        assert text.count(old) == 1
        text = text.replace(old, 'route_commit_controller #(.FACTORED_PATH_WRITES(1),')
    declarations = f'''
 integer bank_fd,bank_cycle=0;reg bank_seen=0;string bank_path;
 reg[31:0]bank_previous[0:1][0:{words-1}];
'''
    text = text.replace('module tb_route_commit;', 'module tb_route_commit;\n'+declarations)
    monitor = '''
 initial begin
  if(!$value$plusargs("bank_events=%s",bank_path))$fatal(1,"bank events path");
  bank_fd=$fopen(bank_path,"w");if(!bank_fd)$fatal(1,"bank events open");
 end
 always @(negedge clk)begin
  bank_cycle=bank_cycle+1;
  for(integer bank_slot=0;bank_slot<2;bank_slot=bank_slot+1)
   for(integer bank_word=0;bank_word<WORDS;bank_word=bank_word+1)begin
    if(!bank_seen||dut.path[bank_slot][bank_word]!==bank_previous[bank_slot][bank_word])
     $fdisplay(bank_fd,"BANK %0d %0d %0d %08h",bank_cycle,bank_slot,bank_word,dut.path[bank_slot][bank_word]);
    bank_previous[bank_slot][bank_word]=dut.path[bank_slot][bank_word];
   end
  bank_seen=1;$fflush(bank_fd);
 end
'''.replace('WORDS', str(words))
    assert text.count('\nendmodule') == 1
    text = text.replace('\nendmodule', monitor+'\nendmodule')
    return text, marker
