set b_root [file normalize [file join [file dirname [info script]] ../..]]
puts "AUTO_PAGER_BEGIN version=[version -short]"
puts [exec python3 [file join $b_root scripts/run_auto_pager.py] [file join $b_root results/auto_pager_20261024] 2>@1]
puts "AUTO_PAGER_END"
