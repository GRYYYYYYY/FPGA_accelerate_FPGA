"""Isolate the native recursive controller/capture/frames feedback region."""
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=Path('/tmp/B_state_residency_offer_20261025/restore_seed_synth_on_v1/sources')
NAMES={'recursive_candidate_controller.sv':'recursive/recursive_candidate_controller.sv',
       'expansion_capture.sv':'capture/expansion_capture.sv','children_frames.sv':'capture/children_frames.sv'}

def sources(fixed):
    result={n:(BASE/rel).read_text()for n,rel in NAMES.items()}
    if fixed:
        old=' assign expand_ready=!rst&&!stopped&&!subsystem_fault&&!abort&&enable&&state==IDLE&&e_expand_ready;\n assign e_expand_valid=(expand_valid&&expand_ready&&!invalid)||(!rst&&!stopped&&state==DESCEND);'
        new=''' // Offer is independent of the consumer ready path. Invalid roots are
 // rejected locally and must not require an expander handshake.
 wire root_permit=!rst&&!stopped&&!subsystem_fault&&!abort&&enable&&state==IDLE;
 assign expand_ready=root_permit&&(invalid||e_expand_ready);
 assign e_expand_valid=(expand_valid&&root_permit&&!invalid)||(!rst&&!stopped&&state==DESCEND);'''
        s=result['recursive_candidate_controller.sv'];assert s.count(old)==1;result['recursive_candidate_controller.sv']=s.replace(old,new)
        old='.frame_done(frame_done),.pop_valid(result_valid&&result_ready),.pop_ready(pop_ready));'
        new='''// pop_ready already qualifies frame_done. Supplying the independent
 // consumer intent avoids frame_done -> pop_valid -> begin_ready -> push
 // -> frame_done feedback; the actual pop handshake is unchanged.
 .frame_done(frame_done),.pop_valid(result_ready&&state==0&&(fault||!expand_valid||result_offered)),.pop_ready(pop_ready));'''
        s=result['expansion_capture.sv'];assert s.count(old)==1;result['expansion_capture.sv']=s.replace(old,new)
    return result

def ports(text):
    header=text.split(')(\n',1)[1].split('\n);',1)[0]
    result=[];direction=width=None
    for token in header.split(','):
        token=token.strip()
        m=re.match(r'^(input|output)\s+(?:wire|reg)\s*(\[[^]]+\])?\s*(\w+)$',token)
        if m:direction,width,name=m.groups();width=width or ''
        else:
            assert re.fullmatch(r'\w+',token),token
            assert direction is not None;name=token
        result.append((direction,width,name))
    assert len({n for _,_,n in result})==len(result)
    return result

def wrapper():
    cp=ports(sources(False)['recursive_candidate_controller.sv'])
    physical=[(d,w,'b_'+n[2:])for d,w,n in ports(sources(False)['expansion_capture.sv'])if n.startswith('e_')]
    external=[x for x in cp if not x[2].startswith('e_')]+physical+[('output','','cap_busy'),('output','','cap_fault')]
    text='`timescale 1ns/1ps\nmodule capture_loop_slice(\n'+',\n'.join(f' {d} wire {w} {n}'for d,w,n in external)+'\n);\n'
    text+='\n'.join(f'wire {w} {n};'for d,w,n in cp if n.startswith('e_'))+'\nwire[31:0]e_result_detail;\n'
    text+='recursive_candidate_controller #(.MAX_CYCLES(10000)) d(.*);\n'
    tb=(ROOT/'hardware/variants/recursive_controller_v1/tb_recursive_candidate_controller.sv').read_text()
    capture=tb.split('expansion_capture #(',1)[1].split('));',1)[0]
    text+='expansion_capture #('+capture+'));\nendmodule\n'
    return text

