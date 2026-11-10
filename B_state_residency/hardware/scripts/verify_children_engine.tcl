set b_root [file normalize [file join [file dirname [info script]] ../..]]
puts "CHILDREN_ENGINE_BEGIN version=[version -short]"
puts [exec python3 [file join $b_root scripts/run_children_engine.py] [file join $b_root results children_engine_20261024] 2>@1]
puts "CHILDREN_ENGINE_DONE"
