set b_root [file normalize [file join [file dirname [info script]] ../..]]
set b_sim [file join $b_root results owner_axi_v2_20261024]
set b_boundary [file join $b_root results owner_axi_boundaries_20261024]
puts [exec /usr/bin/python3 -I [file join $b_root scripts audit_owner_axi.py] $b_sim 2>@1]
puts [exec /usr/bin/python3 -I [file join $b_root scripts audit_owner_axi_boundaries.py] $b_boundary 2>@1]
set b_out [file join $b_root results owner_axi_synthesis_20261024]
if {[file exists $b_out]} {error "Preserve existing results"}
file mkdir $b_out
file copy [file join $b_sim sources owner_state_store.sv] [file join $b_out owner_state_store.sv]
file copy [file join $b_sim source_bound_audit.json] [file join $b_out simulation_audit.json]
file copy [file join $b_boundary source_bound_audit.json] [file join $b_out boundary_audit.json]
file copy [info script] [file join $b_out synthesize_owner_axi.tcl]
puts "OWNER_AXI_SYNTH_BEGIN version=[version -short]"
set_param general.maxThreads 2
create_project -in_memory -part xcu280-fsvh2892-2L-e
read_verilog -sv [file join $b_out owner_state_store.sv]
set b_f [open [file join $b_out research_clock.xdc] w]
puts $b_f {create_clock -name research_clock -period 10.000 [get_ports clk]}
close $b_f
read_xdc [file join $b_out research_clock.xdc]
synth_design -top owner_state_store -part xcu280-fsvh2892-2L-e -mode out_of_context
report_utilization -file [file join $b_out utilization.rpt]
report_drc -checks [get_drc_checks LUTLP-1] -file [file join $b_out combinational_loops.rpt]
check_timing -verbose -file [file join $b_out check_timing.rpt]
write_checkpoint [file join $b_out owner_state_store.dcp]
close_project
puts "OWNER_AXI_SYNTH_DONE"
