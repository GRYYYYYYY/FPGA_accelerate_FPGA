set b_root [file normalize [file join [file dirname [info script]] ../..]]
puts "COST_SERVICE_BEGIN version=[version -short]"
puts [exec /usr/bin/python3 -I [file join $b_root scripts/run_cost_service.py] [file join $b_root results cost_service_20261024] 2>@1]
puts "COST_SERVICE_DONE"
