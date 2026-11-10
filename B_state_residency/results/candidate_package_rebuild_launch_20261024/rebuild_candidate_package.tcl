set b_root [file normalize [file join [file dirname [info script]] ../..]]
set candidate_output [file join $b_root results candidate_package_rebuild_20261024]
source [file join $b_root hardware candidates native_epoch6_record Scripts synth.tcl]
