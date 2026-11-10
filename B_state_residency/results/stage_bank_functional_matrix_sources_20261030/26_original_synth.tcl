set_param general.maxThreads 2
if {[version -short] ne "2022.2"} {error "Expected2022.2"}
read_verilog -sv controller.sv
synth_design -mode out_of_context -top route_commit_controller -part xcu280-fsvh2892-2L-e -flatten_hierarchy rebuilt -generic MAX_PATH=32 -generic MAX_CYCLES=256 -generic PATH_SLOTS=4 -generic PATH_SLOT_BITS=2
create_clock -name core_clk -period 10.000 [get_ports clk]
write_checkpoint synth.dcp
write_verilog -mode funcsim functional.v
report_utilization -file utilization.rpt
puts STAGE_MATRIX_SYNTH_DONE
close_project
