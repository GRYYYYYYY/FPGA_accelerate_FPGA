"""Drive only supported scheduling enables to withhold four drain prerequisites."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def generate():
 text=(ROOT/'hardware/tb/tb_retained_endpoint.sv').read_text()
 def r(before,after):
  nonlocal text
  assert text.count(before)==1,before
  text=text.replace(before,after)
 r('module tb_retained_endpoint;','''module tb_retained_endpoint_stalls;
    reg hold_dispatch=0,hold_execute=0,hold_fence=0,hold_ack=0;
    integer blocked_cycles=0,blocked_cases=0,stall_i;
    reg [TB_TAG-1:0] blocked_tag;''')
 for before,after in [('dispatch_enable=cycle%5!=0','dispatch_enable=!hold_dispatch && cycle%5!=0'),('execute_enable=cycle%7>=2','execute_enable=!hold_execute && cycle%7>=2'),('fence_service_enable=cycle%11>=4','fence_service_enable=!hold_fence && cycle%11>=4'),('ack_receive_enable=cycle%13>=5','ack_receive_enable=!hold_ack && cycle%13>=5')]:r(before,after)
 r('''            // Garbage public query/price must not replace the retained identity.
            send_host(12,3,99,3,15,7,63,4,32'hdeadbeef,0);''','''            @(negedge clk);
            hold_dispatch=loop_id%4==0;hold_execute=loop_id%4==1;
            hold_fence=loop_id%4==2;hold_ack=loop_id%4==3;
            blocked_tag=fence_tag;
            send_host(12,3,99,3,15,7,63,4,32'hdeadbeef,0);
            for(stall_i=0;stall_i<100;stall_i=stall_i+1)begin
                @(negedge clk);
                if(rsp_valid || cmd_ready || fault || fence_tag!=blocked_tag || allocated!=1
                   || dut.state>=24 || !dut.memory.memory_service.directory.tx_used)
                    $fatal(1,"checkpoint bypassed blocked prerequisite kind=%0d state=%0d",loop_id%4,dut.state);
                blocked_cycles=blocked_cycles+1;
            end
            case(loop_id%4)
                0:if(dut.pages.request_count==0)$fatal(1,"dispatch stall not exercised");
                1:if(dut.pages.work_count==0)$fatal(1,"execute stall not exercised");
                2:if(dut.pages.fence_request_count==0 || dut.pages.acknowledged)$fatal(1,"fence service stall not exercised");
                3:if(dut.pages.fence_ack_count==0 || dut.pages.acknowledged)$fatal(1,"ACK stall not exercised");
            endcase
            blocked_cases=blocked_cases+1;
            hold_dispatch=0;hold_execute=0;hold_fence=0;hold_ack=0;''')
 r('        $display("RETAINED_ENDPOINT_PASS', '''        if(blocked_cases!=20 || blocked_cycles!=2000)$fatal(1,"missing blocking coverage");
        $display("RETAINED_STALL_PASS cases=%0d blocked_cycles=%0d",blocked_cases,blocked_cycles);
        $display("RETAINED_ENDPOINT_PASS''')
 return text
if __name__=='__main__':(ROOT/'hardware/tb/tb_retained_endpoint_stalls.sv').write_text(generate())
