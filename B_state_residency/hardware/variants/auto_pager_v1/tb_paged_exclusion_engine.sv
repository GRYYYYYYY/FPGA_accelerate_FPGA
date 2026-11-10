`timescale 1ns/1ps
module tb_paged_exclusion_engine;
`ifdef PAGER_SINGLE
    localparam SLOTS=1,TX_BITS=6,GEN_BITS=3,FRAMES=256,INDEX_BITS=8,STRIDE=17;
`elsif PAGER_BUDGET
    localparam SLOTS=32,TX_BITS=6,GEN_BITS=16,FRAMES=256,INDEX_BITS=8,STRIDE=97;
`elsif PAGER_WRAP
    localparam SLOTS=1,TX_BITS=16,GEN_BITS=16,FRAMES=16,INDEX_BITS=4,STRIDE=1;
`elsif PAGER_FAULT
    localparam SLOTS=1,TX_BITS=6,GEN_BITS=16,FRAMES=2,INDEX_BITS=1,STRIDE=1;
`else
    localparam SLOTS=32,TX_BITS=16,GEN_BITS=16,FRAMES=256,INDEX_BITS=8,STRIDE=1;
`endif
    reg clk=0;always #5 clk=~clk;
    reg rst=1,ctrl_valid=0,ctrl_rsp_ready=0,io_valid=0,io_rsp_ready=0,io_write=0;
    reg [1:0] ctrl_op=0,ctrl_query=1;reg [3:0] ctrl_price=3;
    reg [31:0] io_node=0,io_value=0;reg [2:0] io_field=0;
    wire ctrl_ready,ctrl_rsp_valid,io_ready,io_rsp_valid,io_present;
    wire [3:0] ctrl_status,io_status;wire [159:0] io_payload;
    reg edge_valid=0,result_ready=0;
    reg [31:0] edge_cookie=0,edge_parent=0,edge_child=0,edge_flags=0,edge_created=0,edge_has_laguna=0;
    wire edge_ready,result_valid,result_excluded,fault,active,draining;
    wire [3:0] result_status,active_price;wire [31:0] result_detail,result_cookie,result_generation;
    wire [1:0] active_query,fence_tag;wire [31:0] page_leases,memory_leases;wire [INDEX_BITS:0] allocated;
    integer cycles=0;reg hold_services=0;
    wire dispatch_enable=!hold_services&&cycles%5!=0,execute_enable=!hold_services&&cycles%7>=2;
    wire fence_service_enable=!hold_services&&cycles%11>=3,ack_receive_enable=!hold_services&&cycles%13>=4;
    wire [31:0] m_awaddr,m_araddr;wire [7:0] m_awlen,m_arlen;wire [2:0] m_awsize,m_arsize;
    wire [1:0] m_awburst,m_arburst;wire [3:0] m_awid,m_arid;
    wire m_awvalid,m_wvalid,m_arvalid,m_wlast,m_bready,m_rready;
    wire [511:0] m_wdata;wire [63:0] m_wstrb;
    wire m_awready,m_wready,m_arready;
    reg m_bvalid=0,m_rvalid=0,m_rlast=0;reg [3:0] m_bid=0,m_rid=0;
    reg [1:0] m_bresp=0,m_rresp=0;reg [511:0] m_rdata=0;
    paged_exclusion_engine #(.SLOTS(SLOTS),.TX_BITS(TX_BITS),.GEN_BITS(GEN_BITS),
        .FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(INDEX_BITS),.PROBE_LIMIT(FRAMES<64?FRAMES:64)) dut(.*);

    reg [159:0] golden[0:96][0:7];reg [7:0] golden_mask[0:96];
    reg [511:0] memory[0:FRAMES*3-1],write_words[0:2];
    reg [1535:0] expected_write,expected_read;
    reg aw_pending=0,wlast_seen=0,read_active=0,fail_b=0,fail_r=0,expected_failure=0,check_bytes=1;
    reg [31:0] aw_address=0,ar_address=0;
    integer memory_i,shadow_i;
    integer aw_length=0,write_count=0,b_delay=0,read_length=0,read_position=0,wb_beats=0,rf_beats=0;
    integer aw_count=0,b_count=0,ar_count=0,r_count=0;
    integer wb_count=0,rf_count=0,empty_count=0,cp_count=0,auto_cp_count=0,gen_cp_count=0;
    integer native_reads=0;
    integer binds=0,releases=0,checks=0,edges=0,requests=0,responses=0,hls_calls=0,tx_count=0,max_tx=0;
    integer pending_op=0,pending_slot=0,pending_page=0,pending_gen=0;
    reg pending=0;reg [31:0] shadow_valid=0,shadow_dirty=0;
    reg [20:0] shadow_page[0:31];reg [15:0] shadow_generation[0:31];
    integer k,j,p,o,f,index,fixture,rc,fields[0:18],edge_index=0,read_index=0,response_index=0,expected_generation=0;
    integer starting_aw,starting_ar,starting_cp,starting_bind,read_before,error_cases=0;
    reg active_edge=0;reg [4095:0] fixture_path;
    reg held_aw=0,held_w=0,held_ar=0,held_io=0,held_ctrl=0,held_result=0,held_native=0;
    reg [48:0] saved_aw,saved_ar;reg [576:0] saved_w;
    reg [164:0] saved_io;reg [3:0] saved_ctrl;reg [100:0] saved_result;
    reg [89:0] saved_native;
    function [20:0] page_for(input integer pi);
        page_for=pi==95?21'h1fffff:(pi==96?21'd3:21'h1234+pi*12347);
    endfunction
    function integer page_index(input [20:0] pg);
        integer a;begin page_index=-1;for(a=0;a<97;a=a+1)if(page_for(a)==pg)page_index=a;end
    endfunction
    function [1535:0] pack_page(input [20:0] pg);
        integer a,pi;reg [1535:0] packed_page;
        begin
            pi=page_index(pg);packed_page=0;
            if(pi>=0)begin packed_page[7:0]=golden_mask[pi];for(a=0;a<8;a=a+1)packed_page[8+a*160+:160]=golden[pi][a];end
            pack_page=packed_page;
        end
    endfunction
    function [31:0] value_for(input integer pi,off,field_id);
        if(field_id==4)value_for=(pi*7+off)&255;
        else if(field_id==2&&off==0)value_for=32'hffffffff;
        else value_for=(32'h80000000+pi*1024+off*16+field_id)^(pi%3==0?32'h80000000:0);
    endfunction
    function [31:0] label_value(input integer phase);
        if(phase==1||phase==4)label_value=fields[6];else if(phase==2)label_value=fields[7];else label_value=fields[8];
    endfunction

    assign m_awready=!rst&&!aw_pending&&!m_bvalid&&cycles%7>=2&&(write_count!=0||cycles%2==0);
    assign m_wready=!rst&&!wlast_seen&&!m_bvalid&&cycles%5>=2;
    assign m_arready=!rst&&!read_active&&!m_rvalid&&cycles%7>=3;
    always @(posedge clk)begin
        cycles<=cycles+1;
        if(rst)begin
            aw_pending<=0;wlast_seen<=0;write_count<=0;b_delay<=0;m_bvalid<=0;
            read_active<=0;m_rvalid<=0;read_position<=0;held_aw<=0;held_w<=0;held_ar<=0;
        end else begin
            if(held_aw&&(!m_awvalid||{m_awaddr,m_awlen,m_awsize,m_awburst,m_awid}!==saved_aw))$fatal(1,"AW unstable");
            if(held_w&&(!m_wvalid||{m_wdata,m_wstrb,m_wlast}!==saved_w))$fatal(1,"W unstable");
            if(held_ar&&(!m_arvalid||{m_araddr,m_arlen,m_arsize,m_arburst,m_arid}!==saved_ar))$fatal(1,"AR unstable");
            held_aw<=m_awvalid&&!m_awready;saved_aw<={m_awaddr,m_awlen,m_awsize,m_awburst,m_awid};
            held_w<=m_wvalid&&!m_wready;saved_w<={m_wdata,m_wstrb,m_wlast};
            held_ar<=m_arvalid&&!m_arready;saved_ar<={m_araddr,m_arlen,m_arsize,m_arburst,m_arid};
            if(m_awvalid&&m_awready)begin
                if(m_awid!=0||m_awsize!=6||m_awburst!=1||m_awaddr[5:0]!=0||m_awlen>2||
                   ({1'b0,m_awaddr[11:0]}+((m_awlen+1)*64)>4096)||((m_awaddr>>6)+m_awlen>=FRAMES*3))$fatal(1,"invalid AW");
                aw_pending<=1;aw_address<=m_awaddr;aw_length<=m_awlen+1;aw_count<=aw_count+1;
            end
            if(m_wvalid&&m_wready)begin
                if(write_count>2||m_wstrb!==64'hffffffffffffffff)$fatal(1,"invalid W");
                if(check_bytes&&(wb_beats>=3||m_wdata!==expected_write[wb_beats*512+:512]))$fatal(1,"WB bytes disagree with independent label model beat=%0d",wb_beats);
                write_words[write_count]<=m_wdata;write_count<=write_count+1;wb_beats<=wb_beats+1;
                if(m_wlast)wlast_seen<=1;
            end
            if(aw_pending&&wlast_seen&&!m_bvalid)begin
                if(write_count!=aw_length)$fatal(1,"AW/WLAST length mismatch");
                if(b_delay<9)b_delay<=b_delay+1;
                else begin
                    if(!fail_b)for(memory_i=0;memory_i<aw_length;memory_i=memory_i+1)memory[(aw_address>>6)+memory_i]<=write_words[memory_i];
                    m_bvalid<=1;m_bid<=0;m_bresp<=fail_b?2:0;
                end
            end
            if(m_bvalid&&m_bready)begin
                m_bvalid<=0;aw_pending<=0;wlast_seen<=0;write_count<=0;b_delay<=0;b_count<=b_count+1;
            end
            if(m_arvalid&&m_arready)begin
                if(m_arid!=0||m_arsize!=6||m_arburst!=1||m_araddr[5:0]!=0||m_arlen>2||
                   ({1'b0,m_araddr[11:0]}+((m_arlen+1)*64)>4096)||((m_araddr>>6)+m_arlen>=FRAMES*3))$fatal(1,"invalid AR");
                read_active<=1;ar_address<=m_araddr;read_length<=m_arlen+1;read_position<=0;ar_count<=ar_count+1;
            end
            if(read_active&&!m_rvalid&&cycles%5>=2)begin
                m_rvalid<=1;m_rdata<=memory[(ar_address>>6)+read_position];m_rid<=0;m_rresp<=fail_r?2:0;m_rlast<=read_position==read_length-1;
            end
            if(m_rvalid&&m_rready)begin
                if(check_bytes&&(rf_beats>=3||m_rdata!==expected_read[rf_beats*512+:512]))$fatal(1,"RF bytes disagree with independent label model beat=%0d",rf_beats);
                rf_beats<=rf_beats+1;m_rvalid<=0;r_count<=r_count+1;
                if(read_position==read_length-1)read_active<=0;else read_position<=read_position+1;
            end
        end
    end

    // Independent observer derives ownership from acknowledged native commands.
    always @(posedge clk)begin
        if(rst)begin
            pending<=0;shadow_valid<=0;shadow_dirty<=0;tx_count<=0;
            held_io<=0;held_ctrl<=0;held_result<=0;held_native<=0;
            for(shadow_i=0;shadow_i<32;shadow_i=shadow_i+1)begin shadow_page[shadow_i]<=0;shadow_generation[shadow_i]<=0;end
        end else begin
            if(held_io&&(!io_rsp_valid||{io_status,io_payload,io_present}!==saved_io))$fatal(1,"IO response unstable");
            if(held_ctrl&&(!ctrl_rsp_valid||ctrl_status!==saved_ctrl))$fatal(1,"control response unstable");
            if(held_result&&(!result_valid||{result_status,result_detail,result_cookie,result_generation,result_excluded}!==saved_result))$fatal(1,"edge response unstable");
            if(held_native&&!fault&&(!dut.native_cmd_valid||{dut.native_cmd_op,dut.native_cmd_slot,dut.native_cmd_query,dut.native_cmd_page,dut.native_cmd_price,dut.native_cmd_generation,dut.native_cmd_offset,dut.native_cmd_field,dut.native_cmd_value}!==saved_native))$fatal(1,"native command unstable");
            held_io<=io_rsp_valid&&!io_rsp_ready;saved_io<={io_status,io_payload,io_present};
            held_ctrl<=ctrl_rsp_valid&&!ctrl_rsp_ready;saved_ctrl<=ctrl_status;
            held_result<=result_valid&&!result_ready;saved_result<={result_status,result_detail,result_cookie,result_generation,result_excluded};
            held_native<=dut.native_cmd_valid&&!dut.native_cmd_ready;
            saved_native<={dut.native_cmd_op,dut.native_cmd_slot,dut.native_cmd_query,dut.native_cmd_page,dut.native_cmd_price,dut.native_cmd_generation,dut.native_cmd_offset,dut.native_cmd_field,dut.native_cmd_value};
            if(active_edge&&(ctrl_ready||io_ready||edge_ready))$fatal(1,"query or label mutation admitted during active edge");
            if(fault&&!expected_failure)$fatal(1,"unexpected pager fault edge=%0d action=%0d status=%0d",edge_index,dut.pager.action,dut.native_rsp_status);
            if(dut.native_cmd_valid&&dut.native_cmd_ready)begin
                if(pending)$fatal(1,"native transaction overlap");pending<=1;
                if(dut.native_cmd_op==2)native_reads<=native_reads+1;
                pending_op<=dut.native_cmd_op;pending_slot<=dut.native_cmd_slot;pending_page<=dut.native_cmd_page;pending_gen<=dut.native_cmd_generation;
                if(dut.native_cmd_slot>=SLOTS)$fatal(1,"slot out of managed range");
                if(dut.native_cmd_op==1)begin
                    if(shadow_valid[dut.native_cmd_slot]||dut.native_cmd_generation==0||dut.native_cmd_generation<=shadow_generation[dut.native_cmd_slot]||dut.native_cmd_generation>((1<<GEN_BITS)-1))$fatal(1,"unsafe binding generation");
                end
                if(dut.native_cmd_op>=2&&dut.native_cmd_op<=6)begin
                    if(!shadow_valid[dut.native_cmd_slot]||shadow_page[dut.native_cmd_slot]!==dut.native_cmd_page||shadow_generation[dut.native_cmd_slot]!==dut.native_cmd_generation)$fatal(1,"native operation without matching binding");
                end
                if(dut.native_cmd_op==4&&shadow_dirty[dut.native_cmd_slot])$fatal(1,"dirty RELEASE before successful WB");
                if(dut.native_cmd_op==12&&(shadow_valid!=0||page_leases!=0||memory_leases!=0))$fatal(1,"checkpoint before slot/lease retirement");
                if(dut.native_cmd_op==5)begin expected_write<=pack_page(dut.native_cmd_page);wb_beats<=0;end
                if(dut.native_cmd_op==6)begin expected_read<=pack_page(dut.native_cmd_page);rf_beats<=0;end
            end
            if(dut.native_rsp_valid&&dut.native_rsp_ready)begin
                if(!pending)$fatal(1,"unowned native response");pending<=0;
                if(dut.native_rsp_status==0)begin
                    case(pending_op)
                        1:begin shadow_valid[pending_slot]<=1;shadow_dirty[pending_slot]<=0;shadow_page[pending_slot]<=pending_page;shadow_generation[pending_slot]<=pending_gen;binds<=binds+1;end
                        3:shadow_dirty[pending_slot]<=1;
                        4:begin shadow_valid[pending_slot]<=0;releases<=releases+1;end
                        5,6:begin
                            if(dut.native_rsp_tx!==tx_count[TX_BITS-1:0]||tx_count>=(1<<TX_BITS))$fatal(1,"transaction budget exhausted or skipped");
                            tx_count<=tx_count+1;if(tx_count+1>max_tx)max_tx<=tx_count+1;
                            shadow_dirty[pending_slot]<=0;
                            if(pending_op==5)begin if(wb_beats!=3)$fatal(1,"WB retired before all bytes");wb_count<=wb_count+1;end
                            else begin if(rf_beats!=3)$fatal(1,"RF retired before all bytes");rf_count<=rf_count+1;end
                        end
                        11,12:begin
                            tx_count<=0;for(shadow_i=0;shadow_i<32;shadow_i=shadow_i+1)shadow_generation[shadow_i]<=0;
                            if(pending_op==12)begin
                                cp_count<=cp_count+1;if(dut.pager.resume_request)auto_cp_count<=auto_cp_count+1;
                                if(shadow_generation[0]==((1<<GEN_BITS)-1))gen_cp_count<=gen_cp_count+1;
                            end
                        end
                    endcase
                end else if(pending_op==6&&dut.native_rsp_status==8)empty_count<=empty_count+1;
                else if(!(pending_op==11&&dut.native_rsp_status==7)&&!expected_failure)$fatal(1,"unexpected native status op=%0d status=%0d",pending_op,dut.native_rsp_status);
            end
            if(dut.resolve_valid&&dut.resolve_ready)begin
                if(!active_edge||read_index>=fields[10]||dut.resolve_generation!==expected_generation||dut.resolve_phase!==fields[11+2*read_index]||dut.resolve_page!==(fields[12+2*read_index]>>3))$fatal(1,"paged label request order mismatch");
                read_index<=read_index+1;requests<=requests+1;
            end
            if(dut.engine.ap_start&&dut.engine.ap_ready)begin
                hls_calls<=hls_calls+1;
                if(dut.engine.hls_command[31:0]==1)begin
                    if(response_index>=fields[10]||dut.engine.hls_command[223:192]!==expected_generation||dut.engine.hls_command[255:224]!==fields[11+2*response_index]||dut.engine.hls_command[287:256]!==label_value(fields[11+2*response_index]))$fatal(1,"paged HLS label value mismatch");
                    response_index<=response_index+1;responses<=responses+1;
                end
            end
        end
    end
    initial begin #1000000000;$fatal(1,"paged watchdog edge=%0d checks=%0d state=%0d",edge_index,checks,dut.pager.state);end

    task cold_start;
        integer a,b;
        begin
            @(negedge clk);rst=1;ctrl_valid=0;io_valid=0;edge_valid=0;ctrl_rsp_ready=0;io_rsp_ready=0;result_ready=0;
            fail_b=0;fail_r=0;expected_failure=0;active_edge=0;expected_generation=0;hold_services=0;check_bytes=1;
            for(a=0;a<97;a=a+1)begin golden_mask[a]=0;for(b=0;b<8;b=b+1)golden[a][b]=0;end
            repeat(6)@(negedge clk);rst=0;repeat(3)@(negedge clk);
        end
    endtask
    task control(input integer op,q,pr,status);
        begin
            @(negedge clk);ctrl_op=op;ctrl_query=q;ctrl_price=pr;ctrl_valid=1;
            do @(posedge clk);while(!ctrl_ready);
            @(negedge clk);ctrl_valid=0;wait(ctrl_rsp_valid);repeat(4)@(negedge clk);
            if(ctrl_status!==status[3:0])$fatal(1,"control status op=%0d got=%0d expected=%0d",op,ctrl_status,status);
            ctrl_rsp_ready=1;@(negedge clk);ctrl_rsp_ready=0;checks=checks+1;
        end
    endtask
    task access_label(input integer write_flag,input [31:0] node,input integer fi,input [31:0] val,input integer status);
        integer pi,off;
        begin
            @(negedge clk);io_write=write_flag;io_node=node;io_field=fi;io_value=val;io_valid=1;
            do @(posedge clk);while(!io_ready);
            @(negedge clk);io_valid=0;io_node=32'hdeadbeef;io_value='1;io_field=7;
            wait(io_rsp_valid);repeat(3)@(negedge clk);
            if(io_status!==status[3:0])$fatal(1,"IO status node=%h got=%0d expected=%0d",node,io_status,status);
            if(status==0)begin
                pi=page_index(node[23:3]);off=node&7;
                if(write_flag)begin
                    if(pi<0)$fatal(1,"unmodeled write");
                    golden_mask[pi][off]=1;
                    if(fi==4)golden[pi][off][135:128]=val[7:0];else golden[pi][off][fi*32+:32]=val;
                end else if(pi>=0)begin
                    if(io_present!==golden_mask[pi][off]||io_payload!==golden[pi][off])$fatal(1,"lost/reused label node=%h got=%h expected=%h present=%b/%b",node,io_payload,golden[pi][off],io_present,golden_mask[pi][off]);
                end else if(io_present||io_payload!=0)$fatal(1,"unknown empty page contains stale state");
            end
            io_rsp_ready=1;@(negedge clk);io_rsp_ready=0;checks=checks+1;
        end
    endtask
    task run_edge;
        begin
            @(negedge clk);edge_cookie=32'hbed00000+edge_index;edge_parent=fields[1];edge_child=fields[2];edge_flags=fields[3];edge_created=fields[4];edge_has_laguna=fields[5];edge_valid=1;
            do @(posedge clk);while(!edge_ready);
            @(negedge clk);edge_valid=0;active_edge=1;read_index=0;response_index=0;
            edge_parent='1;edge_child='1;edge_flags='1;edge_created='1;edge_has_laguna='1;
            // Pending host mutation/lifecycle commands must not interrupt an edge.
            io_valid=1;io_node=32'hffffffff;ctrl_valid=1;ctrl_op=3;
            wait(result_valid);repeat(4)@(negedge clk);
            if(fault||result_status!=0||result_cookie!==32'hbed00000+edge_index||result_generation!==expected_generation||result_excluded!==fields[9][0]||read_index!=fields[10]||response_index!=fields[10])$fatal(1,"paged edge result mismatch edge=%0d",edge_index);
            io_valid=0;ctrl_valid=0;result_ready=1;@(negedge clk);result_ready=0;active_edge=0;edges=edges+1;checks=checks+1;
        end
    endtask


    task assert_stopped;
        begin
            repeat(20)@(negedge clk);
            if(!fault||ctrl_ready||io_ready||edge_ready||dut.native_cmd_valid)$fatal(1,"faulted pager continued issuing work");
            error_cases=error_cases+1;
        end
    endtask
    task failing_edge;
        begin
            @(negedge clk);edge_cookie=32'hbad00001;edge_parent=fields[1];edge_child=fields[2];edge_flags=0;edge_created=1;edge_has_laguna=1;edge_valid=1;
            do @(posedge clk);while(!edge_ready);
            @(negedge clk);edge_valid=0;active_edge=1;read_index=0;response_index=0;
            wait(result_valid);repeat(4)@(negedge clk);
            if(!fault||result_status!=5||result_excluded||result_cookie!=32'hbad00001||response_index!=0||read_index!=1)$fatal(1,"RF failure became HLS data or a valid decision");
            result_ready=1;@(negedge clk);result_ready=0;active_edge=0;
        end
    endtask
    initial begin
        cold_start;
`ifdef PAGER_WRAP
        control(0,1,3,0);starting_cp=cp_count;starting_bind=binds;
        for(p=0;p<65536;p=p+1)access_label(0,((p+100)<<3)+(p&7),0,0,0);
        if(cp_count-starting_cp!=1||auto_cp_count!=1||binds-starting_bind!=65536||shadow_generation[0]!=1||allocated!=0||aw_count!=0||ar_count!=0||tx_count!=0)$fatal(1,"generation16 recycle failed");
        control(2,1,3,0);
        if(active||page_leases||memory_leases||allocated)$fatal(1,"generation test close incomplete");
        $display("PAGER_WRAP_PASS requests=65536 checkpoints=1 final_binding_before_close=1 checks=%0d",checks);$finish;
