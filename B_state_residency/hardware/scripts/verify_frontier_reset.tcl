set b_root [file normalize [file join [file dirname [info script]] ../..]]
puts "FRONTIER_RESET_BEGIN version=[version -short]"
puts [exec /usr/bin/python3 -I [file join $b_root scripts/verify_frontier_reset.py] [file join $b_root results frontier_reset_20261024] 2>@1]
puts "FRONTIER_RESET_DONE"
