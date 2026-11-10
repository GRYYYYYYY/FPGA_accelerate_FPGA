open_vcd debug.vcd
log_vcd [get_objects /tb_exclusion_hls_call/*]
log_vcd [get_objects /tb_exclusion_hls_call/dut/*]
run 1ms
close_vcd
quit
