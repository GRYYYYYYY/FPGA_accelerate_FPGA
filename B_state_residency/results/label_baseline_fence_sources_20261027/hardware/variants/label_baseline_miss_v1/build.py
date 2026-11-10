from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
BASE=ROOT/'hardware/variants/label_frame_export_v1/expansion_20261024/pager/pager/resident_page_manager.sv'
def make():
 s=BASE.read_text().replace('SLOTS=32,TX_BITS=16,GEN_BITS=16','SLOTS=32,TX_BITS=16,GEN_BITS=16,ENABLE_BASELINE=0')
 s=s.replace('input wire clk,rst,client_quiescent,','''input wire clk,rst,client_quiescent,
    input wire baseline_permit,input wire[63:0]baseline_epoch,
    output wire baseline_req_valid,input wire baseline_req_ready,
    output wire[31:0]baseline_req_node,output wire[63:0]baseline_req_epoch,
    input wire baseline_rsp_valid,output wire baseline_rsp_ready,
    input wire[3:0]baseline_rsp_status,input wire[31:0]baseline_rsp_node,
    input wire[63:0]baseline_rsp_epoch,input wire[159:0]baseline_rsp_payload,''')
 s=s.replace('CTRL_REPLY=10,FLUSH=11;', 'CTRL_REPLY=10,FLUSH=11,BASE_SEND=12,BASE_WAIT=13;')
 s=s.replace('FINISH_CLOSE=11,CLIENT=12;', 'FINISH_CLOSE=11,CLIENT=12,SEED=13,PROBE=14;')
 s=s.replace('reg writing;', '''reg writing;
    reg[63:0]active_baseline_epoch;reg[159:0]seed_payload;reg[2:0]seed_field;
    assign baseline_req_valid=!rst&&state==BASE_SEND;
    assign baseline_req_node={8'b0,page,offset};
    assign baseline_req_epoch=active_baseline_epoch;
    assign baseline_rsp_ready=!rst&&state==BASE_WAIT;
    task original_access;
     begin launch(writing?4'd3:4'd2,chosen,page,generations[chosen],offset,field,value,leased?CLIENT:ACCESS);end
    endtask
    task probe_access(input[4:0]sl,input[15:0]gen);
     begin launch(2,sl,page,gen,offset,field,0,PROBE);end
    endtask''')
 old="else launch(writing?4'd3:4'd2,chosen,page,generations[chosen],offset,field,value,ACCESS);"
 assert old in s;s=s.replace(old,"else if(ENABLE_BASELINE)probe_access(chosen,generations[chosen]);\n            "+old)
 old="else launch(writing?4'd3:4'd2,scan[4:0],page,generations[scan],offset,field,value,ACCESS);"
 assert old in s;s=s.replace(old,"else if(ENABLE_BASELINE)probe_access(scan[4:0],generations[scan]);\n                        "+old)
 s=s.replace('ctrl_status<=0;io_status<=0;io_payload<=0;io_present<=0;map_status<=0;', 'active_baseline_epoch<=0;seed_payload<=0;seed_field<=0;\n            ctrl_status<=0;io_status<=0;io_payload<=0;io_present<=0;map_status<=0;')
 s=s.replace('else begin\n                                launch(0,0,0,0,0,0,0,OPEN);', '''else if(ENABLE_BASELINE&&(!baseline_permit||baseline_epoch==0))begin ctrl_status<=1;state<=CTRL_REPLY;end
                            else begin
                                active_baseline_epoch<=baseline_epoch;
                                launch(0,0,0,0,0,0,0,OPEN);''')
 old='else launch(2,chosen,page,generations[chosen],client_cmd_offset,client_cmd_field,0,CLIENT);'
 assert old in s;s=s.replace(old,'''else begin
                        if(ENABLE_BASELINE)begin
                         offset<=client_cmd_offset;field<=client_cmd_field;writing<=0;value<=0;
                         launch(2,chosen,page,generations[chosen],client_cmd_offset,client_cmd_field,0,PROBE);
                        end else launch(2,chosen,page,generations[chosen],client_cmd_offset,client_cmd_field,0,CLIENT);
                    end''')
 marker='                        ACCESS:begin'
 insert='''                        PROBE:begin
                            if(!native_rsp_present)state<=BASE_SEND;
                            else if(writing)original_access;
                            else if(leased)begin client_rsp_status<=0;client_rsp_payload<=native_rsp_payload;client_rsp_present<=1;state<=CLIENT_REPLY;end
                            else begin io_status<=0;io_payload<=native_rsp_payload;io_present<=1;state<=IO_REPLY;end
                        end
                        SEED:begin
                            dirty_slots[chosen]<=1;
                            if(seed_field==4)original_access;
                            else begin
                             seed_field<=seed_field+1'b1;
                             launch(3,chosen,page,generations[chosen],offset,seed_field+1'b1,seed_payload[(seed_field+1)*32+:32],SEED);
                            end
                        end
'''
 assert marker in s;s=s.replace(marker,insert+marker)
 s=s.replace('                FLUSH:begin', '''                BASE_SEND:if(baseline_req_ready)state<=BASE_WAIT;
                BASE_WAIT:if(baseline_rsp_valid&&baseline_rsp_ready)begin
                    if(baseline_rsp_status!=0||baseline_rsp_node!={8'b0,page,offset}||
                       baseline_rsp_epoch!=active_baseline_epoch||baseline_rsp_payload[159:136]!=0)fail_request(10);
                    else begin
                     seed_payload<=baseline_rsp_payload;seed_field<=0;
                     launch(3,chosen,page,generations[chosen],offset,0,baseline_rsp_payload[31:0],SEED);
                    end
                end
                FLUSH:begin''')
 s=s.replace('reg[63:0]active_baseline_epoch;', 'reg baseline_poison;reg[63:0]active_baseline_epoch;')
 s=s.replace('active_baseline_epoch<=0;', 'baseline_poison<=0;active_baseline_epoch<=0;')
 s=s.replace('if(!stopped&&abort_now)begin', 'if(abort_now&&(state==BASE_SEND||state==BASE_WAIT))baseline_poison<=1;\n            if(!stopped&&abort_now&&state!=BASE_SEND&&state!=BASE_WAIT)begin')
 s=s.replace('if(!native_rsp_present)state<=BASE_SEND;', 'if(!native_rsp_present)begin baseline_poison<=0;state<=BASE_SEND;end')
 s=s.replace('if(baseline_rsp_status!=0||', 'if(baseline_poison||abort_now||baseline_rsp_status!=0||')
 return s
if __name__=='__main__':(HERE/'resident_page_manager.sv').write_text(make())
