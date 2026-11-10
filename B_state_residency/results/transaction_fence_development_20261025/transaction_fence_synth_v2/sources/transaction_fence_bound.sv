`timescale 1ns/1ps
// Actual request/reply field widths, zero padding only; no fixed runtime data.
module transaction_fence_bound(
 input wire clk,rst,work_permit,normal_fault,backend_drained,backend_idle,route_block,
 input wire[16-1:0]s_valid,output wire[16-1:0]s_ready,input wire[5289:0]s_payload,
 output wire[16-1:0]s_rsp_valid,input wire[16-1:0]s_rsp_ready,output wire[1185:0]s_rsp_payload,
 input wire[16-1:0]cb_valid,output wire[16-1:0]cb_ready,input wire[1614:0]cb_payload,
 output wire[16-1:0]cb_rsp_valid,input wire[16-1:0]cb_rsp_ready,output wire[287:0]cb_rsp_payload,
 output wire[16-1:0]d_valid,input wire[16-1:0]d_ready,output wire[5289:0]d_payload,
 input wire[16-1:0]d_rsp_valid,output wire[16-1:0]d_rsp_ready,input wire[1185:0]d_rsp_payload,
 input wire route_valid,output wire route_ready,input wire[191:0]route_payload,output wire route_rsp_valid,input wire route_rsp_ready,
 output wire backend_route_valid,input wire backend_route_ready,output wire[191:0]backend_route_payload,input wire backend_route_rsp_valid,output wire backend_route_rsp_ready,input wire route_error,
 input wire recover_valid,output wire recover_ready,output wire backend_recover_valid,input wire backend_recover_ready,
 output wire recover_rsp_valid,input wire recover_rsp_ready,input wire backend_recover_rsp_valid,output wire backend_recover_rsp_ready,input wire recover_error,
 output wire normal_retired,output wire recovery_owned,output wire fault,output wire[3:0]phase,output wire[16-1:0]callback_pending
);
wire[38911:0]full_s_payload;
wire[38911:0]full_cb_payload;
wire[38911:0]full_d_payload;
wire[4095:0]full_s_rsp_payload;
wire[4095:0]full_cb_rsp_payload;
wire[4095:0]full_d_rsp_payload;
assign full_s_payload[0+:256]=s_payload[0+:256];
assign full_s_payload[256+:2176]=0;
assign full_s_payload[2432+:256]=s_payload[256+:256];
assign full_s_payload[2688+:2176]=0;
assign full_s_payload[4864+:96]=s_payload[512+:96];
assign full_s_payload[4960+:2336]=0;
assign full_s_payload[7296+:192]=s_payload[608+:192];
assign full_s_payload[7488+:2240]=0;
assign full_s_payload[9728+:256]=s_payload[800+:256];
assign full_s_payload[9984+:2176]=0;
assign full_s_payload[12160+:352]=s_payload[1056+:352];
assign full_s_payload[12512+:2080]=0;
assign full_s_payload[14592+:40]=s_payload[1408+:40];
assign full_s_payload[14632+:2392]=0;
assign full_s_payload[17024+:131]=s_payload[1448+:131];
assign full_s_payload[17155+:2301]=0;
assign full_s_payload[19456+:68]=s_payload[1579+:68];
assign full_s_payload[19524+:2364]=0;
assign full_s_payload[21888+:99]=s_payload[1647+:99];
assign full_s_payload[21987+:2333]=0;
assign full_s_payload[24320+:262]=s_payload[1746+:262];
assign full_s_payload[24582+:2170]=0;
assign full_s_payload[26752+:448]=s_payload[2008+:448];
assign full_s_payload[27200+:1984]=0;
assign full_s_payload[29184+:160]=s_payload[2456+:160];
assign full_s_payload[29344+:2272]=0;
assign full_s_payload[31616+:138]=s_payload[2616+:138];
assign full_s_payload[31754+:2294]=0;
assign full_s_payload[34048+:135]=s_payload[2754+:135];
assign full_s_payload[34183+:2297]=0;
assign full_s_payload[36480+:2401]=s_payload[2889+:2401];
assign full_s_payload[38881+:31]=0;
assign full_cb_payload[0+:256]=cb_payload[0+:256];
assign full_cb_payload[256+:2176]=0;
assign full_cb_payload[2432+:256]=cb_payload[256+:256];
assign full_cb_payload[2688+:2176]=0;
assign full_cb_payload[4864+:96]=cb_payload[512+:96];
assign full_cb_payload[4960+:2336]=0;
assign full_cb_payload[7296+:192]=cb_payload[608+:192];
assign full_cb_payload[7488+:2240]=0;
assign full_cb_payload[9728+:256]=cb_payload[800+:256];
assign full_cb_payload[9984+:2176]=0;
assign full_cb_payload[12160+:352]=cb_payload[1056+:352];
assign full_cb_payload[12512+:2080]=0;
assign full_cb_payload[14592+:40]=cb_payload[1408+:40];
assign full_cb_payload[14632+:2392]=0;
assign full_cb_payload[17024+:131]=0;
assign full_cb_payload[17155+:2301]=0;
assign full_cb_payload[19456+:68]=cb_payload[1448+:68];
assign full_cb_payload[19524+:2364]=0;
assign full_cb_payload[21888+:99]=cb_payload[1516+:99];
assign full_cb_payload[21987+:2333]=0;
assign full_cb_payload[24320+:262]=0;
assign full_cb_payload[24582+:2170]=0;
assign full_cb_payload[26752+:448]=0;
assign full_cb_payload[27200+:1984]=0;
assign full_cb_payload[29184+:160]=0;
assign full_cb_payload[29344+:2272]=0;
assign full_cb_payload[31616+:138]=0;
assign full_cb_payload[31754+:2294]=0;
assign full_cb_payload[34048+:135]=0;
assign full_cb_payload[34183+:2297]=0;
assign full_cb_payload[36480+:2401]=0;
assign full_cb_payload[38881+:31]=0;
assign d_payload[0+:256]=full_d_payload[0+:256];
assign d_payload[256+:256]=full_d_payload[2432+:256];
assign d_payload[512+:96]=full_d_payload[4864+:96];
assign d_payload[608+:192]=full_d_payload[7296+:192];
assign d_payload[800+:256]=full_d_payload[9728+:256];
assign d_payload[1056+:352]=full_d_payload[12160+:352];
assign d_payload[1408+:40]=full_d_payload[14592+:40];
assign d_payload[1448+:131]=full_d_payload[17024+:131];
assign d_payload[1579+:68]=full_d_payload[19456+:68];
assign d_payload[1647+:99]=full_d_payload[21888+:99];
assign d_payload[1746+:262]=full_d_payload[24320+:262];
assign d_payload[2008+:448]=full_d_payload[26752+:448];
assign d_payload[2456+:160]=full_d_payload[29184+:160];
assign d_payload[2616+:138]=full_d_payload[31616+:138];
assign d_payload[2754+:135]=full_d_payload[34048+:135];
assign d_payload[2889+:2401]=full_d_payload[36480+:2401];
assign s_rsp_payload[0+:3]=full_s_rsp_payload[0+:3];
assign s_rsp_payload[3+:3]=full_s_rsp_payload[256+:3];
assign s_rsp_payload[6+:3]=full_s_rsp_payload[512+:3];
assign s_rsp_payload[9+:3]=full_s_rsp_payload[768+:3];
assign s_rsp_payload[12+:3]=full_s_rsp_payload[1024+:3];
assign s_rsp_payload[15+:3]=full_s_rsp_payload[1280+:3];
assign s_rsp_payload[18+:4]=full_s_rsp_payload[1536+:4];
assign s_rsp_payload[22+:132]=full_s_rsp_payload[1792+:132];
assign s_rsp_payload[154+:165]=full_s_rsp_payload[2048+:165];
assign s_rsp_payload[319+:101]=full_s_rsp_payload[2304+:101];
assign s_rsp_payload[420+:200]=full_s_rsp_payload[2560+:200];
assign s_rsp_payload[620+:166]=full_s_rsp_payload[2816+:166];
assign s_rsp_payload[786+:160]=full_s_rsp_payload[3072+:160];
assign s_rsp_payload[946+:238]=full_s_rsp_payload[3328+:238];
assign s_rsp_payload[1184+:1]=full_s_rsp_payload[3584+:1];
assign s_rsp_payload[1185+:1]=full_s_rsp_payload[3840+:1];
assign cb_rsp_payload[0+:3]=full_cb_rsp_payload[0+:3];
assign cb_rsp_payload[3+:3]=full_cb_rsp_payload[256+:3];
assign cb_rsp_payload[6+:3]=full_cb_rsp_payload[512+:3];
assign cb_rsp_payload[9+:3]=full_cb_rsp_payload[768+:3];
assign cb_rsp_payload[12+:3]=full_cb_rsp_payload[1024+:3];
assign cb_rsp_payload[15+:3]=full_cb_rsp_payload[1280+:3];
assign cb_rsp_payload[18+:4]=full_cb_rsp_payload[1536+:4];
assign cb_rsp_payload[22+:165]=full_cb_rsp_payload[2048+:165];
assign cb_rsp_payload[187+:101]=full_cb_rsp_payload[2304+:101];
assign full_d_rsp_payload[0+:3]=d_rsp_payload[0+:3];
assign full_d_rsp_payload[3+:253]=0;
assign full_d_rsp_payload[256+:3]=d_rsp_payload[3+:3];
assign full_d_rsp_payload[259+:253]=0;
assign full_d_rsp_payload[512+:3]=d_rsp_payload[6+:3];
assign full_d_rsp_payload[515+:253]=0;
assign full_d_rsp_payload[768+:3]=d_rsp_payload[9+:3];
assign full_d_rsp_payload[771+:253]=0;
assign full_d_rsp_payload[1024+:3]=d_rsp_payload[12+:3];
assign full_d_rsp_payload[1027+:253]=0;
assign full_d_rsp_payload[1280+:3]=d_rsp_payload[15+:3];
assign full_d_rsp_payload[1283+:253]=0;
assign full_d_rsp_payload[1536+:4]=d_rsp_payload[18+:4];
assign full_d_rsp_payload[1540+:252]=0;
assign full_d_rsp_payload[1792+:132]=d_rsp_payload[22+:132];
assign full_d_rsp_payload[1924+:124]=0;
assign full_d_rsp_payload[2048+:165]=d_rsp_payload[154+:165];
assign full_d_rsp_payload[2213+:91]=0;
assign full_d_rsp_payload[2304+:101]=d_rsp_payload[319+:101];
assign full_d_rsp_payload[2405+:155]=0;
assign full_d_rsp_payload[2560+:200]=d_rsp_payload[420+:200];
assign full_d_rsp_payload[2760+:56]=0;
assign full_d_rsp_payload[2816+:166]=d_rsp_payload[620+:166];
assign full_d_rsp_payload[2982+:90]=0;
assign full_d_rsp_payload[3072+:160]=d_rsp_payload[786+:160];
assign full_d_rsp_payload[3232+:96]=0;
assign full_d_rsp_payload[3328+:238]=d_rsp_payload[946+:238];
assign full_d_rsp_payload[3566+:18]=0;
assign full_d_rsp_payload[3584+:1]=d_rsp_payload[1184+:1];
assign full_d_rsp_payload[3585+:255]=0;
assign full_d_rsp_payload[3840+:1]=d_rsp_payload[1185+:1];
assign full_d_rsp_payload[3841+:255]=0;
transaction_fence #(.LANES(16),.REQ_BITS(2432),.RSP_BITS(256),.ADMIN_FIRST(14),.CALLBACK_MASK(16'h037f))dut(.s_payload(full_s_payload),.cb_payload(full_cb_payload),.d_payload(full_d_payload),.s_rsp_payload(full_s_rsp_payload),.cb_rsp_payload(full_cb_rsp_payload),.d_rsp_payload(full_d_rsp_payload),.*);
endmodule
