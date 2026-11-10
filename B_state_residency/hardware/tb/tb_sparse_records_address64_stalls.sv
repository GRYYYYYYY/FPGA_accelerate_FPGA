`timescale 1ns/1ps
module tb_sparse_records_address64_stalls;
    localparam integer SMALL=1;
    localparam integer TB_HASH=SMALL?2:15;
    integer finish_retries=0;
    localparam integer SPARSE_RF=1;
    localparam integer TB_TX=SMALL?6:16,TB_GEN=SMALL?3:16,TB_TAG=SMALL?1:2;
    localparam integer TB_FRAMES=SMALL?32:512,TB_INDEX=SMALL?5:9;
    reg hold_dispatch=0,hold_execute=0,hold_fence=0,hold_ack=0;
    integer blocked_cases=0,blocked_cycles=0,stall_i;
    reg [TB_TAG-1:0] blocked_tag;
    reg clk=0;always #5 clk=~clk;
    reg rst=1,cmd_valid=0,rsp_ready=0;wire cmd_ready,rsp_valid;
    reg [3:0] cmd_op=0,cmd_price=0;reg [4:0] cmd_slot=0;reg [1:0] cmd_query=0;
    reg [20:0] cmd_page=0;reg [TB_GEN-1:0] cmd_generation=0;
    reg [2:0] cmd_offset=0;reg [2:0] cmd_field=0;reg [31:0] cmd_value=0;
    wire [3:0] rsp_status;wire [159:0] rsp_payload;wire rsp_present,rsp_dirty;
    wire [TB_TX-1:0] rsp_tx;wire fault,draining;
    wire [31:0] page_leases,memory_leases;wire [TB_INDEX:0] allocated;wire [TB_TAG-1:0] fence_tag;
    wire dispatch_enable,execute_enable,fence_service_enable,ack_receive_enable;
    wire [31:0] m_awaddr,m_araddr;wire [7:0] m_awlen,m_arlen;wire [2:0] m_awsize,m_arsize;
    wire [1:0] m_awburst,m_arburst;wire [3:0] m_awid,m_arid;wire m_awvalid,m_arvalid;
    wire m_awready,m_arready,m_wready;wire [511:0] m_wdata;wire [63:0] m_wstrb;wire m_wlast,m_wvalid;
    reg [3:0] m_bid=0,m_rid=0;reg [1:0] m_bresp=0,m_rresp=0;reg m_bvalid=0,m_rvalid=0,m_rlast=0;
    wire m_bready,m_rready;reg [511:0] m_rdata=0;
    localparam [63:0] BASE=64'h00000012fffff000;
    wire [63:0] outer_awaddr,outer_araddr;
    wire cfg_base_ready,cfg_rsp_valid,configured;wire [1:0] cfg_rsp_status;
    reg [5:0] config_delay=0;
    always @(posedge clk)if(rst)config_delay<=0;else if(config_delay<23)config_delay<=config_delay+1'b1;
    wire cfg_base_valid=!rst && config_delay>=20;
    wire [63:0] cfg_base_address=BASE;wire cfg_rsp_ready=1'b1;
    assign m_awaddr=outer_awaddr-BASE;
    assign m_araddr=outer_araddr-BASE;
    integer aw_carries=0,ar_carries=0;
    always @(posedge clk)if(!rst)begin
        if(!configured && (cmd_ready || m_awvalid || m_arvalid || m_wvalid))$fatal(1,"unconfigured ingress or AXI traffic");
        if(cfg_rsp_valid && cfg_rsp_status!=0)$fatal(1,"valid base rejected");
        if(m_awvalid && (outer_awaddr!=BASE+{32'b0,m_awaddr} || outer_awaddr<BASE || m_awaddr+m_awlen*64+64>TB_FRAMES*192))$fatal(1,"bad 64bit AW rebase");
        if(m_arvalid && (outer_araddr!=BASE+{32'b0,m_araddr} || outer_araddr<BASE || m_araddr+m_arlen*64+64>TB_FRAMES*192))$fatal(1,"bad 64bit AR rebase");
        if(m_awvalid && m_awready && outer_awaddr[63:32]!=BASE[63:32])aw_carries=aw_carries+1;
        if(m_arvalid && m_arready && outer_araddr[63:32]!=BASE[63:32])ar_carries=ar_carries+1;
    end
    memory_scratch_endpoint_address64 #(.TX_BITS(TB_TX),.GENERATION_BITS(TB_GEN),.TAG_BITS(TB_TAG),.FRAMES(TB_FRAMES),.INDEX_BITS(TB_INDEX),.HASH_BITS(SMALL?2:15),.PROBE_LIMIT(SMALL?1:64),.EPOCH_BITS(16)) dut(.m_awaddr(outer_awaddr),.m_araddr(outer_araddr),.*);
    reg [511:0] memory[0:TB_FRAMES*3-1],write_words[0:2],expected[0:2];
    reg [511:0] raw_expected[0:127805];
    reg [159:0] golden[0:7];reg [7:0] golden_bitmap=0;
    longint unsigned cycle=0;
    integer active_op=0,stream_write=0,stream_read=0,record_acks=0,completed_transfers=0,completed_fences=0;
    integer closure_gap_cycles=0,starts=0,tag_wraps=0,host_stalls=0,read_bytes_check=1;
    reg memory_completed=0,page_completed=0,page_fence_completed=0,held_rsp=0;
    reg [165+TB_TX:0] saved_rsp;
    reg [TB_TAG-1:0] previous_tag=0;
    assign dispatch_enable=!hold_dispatch && cycle%5!=0;
    assign execute_enable=!hold_execute && cycle%7>=2;
    assign fence_service_enable=!hold_fence && cycle%11>=4;
    assign ack_receive_enable=!hold_ack && cycle%13>=5;
    reg aw_pending=0,wlast_seen=0,read_active=0;
    reg [31:0] aw_address=0,ar_address=0;
    integer aw_length=0,write_count=0,read_length=0,read_position=0,b_delay=0;
    integer aw_count=0,b_count=0,ar_count=0,r_count=0,checks=0,write_pages=0,read_pages=0;
    integer expected_next_aw=0,expected_next_ar=0,mode=0,current_frame=0,test_slot=0;
    integer j,k,fr,txid=0,baseline_b,expected_b,reads,words,deadline,errors=0;
    reg [63:0] offset_coverage=0,cookie;
    reg [4095:0] fixture_path;
    reg held_aw=0,held_w=0,held_ar=0;
    reg [48:0] saved_aw,saved_ar;
    reg [576:0] saved_w;

    assign m_awready=!rst && !aw_pending && !m_bvalid && (cycle%7!=0)
        && (current_frame%2==0 || m_wvalid || write_count!=0);
    assign m_wready=!rst && !wlast_seen && !m_bvalid && (cycle%5>=2);
    assign m_arready=!rst && !read_active && !m_rvalid && cycle%7>=2;
    // Independent burst slave, including W-before-AW acceptance, delayed B,
    // response errors, address/length validation and held valid outputs.
    always @(posedge clk) begin
        cycle<=cycle+1;
        if(rst)begin
            aw_pending<=0;wlast_seen<=0;write_count<=0;b_delay<=0;m_bvalid<=0;
            read_active<=0;read_position<=0;m_rvalid<=0;
            held_aw<=0;held_w<=0;held_ar<=0;
        end else begin
            if(held_aw && (!m_awvalid || {m_awaddr,m_awlen,m_awsize,m_awburst,m_awid}!==saved_aw))$fatal(1,"AW changed under backpressure");
            if(held_ar && (!m_arvalid || {m_araddr,m_arlen,m_arsize,m_arburst,m_arid}!==saved_ar))$fatal(1,"AR changed under backpressure");
            if(held_w && (!m_wvalid || {m_wdata,m_wstrb,m_wlast}!==saved_w))$fatal(1,"W changed under backpressure");
            held_aw<=m_awvalid&&!m_awready;saved_aw<={m_awaddr,m_awlen,m_awsize,m_awburst,m_awid};
            held_ar<=m_arvalid&&!m_arready;saved_ar<={m_araddr,m_arlen,m_arsize,m_arburst,m_arid};
            held_w<=m_wvalid&&!m_wready;saved_w<={m_wdata,m_wstrb,m_wlast};
            if(m_awvalid && m_awready)begin
                if(aw_pending || m_awid!=0 || m_awsize!=6 || m_awburst!=1 || m_awaddr[5:0]!=0 || m_awlen>2
                   || ({1'b0,m_awaddr[11:0]}+((m_awlen+1)*64)>4096) || m_awaddr!==expected_next_aw[31:0])$fatal(1,"bad AW burst address=%h expected=%h len=%0d",m_awaddr,expected_next_aw,m_awlen);
                aw_pending<=1;aw_address<=m_awaddr;aw_length<=m_awlen+1;aw_count<=aw_count+1;
                expected_next_aw=expected_next_aw+(m_awlen+1)*64;
            end
            if(m_wvalid && m_wready)begin
                if(write_count>2 || m_wstrb!==64'hffffffffffffffff)$fatal(1,"bad W beat");
                write_words[write_count]<=m_wdata;write_count<=write_count+1;
                if(m_wlast)wlast_seen<=1;
            end
            if(aw_pending && wlast_seen && !m_bvalid)begin
                if(write_count!=aw_length)$fatal(1,"WLAST/length mismatch");
                if(b_delay<23)b_delay<=b_delay+1;
                else begin
                    for(k=0;k<aw_length;k=k+1)memory[(aw_address>>6)+k]<=write_words[k];
                    m_bvalid<=1;m_bid<=mode==2?1:0;m_bresp<=(mode==1 || (mode==6 && aw_address>=4096))?2:0;
                end
            end
            if(m_bvalid && m_bready)begin
                m_bvalid<=0;aw_pending<=0;wlast_seen<=0;write_count<=0;b_delay<=0;b_count<=b_count+1;
            end
            if(m_arvalid && m_arready)begin
                if(read_active || m_arid!=0 || m_arsize!=6 || m_arburst!=1 || m_araddr[5:0]!=0 || m_arlen>2
                   || ({1'b0,m_araddr[11:0]}+((m_arlen+1)*64)>4096) || m_araddr!==expected_next_ar[31:0])$fatal(1,"bad AR burst");
                read_active<=1;ar_address<=m_araddr;read_length<=m_arlen+1;read_position<=0;ar_count<=ar_count+1;
                expected_next_ar=expected_next_ar+(m_arlen+1)*64;
            end
            if(read_active && !m_rvalid && cycle%5>=2)begin
                m_rvalid<=1;m_rdata<=memory[(ar_address>>6)+read_position];
                m_rid<=mode==5?1:0;m_rresp<=(mode==3 || (mode==7 && ar_address>=4096))?3:0;
                m_rlast<=mode==4?1:(read_position==read_length-1);
            end
            if(m_rvalid && m_rready)begin
                m_rvalid<=0;r_count<=r_count+1;
                if(read_position==read_length-1)read_active<=0;
                else read_position<=read_position+1;
            end
        end
    end
    // Protocol monitors observe internal boundaries but never drive state.
    always @(posedge clk)begin
        if(rst)begin held_rsp<=0;previous_tag<=0;end
        else begin
            if(held_rsp && (!rsp_valid || {rsp_status,rsp_payload,rsp_present,rsp_dirty,rsp_tx}!==saved_rsp))$fatal(1,"host response changed under stall");
            held_rsp<=rsp_valid&&!rsp_ready;saved_rsp<={rsp_status,rsp_payload,rsp_present,rsp_dirty,rsp_tx};
            if(rsp_valid&&!rsp_ready)host_stalls=host_stalls+1;
            if(previous_tag!=fence_tag && fence_tag==0)tag_wraps=tag_wraps+1;
            previous_tag<=fence_tag;
            if(dut.core.fence_open && !dut.core.q_draining)begin
                closure_gap_cycles=closure_gap_cycles+1;
                if(cmd_ready)$fatal(1,"new host command before address recycle");
            end
            if(m_wvalid&&m_wready)begin
                if(stream_write>=3 || m_wdata!==expected[stream_write])$fatal(1,"independent WB byte mismatch beat=%0d",stream_write);
                stream_write=stream_write+1;
            end
            if(m_rvalid&&m_rready)begin
                if(stream_read>=3 || (read_bytes_check && m_rdata!==expected[stream_read]))$fatal(1,"independent RF byte mismatch beat=%0d",stream_read);
                stream_read=stream_read+1;
            end
            if(dut.core.q_valid && dut.core.q_receive && (dut.core.state==9 || dut.core.state==13) && dut.core.q_status==0)record_acks=record_acks+1;
            if(dut.core.m_valid && dut.core.m_receive && dut.core.state==14 && dut.core.m_status==0)memory_completed=1;
            if(dut.core.q_send && dut.core.q_ready && dut.core.q_op==8)begin
                if(!memory_completed || record_acks!=expected_ack_count())$fatal(1,"COMPLETE before memory and 64 record acknowledgements");
            end
            if(dut.core.q_valid && dut.core.q_receive && dut.core.state==16 && dut.core.q_status==0)page_completed=1;
            if(dut.core.m_send && dut.core.m_ready && dut.core.m_op==2 && !page_completed)$fatal(1,"address RETIRE before page COMPLETE acknowledgement");
            if(dut.core.q_valid && dut.core.q_receive && dut.core.state==2 && dut.core.op==11 && dut.core.q_status==0)page_fence_completed=1;
            if(dut.core.m_send && dut.core.m_ready && dut.core.m_op==3)begin
                if(!page_fence_completed || page_leases!=0 || memory_leases!=0)$fatal(1,"address RECYCLE before page fence acknowledgement");
            end
        end
    end

    // Added index-lifecycle observer: never drives the DUT or changes stimulus.
    integer index_clear_cycles=0,index_wraps=0,index_overflows=0;
    reg [3:0] previous_directory_state=0;
    always @(posedge clk)begin
        if(rst)previous_directory_state<=0;
        else begin
            if(dut.core.memory.memory_service.directory.state==14)begin
                index_clear_cycles=index_clear_cycles+1;
                if(dut.core.memory.memory_service.directory.cmd_ready || dut.core.memory.memory_service.directory.rsp_valid)
                    $fatal(1,"index scrub exposed incomplete directory");
                if(dut.core.memory.memory_service.directory.clear_response)begin
                    if(previous_directory_state!=14)index_wraps=index_wraps+1;
                    if(!dut.core.fence_open || cmd_ready)$fatal(1,"index wrap escaped endpoint fence");
                end
            end
            if(dut.core.memory.memory_service.directory.state==3 && !dut.core.memory.memory_service.directory.insertion_slot)
                index_overflows=index_overflows+1;
            previous_directory_state<=dut.core.memory.memory_service.directory.state;
        end
    end

    wire [1535:0] sparse_expected_blob={expected[2],expected[1],expected[0]};
    reg [7:0] sparse_export_seen=0;
    reg sparse_mask_seen=0;
    integer sparse_codec_count=0,sparse_exports=0,sparse_omitted=0,sparse_masks=0;
    function automatic integer expected_ack_count;
        integer bit_id;
        begin
            expected_ack_count=8;
            if(active_op==5 || active_op==6)begin
                expected_ack_count=0;
                for(bit_id=0;bit_id<8;bit_id=bit_id+1)
                    expected_ack_count=expected_ack_count+expected[0][bit_id];
            end
        end
    endfunction
    always @(posedge clk)if(!rst)begin
        if(dut.core.state==6 && dut.core.q_valid && dut.core.q_status==0 && active_op==5)begin
            if(dut.core.q_payload!=={152'b0,expected[0][7:0]})$fatal(1,"WB snapshot bitmap differs from independent page");
            sparse_mask_seen=1;sparse_masks=sparse_masks+1;
        end
        if(dut.core.q_send && dut.core.q_ready && dut.core.q_op==9)begin
            if(!sparse_mask_seen || !expected[0][dut.core.q_offset] || sparse_export_seen[dut.core.q_offset])
                $fatal(1,"WB EXPORT absent/duplicate/unattested offset");
            sparse_export_seen[dut.core.q_offset]=1;sparse_exports=sparse_exports+1;
        end
        if(dut.core.memory.record_in_valid && dut.core.record_in_ready)begin
            if(dut.core.position!=sparse_codec_count || dut.core.present!==expected[0][dut.core.position]
               || dut.core.record!==sparse_expected_blob[8+dut.core.position*160 +:160])
                $fatal(1,"WB codec representation differs from independent page");
            sparse_codec_count=sparse_codec_count+1;
            if(!dut.core.present)sparse_omitted=sparse_omitted+1;
        end
        if(dut.core.q_send && dut.core.q_ready && dut.core.q_op==8 && active_op==5)begin
            if(!sparse_mask_seen || sparse_codec_count!=8 || sparse_export_seen!==expected[0][7:0])
                $fatal(1,"WB COMPLETE without exact offset coverage");
        end
    end
    reg [7:0] rf_beat_seen=0;
    reg rf_seal_ack=0;
    integer rf_codec_count=0,rf_beats=0,rf_omitted=0,rf_masks=0;
    always @(posedge clk)if(!rst && SPARSE_RF)begin
        if(dut.core.record_out_valid && dut.core.memory.record_out_ready)begin
            if(dut.core.record_out_offset!=rf_codec_count || dut.core.record_out_present!==expected[0][dut.core.record_out_offset]
               || dut.core.record_out_payload!==sparse_expected_blob[8+dut.core.record_out_offset*160 +:160])
                $fatal(1,"RF decoded representation differs from independent page");
            rf_codec_count=rf_codec_count+1;
            if(!dut.core.record_out_present)rf_omitted=rf_omitted+1;
        end
        if(dut.core.q_send && dut.core.q_ready && dut.core.q_op==7)begin
            if(active_op!=6 || !expected[0][dut.core.q_offset] || rf_beat_seen[dut.core.q_offset])
                $fatal(1,"RF BEAT absent/duplicate offset");
            rf_beat_seen[dut.core.q_offset]=1;rf_beats=rf_beats+1;
        end
        if(dut.core.q_send && dut.core.q_ready && dut.core.q_op==14)begin
            if(active_op!=6 || dut.core.state!=30 || rf_codec_count!=8 || rf_beat_seen!==expected[0][7:0]
               || dut.core.pages.cmd_payload!=={152'b0,expected[0][7:0]})
                $fatal(1,"RF seal without complete exact representation");
            rf_masks=rf_masks+1;
        end
        if(dut.core.state==31 && dut.core.q_valid && dut.core.q_status==0)rf_seal_ack=1;
        if(dut.core.q_send && dut.core.q_ready && dut.core.q_op==8 && active_op==6)begin
            if(!rf_seal_ack || rf_codec_count!=8 || rf_beat_seen!==expected[0][7:0])
                $fatal(1,"RF COMPLETE before seal acknowledgement");
        end
    end
    task automatic cold_start;
        begin
            @(negedge clk);rst=1;cmd_valid=0;rsp_ready=0;mode=0;read_bytes_check=1;
            repeat(3)@(negedge clk);rst=0;
        end
    endtask
    task automatic pack_golden;
        reg [10751:0] blob;integer n;
        begin
            blob=0;blob[7:0]=golden_bitmap;
            for(n=0;n<8;n=n+1)blob[8+n*160 +:160]=golden[n];
            for(n=0;n<3;n=n+1)expected[n]=blob[n*512 +:512];
        end
    endtask
    task automatic clear_golden;
        integer n;
        begin golden_bitmap=0;for(n=0;n<8;n=n+1)golden[n]=0;pack_golden;end
    endtask
    task automatic send_host(input integer op,slot,page,q,price,gen,off,field,input reg [31:0] value,input integer frame);
        integer t;
        begin
            @(negedge clk);cmd_valid=1;cmd_op=op;cmd_slot=slot;cmd_page=page;cmd_query=q;cmd_price=price;
            cmd_generation=gen;cmd_offset=off;cmd_field=field;cmd_value=value;
            active_op=op;page_fence_completed=0;
            if(op==5 || op==6)begin
                current_frame=frame;expected_next_aw=frame*192;expected_next_ar=frame*192;
                stream_write=0;stream_read=0;record_acks=0;memory_completed=0;page_completed=0;
                sparse_export_seen=0;sparse_codec_count=0;sparse_mask_seen=0;rf_beat_seen=0;rf_codec_count=0;rf_seal_ack=0;
            end
            t=0;@(posedge clk);while(!cmd_ready)begin @(posedge clk);t=t+1;if(t>10000)$fatal(1,"host command stuck");end
            starts=starts+1;
            @(negedge clk);cmd_valid=0;cmd_op=15;cmd_slot='1;cmd_page='1;cmd_query='1;cmd_price='1;cmd_generation='1;cmd_offset='1;cmd_field='1;cmd_value='1;
        end
    endtask
    task automatic receive_host(input integer status,input reg [159:0] payload,input integer present,dirty,tx,expected_drain);
        integer t,h;
        begin
            t=0;while(!rsp_valid)begin @(negedge clk);t=t+1;if(t>30000+(1<<(SMALL?2:15)))$fatal(1,"host response timeout check=%0d op=%0d state=%0d",checks,active_op,dut.core.state);end
            repeat(4)begin
                if(!rsp_valid || rsp_status!==status[3:0] || rsp_payload!==payload || rsp_present!==present[0] || rsp_dirty!==dirty[0] || rsp_tx!==TB_TX'(tx) || draining!==expected_drain[0])
                    $fatal(1,"host mismatch check=%0d op=%0d status=%0d/%0d tx=%0d/%0d drain=%0d/%0d payload=%h/%h present=%b/%0d dirty=%b/%0d",checks,active_op,rsp_status,status,rsp_tx,tx,draining,expected_drain,rsp_payload,payload,rsp_present,present,rsp_dirty,dirty);
                @(negedge clk);
            end
            if(status==0 && (active_op==5 || active_op==6))begin
                if(page_leases!=0 || memory_leases!=0 || record_acks!=expected_ack_count() || !page_completed || !memory_completed)$fatal(1,"host success before leases retired");
                completed_transfers=completed_transfers+1;
            end
            if(status==0 && active_op==11)begin
                if(allocated!=0 || page_leases!=0 || memory_leases!=0)$fatal(1,"host fence success before recycle");
                completed_fences=completed_fences+1;
            end
            rsp_ready=1;@(posedge clk);@(negedge clk);rsp_ready=0;checks=checks+1;
        end
    endtask
    task automatic request(input integer op,slot,page,q,price,gen,off,field,input reg [31:0] value,input integer frame,status,input reg [159:0] payload,input integer present,dirty,tx,drain);
        integer retry_count,retained_frames,retained_epoch,response_wait;
        begin
            retry_count=0;retained_frames=allocated;retained_epoch=dut.core.memory.memory_service.directory.epoch;
            begin: request_retry
                forever begin
                    send_host(op,slot,page,q,price,gen,off,field,value,frame);
                    if(op==11 && status==0)begin
                        response_wait=0;while(!rsp_valid)begin @(negedge clk);response_wait=response_wait+1;if(response_wait>30000+(1<<TB_HASH)+2*TB_FRAMES)$fatal(1,"FINISH response timeout");end
                        if(rsp_status==7)begin
                            if(!draining || !dut.core.fence_open || allocated!=retained_frames || page_leases!=0 || memory_leases!=0
                               || dut.core.memory.memory_service.directory.epoch!=retained_epoch)
                                $fatal(1,"FENCE_WAIT changed unretired lifetime state");
                            receive_host(7,0,0,0,0,1);
                            retry_count=retry_count+1;finish_retries=finish_retries+1;
                            if(retry_count>20)$fatal(1,"bounded FINISH retry exhausted");
                        end else begin receive_host(status,payload,present,dirty,tx,drain);disable request_retry;end
                    end else begin receive_host(status,payload,present,dirty,tx,drain);disable request_retry;end
                end
            end
        end
    endtask
    task automatic simple(input integer op,slot,page,q,gen,status,tx,drain);
        begin request(op,slot,page,q,0,gen,0,0,0,0,status,0,0,0,tx,drain);end
    endtask
    task automatic fence_and_next_query;
        integer t;
        begin
            simple(10,0,0,0,0,0,0,1);
            send_host(11,0,0,0,0,0,0,0,0,0);
            t=0;while(dut.core.state!=19)begin @(negedge clk);t=t+1;if(t>3000)$fatal(1,"fence never reached address recycle");end
            // Offer a new query throughout the two-domain retirement gap.
            cmd_valid=1;cmd_op=0;cmd_slot=0;cmd_page=0;cmd_query=0;cmd_price=0;cmd_generation=0;cmd_offset=0;cmd_field=0;cmd_value=0;
            while(!rsp_valid)begin @(negedge clk);if(cmd_ready)$fatal(1,"accepted query during fence recycle");end
            receive_host(0,0,0,0,0,0);
            active_op=0;@(posedge clk);if(!cmd_ready)$fatal(1,"query blocked after complete fence");starts=starts+1;
            @(negedge clk);cmd_valid=0;cmd_op=15;
            receive_host(0,0,0,0,0,0);
        end
    endtask
    integer loop_id,n,err,goal_frame,next_tx,gen_value;
    integer fd,rc,vo,vs,vp,vq,vprice,vg,voff,vfield,vstatus,vpresent,vdirty,vtx,vdrain,vframe,vpage_index,vector_count=0;
    reg [31:0] vv;reg [159:0] vpayload;reg [4095:0] vectors_path,pages_path;
    initial begin #1500000000;$fatal(1,"memory endpoint watchdog");end
    integer checkpoint_count=0;
    reg cp_finish_seen=0,cp_memory_seen=0;
    always @(posedge clk)begin
        if(rst)begin cp_finish_seen<=0;cp_memory_seen<=0;end
        else begin
            if(dut.core.state==21)begin cp_finish_seen<=0;cp_memory_seen<=0;end
            if(dut.core.state==25 && dut.core.q_valid && dut.core.q_status==0)cp_finish_seen<=1;
            if(dut.core.state==26 && dut.core.m_send && dut.core.m_ready)begin
                if(!cp_finish_seen || page_leases!=0 || memory_leases!=0)$fatal(1,"checkpoint before page drain");
            end
            if(dut.core.state==27 && dut.core.m_valid && dut.core.m_status==0)cp_memory_seen<=1;
            if(dut.core.state==28 && !cp_memory_seen)$fatal(1,"query resume before directory reset");
            if(dut.core.state>=21 && cmd_ready)$fatal(1,"checkpoint exposed host ingress");
            if(dut.core.q_send && dut.core.q_op>=12 && !(dut.core.q_op==14 && dut.core.state==30 && active_op==6))$fatal(1,"public checkpoint leaked to queue controls");
        end
    end
    function automatic [159:0] page_word(input integer page_id,node_id);
        reg [159:0] word;
        begin
            word=0;
            word[31:0]=32'h7fc12345 ^ (page_id<<8) ^ node_id;
            word[63:32]=32'h80000000 | (page_id<<16) | node_id;
            word[95:64]=32'hffffffff - page_id*64-node_id;
            word[127:96]=32'h3f800000 + page_id*64+node_id;
            word[135:128]=255-page_id-node_id;
            page_word=word;
        end
    endfunction
    task automatic expected_page(input integer page_id);
        begin clear_golden;golden_bitmap=8'h81;
            golden[0]=page_word(page_id,0);golden[7]=page_word(page_id,7);pack_golden;end
    endtask
    integer pidx,nodeidx,fidx,roundidx,cp_total=0;
    reg [159:0] target_word,partial_word;
    initial begin
        clear_golden;cold_start;
        request(0,0,0,2,9,0,0,0,0,0,0,0,0,0,0,0);
        for(pidx=0;pidx<32;pidx=pidx+1)begin
            expected_page(pidx);
            request(1,pidx,1048676+pidx,2,9,0,0,0,0,pidx,0,0,0,0,0,0);
            for(nodeidx=0;nodeidx<2;nodeidx=nodeidx+1)begin
                target_word=page_word(pidx,nodeidx==0?0:7);partial_word=0;
                for(fidx=0;fidx<5;fidx=fidx+1)begin
                    partial_word[fidx*32 +:32]=target_word[fidx*32 +:32];
                    request(3,pidx,1048676+pidx,2,9,0,nodeidx==0?0:7,fidx,target_word[fidx*32 +:32],pidx,0,partial_word,1,1,0,0);
                end
            end
            request(5,pidx,1048676+pidx,2,9,0,0,0,0,pidx,0,0,0,0,pidx,0);

        end
        if(dut.core.bound_mask!==32'hffffffff)$fatal(1,"not all slots simultaneously bound");
        simple(12,0,999,0,7,4,0,0);
        for(pidx=31;pidx>=0;pidx=pidx-1)begin
            for(nodeidx=0;nodeidx<2;nodeidx=nodeidx+1)begin
                target_word=page_word(pidx,nodeidx==0?0:7);
                request(2,pidx,1048676+pidx,2,9,0,nodeidx==0?0:7,0,0,pidx,0,target_word,1,0,0,0);
            end
            request(4,pidx,1048676+pidx,2,9,0,0,0,0,pidx,0,0,0,0,0,0);
        end
        for(roundidx=0;roundidx<8;roundidx=roundidx+1)begin
            @(negedge clk);hold_dispatch=roundidx%4==0;hold_execute=roundidx%4==1;
            hold_fence=roundidx%4==2;hold_ack=roundidx%4==3;blocked_tag=fence_tag;
            send_host(12,0,999,0,0,7,0,0,0,0);
            for(stall_i=0;stall_i<100;stall_i=stall_i+1)begin
                @(negedge clk);
                if(rsp_valid || cmd_ready || fault || fence_tag!=blocked_tag || allocated!=32
                   || dut.core.state>=24 || !dut.core.memory.memory_service.directory.tx_used)
                    $fatal(1,"checkpoint bypassed blocked prerequisite kind=%0d state=%0d",roundidx%4,dut.core.state);
                blocked_cycles=blocked_cycles+1;
            end
            case(roundidx%4)
                0:if(dut.core.pages.request_count==0)$fatal(1,"dispatch stall not exercised");
                1:if(dut.core.pages.work_count==0)$fatal(1,"execute stall not exercised");
                2:if(dut.core.pages.fence_request_count==0 || dut.core.pages.acknowledged)$fatal(1,"fence stall not exercised");
                3:if(dut.core.pages.fence_ack_count==0 || dut.core.pages.acknowledged)$fatal(1,"ACK stall not exercised");
            endcase
            blocked_cases=blocked_cases+1;hold_dispatch=0;hold_execute=0;hold_fence=0;hold_ack=0;
            receive_host(0,0,0,0,0,0);cp_total=cp_total+1;
            if(dut.core.memory.memory_service.directory.epoch!==16'd1 || allocated!=32 || fault || !cp_finish_seen || !cp_memory_seen)$fatal(1,"multipage checkpoint metadata");
            for(pidx=0;pidx<32;pidx=pidx+1)begin
                expected_page(pidx);
                request(1,pidx,1048676+pidx,2,9,0,0,0,0,pidx,0,0,0,0,0,0);
                request(6,pidx,1048676+pidx,2,9,0,0,0,0,pidx,0,0,0,0,pidx,0);
            end
            if(dut.core.bound_mask!==32'hffffffff)$fatal(1,"refill bindings incomplete");
            simple(12,0,999,0,7,4,0,0);
            for(pidx=31;pidx>=0;pidx=pidx-1)begin
                for(nodeidx=0;nodeidx<2;nodeidx=nodeidx+1)begin
                    target_word=page_word(pidx,nodeidx==0?0:7);
                    request(2,pidx,1048676+pidx,2,9,0,nodeidx==0?0:7,0,0,pidx,0,target_word,1,0,0,0);
                end
                request(4,pidx,1048676+pidx,2,9,0,0,0,0,pidx,0,0,0,0,0,0);
            end
        end
        if(cp_total!=8 || completed_transfers!=288 || tag_wraps!=4 || checks!=1778)$fatal(1,"multipage coverage");
        if(blocked_cases!=8 || blocked_cycles!=800)$fatal(1,"missing blocking coverage");
        $display("SMALL_STALLS_PASS cases=8 blocked_cycles=800");
        $display("SMALL_32SLOTS_PASS pages=32 fields=5 checkpoints=%0d transfers=%0d checks=%0d tag_wraps=%0d",cp_total,completed_transfers,checks,tag_wraps);
        $display("SPARSE_WB_COUNTS exports=%0d omitted=%0d masks=%0d",sparse_exports,sparse_omitted,sparse_masks);$display("SPARSE_RF_COUNTS beats=%0d omitted=%0d masks=%0d",rf_beats,rf_omitted,rf_masks);$display("FINISH_RETRY_COUNTS retries=%0d",finish_retries);if(aw_carries==0 || ar_carries==0)$fatal(1,"carry not exercised");
        $display("SPARSE_RECORDS_ADDRESS64_PASS base=%h aw_carries=%0d ar_carries=%0d",BASE,aw_carries,ar_carries);$finish;
    end
endmodule
