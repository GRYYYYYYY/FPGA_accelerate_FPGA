set b_root [file normalize [file join [file dirname [info script]] ../..]]
puts "FRONTIER_SERVICE_BEGIN version=[version -short]"
puts [exec /usr/bin/python3 -I [file join $b_root scripts/run_frontier_service.py] [file join $b_root results frontier_service_v2_20261024] 2>@1]
puts "FRONTIER_SERVICE_DONE"
