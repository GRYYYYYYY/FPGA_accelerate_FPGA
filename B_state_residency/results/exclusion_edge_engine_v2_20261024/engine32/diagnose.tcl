run 60ms
foreach n {edges error_mode errors_tested checks hls_calls responses edge_index k rst bridge_mode hold_native hold_reply ep_valid ep_ready fault result_valid edge_valid edge_ready resolve_valid map_valid active_edge} {puts "STATE $n=[get_value -radix unsigned /tb_exclusion_edge_engine/$n]"}
foreach n {controller/state controller/stopped calls/state calls/stopped labels/state labels/stopped} {puts "STATE dut/$n=[get_value -radix unsigned /tb_exclusion_edge_engine/dut/$n]"}
quit
