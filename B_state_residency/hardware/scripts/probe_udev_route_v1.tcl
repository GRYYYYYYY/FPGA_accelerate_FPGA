if {[version -short] ne "2022.2"} {error "Expected matched Vivado 2022.2"}
set_param general.maxThreads 2
config_webtalk -info
set probe_maps [open /proc/[pid]/maps r]
set probe_out [open runtime_maps.txt w]
puts $probe_out [read $probe_maps]
close $probe_maps
close $probe_out
read_verilog fixture.v
synth_design -top udev_route_probe_v1 -part xcu280-fsvh2892-2L-e -mode out_of_context
create_clock -name core_clk -period 10.000 [get_ports clk]
opt_design
place_design -directive Default
write_checkpoint placed.dcp
route_design -directive Default
write_checkpoint routed.dcp
report_route_status -file route_status.rpt
report_timing_summary -file timing_routed.rpt
close_design
open_checkpoint routed.dcp
report_route_status -file route_status_reopened.rpt
report_timing_summary -file timing_reopened.rpt
set probe_done [open completed.txt w]
puts $probe_done UDEV_ROUTE_PROBE_REOPENED
close $probe_done
puts UDEV_ROUTE_PROBE_REOPENED
close_project
