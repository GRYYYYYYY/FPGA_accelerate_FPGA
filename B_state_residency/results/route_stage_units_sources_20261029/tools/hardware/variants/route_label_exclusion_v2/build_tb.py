"""Preserve original tests; keep native-qualified and overlap suites separate."""
from pathlib import Path


def build(root, mode, suite):
    root = Path(root)
    base = (root/'hardware/variants/route_commit_v1/tb_route_commit.sv').read_text()
    cp = (root/'hardware/variants/route_checkpoint_v1/tb_route_commit.sv').read_text()
    cp_declarations = cp.split(' localparam CP_CAPACITY=8;', 1)[1].split(' reg clk=0;', 1)[0]
    cp_declarations = ' localparam CP_CAPACITY=8;'+cp_declarations
    if suite == 'route':
        text = base.replace('module tb_route_commit;', 'module tb_route_commit;\n'+cp_declarations)
        marker = 'ROUTE_COMMIT_PASS'
    elif suite in ['checkpoint', 'native_checkpoint']:
        text = cp
        marker = 'ROUTE_CHECKPOINT_PASS'
        if suite == 'native_checkpoint':
            old = 'l_ready<=ticks%4==0&&mode!=6;'
            assert text.count(old) == 1
            text = text.replace(old, 'l_ready<=ticks%4==0&&mode!=6&&!l_rsp_valid&&lwait==0;')
            monitor = '''
 always @(posedge clk)if(!rst)begin
  if((l_ready&&l_rsp_valid)!==1'b0)$fatal(1,"native label overlap or unknown");
  if(l_valid&&l_ready)native_requests=native_requests+1;
  if(l_rsp_valid&&l_rsp_ready)native_replies=native_replies+1;
 end
'''
            text = text.replace('module tb_route_commit;', 'module tb_route_commit;\n integer native_requests=0,native_replies=0;')
            text = text.replace('\nendmodule', monitor+'\nendmodule')
            old = '  $fflush(events);$fclose(events);$display("ROUTE_CHECKPOINT_PASS'
            assert text.count(old) == 1
            check = '''  if(native_requests==0||native_requests!=native_replies)$fatal(1,"native label coverage");
  $fdisplay(events,"NATIVE_LABEL %0d %0d",native_requests,native_replies);
'''
            text = text.replace(old, check+old)
    elif suite == 'generic_overlap':
        prefix = base.split(' reg[31:0]nodes', 1)[0]
        text = prefix.replace('module tb_route_commit;', 'module tb_route_commit;\n'+cp_declarations)
        expected = 1 if mode == 'exclusive' else 0
        text += '''
 integer events,ticks=0;string path;
 always @(posedge clk)begin ticks=ticks+1;if(ticks>200)$fatal(1,"overlap watchdog");end
 initial begin
  if(!$value$plusargs("events=%s",path))$fatal(1,"events path");events=$fopen(path,"w");
  repeat(3)@(negedge clk);rst=0;
  @(negedge clk);req_valid=1;
  do @(posedge clk);while(!req_ready);
  @(negedge clk);req_valid=0;
  wait(l_valid);@(negedge clk);l_ready=1;l_rsp_valid=1;
  #1;
  if(dut.state!=1||dut.unexpected!=EXPECTED||fault!=EXPECTED)$fatal(1,"generic overlap contract mismatch");
  $fdisplay(events,"OVERLAP %0d %0d %0d",dut.state,dut.unexpected,fault);
  $fflush(events);$fclose(events);
  $display("ROUTE_LABEL_OVERLAP_PASS specialized=EXPECTED unexpected=%0d",dut.unexpected);
  $finish;
 end
endmodule
'''.replace('EXPECTED', str(expected))
        marker = 'ROUTE_LABEL_OVERLAP_PASS'
    else:
        raise ValueError(suite)
    text = text.replace('module tb_route_commit;', 'module tb_route_commit;\n wire idle_fault;')
    if mode == 'exclusive':
        old = 'route_commit_controller #(.MAX_PATH(8),'
        assert text.count(old) == 1
        text = text.replace(old, 'route_commit_controller #(.LABEL_RESPONSE_EXCLUSIVE(1),.MAX_PATH(8),')
    assert mode in ['baseline', 'default', 'exclusive']
    return text, marker
