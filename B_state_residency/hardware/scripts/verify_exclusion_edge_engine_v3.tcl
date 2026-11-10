set b_root [file normalize [file join [file dirname [info script]] ../..]]
puts "EXCLUSION_ENGINE_BEGIN version=[version -short]"
puts [exec python3 [file join $b_root scripts/run_exclusion_edge_engine_v3.py] [file join $b_root results/exclusion_edge_engine_v3_20261024] 2>@1]
puts "EXCLUSION_ENGINE_END"
