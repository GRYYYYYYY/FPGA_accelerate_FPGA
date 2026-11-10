set b_root [file normalize [file join [file dirname [info script]] ../..]]
puts "DESIGN_STORE_BEGIN version=[version -short]"
puts [exec python3 [file join $b_root scripts/run_design_store_v2.py] [file join $b_root results design_store_v2_20261024] 2>@1]
puts "DESIGN_STORE_DONE"
