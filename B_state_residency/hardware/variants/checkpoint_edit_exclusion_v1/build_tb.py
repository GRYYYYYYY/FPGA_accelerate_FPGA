"""Keep original CP/rebase tests and add separate native and overlap scenarios."""
def build(root,mode,suite):
    assert mode in ('baseline','default','exclusive')
    assert suite in ('checkpoint','rebase','native_cp','generic_overlap')
    extra='.CP_SAFE_EXCLUDES_HOST_EDIT(1)'if mode=='exclusive'else''
    if suite=='checkpoint':
        s=(root/'hardware/variants/query_checkpoint_v1/tb_query_checkpoint.sv').read_text()
        old='query_lifecycle dut(.*);';assert s.count(old)==1
        params=f' #({extra})'if extra else''
        ties=".cp_rebase(1'b0),.cp_rebase_permit(1'b0),.cp_source_version(32'd0),.cp_source_query(2'd0),.cp_source_price(4'd0),"
        return s.replace(old,f'query_lifecycle{params} dut({ties}.*);'),'tb_query_checkpoint','events.txt','QUERY_CHECKPOINT_PASS'
    s=(root/'hardware/variants/query_warm_rebase_v1/tb_rebase.sv').read_text()
    old='query_lifecycle #(.ENABLE_REBASE(1))';assert s.count(old)==1
    s=s.replace(old,'query_lifecycle #(.ENABLE_REBASE(1)'+(','+extra if extra else'')+')')
    if suite=='rebase':return s,'tb_rebase','native.txt','QUERY_REBASE_PASS'
    # Separate scenarios, not edits to the original compatibility stimulus.
    s=s.replace(".host_label_edit(1'b0)",'.host_label_edit(edit)').replace(".cp_safe(1'b1)",'.cp_safe(safe)')
    s=s.replace('query_lifecycle #','reg safe=1,edit=0;\nquery_lifecycle #',1)
    start=s.index('initial begin\n trace=$fopen(')
    prefix=s[:start]
    init='''initial begin
 trace=$fopen("native.txt","w");$readmemh("query.hex",image);repeat(3)@(negedge clk);rst=0;expected_crc=sum();
'''
    if suite=='native_cp':
        stimulus='''
 start(1);words(5);check(dut.last_sequence==0);
 @(negedge clk);safe=0;edit=1;result(2,0);check(crc==0);
 @(negedge clk);edit=0;safe=1;
 start(1);words(10);result(0,1);check(crc==sum());
 rebase=0;start(0);wait(mvalid);@(negedge clk);safe=0;edit=1;
 for(integer i=0;i<10;i=i+1)begin
  wait(mvalid);@(negedge clk);check(mindex==i&&mlast==(i==9));
  repeat(3)begin @(negedge clk);check(mvalid&&mindex==i);end
  mready=1;@(negedge clk);mready=0;
 end
 result(2,1);check(dut.label_state_dirty);
 @(negedge clk);edit=0;safe=1;
'''
    else:
        stimulus='''
 start(1);words(5);check(dut.last_sequence==0);
 @(negedge clk);edit=1;
'''
        if mode=='exclusive':
            stimulus+='''
 for(integer i=5;i<10;i=i+1)begin
  @(negedge clk);index=i;data=image[i];slast=i==9;svalid=1;
  do @(posedge clk);while(!sready);@(negedge clk);svalid=0;
 end
 edit=0;result(0,1);check(crc==sum());
'''
        else:stimulus+='result(2,0);check(crc==0);@(negedge clk);edit=0;\n'
    monitor='''
 integer safe_busy=0,edit_busy=0,overlaps=0;
 always @(posedge clk)if(!rst&&busy)begin
  if(safe)safe_busy=safe_busy+1;
  if(edit)edit_busy=edit_busy+1;
  if(safe&&edit)overlaps=overlaps+1;
 end
'''
    # Monitor declarations precede initial block and no DUT state is forced.
    end='''
 check(safe_busy>0&&edit_busy>0);
 OVERLAP_CHECK
 $fdisplay(trace,"CP_EDIT_MONITOR %0d %0d %0d",safe_busy,edit_busy,overlaps);
 $fdisplay(trace,"DONE %0d",checks);$fclose(trace);$display("CHECKPOINT_EDIT_FOCUS_PASS checks=%0d",checks);$finish;
end
endmodule
'''.replace('OVERLAP_CHECK','check(overlaps==0);'if suite=='native_cp'else'check(overlaps>0);')
    return prefix+monitor+init+stimulus+end,'tb_rebase','native.txt','CHECKPOINT_EDIT_FOCUS_PASS'
