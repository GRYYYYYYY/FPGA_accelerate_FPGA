set b_root [file normalize [file join [file dirname [info script]] ../..]]
set b_verified [file join $b_root results exclusion_label_adapter_v2_20261024]
puts [exec python3 [file join $b_root scripts/audit_exclusion_label_adapter.py] 2>@1]
set b_out [file join $b_root results exclusion_label_adapter_v2_synthesis_20261024]
if {[file exists $b_out]} {error "Result directory exists; preserve evidence"}
file mkdir $b_out
file copy [file join $b_verified sources exclusion_label_adapter.sv] [file join $b_out exclusion_label_adapter.sv]
file copy [file join $b_verified source_bound_audit.json] [file join $b_out simulation_audit.json]
file copy [info script] [file join $b_out synthesize_exclusion_label_adapter_v2.tcl]
puts "LABEL_ADAPTER_SYNTH_BEGIN version=[version -short]"
set_param general.maxThreads 2
create_project -in_memory -part xcu280-fsvh2892-2L-e
read_verilog -sv [file join $b_out exclusion_label_adapter.sv]
set b_f [open [file join $b_out research_clock.xdc] w]
puts $b_f {create_clock -name research_clock -period 10.000 [get_ports clk]}
close $b_f
read_xdc [file join $b_out research_clock.xdc]
synth_design -top exclusion_label_adapter -part xcu280-fsvh2892-2L-e -mode out_of_context
report_utilization -file [file join $b_out utilization.rpt]
report_utilization -hierarchical -file [file join $b_out utilization_hierarchical.rpt]
write_checkpoint [file join $b_out exclusion_label_adapter.dcp]
set b_f [open [file join $b_out primitive_counts.tsv] w]
array set b_counts {}
foreach b_cell [get_cells -hier -filter {IS_PRIMITIVE == 1}] {
    set b_ref [get_property REF_NAME $b_cell]
    if {![info exists b_counts($b_ref)]} {set b_counts($b_ref) 0}
    incr b_counts($b_ref)
}
foreach b_ref [lsort [array names b_counts]] {puts $b_f "$b_ref\t$b_counts($b_ref)"}
close $b_f
set b_f [open [file join $b_out completed.txt] w]
puts $b_f "LABEL_ADAPTER_SYNTH_DONE version=[version -short]"
close $b_f
close_project
puts "LABEL_ADAPTER_SYNTH_DONE"
