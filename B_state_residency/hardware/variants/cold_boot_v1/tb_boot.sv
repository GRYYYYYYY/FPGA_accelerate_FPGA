`timescale 1ns/1ps
module tb_boot;
reg  clk=0;
reg  cold_rst=0;
reg  work_rst=0;
reg  required=0;
reg  cfg_valid=0;
wire  cfg_ready;
reg [63:0] cfg_design=0;
reg [63:0] cfg_generation=0;
reg [31:0] cfg_checkpoint=0;
reg [31:0] cfg_version=0;
reg [31:0] cfg_nodes=0;
reg [31:0] cfg_label_count=0;
reg [31:0] cfg_label_crc=0;
reg [31:0] cfg_path_crc=0;
reg [31:0] cfg_query_crc=0;
reg [1:0] cfg_query=0;
reg [1:0] cfg_slots=0;
reg [3:0] cfg_price=0;
reg [2303:0] cfg_payload=0;
wire  pending;
wire  admin_allowed;
wire  done_held;
wire  rsp_valid;
reg  rsp_ready=0;
wire [3:0] rsp_status;
wire [4:0] receipts;
wire [7:0] config_receipts;
reg  verify_valid=0;
wire  verify_ready;
wire [31:0] verified_count;
wire [3:0] verify_status;
reg [15:0] sv=0;
reg [15:0] sr=0;
reg [15:0] srv=0;
reg [15:0] srr=0;
reg [38911:0] sp=0;
reg [4095:0] rp=0;
reg  owner_configured=0;
reg  authority_configured=0;
reg [63:0] authority_design=0;
reg [63:0] authority_generation=0;
reg [31:0] authority_checkpoint=0;
reg  providers_configured=0;
reg  active=0;
reg [63:0] active_design=0;
reg [31:0] active_version=0;
reg [31:0] published_version=0;
reg [1:0] active_query=0;
reg [1:0] route_slots=0;
reg [3:0] active_price=0;
reg  recovery_permit=0;
reg [63:0] recovery_design=0;
reg [31:0] recovery_checkpoint=0;
reg  path_accept=0;
reg  path_restore=0;
reg  path_done=0;
reg [3:0] path_status=0;
reg [31:0] path_crc=0;
reg  query_accept=0;
reg  query_restore=0;
reg  query_done=0;
reg [3:0] query_status=0;
reg [31:0] query_crc=0;
reg  retired=0;
reg  lease_owned=0;
boot_restore_gate dut(.clk(clk),.cold_rst(cold_rst),.work_rst(work_rst),.required(required),.cfg_valid(cfg_valid),.cfg_ready(cfg_ready),.cfg_design(cfg_design),.cfg_generation(cfg_generation),.cfg_checkpoint(cfg_checkpoint),.cfg_version(cfg_version),.cfg_nodes(cfg_nodes),.cfg_label_count(cfg_label_count),.cfg_label_crc(cfg_label_crc),.cfg_path_crc(cfg_path_crc),.cfg_query_crc(cfg_query_crc),.cfg_query(cfg_query),.cfg_slots(cfg_slots),.cfg_price(cfg_price),.cfg_payload(cfg_payload),.pending(pending),.admin_allowed(admin_allowed),.done_held(done_held),.rsp_valid(rsp_valid),.rsp_ready(rsp_ready),.rsp_status(rsp_status),.receipts(receipts),.config_receipts(config_receipts),.verify_valid(verify_valid),.verify_ready(verify_ready),.verified_count(verified_count),.verify_status(verify_status),.sv(sv),.sr(sr),.srv(srv),.srr(srr),.sp(sp),.rp(rp),.owner_configured(owner_configured),.authority_configured(authority_configured),.authority_design(authority_design),.authority_generation(authority_generation),.authority_checkpoint(authority_checkpoint),.providers_configured(providers_configured),.active(active),.active_design(active_design),.active_version(active_version),.published_version(published_version),.active_query(active_query),.route_slots(route_slots),.active_price(active_price),.recovery_permit(recovery_permit),.recovery_design(recovery_design),.recovery_checkpoint(recovery_checkpoint),.path_accept(path_accept),.path_restore(path_restore),.path_done(path_done),.path_status(path_status),.path_crc(path_crc),.query_accept(query_accept),.query_restore(query_restore),.query_done(query_done),.query_status(query_status),.query_crc(query_crc),.retired(retired),.lease_owned(lease_owned));
always #5 clk=~clk;
integer checks=0;
task tick;begin @(posedge clk);#1;@(negedge clk);end endtask
task check(input bit good,input string why);begin checks=checks+1;if(!good)$fatal(1,"CHECK %0d %s receipts=%h cfg=%h",checks,why,receipts,config_receipts);end endtask
task reset_boot;begin required=1;retired=0;lease_owned=0;cold_rst=1;tick();cold_rst=0;tick();check(pending&&!admin_allowed&&!rsp_valid,"cold reset closed");end endtask
task descriptor;begin cfg_valid=1;tick();cfg_valid=0;tick();check(admin_allowed,"descriptor accepted");end endtask
task config_lane(input integer lane,input bit wrong,input bit failed);begin
 sp=0;if(lane<6)sp[lane*2432+:384]=cfg_payload[lane*384+:384];
 else if(lane==14)begin sp[34048]=1;sp[34049+:64]=cfg_design;sp[34113+:32]=cfg_checkpoint;sp[34145+:32]=cfg_version;sp[34177+:2]=cfg_query;sp[34179+:4]=cfg_price;end
 else begin sp[36480+:2304]=cfg_payload;sp[38784+:64]=cfg_design;sp[38848+:32]=cfg_checkpoint;sp[38880]=1;end
 if(wrong)sp[lane*2432]=~sp[lane*2432];sv=1<<lane;sr=sv;tick();sv=0;sr=0;sp=0;rp=0;rp[lane*256]=failed;srv=1<<lane;srr=srv;tick();srv=0;srr=0;rp=0;tick();
end endtask
task all_config;begin for(integer k=0;k<6;k=k+1)config_lane(k,0,0);config_lane(14,0,0);config_lane(15,0,0);check(config_receipts==255,"eight actual config replies");end endtask
task path_receipt(input bit bad);begin path_accept=1;path_restore=1;tick();path_accept=0;tick();path_done=1;path_crc=bad?cfg_path_crc^1:cfg_path_crc;tick();path_done=0;tick();end endtask
task query_receipt(input bit bad);begin query_accept=1;query_restore=1;tick();query_accept=0;tick();query_done=1;query_crc=bad?cfg_query_crc^1:cfg_query_crc;tick();query_done=0;tick();end endtask
task read_label(input integer node,input bit bad);begin
 sp=0;sp[19457+:32]=node;sv=256;sr=256;tick();sv=0;sr=0;sp=0;rp=0;rp[2052]=1;rp[2053+:160]={32'd15,32'd14,32'd13,32'd12,32'd11};if(bad)rp[2053]=~rp[2053];srv=256;srr=256;tick();srv=0;srr=0;rp=0;tick();
end endtask
initial begin
 cfg_design=64'h123456789abcdef0;cfg_generation=64'h100000002;cfg_checkpoint=18;cfg_version=4;cfg_nodes=100;cfg_query=2;cfg_price=4;cfg_slots=1;
 cfg_payload=2304'h123;cfg_label_count=1;cfg_label_crc=32'hd4cfb66d;cfg_path_crc=32'habcd;cfg_query_crc=32'h1234;
 owner_configured=1;authority_configured=1;authority_design=cfg_design;authority_generation=cfg_generation;authority_checkpoint=18;
 providers_configured=1;active=1;active_design=cfg_design;active_version=4;published_version=4;active_query=2;active_price=4;recovery_permit=1;recovery_design=cfg_design;recovery_checkpoint=18;route_slots=1;
 reset_boot();check(receipts[1]==0,"configured booleans alone insufficient");cfg_generation=0;cfg_valid=1;tick();cfg_valid=0;check(rsp_valid&&rsp_status==1&&pending,"zero generation rejected");repeat(3)tick();check(pending,"error held");rsp_ready=1;tick();rsp_ready=0;cfg_generation=64'h100000002;descriptor();
 config_lane(0,1,0);check(config_receipts[0]==0,"wrong payload rejected");config_lane(0,0,1);check(config_receipts[0]==0,"failed config reply rejected");all_config();
 verify_valid=1;tick();verify_valid=0;read_label(7,1);check(!receipts[2]&&verify_status==2,"bad label CRC rejected");
 verify_valid=1;tick();verify_valid=0;read_label(100,0);check(!receipts[2]&&verify_status==1,"out of range label rejected");
 verify_valid=1;tick();verify_valid=0;read_label(7,0);check(receipts[2]&&verified_count==1,"label CRC verified");
 path_receipt(1);check(!receipts[3],"bad path CRC rejected");query_receipt(1);check(!receipts[4],"bad query CRC rejected");path_receipt(0);query_receipt(0);check(receipts==31,"all receipts collected");
 repeat(3)tick();check(!rsp_valid&&pending,"no retirement no completion");retired=1;repeat(2)tick();check(!rsp_valid,"lease required");lease_owned=1;tick();check(rsp_valid&&pending&&!admin_allowed,"completion holds gate closed");repeat(4)tick();check(rsp_valid&&pending,"backpressure holds gate");rsp_ready=1;tick();rsp_ready=0;check(!pending,"consumed completion opens gate");
 reset_boot();descriptor();all_config();verify_valid=1;tick();verify_valid=0;read_label(7,0);path_receipt(0);query_receipt(0);work_rst=1;tick();work_rst=0;tick();check(pending&&!rsp_valid&&!admin_allowed&&config_receipts==0,"work reset cancels bootstrap");
 descriptor();all_config();verify_valid=1;tick();verify_valid=0;read_label(7,0);path_receipt(0);query_receipt(0);
 // Deliberately deliver a successful query reply on the same edge as config mutation.
 query_accept=1;query_restore=1;tick();query_accept=0;query_done=1;query_crc=cfg_query_crc;sv=64;sr=64;tick();query_done=0;sv=0;sr=0;
 check(!receipts[4]&&!receipts[3]&&!receipts[2]&&!rsp_valid,"mutation beats simultaneous receipt");
 query_done=1;tick();query_done=0;check(!receipts[4],"late canceled import ignored");
 authority_generation=64'h0000000000000002;tick();check(!receipts[0]&&!verify_ready,"full 64-bit generation required");authority_generation=cfg_generation;
 verify_valid=1;tick();verify_valid=0;
 sp=0;sp[19457+:32]=7;sv=256;sr=256;tick();sv=0;sr=0;sp=0;rp=0;srv=256;srr=256;tick();srv=0;srr=0;check(verify_status==1&&!receipts[2],"absent label rejected");
 verify_valid=1;tick();verify_valid=0;
 sp=0;sp[19457+:32]=7;sv=256;sr=256;tick();sv=0;sr=0;sp=0;rp=0;rp[2052]=1;rp[2053+:160]={32'd15,32'd14,32'd13,32'd12,32'd11};srv=256;srr=256;
 // Host control and last label read reply can retire together at the observer.
 sv=64;sr=64;tick();sv=0;sr=0;srv=0;srr=0;rp=0;check(!receipts[2],"mutation beats final label reply");
 required=0;cold_rst=1;tick();cold_rst=0;tick();check(!pending&&!rsp_valid,"explicit normal boot mode");
 $display("BOOT_GATE_PASS checks=%0d",checks);$finish;
end
initial begin #200000;$fatal(1,"timeout");end
endmodule