def ready_test():
    cp=ports(sources(False)['recursive_candidate_controller.sv'])
    text='`timescale 1ns/1ps\nmodule tb_root_offer;\n'
    for d,w,n in cp:
        if d=='output' or n=='e_expand_ready':text+=f'wire {w} {n};\n'
        else:text+=f'reg {w} {n}=0;\n'
    text+='''always #5 clk=~clk;
reg permit=0;integer expected_stall=0,accepted=0,checks=0;
recursive_candidate_controller #(.MAX_CYCLES(1000))dut(.*);
// A legal receiver may wait for VALID before asserting READY.
assign e_expand_ready=permit&&e_expand_valid;
always @(posedge clk)if(!rst&&e_expand_valid&&e_expand_ready)begin
 accepted=accepted+1;
 if(!expand_valid||!expand_ready||e_expand_cookie!=201||e_expand_parent!=1)$fatal(1,"unpaired root acceptance");
 $display("ACCEPT %0d %0d",accepted,e_expand_cookie);
end
task tick;begin @(posedge clk);#1;end endtask
initial begin
 if(!$value$plusargs("expected_stall=%d",expected_stall))$fatal(1,"missing mode");
 rst=1;repeat(3)tick;@(negedge clk);rst=0;
 enable=1;active=1;active_version=3;active_design=99;active_query=1;active_price=3;nodes=4;
 expand_cookie=201;expand_parent=1;expand_sink=3;expand_net=5;expand_valid=1;
 repeat(5)begin tick;
  if(expand_ready||accepted||operation_pending)$fatal(1,"accepted before permission");
  if(!expected_stall&&(!e_expand_valid||e_expand_cookie!=201||e_expand_parent!=1))$fatal(1,"offer not held while ready low");
  checks=checks+1;
 end
 @(negedge clk);permit=1;
 if(expected_stall)begin
  repeat(16)begin tick;if(expand_ready||accepted||operation_pending)$fatal(1,"baseline unexpectedly accepted");end
  $display("ROOT_OFFER_BASELINE_BLOCKED cycles=16");$finish;
 end
 tick;if(accepted!=1||!operation_pending)$fatal(1,"offer did not make progress");
 @(negedge clk);expand_valid=0;expand_parent=99;e_depth=1;e_result_cookie=201;e_result_valid=1;
 #1;if(!e_result_ready)$fatal(1,"empty completion blocked");tick;
 @(negedge clk);e_result_valid=0;e_depth=0;
 repeat(8)begin tick;if(!result_valid||result_status||result_cookie!=201||!operation_pending||accepted!=1)$fatal(1,"held result changed");checks=checks+1;end
 @(negedge clk);result_ready=1;tick;@(negedge clk);result_ready=0;
 tick;if(operation_pending||stopped)$fatal(1,"root not retired");
 // Invalid root must complete locally, even with physical receiver not ready.
 @(negedge clk);permit=0;expand_parent=9;expand_cookie=202;expand_valid=1;
 #1;if(!expand_ready||e_expand_valid)$fatal(1,"invalid root depended on expander ready");tick;
 @(negedge clk);expand_valid=0;
 repeat(5)begin tick;if(!result_valid||result_status!=1||result_cookie!=202||accepted!=1)$fatal(1,"invalid root leaked request");checks=checks+1;end
 @(negedge clk);result_ready=1;tick;@(negedge clk);result_ready=0;
 if(operation_pending||stopped)$fatal(1,"invalid root retirement");
 $display("ROOT_OFFER_FIXED_PASS checks=%0d accepted=%0d",checks,accepted);$finish;
end
initial begin #10000;$fatal(1,"watchdog");end
endmodule
'''
    return text

if __name__=='__main__':
    for mode in ['baseline','fixed']:
        d=HERE/mode;d.mkdir(exist_ok=False)
        for name,text in sources(mode=='fixed').items():(d/name).write_text(text)
    (HERE/'capture_loop_slice.sv').write_text(wrapper())
    (HERE/'tb_root_offer.sv').write_text(ready_test())
