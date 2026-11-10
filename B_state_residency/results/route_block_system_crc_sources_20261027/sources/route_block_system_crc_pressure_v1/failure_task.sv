task seed_fail_then_retry;begin
 // The first attempt has already repaired the three G4 owner keys.
 seed_trial=1;cancel_started=1;
 if(!$value$plusargs("g4imports=%s",warm_path))$fatal(1,"seed failure source");
 warm_fd=$fopen(warm_path,"r");if(!warm_fd)$fatal(1,"seed failure source open");
 $fdisplay(trace,"SEED_FAILURE_BEGIN %0d %0d %0d %0d",cycles,SEED_CRC_FAILURE,k_count,k_corrected);
 for(integer x=0;x<(SEED_CRC_FAILURE?g4_saved_count:1);x=x+1)begin
  rc=$fscanf(warm_fd,"%d",import_node);if(rc!=1)$fatal(1,"seed failure node");
  for(integer f=0;f<5;f=f+1)begin rc=$fscanf(warm_fd,"%h",word);if(rc!=1)$fatal(1,"seed failure field");import_record[f*32+:32]=word;end
  if(SEED_CRC_FAILURE&&x+1==g4_saved_count)import_record[0]=~import_record[0];
  @(negedge clk);lr_s_valid=1;lr_s_node=import_node;lr_s_payload=import_record;lr_s_last=x+1==g4_saved_count;
  do @(posedge clk);while(!lr_s_ready);@(negedge clk);lr_s_valid=0;
 end
 $fclose(warm_fd);
 if(!SEED_CRC_FAILURE)begin
  // Cancel on an actual native write acceptance, with its reply outstanding.
  do @(posedge clk);while(!(system.inner.backend.dut.core.p.native_cmd_valid&&
     system.inner.backend.dut.core.p.native_cmd_ready&&
     system.inner.backend.dut.core.p.native_cmd_op==3&&
     system.inner.backend.dut.core.p.native_cmd_field==2));
  @(negedge clk);
  if(seed_requests!=3||lr_written||lr_verified||!system.inner.backend.label_restore.l_import||
     !system.inner.backend.dut.core.p.pager.restore_write||
     system.inner.backend.dut.core.p.native_rsp_valid)
    $fatal(1,"seed cancel did not hit third native write in flight");
  abort=1;
  $fdisplay(trace,"SEED_ABORT %0d %0d %0d %0d",cycles,seed_requests,lr_written,lr_verified);
 end
 wait(k_rsp_valid);
 repeat(8)begin @(negedge clk);
  if(k_rsp_status!=6||k_rsp_cookie!=32'hc0040001||k_count!=3||k_saved_checkpoint!=20||
     !wm_owned||!wm_fault||recover_open||!system.wm_retired||lr_busy||
     qc_cmd_ready||rc_req_ready||pc_acquire_ready||wm_receipts)
    $fatal(1,"seed failure escaped quarantine status=%0d",k_rsp_status);
  $fdisplay(trace,"SEED_FAILURE_HELD %0d %0d %0d %0d %0d %0d %0d",cycles,
    k_rsp_status,k_count,lr_written,lr_verified,system.wm_retired,wm_owned);
 end
 if(!seed_failure_seen||seed_requests!=(SEED_CRC_FAILURE?3900:3)||
    lr_rsp_status!=(SEED_CRC_FAILURE?8:7)||lr_written!=(SEED_CRC_FAILURE?780:0)||lr_verified)
   $fatal(1,"seed native failure receipt mismatch");
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;abort=0;
 repeat(8)begin @(negedge clk);if(!wm_owned||!wm_fault||recover_open||qc_cmd_ready||rc_req_ready||pc_acquire_ready)$fatal(1,"seed failure opened work");end
 // The failed attempt7 remains consumed, even when no full label was written.
 retry_cookie=32'hc00400ff;k_rec_valid=1;
 do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rsp_valid);repeat(8)begin @(negedge clk);
  if(k_rsp_status!=1||k_rsp_cookie!=retry_cookie||k_count!=3||!wm_owned||!wm_fault||recover_open)
   $fatal(1,"seed same attempt accepted");
 end
 $fdisplay(trace,"SEED_RETRY_REJECT %0d %0d %0d %08h",cycles,k_rsp_status,k_count,k_rsp_cookie);
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;repeat(8)@(negedge clk);
 // Re-arm only after the failed services and reply have actually retired.
 seed_trial=2;seed_start_consumed=0;seed_requests=0;
 as_recover_version=8;as_recover_query=2;retry_cookie=32'hc0040002;
 $fdisplay(trace,"SEED_RETRY_START %0d %0d %0d %0d",cycles,as_recover_version,as_recover_query,k_count);
 k_rec_valid=1;do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rcfg_valid);@(negedge clk);restore_epoch=k_new_query;restore_version=k_new_version;
 wait(k_labels_valid);@(negedge clk);
 if(k_count!=3||k_corrected!=0||!wm_owned||wm_fault||as_bound_generation!=64'h100000004)
  $fatal(1,"seed retry owner verification");
 $fdisplay(trace,"SEED_RETRY_OWNER %0d %0d %0d",cycles,k_corrected,k_count);
end endtask
