    // Protocol monitors observe internal boundaries but never drive state.
    always @(posedge clk)begin
        if(rst)begin held_rsp<=0;previous_tag<=0;end
        else begin
            if(held_rsp && (!rsp_valid || {rsp_status,rsp_payload,rsp_present,rsp_dirty,rsp_tx}!==saved_rsp))$fatal(1,"host response changed under stall");
            held_rsp<=rsp_valid&&!rsp_ready;saved_rsp<={rsp_status,rsp_payload,rsp_present,rsp_dirty,rsp_tx};
            if(rsp_valid&&!rsp_ready)host_stalls=host_stalls+1;
            if(previous_tag!=fence_tag && fence_tag==0)tag_wraps=tag_wraps+1;
            previous_tag<=fence_tag;
            if(dut.fence_open && !dut.q_draining)begin
                closure_gap_cycles=closure_gap_cycles+1;
                if(cmd_ready)$fatal(1,"new host command before address recycle");
            end
            if(m_wvalid&&m_wready)begin
                if(stream_write>=21 || m_wdata!==expected[stream_write])$fatal(1,"independent WB byte mismatch beat=%0d",stream_write);
                stream_write=stream_write+1;
            end
            if(m_rvalid&&m_rready)begin
                if(stream_read>=21 || (read_bytes_check && m_rdata!==expected[stream_read]))$fatal(1,"independent RF byte mismatch beat=%0d",stream_read);
                stream_read=stream_read+1;
            end
            if(dut.q_valid && dut.q_receive && (dut.state==9 || dut.state==13) && dut.q_status==0)record_acks=record_acks+1;
            if(dut.m_valid && dut.m_receive && dut.state==14 && dut.m_status==0)memory_completed=1;
            if(dut.q_send && dut.q_ready && dut.q_op==8)begin
                if(!memory_completed || record_acks!=64)$fatal(1,"COMPLETE before memory and 64 record acknowledgements");
            end
            if(dut.q_valid && dut.q_receive && dut.state==16 && dut.q_status==0)page_completed=1;
            if(dut.m_send && dut.m_ready && dut.m_op==2 && !page_completed)$fatal(1,"address RETIRE before page COMPLETE acknowledgement");
            if(dut.q_valid && dut.q_receive && dut.state==2 && dut.op==11 && dut.q_status==0)page_fence_completed=1;
            if(dut.m_send && dut.m_ready && dut.m_op==3)begin
                if(!page_fence_completed || page_leases!=0 || memory_leases!=0)$fatal(1,"address RECYCLE before page fence acknowledgement");
            end
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
            blob=0;blob[63:0]=golden_bitmap;
            for(n=0;n<64;n=n+1)blob[64+n*160 +:160]=golden[n];
            for(n=0;n<21;n=n+1)expected[n]=blob[n*512 +:512];
        end
    endtask
    task automatic clear_golden;
        integer n;
        begin golden_bitmap=0;for(n=0;n<64;n=n+1)golden[n]=0;pack_golden;end
    endtask
    task automatic send_host(input integer op,slot,page,q,price,gen,off,field,input reg [31:0] value,input integer frame);
        integer t;
        begin
            @(negedge clk);cmd_valid=1;cmd_op=op;cmd_slot=slot;cmd_page=page;cmd_query=q;cmd_price=price;
            cmd_generation=gen;cmd_offset=off;cmd_field=field;cmd_value=value;
            active_op=op;page_fence_completed=0;
            if(op==5 || op==6)begin
                current_frame=frame;expected_next_aw=frame*1344;expected_next_ar=frame*1344;
                stream_write=0;stream_read=0;record_acks=0;memory_completed=0;page_completed=0;
            end
            t=0;@(posedge clk);while(!cmd_ready)begin @(posedge clk);t=t+1;if(t>10000)$fatal(1,"host command stuck");end
            starts=starts+1;
            @(negedge clk);cmd_valid=0;cmd_op=15;cmd_slot='1;cmd_page='1;cmd_query='1;cmd_price='1;cmd_generation='1;cmd_offset='1;cmd_field='1;cmd_value='1;
        end
    endtask
    task automatic receive_host(input integer status,input reg [159:0] payload,input integer present,dirty,tx,expected_drain);
        integer t,h;
        begin
            t=0;while(!rsp_valid)begin @(negedge clk);t=t+1;if(t>30000)$fatal(1,"host response timeout check=%0d op=%0d state=%0d",checks,active_op,dut.state);end
            repeat(4)begin
                if(!rsp_valid || rsp_status!==status[3:0] || rsp_payload!==payload || rsp_present!==present[0] || rsp_dirty!==dirty[0] || rsp_tx!==TB_TX'(tx) || draining!==expected_drain[0])
                    $fatal(1,"host mismatch check=%0d op=%0d status=%0d/%0d tx=%0d/%0d drain=%0d/%0d payload=%h/%h present=%b/%0d dirty=%b/%0d",checks,active_op,rsp_status,status,rsp_tx,tx,draining,expected_drain,rsp_payload,payload,rsp_present,present,rsp_dirty,dirty);
                @(negedge clk);
            end
            if(status==0 && (active_op==5 || active_op==6))begin
                if(page_leases!=0 || memory_leases!=0 || record_acks!=64 || !page_completed || !memory_completed)$fatal(1,"host success before leases retired");
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
        begin send_host(op,slot,page,q,price,gen,off,field,value,frame);receive_host(status,payload,present,dirty,tx,drain);end
    endtask
    task automatic simple(input integer op,slot,page,q,gen,status,tx,drain);
        begin request(op,slot,page,q,0,gen,0,0,0,0,status,0,0,0,tx,drain);end
    endtask
    task automatic fence_and_next_query;
        integer t;
        begin
            simple(10,0,0,0,0,0,0,1);
            send_host(11,0,0,0,0,0,0,0,0,0);
            t=0;while(dut.state!=19)begin @(negedge clk);t=t+1;if(t>3000)$fatal(1,"fence never reached address recycle");end
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
    initial begin
        clear_golden;cold_start;
        if(!SMALL)begin
            if(!$value$plusargs("VECTORS=%s",vectors_path) || !$value$plusargs("PAGES=%s",pages_path))$fatal(1,"missing actual vectors");
            $readmemh(pages_path,raw_expected);fd=$fopen(vectors_path,"r");if(!fd)$fatal(1,"cannot open vectors");
            while(!$feof(fd))begin
                rc=$fscanf(fd,"%h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h\n",vo,vs,vp,vq,vprice,vg,voff,vfield,vv,vstatus,vpayload,vpresent,vdirty,vtx,vdrain,vframe,vpage_index);
                if(rc!=17)$fatal(1,"invalid public vector line");
                if(vo==5 || vo==6)begin
                    for(n=0;n<21;n=n+1)expected[n]=raw_expected[vpage_index*21+n];
                    offset_coverage[(vframe*21)%64]=1;
                end
                request(vo,vs,vp,vq,vprice,vg,voff,vfield,vv,vframe,vstatus,vpayload,vpresent,vdirty,vtx,vdrain);
                vector_count=vector_count+1;
            end
            $fclose(fd);
            if(vector_count!=77099 || completed_transfers!=6086 || completed_fences!=19 || offset_coverage!==64'hffffffffffffffff)$fatal(1,"actual coverage incomplete");
        end else begin
            for(n=7;n<16;n=n+1)if(n!=10 && n!=11)simple(n,0,0,0,0,3,0,0);
            simple(11,0,0,0,0,7,0,0);simple(0,0,0,0,0,0,0,0);simple(1,0,0,0,0,0,0,0);
            simple(6,0,0,0,0,8,0,0);if(allocated!=0)$fatal(1,"refill miss allocated frame");
            golden_bitmap=64'h8000000000000001;
            golden[0]=160'h000000ff7fffffffFFFFFFFF800000007fc12345;golden[63]=0;pack_golden;
            for(n=0;n<5;n=n+1)begin
                vpayload=golden[0]&((160'd1<<((n+1)*32))-1);
                request(3,0,0,0,0,0,0,n,golden[0][n*32 +:32],0,0,vpayload,1,1,0,0);
            end
            request(3,0,0,0,0,0,63,0,0,0,0,0,1,1,0,0);
            request(4,0,0,0,0,0,0,0,0,0,2,0,0,1,0,0);
            request(10,0,0,0,0,0,0,0,0,0,2,0,0,1,0,0);
            simple(5,0,0,0,0,0,0,0);
            request(2,0,0,0,0,0,0,0,0,0,0,golden[0],1,0,0,0);
            simple(4,0,0,0,0,0,0,0);simple(1,1,0,0,0,0,0,0);simple(6,1,0,0,0,0,1,0);
            request(2,1,0,0,0,0,0,0,0,0,0,golden[0],1,0,0,0);
            request(2,1,0,0,0,0,63,0,0,0,0,0,1,0,0,0);
            simple(2,0,0,0,0,1,0,0);simple(4,1,0,0,0,0,0,0);
            simple(0,0,0,1,0,0,0,0);simple(1,0,0,1,1,0,0,0);simple(6,0,0,1,1,8,0,0);simple(2,0,0,1,1,0,0,0);simple(4,0,0,1,1,0,0,0);
            simple(0,0,0,0,0,5,0,0);simple(0,0,0,2,0,0,0,0);simple(0,0,0,3,0,0,0,0);
            clear_golden;
            for(n=1;n<=3;n=n+1)begin
                simple(1,0,n,3,n+1,0,0,0);
                request(5,0,n,3,0,n+1,0,0,0,n,0,0,0,0,n+1,0);
                simple(4,0,n,3,n+1,0,0,0);
            end
            simple(1,0,4,3,5,0,0,0);simple(5,0,4,3,5,9,0,0);simple(2,0,4,3,5,0,0,0);simple(4,0,4,3,5,0,0,0);
            simple(1,0,1,3,6,0,0,0);
            for(n=5;n<8;n=n+1)request(5,0,1,3,0,6,0,0,0,1,0,0,0,0,n,0);
            simple(5,0,1,3,6,5,0,0);simple(4,0,1,3,6,0,0,0);simple(1,0,1,3,0,5,0,0);
            simple(1,0,1,3,7,0,0,0);simple(4,0,1,3,7,0,0,0);
            fence_and_next_query;
            for(loop_id=0;loop_id<12;loop_id=loop_id+1)begin
                clear_golden;golden_bitmap=1;golden[0]=loop_id+1;pack_golden;
                simple(1,0,0,0,0,0,0,0);
                request(3,0,0,0,0,0,0,0,loop_id+1,0,0,golden[0],1,1,0,0);
                simple(5,0,0,0,0,0,0,0);simple(4,0,0,0,0,0,0,0);simple(1,0,0,0,1,0,0,0);simple(6,0,0,0,1,0,1,0);
                request(2,0,0,0,0,1,0,0,0,0,0,golden[0],1,0,0,0);simple(4,0,0,0,1,0,0,0);
                fence_and_next_query;
                simple(1,0,0,0,0,0,0,0);simple(6,0,0,0,0,8,0,0);simple(4,0,0,0,0,0,0,0);
                // Release this new generation domain before next iteration's gen0.
                fence_and_next_query;
            end
            for(err=1;err<=9;err=err+1)begin
                cold_start;clear_golden;simple(0,0,0,0,0,0,0,0);
                goal_frame=(err>=6 && err<=8)?3:0;
                for(n=0;n<goal_frame;n=n+1)begin
                    simple(1,0,n,0,n,0,0,0);request(5,0,n,0,0,n,0,0,0,n,0,0,0,0,n,0);simple(4,0,n,0,n,0,0,0);
                end
                next_tx=goal_frame;gen_value=goal_frame;simple(1,0,goal_frame,0,gen_value,0,0,0);
                reads=(err==3 || err==4 || err==5 || err==7 || err==9);
                if(reads)begin
                    request(5,0,goal_frame,0,0,gen_value,0,0,0,goal_frame,0,0,0,0,next_tx,0);
                    simple(4,0,goal_frame,0,gen_value,0,0,0);gen_value=gen_value+1;next_tx=next_tx+1;simple(1,0,goal_frame,0,gen_value,0,0,0);
                end
                mode=err==8?1:(err==9?0:err);
                if(err==9)begin memory[20]=memory[20]^(512'd1<<511);read_bytes_check=0;end
                request(reads?6:5,0,goal_frame,0,0,gen_value,0,0,0,goal_frame,10,0,0,0,0,0);
                if(!fault || page_leases!=1 || memory_leases!=1 || read_active || m_rvalid)$fatal(1,"failed transfer lost quarantine or left accepted read undrained");
                simple(2,0,goal_frame,0,gen_value,10,0,0);simple(4,0,goal_frame,0,gen_value,10,0,0);simple(8,0,goal_frame,0,gen_value,10,0,0);simple(11,0,0,0,0,10,0,0);
                if(page_leases!=1 || memory_leases!=1)$fatal(1,"fault commands released lease");errors=errors+1;
            end
            if(completed_fences!=25 || tag_wraps!=12 || errors!=9 || closure_gap_cycles==0)$fatal(1,"small coverage incomplete fences=%0d wraps=%0d",completed_fences,tag_wraps);
        end
        $display("TEST_PASS memory_endpoint small=%0d checks=%0d transfers=%0d fences=%0d tag_wraps=%0d errors=%0d gap_cycles=%0d host_stalls=%0d aw=%0d ar=%0d b=%0d r=%0d",SMALL,checks,completed_transfers,completed_fences,tag_wraps,errors,closure_gap_cycles,host_stalls,aw_count,ar_count,b_count,r_count);
        $finish;
    end
