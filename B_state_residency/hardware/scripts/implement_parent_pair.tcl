# Non-project Vivado 2022.2, matched default synthesis/place/route and 10ns clock.
set parent_out {@OUT@}
set parent_old_dir [pwd]
cd $parent_out
set_param general.maxThreads 2
set parent_flow [open [file join $parent_out milestones.txt] w]
puts $parent_flow "BEGIN version=[version -short]"
flush $parent_flow
 puts "PARENT_PHYSICAL_BEGIN version=[version -short]"
 foreach variant {baseline cached} {
  set pdir [file join $parent_out $variant]
  if {[file exists $pdir]} {error "Preserve existing physical results $pdir"}
  file mkdir $pdir
  create_project -in_memory -part xcu280-fsvh2892-2L-e
  foreach source [lsort [glob [file join $parent_out sources center *]]] {
   if {[file extension $source] eq ".sv"} {read_verilog -sv $source} else {read_verilog $source}
  }
  read_verilog -sv [file join $parent_out sources $variant postprev_inputs.sv]
  set cf [open [file join $pdir research_clock.xdc] w]
  puts $cf {create_clock -name research_clock -period 10.000 [get_ports clk]}
  close $cf
  read_xdc [file join $pdir research_clock.xdc]
  puts "PARENT_PHYSICAL_SYNTH $variant"
  puts $parent_flow "SYNTH $variant [clock seconds]";flush $parent_flow
  synth_design -top postprev_inputs -part xcu280-fsvh2892-2L-e -mode out_of_context
  report_utilization -file [file join $pdir utilization_synth.rpt]
  report_utilization -hierarchical -file [file join $pdir utilization_synth_hier.rpt]
  report_methodology -file [file join $pdir methodology_synth.rpt]
  report_timing_summary -check_timing_verbose -report_unconstrained -max_paths 10 -file [file join $pdir timing_synth.rpt]
  report_drc -checks [get_drc_checks LUTLP-1] -file [file join $pdir combinational_loops.rpt]
  write_checkpoint [file join $pdir synthesized.dcp]
  write_xdc -exclude_physical [file join $pdir constraints_synth.xdc]
  puts "PARENT_PHYSICAL_PLACE_ROUTE $variant"
  puts $parent_flow "PLACE_ROUTE $variant [clock seconds]";flush $parent_flow
  opt_design
  place_design -directive Default
  write_checkpoint [file join $pdir placed.dcp]
  route_design -directive Default
  report_route_status -file [file join $pdir route_status.rpt]
  report_utilization -file [file join $pdir utilization_routed.rpt]
  report_utilization -hierarchical -file [file join $pdir utilization_routed_hier.rpt]
  report_methodology -file [file join $pdir methodology_routed.rpt]
  report_drc -file [file join $pdir drc_routed.rpt]
  report_timing_summary -check_timing_verbose -report_unconstrained -max_paths 10 -file [file join $pdir timing_routed.rpt]
  write_xdc -exclude_physical [file join $pdir constraints_routed.xdc]
  write_checkpoint [file join $pdir routed.dcp]
  set tf [open [file join $pdir internal_paths.tsv] w]
  puts $tf "delay_type\tslack_ns\tstartpoint\tendpoint\tdatapath_delay_ns\trequirement_ns"
  foreach dtype {max min} {
   set paths [get_timing_paths -from [get_clocks research_clock] -to [get_clocks research_clock] -delay_type $dtype -max_paths 10]
   if {[llength $paths]==0} {error "No constrained internal timing paths"}
   foreach path $paths {puts $tf "$dtype\t[get_property SLACK $path]\t[get_property STARTPOINT_PIN $path]\t[get_property ENDPOINT_PIN $path]\t[get_property DATAPATH_DELAY $path]\t[get_property REQUIREMENT $path]"}
  }
  close $tf
  set done [open [file join $pdir completed.txt] w]
  puts $done "PARENT_PHYSICAL_VARIANT_DONE $variant version=[version -short] part=[get_property PART [current_design]] period=[get_property PERIOD [get_clocks research_clock]]"
  close $done
  puts "PARENT_PHYSICAL_VARIANT_DONE $variant"
  puts $parent_flow "DONE $variant [clock seconds]";flush $parent_flow
  close_project
 }
 puts "PARENT_PHYSICAL_PAIR_DONE"
puts $parent_flow "PARENT_PHYSICAL_PAIR_DONE"
close $parent_flow
cd $parent_old_dir
