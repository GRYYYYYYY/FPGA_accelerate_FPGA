// Observe actual ports and live ledger. No stimulus is injected behind a port.
function automatic[135:0]he_ledger;
 begin
  he_ledger={system.controller.sequence_seen,system.controller.label_state_dirty,
   system.controller.last_sequence,system.controller.last_design,
   system.controller.last_version,system.controller.last_query,system.controller.last_price};
 end
endfunction

always @(posedge clk)if(he_active)begin
 he_cycles=he_cycles+1;
 if(he_cycles>100000)$fatal(1,"host edit extension watchdog");
 if((^{host_io_valid,host_io_ready,host_io_rsp_valid,host_io_rsp_ready,
       system.controller.cp_safe,system.controller.host_label_edit})===1'bx)
  $fatal(1,"host edit port unknown");
 if(system.controller.host_label_edit!==
    (host_io_valid&&host_io_ready&&host_io_write))
  $fatal(1,"host edit actual handshake alias");
 if(host_io_valid&&host_io_ready)begin
  if(he_io_pending||system.controller.cp_safe!==1'b0||pc_owned||system.controller.owned||
     host_io_node!=66893||f_sv[8]!==1'b1||f_sr[8]!==1'b1)
   $fatal(1,"host edit request outside native contract");
  if(host_io_write)begin
   if(he_phase!=1||host_io_field!=3||host_io_value!==he_label_saved[96+:32])
    $fatal(1,"host edit write payload");
   he_writes=he_writes+1;
   $fdisplay(trace,"HOST_EDIT_WRITE %0d %0d %0d %08h",cycles,host_io_node,host_io_field,host_io_value);
  end
  he_io_pending=1;he_pending_write=host_io_write;he_io_requests=he_io_requests+1;
 end
 if(host_io_rsp_valid&&host_io_rsp_ready)begin
  if(!he_io_pending||host_io_status!==0)$fatal(1,"host edit response ownership/status");
  he_io_pending=0;he_io_replies=he_io_replies+1;
  if(he_pending_write)begin
   he_write_replies=he_write_replies+1;
   $fdisplay(trace,"HOST_EDIT_WRITE_REPLY %0d %0d",cycles,host_io_status);
  end
 end
 if(qc_cp_valid&&qc_cp_ready)begin
  if(!pc_owned||system.controller.cp_safe!==1'b1||system.controller.host_label_edit!==1'b0)
   $fatal(1,"host edit checkpoint admission");
  he_cp_requests=he_cp_requests+1;
 end
 if(qc_cp_rsp_valid&&qc_cp_rsp_ready)begin
  if(he_phase!=2&&he_phase!=3&&he_phase!=4)$fatal(1,"host edit unexpected checkpoint response");
  if(qc_cp_status!==(he_phase==3?4'd1:4'd0))$fatal(1,"host edit checkpoint status");
  he_cp_replies=he_cp_replies+1;
  $fdisplay(trace,"HOST_EDIT_CP_REPLY %0d %0d %0d %08h %0d",cycles,he_phase,qc_cp_status,qc_cp_crc,qc_restore_pending);
 end
 if(qc_cp_s_valid&&qc_cp_s_ready)he_import_words=he_import_words+1;
 if(qc_cp_m_valid&&qc_cp_m_ready)he_export_words=he_export_words+1;
 if(system.controller.cp_state==2&&(he_phase==3||he_phase==4))begin
  // Exclude every alternative cause in CP_CHECK before examining dirty clearing.
  if(system.controller.rst!==1'b0||system.controller.cp_importing!==1'b1||system.controller.cp_rebasing!==1'b0||
     system.controller.cp_failed!==1'b0||system.controller.abort!==1'b0||
     system.controller.backend_fault!==1'b0||system.controller.cp_drift!==1'b0||
     system.controller.cp_bad!==1'b0||
     (~system.controller.cp_running)!==system.controller.cp_wanted||
     system.controller.cp_stage[7][6]!==1'b1||system.controller.cp_stage[8]!==32'd180330||
     system.controller.last_sequence!==32'd180330||system.controller.label_state_dirty!==1'b1||
     qc_restore_pending!==1'b1)
   $fatal(1,"host edit import has alternative rejection cause");
  if(system.controller.cp_stage[7][7]!==(he_phase==4))$fatal(1,"host edit imported dirty flag");
  if(he_phase==3)he_reject_checks=he_reject_checks+1;else he_accept_checks=he_accept_checks+1;
  $fdisplay(trace,"HOST_EDIT_CP_CHECK %0d %0d %08h %08h %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d",cycles,he_phase,
   ~system.controller.cp_running,system.controller.cp_wanted,
   system.controller.label_state_dirty,system.controller.cp_stage[7][7],
   system.controller.cp_bad,system.controller.cp_failed,system.controller.cp_drift,
   system.controller.abort,system.controller.backend_fault,system.controller.cp_rebasing,
   system.controller.cp_stage[7][6],system.controller.cp_stage[8],system.controller.last_sequence);
 end
 #1;
 if(he_keep_dirty)begin
  if(he_ledger()!==he_dirty_ledger||rc_slots!==he_slots_saved||
     system.inner.backend.config_restore.descriptor!==he_descriptor_saved||
     k_count!==he_count_saved||k_saved_checkpoint!==he_checkpoint_saved)
   $fatal(1,"host edit checkpoint changed live ledger or retained context");
  he_atomic_checks=he_atomic_checks+1;
 end
end

task host_edit_extension;begin
 if(he_active||he_finished||pc_owned||system.controller.owned||qc_restore_pending||qc_cp_busy||
    system.controller.label_state_dirty!==1'b0||system.controller.sequence_seen!==1'b1||
    system.controller.last_sequence!==32'd180330||rc_slots!==4'hf||
    qcp_image[6]!==32'd8||qcp_image[7]!==32'h62||qcp_image[8]!==32'd180330||
    {qcp_image[5],qcp_image[4]}!==64'h100000004||qcp_sum()!==qc_cp_crc)
  $fatal(1,"host edit initial clean checkpoint/context");
 he_clean_crc=qc_cp_crc;he_clean_ledger=he_ledger();
 he_slots_saved=rc_slots;he_descriptor_saved=system.inner.backend.config_restore.descriptor;
 he_count_saved=k_count;he_checkpoint_saved=k_saved_checkpoint;he_edit_before=ce_edit;
 for(integer x=0;x<10;x=x+1)begin
  he_clean_image[x]=qcp_image[x];
  $fdisplay(trace,"HOST_EDIT_CLEAN_WORD %0d %0d %08h",cycles,x,qcp_image[x]);
 end
 he_phase=1;he_active=1;
 $fdisplay(trace,"HOST_EDIT_BEGIN %0d %08h %0d %0d",cycles,he_clean_crc,k_count,k_saved_checkpoint);
 label_read(66893);he_label_saved=host_record;
 if((^he_label_saved)===1'bx)$fatal(1,"host edit source label unknown");
 $fdisplay(trace,"HOST_EDIT_LABEL_BEFORE %0d %040h",cycles,he_label_saved);
 label_write(66893,3,he_label_saved[96+:32]);
 // sequence_seen is bit135, dirty is bit134 in the explicit ledger concatenation.
 he_dirty_ledger=he_clean_ledger|(136'b1<<134);
 if(he_ledger()!==he_dirty_ledger||he_writes!=1||he_write_replies!=1||ce_edit-he_edit_before!=1)
  $fatal(1,"host edit did not dirty ledger on the actual write");
 he_keep_dirty=1;
 label_read(66893);
 if(host_record!==he_label_saved||he_io_requests!=3||he_io_replies!=3||he_io_pending)
  $fatal(1,"host edit same-value write changed label or failed to retire");
 $fdisplay(trace,"HOST_EDIT_LABEL_AFTER %0d %040h",cycles,host_record);
 // Flush through the real control lane so the same-value write also reaches backing memory.
 control(1);
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);
 @(negedge clk);pc_acquire_valid=0;if(!pc_owned)$fatal(1,"host edit lease acquisition");
 he_phase=2;qc_cp_generation=0;qcp_start(0);
 for(integer x=0;x<10;x=x+1)begin
  wait(qc_cp_m_valid);@(negedge clk);
  if(qc_cp_m_index!==x||qc_cp_m_last!==(x==9))$fatal(1,"host edit dirty export boundary");
  qcp_image[x]=qc_cp_m_data;he_dirty_image[x]=qc_cp_m_data;
  if(qc_cp_m_data!==(he_clean_image[x]^(x==7?32'h80:32'd0)))
   $fatal(1,"host edit dirty export changed other bits");
  $fdisplay(trace,"HOST_EDIT_DIRTY_WORD %0d %0d %08h",cycles,x,qc_cp_m_data);
  qc_cp_m_ready=1;@(negedge clk);qc_cp_m_ready=0;
 end
 qcp_result(0);he_dirty_crc=qc_cp_crc;
 if(qcp_sum()!==he_dirty_crc||he_dirty_crc===he_clean_crc)$fatal(1,"host edit dirty export CRC");
 for(integer x=0;x<10;x=x+1)qcp_image[x]=he_clean_image[x];
 if(qcp_sum()!==he_clean_crc)$fatal(1,"host edit saved clean CRC");
 he_phase=3;qc_cp_expected_crc=he_clean_crc;qcp_load(1);
 if(qc_restore_pending!==1'b1||he_reject_checks!=1||he_ledger()!==he_dirty_ledger)
  $fatal(1,"host edit clean import did not preserve atomic dirty ledger/pending");
 // A rejected import deliberately leaves pending set. Recover using the valid dirty image.
 for(integer x=0;x<10;x=x+1)qcp_image[x]=he_dirty_image[x];
 if(qcp_sum()!==he_dirty_crc)$fatal(1,"host edit saved dirty CRC");
 he_phase=4;qc_cp_expected_crc=he_dirty_crc;qcp_load(0);
 if(qc_restore_pending!==1'b0||he_accept_checks!=1||he_ledger()!==he_dirty_ledger)
  $fatal(1,"host edit valid dirty import failed to recover");
 pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);
 @(negedge clk);pc_release_valid=0;wait(!pc_owned);
 if(he_cp_requests!=3||he_cp_replies!=3||he_import_words!=20||he_export_words!=10||
    he_writes!=1||he_write_replies!=1||he_io_requests!=3||he_io_replies!=3||he_io_pending||
    he_reject_checks!=1||he_accept_checks!=1||he_atomic_checks==0||ce_edit-he_edit_before!=1)
  $fatal(1,"host edit coverage missing or unbalanced");
 $fdisplay(trace,"HOST_EDIT_PASS %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d %08h %08h %0d %0d %0d %0d %0d",
  cycles,he_io_requests,he_io_replies,he_writes,he_write_replies,he_cp_requests,he_cp_replies,
  he_import_words,he_export_words,he_reject_checks,he_accept_checks,he_atomic_checks,he_cycles,
  he_clean_crc,he_dirty_crc,qc_restore_pending,system.controller.label_state_dirty,
  system.controller.last_sequence,rc_slots,pc_owned);
 $display("HOST_EDIT_NATIVE_PASS writes=%0d replies=%0d clean_rejected=%0d dirty_accepted=%0d atomic_checks=%0d",
  he_writes,he_write_replies,he_reject_checks,he_accept_checks,he_atomic_checks);
 he_finished=1;he_active=0;he_keep_dirty=0;he_phase=5;
end endtask
