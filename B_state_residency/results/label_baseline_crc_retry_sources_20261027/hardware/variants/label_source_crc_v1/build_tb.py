from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'label_frame_export_v1/build_tb.py'
def make():
 s=runpy.run_path(str(BASE))['make']()
 decl='''reg bad_crc=0,crc_pin_flip=0;wire[31:0]lr_source_crc;wire[31:0]crc_input;
initial begin if($value$plusargs("badcrc=%d",bad_crc))begin end end
'''
 pos=s.index('`endif',s.index('localparam FRAMES=16384,INDEX_BITS=14,HASH_BITS=15;'))+len('`endif');s=s[:pos]+'\n'+decl+s[pos:]
 s=s.replace('wm_fault&&!cancel_started','wm_fault&&!cancel_started&&!bad_crc')
 s=s.replace('.ENABLE_FRAME_SCAN(1))system(','.ENABLE_FRAME_SCAN(1),.CHECK_LABEL_CRC(1))system(.snapshot_label_crc(crc_input),.lr_source_crc(lr_source_crc),')
 marker='wait(k_rcfg_valid);@(negedge clk);restore_epoch=k_new_query;restore_version=k_new_version;'
 # Only the actual iter2 task gets the pin-change challenge.
 pos=s.index('task iter2_g2_warm_restore;');s=s[:pos]+s[pos:].replace(marker,marker+'crc_pin_flip=1;$fdisplay(trace,"CRC_PIN_CHANGED %0d %08h",cycles,crc_input);',1)
 marker=' wait(wm_receipts[0]);if(lr_written!=822'
 assert s.count(marker)==1;s=s.replace(marker,''' if(bad_crc)begin
  wait(k_rsp_valid);repeat(8)begin @(negedge clk);if(k_rsp_status!=6||k_count!=2||!wm_owned||!wm_fault||recover_open||wm_receipts||lr_written!=821||lr_verified||lr_source_crc!=ls_crc)$fatal(1,"bad source CRC released recovery");end
  $fdisplay(trace,"LABEL_CRC_REJECT_PASS %0d %0d %0d %0d %08h %08h",cycles,k_rsp_status,k_count,lr_written,lr_source_crc,ls_crc);
  k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;repeat(8)begin @(negedge clk);if(!wm_owned||!wm_fault||recover_open||qc_cmd_ready||rc_req_ready||pc_acquire_ready)$fatal(1,"CRC failure quarantine");end
  $fflush(trace);$fclose(trace);$display("LABEL_CRC_REJECT_PASS");$finish;
 end
 wait(wm_receipts[0]);if(lr_source_crc!=ls_crc)$fatal(1,"source CRC binding");if(lr_written!=822''')
 extra='''
assign crc_input=ls_crc^(bad_crc?32'd1:32'd0)^(crc_pin_flip?32'h100:32'd0);
always @(posedge clk)if(!k_cold_rst)begin
 if(k_rec_valid&&k_rec_ready)$fdisplay(trace,"LABEL_CRC_DESCRIPTOR %0d %08h %08h",cycles,crc_input,ls_crc);
 if(lr_rsp_valid&&lr_rsp_ready)$fdisplay(trace,"LABEL_CRC_RESULT %0d %0d %0d %0d %08h",cycles,lr_rsp_status,lr_written,lr_verified,lr_source_crc);
end
'''
 return s.replace('\nendmodule',extra+'\nendmodule')
def make_default(base):return runpy.run_path(str(base))['make']()
if __name__=='__main__':HERE.joinpath('tb_crc.sv').write_text(make())
