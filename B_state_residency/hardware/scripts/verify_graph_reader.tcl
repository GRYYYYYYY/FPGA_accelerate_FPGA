set b_root [file normalize [file join [file dirname [info script]] ../..]]
puts "GRAPH_READER_BEGIN version=[version -short]"
puts [exec python3 [file join $b_root scripts/run_graph_reader.py] [file join $b_root results graph_reader_20261024] 2>@1]
puts "GRAPH_READER_DONE"
