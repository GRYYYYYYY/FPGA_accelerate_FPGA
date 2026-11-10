set_param general.maxThreads 2
puts [list VIVADO_VERSION [version -short]]
open_checkpoint {/tmp/B_state_residency_offer_20261025/restore_seed_synth_off_v1/synth.dcp}
write_xdc -force -exclude_physical {/tmp/B_state_residency_offer_20261025/restore_seed_synth_off_v1/results/methodology_v1/effective.xdc}
report_methodology -no_waivers -file {/tmp/B_state_residency_offer_20261025/restore_seed_synth_off_v1/results/methodology_v1/methodology.rpt}
proc dump_objects {objects filename} {
 set f [open $filename w]
 foreach obj $objects {
  puts $f [list OBJECT $obj]
  foreach prop [lsort [list_property $obj]] {
   puts $f [list PROPERTY $prop [get_property $prop $obj]]
  }
 }
 close $f
}
dump_objects [get_methodology_violations] {/tmp/B_state_residency_offer_20261025/restore_seed_synth_off_v1/results/methodology_v1/methodology_objects.tcllist}
set loop_checks [get_drc_checks LUTLP-1]
if {[llength $loop_checks] != 1} {error "LUTLP-1 unavailable"}
report_drc -no_waivers -checks $loop_checks -file {/tmp/B_state_residency_offer_20261025/restore_seed_synth_off_v1/results/methodology_v1/loops.rpt}
dump_objects [get_drc_violations] {/tmp/B_state_residency_offer_20261025/restore_seed_synth_off_v1/results/methodology_v1/loop_objects.tcllist}
set f [open {/tmp/B_state_residency_offer_20261025/restore_seed_synth_off_v1/results/methodology_v1/loop_elements.tcllist} w]
foreach v [get_drc_violations] {
 puts $f [list VIOLATION $v]
 puts $f [list CELLS [get_cells -quiet -of_objects $v]]
 puts $f [list NETS [get_nets -quiet -of_objects $v]]
 puts $f [list PINS [get_pins -quiet -of_objects $v]]
}
close $f
check_timing -verbose -file {/tmp/B_state_residency_offer_20261025/restore_seed_synth_off_v1/results/methodology_v1/check_timing.rpt}
report_clocks -file {/tmp/B_state_residency_offer_20261025/restore_seed_synth_off_v1/results/methodology_v1/clocks.rpt}
dump_objects [get_timing_paths -delay_type max -max_paths 10 -nworst 1] {/tmp/B_state_residency_offer_20261025/restore_seed_synth_off_v1/results/methodology_v1/timing_path_objects.tcllist}
puts RESTORE_SEED_DIAGNOSTICS_DONE
