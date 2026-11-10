`timescale 1ns/1ps
module tb_join;
reg clk=0;always #5 clk=~clk;
reg rst=1,abort=0,owned_in=1,drained=1,repaired=0,arm=0,finish=0;
reg[31:0]version=0,arm_cp=18;wire arm_ready,owned,la,safe,pa,qa,joined,fault;wire[2:0]receipts;
reg[31:0]pcrc,qcrc;integer trace,cycles=0,checks=0,scenario=0;reg[11:0]old_g=12'hfff;reg[39:0]old_i=40'hffffffffff;
reg lv=0,lack=0,lsv=0,llast=0;wire lr,lrsp,lsr,lbusy,lfault;reg[31:0]lnode=0,lcookie=777;reg[159:0]ldata=0;wire[3:0]lstatus;wire[31:0]lrcookie,lwritten,lverified;
wire cv,cr,crv,crr;wire[1:0]cop,cquery;wire[3:0]cprice;wire[31:0]cversion;
reg crvalid=0;assign crv=crvalid;assign cr=!crvalid;
wire mv,mready,mwrite,mrv,mrr,mpresent;wire[31:0]mnode,mvalue;wire[2:0]mfield;wire[159:0]mpayload;reg mrvalid=0,mrpresent=0;reg[159:0]mrdata=0;
assign mready=!mrvalid;assign mrv=mrvalid;assign mpresent=mrpresent;assign mpayload=mrdata;
reg[191:0]rows[0:327];reg[159:0]memory[0:327];reg present[0:327];integer mi;
reg pv=0,pack=0,psv=0,plast=0;reg[31:0]pi=0,pdata=0,expected_pcrc;wire pr,prsp,psr,pbusy,pfault;wire[3:0]pstatus;wire[31:0]actual_pcrc;wire[1:0]slots;
reg qv=0,qack=0,qsv=0,qlast=0;reg[31:0]qi=0,qdata=0,expected_qcrc;wire qr,qrsp,qsr,qbusy;wire[3:0]qstatus;wire[31:0]actual_qcrc;
reg[31:0]path_image[0:77],query_image[0:9];
wire retired=!lbusy&&!pbusy&&!qbusy&&!crvalid&&!mrvalid;
warm_restore_receipt_join gate(.clk(clk),.cold_rst(rst),.abort(abort),.recovery_owned(owned_in),.backend_drained(drained),.retired(retired),.owner_repaired(repaired),.arm_valid(arm),.arm_ready(arm_ready),.arm_design(64'h123456789abcdef0),.arm_generation(64'h100000002),.bound_design(64'h123456789abcdef0),.bound_generation(64'h100000002),.arm_checkpoint(arm_cp),.bound_checkpoint(32'd18),.arm_version(32'd5),.active_version(version),.arm_query(2'd3),.active_query(2'd3),.arm_price(4'd5),.active_price(4'd5),.arm_cookie(32'd777),.arm_labels(32'd328),.arm_path_crc(pcrc),.arm_query_crc(qcrc),
.label_accept(lv&&la&&lr),.label_done(lrsp&&lack),.label_status(lstatus),.label_cookie(lrcookie),.label_written(lwritten),.label_verified(lverified),.path_accept(pv&&pa&&pr),.path_restore(1'b1),.path_done(prsp&&pack),.path_status(pstatus),.path_crc(actual_pcrc),.query_accept(qv&&qa&&qr),.query_restore(1'b1),.query_done(qrsp&&qack),.query_status(qstatus),.query_crc(actual_qcrc),.completion_consumed(finish),.owned(owned),.label_allow(la),.admin_safe(safe),.path_allow(pa),.query_allow(qa),.joined(joined),.fault(fault),.receipts(receipts));
label_restore_controller labels(.clk(clk),.rst(rst),.abort(abort),.backend_drained(drained),.start_valid(lv&&la),.start_ready(lr),.start_design(64'h123456789abcdef0),.expected_design(64'h123456789abcdef0),.start_checkpoint(32'd18),.expected_checkpoint(32'd18),.start_cookie(lcookie),.start_count(32'd328),.start_nodes(32'd9089009),.start_probe(32'd0),.start_version(32'd5),.start_query(2'd3),.start_price(4'd5),.s_valid(lsv),.s_ready(lsr),.s_node(lnode),.s_cookie(lcookie),.s_payload(ldata),.s_last(llast),.rsp_valid(lrsp),.rsp_ready(lack),.rsp_status(lstatus),.rsp_cookie(lrcookie),.written(lwritten),.verified(lverified),.busy(lbusy),.fault(lfault),.c_valid(cv),.c_ready(cr),.c_op(cop),.c_query(cquery),.c_price(cprice),.c_version(cversion),.c_rsp_valid(crv),.c_rsp_ready(crr),.c_status(4'd0),.l_valid(mv),.l_ready(mready),.l_write(mwrite),.l_node(mnode),.l_value(mvalue),.l_field(mfield),.l_rsp_valid(mrv),.l_rsp_ready(mrr),.l_status(4'd0),.l_present(mpresent),.l_payload(mpayload));
route_commit_controller paths(.clk(clk),.rst(rst),.abort(abort),.active(1'b1),.lease(safe),.cp_valid(pv&&pa),.cp_ready(pr),.cp_restore(1'b1),.cp_safe(safe),.cp_design(64'h123456789abcdef0),.cp_nodes(32'd9089009),.cp_nets(32'd27960),.cp_expected_crc(expected_pcrc),.cp_busy(pbusy),.cp_rsp_valid(prsp),.cp_rsp_ready(pack),.cp_status(pstatus),.cp_crc(actual_pcrc),.cp_s_valid(psv),.cp_s_ready(psr),.cp_s_index(pi),.cp_s_data(pdata),.cp_s_last(plast),.cp_m_ready(1'b0),.active_query(2'd3),.active_price(4'd5),.active_version(version),.active_design(64'h123456789abcdef0),.req_valid(1'b0),.rsp_ready(1'b0),.slot_valid(slots),.busy(),.fault(pfault),.l_ready(1'b0),.l_rsp_valid(1'b0),.l_status(4'd0),.l_present(1'b0),.l_payload(160'd0),.o_ready(1'b0),.o_rsp_valid(1'b0),.o_status(4'd0),.o_rsp_cookie(32'd0));
query_lifecycle #(.ENABLE_REBASE(1)) queries(.clk(clk),.rst(rst),.abort(abort),.admit(1'b0),.backend_fault(1'b0),.backend_drained(drained),.active(1'b1),.host_label_edit(1'b0),.active_generation(64'h100000002),.cp_rebase(1'b1),.cp_rebase_permit(safe),.cp_source_version(32'd4),.cp_source_query(2'd2),.cp_source_price(4'd4),.cp_valid(qv&&qa),.cp_restore(1'b1),.cp_safe(safe),.cp_ready(qr),.cp_busy(qbusy),.cp_expected_crc(expected_qcrc),.cp_rsp_valid(qrsp),.cp_rsp_ready(qack),.cp_status(qstatus),.cp_crc(actual_qcrc),.cp_s_valid(qsv),.cp_s_ready(qsr),.cp_s_index(qi),.cp_s_data(qdata),.cp_s_last(qlast),.cp_m_ready(1'b0),.active_design(64'h123456789abcdef0),.active_version(version),.active_query(2'd3),.active_price(4'd5),.route_slots(slots),.cmd_valid(1'b0),.service_ready(1'b0),.service_rsp_valid(1'b0),.service_rsp_payload(256'd0),.search_ready(1'b0),.search_rsp_valid(1'b0),.search_status(4'd0),.search_rsp_cookie(32'd0),.search_result_node(32'd0),.route_ready(1'b0),.route_rsp_valid(1'b0),.route_status(4'd0),.route_rsp_cookie(32'd0),.route_nodes(32'd0),.route_acked(32'd0));
// Behavioral mutable label storage: actual writes and later readback, no forced replies.
always @(posedge clk)begin
 if(rst)begin crvalid<=0;mrvalid<=0;end else begin
  if(cv&&cr)begin
   if(cversion!=5||cquery!=3||cprice!=5||cop>1)$fatal(1,"control context");
   if(cop==0)version<=5;
   if(cop==0)for(integer i=0;i<328;i=i+1)begin present[i]<=0;memory[i]<=0;end
   crvalid<=1;$fdisplay(trace,"C %0d %0d %0d",scenario,cycles,cop);
  end else if(crvalid&&crr)crvalid<=0;
  if(mv&&mready)begin
   mi=-1;for(integer i=0;i<328;i=i+1)if(rows[i][191:160]==mnode)mi=i;
   mrdata<=0;mrpresent<=0;
   if(mwrite)begin if(mi<0||mfield>4)$fatal(1,"bad memory write");memory[mi][mfield*32+:32]<=mvalue;present[mi]<=1;end
   else if(mi>=0)begin mrdata<=memory[mi];mrpresent<=present[mi];end
   mrvalid<=1;$fdisplay(trace,"B %0d %0d %0d %0d %0d %08h",scenario,cycles,mwrite,mnode,mfield,mvalue);
  end else if(mrvalid&&mrr)mrvalid<=0;
 end
end
function automatic[31:0]image_crc(input bit query_packet);reg[31:0]v;begin v=32'hffffffff;for(integer i=0;i<(query_packet?10:78);i=i+1)begin v=v^(query_packet?query_image[i]:path_image[i]);for(integer b=0;b<32;b=b+1)v=v[0]?(v>>1)^32'hedb88320:v>>1;end image_crc=~v;end endfunction
task check(input bit ok);begin checks=checks+1;if(!ok)$fatal(1,"check %0d scenario=%0d state=%0d receipts=%b",checks,scenario,gate.state,receipts);end endtask
task reset_all;begin check(retired);@(negedge clk);rst=1;repeat(3)@(negedge clk);rst=0;abort=0;repaired=0;version=0;arm_cp=18;lcookie=777;expected_pcrc=pcrc;expected_qcrc=qcrc;end endtask
task start_join;begin @(negedge clk);arm=1;do @(posedge clk);while(!arm_ready);@(negedge clk);arm=0;repeat(8)begin @(negedge clk);check(owned&&!la&&!safe&&!joined&&!fault);end repaired=1;end endtask
task restore_labels;begin
 repeat(2)begin @(negedge clk);check(!fault&&la);end
 @(negedge clk);lv=1;do @(posedge clk);while(!(la&&lr));@(negedge clk);
 for(integer i=0;i<328;i=i+1)begin @(negedge clk);lnode=rows[i][191:160];ldata=rows[i][159:0];llast=i==327;lsv=1;do @(posedge clk);while(!lsr);@(negedge clk);lsv=0;end
 wait(lrsp);repeat(8)begin @(negedge clk);check(!safe&&!joined&&receipts==0&&lstatus==0&&lwritten==328&&lverified==328);end lack=1;@(negedge clk);lack=0;repeat(8)begin @(negedge clk);check(!la&&owned&&!joined);end lv=0;
end endtask
task path_start;begin @(negedge clk);pv=1;do @(posedge clk);while(!(pa&&pr));@(negedge clk);pv=0;end endtask
task path_words(input integer first,last);begin for(integer i=first;i<last;i=i+1)begin @(negedge clk);pi=i;pdata=path_image[i];plast=i==77;psv=1;do @(posedge clk);while(!psr);@(negedge clk);psv=0;end end endtask
task path_reply(input[3:0]want);begin wait(prsp);repeat(8)begin @(negedge clk);check(pstatus==want&&!joined&&receipts==1);end pack=1;@(negedge clk);pack=0;end endtask
task query_start;begin @(negedge clk);qv=1;do @(posedge clk);while(!(qa&&qr));@(negedge clk);qv=0;end endtask
task query_words(input integer first,last);begin for(integer i=first;i<last;i=i+1)begin @(negedge clk);qi=i;qdata=query_image[i];qlast=i==9;qsv=1;do @(posedge clk);while(!qsr);@(negedge clk);qsv=0;end end endtask
task query_reply(input[3:0]want);begin wait(qrsp);repeat(8)begin @(negedge clk);check(qstatus==want&&!joined&&receipts==3);end qack=1;@(negedge clk);qack=0;end endtask
task successful_restores;begin
 restore_labels;repeat(20)begin @(negedge clk);check(safe&&!joined&&receipts==1&&!lrsp);end
 path_start;path_words(0,39);repeat(10)begin @(negedge clk);check(safe&&!retired&&!joined&&receipts==1&&slots==0);end path_words(39,78);path_reply(0);
 query_start;query_words(0,5);repeat(10)begin @(negedge clk);check(safe&&!retired&&!joined&&receipts==3&&queries.last_sequence==0);end query_words(5,10);query_reply(0);
 wait(joined);check(slots==1&&queries.last_sequence==1&&queries.last_version==5&&queries.last_query==3&&queries.last_price==5);
end endtask
always @(posedge clk)begin
 cycles=cycles+1;
 if({rst,abort,owned_in,drained,repaired,version,arm_cp[2:0]}!=old_i)begin
  $fdisplay(trace,"I %0d %0d %0d %0d %0d %0d %0d %0d %0d",scenario,cycles,rst,abort,owned_in,drained,repaired,version,arm_cp);old_i={rst,abort,owned_in,drained,repaired,version,arm_cp[2:0]};
 end
 if(!rst&&{gate.state,receipts,joined,fault,owned,safe,retired,drained,repaired}!=old_g)begin
  $fdisplay(trace,"G %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d",scenario,cycles,gate.state,receipts,joined,fault,owned,safe,retired,drained,repaired);old_g={gate.state,receipts,joined,fault,owned,safe,retired,drained,repaired};
 end
 if(rst)old_g=12'hfff;
 if(cycles>150000)$fatal(1,"watchdog");
 if(arm&&arm_ready)$fdisplay(trace,"A %0d %0d %0d",scenario,cycles,arm_cp);
 if(lv&&la&&lr)$fdisplay(trace,"L %0d %0d %0d",scenario,cycles,lcookie);
 if(lrsp&&lack)$fdisplay(trace,"LR %0d %0d %0d %0d %0d %0d",scenario,cycles,lstatus,lrcookie,lwritten,lverified);
 if(pv&&pa&&pr)$fdisplay(trace,"P %0d %0d %08h",scenario,cycles,expected_pcrc);
 if(psv&&psr)$fdisplay(trace,"PW %0d %0d %0d %08h %0d",scenario,cycles,pi,pdata,plast);
 if(prsp&&pack)$fdisplay(trace,"PR %0d %0d %0d %08h",scenario,cycles,pstatus,actual_pcrc);
 if(qv&&qa&&qr)$fdisplay(trace,"Q %0d %0d %08h",scenario,cycles,expected_qcrc);
 if(qsv&&qsr)$fdisplay(trace,"QW %0d %0d %0d %08h %0d",scenario,cycles,qi,qdata,qlast);
 if(qrsp&&qack)$fdisplay(trace,"QR %0d %0d %0d %08h",scenario,cycles,qstatus,actual_qcrc);
 if(finish)$fdisplay(trace,"F %0d %0d %0d %0d",scenario,cycles,joined,fault);
 if(!rst&&joined&&(receipts!=7||!retired||!owned||fault))$fatal(1,"join qualification");
end
initial begin
 trace=$fopen("native.txt","w");$readmemh("labels.hex",rows);$readmemh("paths.hex",path_image);$readmemh("query.hex",query_image);if(!$value$plusargs("pcrc=%h",pcrc)||!$value$plusargs("qcrc=%h",qcrc))$fatal(1,"crc args");expected_pcrc=pcrc;expected_qcrc=qcrc;
 repeat(3)@(negedge clk);rst=0;
 start_join;successful_restores;repeat(8)begin @(negedge clk);check(joined&&owned&&!safe);end
 drained=0;repeat(8)begin @(negedge clk);check(!joined&&owned&&!fault);end drained=1;@(negedge clk);finish=1;@(negedge clk);finish=0;check(!owned&&receipts==0);
 scenario=1;reset_all;start_join;lcookie=778;restore_labels;repeat(3)@(negedge clk);check(fault&&owned&&!safe&&!joined&&slots==0);reset_all;
 scenario=2;start_join;restore_labels;expected_pcrc=pcrc^1;path_start;path_words(0,78);path_reply(1);repeat(3)@(negedge clk);check(fault&&owned&&!safe&&!joined&&slots==0);reset_all;
 scenario=3;start_join;restore_labels;path_start;path_words(0,78);path_reply(0);query_start;query_words(0,9);@(negedge clk);abort=1;query_reply(2);repeat(3)@(negedge clk);check(fault&&owned&&!joined&&queries.last_sequence==0);reset_all;
 scenario=4;start_join;successful_restores;@(negedge clk);abort=1;finish=1;#1;check(!joined);@(negedge clk);finish=0;check(fault&&owned);reset_all;
 scenario=5;arm_cp=17;@(negedge clk);arm=1;do @(posedge clk);while(!arm_ready);@(negedge clk);arm=0;check(fault&&owned&&!safe&&!joined);reset_all;
 scenario=6;start_join;restore_labels;@(negedge clk);version=6;@(negedge clk);check(fault&&owned&&!safe&&!joined);reset_all;
 scenario=7;start_join;restore_labels;path_image[7]=42;expected_pcrc=image_crc(0);path_start;path_words(0,78);path_reply(0);repeat(3)@(negedge clk);check(fault&&owned&&!joined&&slots==1);reset_all;$readmemh("paths.hex",path_image);
 scenario=8;start_join;restore_labels;path_start;path_words(0,78);path_reply(0);query_image[8]=2;expected_qcrc=image_crc(1);query_start;query_words(0,10);query_reply(0);repeat(3)@(negedge clk);check(fault&&owned&&!joined&&queries.last_sequence==2);reset_all;
 $fdisplay(trace,"DONE %0d",checks);$fclose(trace);$display("WARM_RECEIPT_JOIN_PASS checks=%0d",checks);$finish;
end
endmodule
