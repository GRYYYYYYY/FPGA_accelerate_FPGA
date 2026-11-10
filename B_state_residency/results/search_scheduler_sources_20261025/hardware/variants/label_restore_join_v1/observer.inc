always @(posedge clk)if(!k_cold_rst)begin
 if(lr_c_valid&&lr_c_ready)$fdisplay(trace,"LC %0d %0d",cycles,lr_c_op);
 if(lr_l_valid&&lr_l_ready)$fdisplay(trace,"LL %0d %0d %0d %0d %08h",cycles,lr_l_write,lr_l_node,lr_l_field,lr_l_value);
 if(lr_l_rsp_valid&&lr_l_rsp_ready)begin
  $fdisplay(trace,"LX %0d %0d %0d %040h",cycles,host_io_status,host_io_present,host_io_payload);
  if(label_restore.state==4)$fdisplay(trace,"ABS %0d %040h",cycles,host_io_payload);
  if(label_restore.state==10)$fdisplay(trace,"CHECK %0d %0d %040h",cycles,label_restore.row[191:160],host_io_payload);
 end
 if(lr_s_valid&&lr_s_ready)$fdisplay(trace,"RELOAD %0d %0d %040h",cycles,lr_s_node,lr_s_payload);
 if(lr_busy&&(host_ctrl_ready||host_io_ready))$fatal(1,"label restore exclusive host lease");
end
