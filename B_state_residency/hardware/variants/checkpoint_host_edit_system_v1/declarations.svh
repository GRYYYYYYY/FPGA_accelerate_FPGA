// Verification state only; insert before the original module declarations.
integer he_cycles=0,he_io_requests=0,he_io_replies=0,he_writes=0,he_write_replies=0;
integer he_cp_requests=0,he_cp_replies=0,he_import_words=0,he_export_words=0;
integer he_reject_checks=0,he_accept_checks=0,he_atomic_checks=0,he_phase=0;
integer he_edit_before=0;
reg he_active=0,he_finished=0,he_io_pending=0,he_pending_write=0,he_keep_dirty=0;
reg[31:0]he_clean_image[0:9],he_dirty_image[0:9];
reg[31:0]he_clean_crc,he_dirty_crc,he_count_saved,he_checkpoint_saved;
reg[159:0]he_label_saved;
reg[135:0]he_clean_ledger,he_dirty_ledger;
reg[2303:0]he_descriptor_saved;
reg[3:0]he_slots_saved;
