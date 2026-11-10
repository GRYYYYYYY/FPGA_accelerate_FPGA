"""Paired pilot checker with legal bounded full-fence retry, preserving failures."""
from pathlib import Path
from make_sparse_writeback_tb import render as original_render
ROOT=Path(__file__).resolve().parents[2]
def render():
 s=original_render()['tb_sparse_writeback_pilot.sv']
 s=s.replace('module sparse_writeback_checkpoint_stream_test #(parameter integer SMALL=0,','module sparse_writeback_checkpoint_retry_test #(parameter integer SPARSE_WB=1,SMALL=0,')
 s=s.replace('sparse_writeback_checkpoint_stream_test test();','sparse_writeback_checkpoint_retry_test test();').replace('sparse_writeback_checkpoint_stream_test #(','sparse_writeback_checkpoint_retry_test #(')
 s=s.replace('tb_sparse_writeback_checkpoint_stream','tb_sparse_writeback_checkpoint_retry')
 s=s.replace('if(active_op==5)begin','if(SPARSE_WB && active_op==5)begin')
 s=s.replace('always @(posedge clk)if(!rst)begin','always @(posedge clk)if(!rst && SPARSE_WB)begin')
 before='''        begin send_host(op,slot,page,q,price,gen,off,field,value,frame);receive_host(status,payload,present,dirty,tx,drain);end'''
 after='''        integer retry_count,retained_frames,retained_epoch;
        begin
            retry_count=0;retained_frames=allocated;retained_epoch=dut.memory.memory_service.directory.epoch;
            begin: request_retry
                forever begin
                    send_host(op,slot,page,q,price,gen,off,field,value,frame);
                    if(op==11 && status==0)begin
                        while(!rsp_valid)@(negedge clk);
                        if(rsp_status==7)begin
                            if(!draining || !dut.fence_open || allocated!=retained_frames || page_leases!=0 || memory_leases!=0
                               || dut.memory.memory_service.directory.epoch!=retained_epoch)
                                $fatal(1,"FENCE_WAIT changed unretired lifetime state");
                            receive_host(7,0,0,0,0,1);
                            retry_count=retry_count+1;finish_retries=finish_retries+1;
                            if(retry_count>20)$fatal(1,"bounded FINISH retry exhausted");
                        end else begin receive_host(status,payload,present,dirty,tx,drain);disable request_retry;end
                    end else begin receive_host(status,payload,present,dirty,tx,drain);disable request_retry;end
                end
            end
        end'''
 assert s.count(before)==1;s=s.replace(before,after)
 s=s.replace('integer sparse_codec_count=0,','integer finish_retries=0;\n    integer sparse_codec_count=0,')
 s=s.replace('$display("SPARSE_WB_COUNTS exports=', '$display("FINISH_RETRY_COUNTS retries=%0d",finish_retries);$display("SPARSE_WB_COUNTS exports=')
 s+='\nmodule tb_sparse_writeback_retry_control;sparse_writeback_checkpoint_retry_test #(.SPARSE_WB(0)) test();endmodule\n'
 return s
if __name__=='__main__':
 p=ROOT/'hardware/tb/tb_sparse_writeback_retry.sv';p.write_text(render());print(p)