`endif
`ifdef PAGER_FAULT
        control(0,1,3,0);access_label(1,page_for(0)*8,2,32'h11111111,0);
        starting_bind=binds;fail_b=1;expected_failure=1;
        access_label(0,page_for(1)*8,0,0,10);
        if(binds!=starting_bind||page_leases==0||memory_leases==0)$fatal(1,"failed WB released old binding/leases");
        assert_stopped;
        cold_start;control(0,1,3,0);
        access_label(1,page_for(0)*8,2,32'h11111111,0);access_label(0,page_for(1)*8,0,0,0);
        for(j=0;j<19;j=j+1)fields[j]=0;
        fields[1]=page_for(1)*8;fields[2]=page_for(0)*8;fields[10]=3;fields[11]=1;fields[12]=fields[2];
        expected_generation=1;read_before=native_reads;fail_r=1;expected_failure=1;failing_edge;
        if(native_reads!=read_before||page_leases==0||memory_leases==0)$fatal(1,"failed RF exposed a native READ or retired leases");
        assert_stopped;
        cold_start;control(0,1,3,0);
        access_label(1,page_for(0)*8,2,1,0);access_label(1,page_for(1)*8,2,2,0);access_label(1,page_for(2)*8,2,3,0);
        starting_bind=binds;expected_failure=1;access_label(0,page_for(3)*8,0,0,9);
        if(binds!=starting_bind||!shadow_valid[0]||!shadow_dirty[0]||shadow_page[0]!=page_for(2))$fatal(1,"directory FULL discarded dirty victim");
        assert_stopped;
        cold_start;control(0,1,3,0);access_label(0,page_for(0)*8,0,0,0);control(2,1,3,0);
        if(fault||active||allocated||page_leases||memory_leases||error_cases!=3)$fatal(1,"coordinated cold recovery failed");
        $display("PAGER_FAULT_PASS cases=3 wb_error=1 rf_edge_error=1 directory_full=1 checks=%0d",checks);$finish;
`endif
        control(2,1,3,1);control(1,1,3,1);control(0,1,3,0);control(0,2,4,4);control(3,1,3,3);
        access_label(0,32'h01000000,0,0,3);access_label(0,page_for(0)*8,5,0,3);access_label(1,page_for(0)*8,4,256,3);
        // Sparse pages, explicit -1, high-bit values, all five fields, and present all-zero record.
        for(p=0;p<96;p=p+1)for(o=0;o<8;o=o+1)if((p+o)%3!=0)
            for(f=0;f<5;f=f+1)access_label(1,page_for(p)*8+o,f,value_for(p,o,f),0);
        access_label(1,page_for(0)*8,2,0,0);
        for(p=0;p<96;p=p+1)for(o=7;o>=0;o=o-1)access_label(0,page_for((p*37)%96)*8+o,0,0,0);
        if(wb_count==0||rf_count==0||aw_count==0||ar_count==0)$fatal(1,"page retention test never used backing AXI");
        if(!$value$plusargs("fixture=%s",fixture_path))$fatal(1,"missing fixture");
        fixture=$fopen(fixture_path,"r");if(!fixture)$fatal(1,"fixture open");
        for(edge_index=0;edge_index<27680;edge_index=edge_index+1)begin
            for(j=0;j<19;j=j+1)begin rc=$fscanf(fixture,"%h",fields[j]);if(rc!=1)$fatal(1,"short fixture");end
            if(edge_index%STRIDE==0||edge_index>=27648)begin
                if(fields[0])begin
                    access_label(1,fields[2],2,fields[6],0);access_label(1,fields[2],3,fields[7],0);access_label(1,fields[1],3,fields[8],0);
                end
                expected_generation=expected_generation+1;run_edge;
            end
        end
        rc=$fscanf(fixture,"%h",index);if(rc==1)$fatal(1,"unconsumed fixture");$fclose(fixture);
        // Production16 runs beyond the real transaction limit; smaller cases also
        // force misses, but do not substitute for that production-width proof.
        for(index=0;index<(STRIDE==1?70000:512);index=index+1)
            access_label(0,page_for((index*37)%96)*8+(index&7),0,0,0);
        if(auto_cp_count==0)$fatal(1,"automatic checkpoint not exercised");
        if(STRIDE==1&&max_tx<65502)$fatal(1,"production transaction budget boundary not reached");
        if(GEN_BITS==3&&gen_cp_count==0)$fatal(1,"small generation limit not exercised");
        control(1,1,3,0);
        for(p=0;p<96;p=p+1)for(o=0;o<8;o=o+1)access_label(0,page_for(p)*8+o,0,0,0);
        control(2,1,3,0);
        if(active||allocated||page_leases||memory_leases||shadow_valid)$fatal(1,"query close did not retire/recycle");
        for(p=0;p<97;p=p+1)begin golden_mask[p]=0;for(o=0;o<8;o=o+1)golden[p][o]=0;end
        // A different query/price cannot observe the old backing bytes.
        control(0,2,4,0);starting_ar=ar_count;
        for(p=0;p<96;p=p+1)for(o=0;o<8;o=o+1)access_label(0,page_for(p)*8+o,0,0,0);
        if(ar_count!=starting_ar)$fatal(1,"new query loaded old published pages");
        for(j=0;j<19;j=j+1)fields[j]=0;fields[1]=16;fields[2]=17;
        expected_generation=expected_generation+1;run_edge;control(2,2,4,0);
        if(fault||active||allocated||page_leases||memory_leases||pending||aw_count!=b_count||r_count!=rf_count*3||max_tx>(1<<TX_BITS))$fatal(1,"final conservation/retirement failed");
        $display("PAGER_ENGINE_PASS slots=%0d tx_bits=%0d gen_bits=%0d stride=%0d edges=%0d checks=%0d labels=%0d responses=%0d hls_calls=%0d wb=%0d rf=%0d empty=%0d checkpoints=%0d auto_cp=%0d gen_cp=%0d max_tx=%0d aw=%0d b=%0d ar=%0d r=%0d",SLOTS,TX_BITS,GEN_BITS,STRIDE,edges,checks,requests,responses,hls_calls,wb_count,rf_count,empty_count,cp_count,auto_cp_count,gen_cp_count,max_tx,aw_count,b_count,ar_count,r_count);
        $finish;
    end
endmodule
