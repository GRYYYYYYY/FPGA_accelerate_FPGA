// Real center HLS and real cost AXI requests overlap the held final root reply.
// The frontend parent retires first; backend operation_pending must survive.
task retire_with_dependents;
 reg got_cc,got_cs;reg[63:0]held_cc;reg[127:0]held_cs;
 begin
  @(negedge clk);
  cc_req_words=0;cc_req_cookie=32'hdecc0000+query_index;cc_req_design_id=design_id;cc_req_version=3;cc_req_query=1;cc_req_price=3;cc_req_valid=1;
  cs_req_host=0;cs_req_op=0;cs_req_index=65185;cs_req_value=0;cs_req_cookie=32'hdeca0000+query_index;cs_req_version=3;cs_req_query=1;cs_req_price=3;cs_req_valid=1;
  got_cc=0;got_cs=0;
  while(!got_cc||!got_cs)begin
   @(posedge clk);if(cc_req_valid&&cc_req_ready)got_cc=1;if(cs_req_valid&&cs_req_ready)got_cs=1;
   @(negedge clk);if(got_cc)cc_req_valid=0;if(got_cs)cs_req_valid=0;
  end
  if(!result_valid||!operation_pending)$fatal(1,"dependent lost parent before frontend ACK");
  $fdisplay(trace,"DA %0d %0d",cycles,query_index);
  result_ready=1;@(negedge clk);result_ready=0;
  if(result_valid||!operation_pending||f_normal_retired)$fatal(1,"parent native lifetime ended early");
  wait(cc_rsp_valid&&cs_rsp_valid);@(negedge clk);
  if(cc_rsp_status||cc_rsp_words!==64'd0||cc_rsp_cookie!=32'hdecc0000+query_index||cc_rsp_version!=3||cc_rsp_query!=1||cc_rsp_price!=3||cc_rsp_design_id!=design_id)$fatal(1,"real center dependent response");
  if(cs_rsp_status||cs_rsp_data!==128'h3f800000||cs_rsp_cookie!=32'hdeca0000+query_index||cs_rsp_host||cs_rsp_op!=0||cs_rsp_index!=65185||cs_rsp_version!=3||cs_rsp_query!=1||cs_rsp_price!=3)$fatal(1,"real cost dependent response");
  held_cc=cc_rsp_words;held_cs=cs_rsp_data;
  repeat(7)begin
   @(negedge clk);
   if(!operation_pending||f_normal_retired||result_valid||!cc_rsp_valid||!cs_rsp_valid||cc_rsp_words!==held_cc||cs_rsp_data!==held_cs||host_ctrl_ready||host_io_ready||host_owner_req_ready||host_design_req_ready)$fatal(1,"dependent held response/lease");
   $fdisplay(trace,"DH %0d %0d %016h %032h",cycles,query_index,cc_rsp_words,cs_rsp_data);
  end
  cc_rsp_ready=1;cs_rsp_ready=1;@(negedge clk);cc_rsp_ready=0;cs_rsp_ready=0;
  wait(!operation_pending);@(negedge clk);$fdisplay(trace,"DD %0d %0d",cycles,query_index);
 end
endtask
