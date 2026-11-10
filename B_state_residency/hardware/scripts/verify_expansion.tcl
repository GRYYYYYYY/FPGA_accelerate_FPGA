set b_root [file normalize [file join [file dirname [info script]] ../..]]
puts "EXPANSION_BEGIN version=[version -short]"
puts [exec python3 [file join $b_root scripts/run_expansion.py] [file join $b_root results expansion_20261024] 2>@1]
puts "EXPANSION_DONE"
