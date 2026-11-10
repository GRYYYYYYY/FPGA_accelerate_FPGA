from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[3]
def make():
 p=ROOT/'hardware/variants/recovery_join_v1/build_tb.py';sp=importlib.util.spec_from_file_location('old_builder',p);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);s=mod.make().replace('module tb_candidate_offer;', 'module tb_candidate_offer;\nwire lr_busy,lr_fault,lr_rsp_valid;wire[31:0]lr_rsp_cookie;',1)
 s=s.replace('k_rcfg_done=0,k_labels_done=0;', 'k_rcfg_done=0;wire k_labels_done;')
 s=s.replace('.cold_rst(k_cold_rst),.abort(1\'b0)', '.cold_rst(k_cold_rst),.abort(lr_fault||(lr_rsp_valid&&lr_rsp_cookie!=32\'he0010001))')
 s=s.replace('assign host_ctrl_ready=!rc_block&&raw_host_ctrl_ready;', 'assign host_ctrl_ready=!lr_busy&&!rc_block&&raw_host_ctrl_ready;')
 for port,old,new in [('h_l_valid','host_io_valid','lr_busy?lr_l_valid:host_io_valid'),('h_l_write','host_io_write','lr_busy?lr_l_write:host_io_write'),('h_l_node','host_io_node','lr_busy?lr_l_node:host_io_node'),('h_l_value','host_io_value','lr_busy?lr_l_value:host_io_value'),('h_l_field','host_io_field','lr_busy?lr_l_field:host_io_field'),('h_l_rsp_ready','host_io_rsp_ready','lr_busy?lr_l_rsp_ready:host_io_rsp_ready'),('h_l_ready','host_io_ready','mux_h_l_ready'),('h_l_rsp_valid','host_io_rsp_valid','mux_h_l_rsp_valid')]:
  n='.'+port+'('+old+')';assert s.count(n)==1;s=s.replace(n,'.'+port+'('+new+')')
 n='.host_ctrl_valid((host_ctrl_valid&&!rc_block))';assert n in s;s=s.replace(n,'.host_ctrl_valid(((lr_busy?lr_c_valid:host_ctrl_valid)&&!rc_block)),.host_ctrl_op(lr_busy?lr_c_op:host_ctrl_op),.host_ctrl_query(lr_busy?lr_c_query:host_ctrl_query),.host_ctrl_price(lr_busy?lr_c_price:host_ctrl_price),.host_ctrl_version(lr_busy?lr_c_version:host_ctrl_version),.host_ctrl_rsp_ready(lr_busy?lr_c_rsp_ready:host_ctrl_rsp_ready)')
 s=s.replace('route_commit_host_adapter #',(Path(__file__).parent/'controller.inc').read_text()+'\nroute_commit_host_adapter #',1)
 a=s.index(' control(0);\n // Probe fresh');b=s.index(' if(rc_req_ready||expand_ready||seed_ready||rc_slots!=0||rc_fault)',a)
 s=s[:a]+''' // labels_valid automatically starts the hardware service; TB supplies records only.
 rc=$fseek(imports_fd,0,0);if(rc)$fatal(1,"label stream rewind");
 for(import_i=0;import_i<328;import_i=import_i+1)begin
  rc=$fscanf(imports_fd,"%d",import_node);if(rc!=1)$fatal(1,"stream node");
  for(field_i=0;field_i<5;field_i=field_i+1)begin rc=$fscanf(imports_fd,"%h",word);if(rc!=1)$fatal(1,"stream field");import_record[field_i*32+:32]=word;end
  @(negedge clk);lr_s_valid=1;lr_s_node=import_node;lr_s_payload=import_record;lr_s_last=import_i==327;
  do @(posedge clk);while(!lr_s_ready);@(negedge clk);lr_s_valid=0;
 end
 wait(lr_rsp_valid);@(negedge clk);
 if(lr_rsp_status||lr_rsp_cookie!=32'he0010001||lr_fault||lr_written!=328||lr_verified!=328)$fatal(1,"hardware label restore result");
 $fdisplay(trace,"LD %0d %0d %0d %0d",cycles,lr_rsp_status,lr_written,lr_verified);
 wait(!lr_busy);
'''+s[b:]
 s=s.replace('seed_valid=0;k_labels_done=1;', 'seed_valid=0;').replace('k_labels_done=0;k_rsp_ready=1;', 'k_rsp_ready=1;')
 s=s.replace('RECOVERY_JOIN_PASS','LABEL_RESTORE_JOIN_PASS')
 s=s.replace('initial begin\n trace=$fopen',(Path(__file__).parent/'observer.inc').read_text()+'\ninitial begin\n trace=$fopen',1)
 return s
if __name__=='__main__':(Path(__file__).parent/'tb_label_restore_join.sv').write_text(make())
