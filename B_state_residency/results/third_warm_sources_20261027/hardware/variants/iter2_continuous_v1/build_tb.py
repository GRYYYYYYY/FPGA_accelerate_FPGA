"""Preserve native q180327 and execute observed next-connection old-path ripup."""
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/'iter2_lifecycle_v1/tb_iter2.sv'
def make():
 s=BASE.read_text()
 start=s.index(' stage_no=1;route_command(1,0,204279,180327);')
 end=s.index('\nend\n\ntask ap_get',start)
 s=s[:start]+''' iter2_prepare_continuous;
 $fdisplay(trace,"ITER2_CONTINUOUS_PREP_PASS %0d",cycles);$fflush(trace);$fclose(trace);$display("ITER2_CONTINUOUS_PREP_PASS");$finish;
'''+s[end:]
 extra='''
function [31:0] prep_crc_word(input [31:0] crc,data);reg[31:0] c;integer b;begin c=crc;for(b=0;b<32;b=b+1)begin if(c[0]^data[b])c=(c>>1)^32'hedb88320;else c=c>>1;end prep_crc_word=c;end endfunction
reg[31:0]prep_crc;
task iter2_prepare_continuous;begin
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 cap_path_restore=0;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<78;x=x+1)begin
  wait(cap_path_m_valid);@(negedge clk);if(cap_path_m_index!=x||cap_path_m_last!=(x==77))$fatal(1,"prep export boundary");cap_path_image[x]=cap_path_m_data;cap_path_m_ready=1;@(negedge clk);cap_path_m_ready=0;
 end
 wait(cap_path_rsp_valid);@(negedge clk);if(cap_path_status||cap_path_image[0]!=1||cap_path_image[1]!=3||cap_path_image[39]!=0)$fatal(1,"prep initial slots");cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 // Slot0 comes unmodified from the real committed-path export. Slot1 is the observed historical path.
 cap_path_image[39]=1;cap_path_image[40]=3;cap_path_image[41]=26422;cap_path_image[42]=66893;cap_path_image[43]=67922;cap_path_image[44]=design_id[31:0];cap_path_image[45]=design_id[63:32];
 cap_path_image[46]=990179;cap_path_image[47]=558358;cap_path_image[48]=265324;
 prep_crc=32'hffffffff;for(integer x=0;x<78;x=x+1)prep_crc=prep_crc_word(prep_crc,cap_path_image[x]);warm_pcrc=~prep_crc;
 cap_path_restore=1;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<78;x=x+1)begin
  @(negedge clk);warm_pi=x;warm_pd=cap_path_image[x];warm_plast=x==77;warm_psv=1;do @(posedge clk);while(!system.cp_s_ready);@(negedge clk);warm_psv=0;
  $fdisplay(trace,"PREP_PATH_IMPORT %0d %08h",x,cap_path_image[x]);
 end
 wait(cap_path_rsp_valid);@(negedge clk);if(cap_path_status||cap_path_crc!=warm_pcrc||rc_slots!=3)$fatal(1,"prep historical import");cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 stage_no=4;owner_op(0,990179,2,2);route_command(1,1,67922,180328);
 owner_op(0,990179,1,2);owner_op(0,339193,1,1);owner_op(0,558358,3,2);owner_op(0,265324,4,1);iter2_foreign_probe;
 if(rc_slots!=1||system.controller.last_sequence!=180327||fault||rc_fault||k_fault||!f_all_drained||!f_backend_idle)$fatal(1,"prep continuous state");
 $fdisplay(trace,"PREP_CONTINUITY %0d %0d %0d %0d",cycles,rc_slots,k_count,system.controller.last_sequence);
end endtask
'''
 s=s.replace('\nendmodule',extra+'\nendmodule');return s
if __name__=='__main__':Path(__file__).with_name('tb_continuous.sv').write_text(make())
