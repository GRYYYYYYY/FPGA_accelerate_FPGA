from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=ROOT/'hardware/variants/label_baseline_miss_v1/build_tb.py'
def make():
 b=runpy.run_path(str(BASE));b['make'].__globals__['HERE']=HERE;s=b['make']()
 mark='phase=1;io(0,0,2,0,0,v0);check(misses==1);'
 assert mark in s;s=s.replace(mark,'''phase=1;raw_probe_check(0,0,0);check(misses==0);
 io(0,0,2,0,0,v0);check(misses==1);raw_probe_check(0,1,v0);check(misses==1);
 baseline_raw_probe=1;io(0,1,3,32'd987,3,0);baseline_raw_probe=0;
 io(0,0,2,0,0,v0);check(misses==1);''',1)
 extra='''
task raw_probe_check(input integer n,present,input[159:0]want);begin
 @(negedge clk);baseline_raw_probe=1;io_node=n;io_write=0;io_field=2;io_value=0;io_valid=1;
 do @(posedge clk);while(!io_ready);
 @(negedge clk);io_valid=0;baseline_raw_probe=0;io_node=32'hffffffff;
 wait(io_rsp_valid);#1;check(io_status==0&&io_present==present&&io_payload==want);
 repeat(4)begin @(posedge clk);#1;check(io_rsp_valid&&io_status==0&&io_present==present&&io_payload==want);end
 $fdisplay(tf,"RAW %0d %0d %040h %0d",n,io_present,io_payload,misses);
 @(negedge clk);io_rsp_ready=1;@(posedge clk);@(negedge clk);io_rsp_ready=0;
end endtask
'''
 return s.replace('initial begin\n fd=',extra+'initial begin\n fd=',1) if 'initial begin\n fd='in s else s.replace('\nendmodule',extra+'\nendmodule')
if __name__=='__main__':(HERE/'tb_probe.sv').write_text(make())
