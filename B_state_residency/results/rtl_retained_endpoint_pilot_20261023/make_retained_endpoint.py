"""Derive a checkpoint coordinator without changing the frozen indexed endpoint."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def generate(text):
 def r(a,b):
  nonlocal text
  assert text.count(a)==1,a
  text=text.replace(a,b)
 r('module memory_scratch_endpoint_indexed #(','module memory_scratch_endpoint_retained #(')
 r('record_backing_service_indexed #(','record_backing_service_retained #(')
 r('M_RECYCLE_SEND=19,M_RECYCLE_WAIT=20;','''M_RECYCLE_SEND=19,M_RECYCLE_WAIT=20,
        CP_BEGIN_SEND=21,CP_BEGIN_WAIT=22,CP_DRAIN=23,CP_FINISH_SEND=24,CP_FINISH_WAIT=25,
        CP_MEMORY_SEND=26,CP_MEMORY_WAIT=27,CP_QUERY_SEND=28,CP_QUERY_WAIT=29;''')
 r('reg [4:0] state;','''reg [4:0] state;
    reg query_seen,query_exclusive;
    reg [1:0] retained_query;
    reg [3:0] retained_price,bound_mask;
    reg [INDEX_BITS:0] retained_allocated;
    wire q_fence_active,q_peer_sealed,q_acknowledged;
    wire [2:0] q_requests,q_work,q_responses;
    wire [1:0] q_fence_requests,q_fence_acks;
    wire cp_drained=q_fence_active && q_peer_sealed && q_acknowledged && page_leases==0
        && q_requests==0 && q_work==0 && q_responses==0 && q_fence_requests==0 && q_fence_acks==0;''')
 r('state==Q_COMPLETE_SEND;','state==Q_COMPLETE_SEND || state==CP_BEGIN_SEND || state==CP_FINISH_SEND || state==CP_QUERY_SEND;')
 r('state==Q_COMPLETE_WAIT;','state==Q_COMPLETE_WAIT || state==CP_BEGIN_WAIT || state==CP_FINISH_WAIT || state==CP_QUERY_WAIT;')
 r('wire [3:0] q_op=state==WB_EXPORT_SEND?',"wire [3:0] q_op=state==CP_BEGIN_SEND?4'd10:(state==CP_FINISH_SEND?4'd11:(state==CP_QUERY_SEND?4'd0:(state==WB_EXPORT_SEND?")
 r("4'd8:op));","4'd8:op)))));")
 r('.fence_active(),.peer_sealed(),.acknowledged(),','.fence_active(q_fence_active),.peer_sealed(q_peer_sealed),.acknowledged(q_acknowledged),')
 r('.request_count(),.work_count(),.response_count(),.fence_request_count(),.fence_ack_count());','.request_count(q_requests),.work_count(q_work),.response_count(q_responses),.fence_request_count(q_fence_requests),.fence_ack_count(q_fence_acks));')
 r('state==M_RECYCLE_SEND;','state==M_RECYCLE_SEND || state==CP_MEMORY_SEND;')
 r('state==M_RECYCLE_WAIT;','state==M_RECYCLE_WAIT || state==CP_MEMORY_WAIT;')
 r('wire [2:0] m_op=state==M_LOOK_SEND?',"wire [2:0] m_op=state==CP_MEMORY_SEND?3'd5:(state==M_LOOK_SEND?")
 r("3'd3:3'd1));","3'd3:3'd1)));")
 r('(state==M_LOOK_SEND || state==M_RECYCLE_SEND)?','(state==M_LOOK_SEND || state==M_RECYCLE_SEND || state==CP_MEMORY_SEND)?')
 r('(state==M_LOOK_WAIT || state==M_RECYCLE_WAIT)?','(state==M_LOOK_WAIT || state==M_RECYCLE_WAIT || state==CP_MEMORY_WAIT)?')
 r('.fence_retired(state==M_RECYCLE_SEND)', '.fence_retired(state==M_RECYCLE_SEND || state==CP_MEMORY_SEND)')
 r('state<=IDLE;op<=0;price<=0;', 'query_seen<=0;query_exclusive<=0;retained_query<=0;retained_price<=0;bound_mask<=0;retained_allocated<=0;\n            state<=IDLE;op<=0;price<=0;')
 r('else if((cmd_op>=7 && cmd_op<=9) || cmd_op>=12)', 'else if((cmd_op>=7 && cmd_op<=9) || cmd_op>=13)')
 r('else if(cmd_op==5 || cmd_op==6)state<=M_LOOK_SEND;', '''else if(cmd_op==12)begin
                    if(!query_seen || !query_exclusive)begin rsp_status<=3;rsp_valid<=1;end
                    else if(bound_mask!=0 || page_leases!=0 || memory_leases!=0 || draining)begin rsp_status<=4;rsp_valid<=1;end
                    else begin
                        query_id<=retained_query;price<=retained_price;retained_allocated<=allocated;
                        fence_open<=1;state<=CP_BEGIN_SEND;
                    end
                end
                else if(cmd_op==5 || cmd_op==6)state<=M_LOOK_SEND;''')
 r('Q_HOST_WAIT:if(q_valid)begin', '''Q_HOST_WAIT:if(q_valid)begin
                    if(q_status==0)begin
                        if(op==0)begin
                            query_seen<=1;query_exclusive<=!query_seen;
                            retained_query<=query_id;retained_price<=price;
                        end
                        if(op==1)bound_mask[slot]<=1;
                        if(op==4)bound_mask[slot]<=0;
                    end''')
 r('else begin fence_open<=0;rsp_valid<=1;state<=IDLE;end', 'else begin query_seen<=0;query_exclusive<=0;bound_mask<=0;fence_open<=0;rsp_valid<=1;state<=IDLE;end')
 r('                default:begin end', '''                CP_BEGIN_SEND:if(q_ready)state<=CP_BEGIN_WAIT;
                CP_BEGIN_WAIT:if(q_valid)begin
                    if(q_status!=0)fail_closed;else state<=CP_DRAIN;
                end
                // Keep ingress quiet until real queued peer/ACK retirement.
                CP_DRAIN:if(cp_drained)state<=CP_FINISH_SEND;
                CP_FINISH_SEND:if(q_ready)state<=CP_FINISH_WAIT;
                CP_FINISH_WAIT:if(q_valid)begin
                    if(q_status!=0 || page_leases!=0)fail_closed;else state<=CP_MEMORY_SEND;
                end
                CP_MEMORY_SEND:if(m_ready)state<=CP_MEMORY_WAIT;
                CP_MEMORY_WAIT:if(m_valid)begin
                    if(m_status!=0 || m_cookie!=0 || memory_leases!=0 || allocated!=retained_allocated)fail_closed;
                    else state<=CP_QUERY_SEND;
                end
                CP_QUERY_SEND:if(q_ready)state<=CP_QUERY_WAIT;
                CP_QUERY_WAIT:if(q_valid)begin
                    if(q_status!=0)fail_closed;
                    else begin fence_open<=0;rsp_valid<=1;state<=IDLE;end
                end
                default:begin end''')
 return text
if __name__=='__main__':
 (ROOT/'hardware/rtl/memory_scratch_endpoint_retained.sv').write_text(generate((ROOT/'hardware/rtl/memory_scratch_endpoint_indexed.sv').read_text()))
