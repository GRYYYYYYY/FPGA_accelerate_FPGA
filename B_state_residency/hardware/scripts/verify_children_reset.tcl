set b_root [file normalize [file join [file dirname [info script]] ../..]]
puts [exec python3 [file join $b_root scripts/audit_children_hls.py] 2>@1]
puts "CHILDREN_RESET_BEGIN version=[version -short]"
puts [exec python3 [file join $b_root scripts/verify_children_reset.py] [file join $b_root results children_reset_20261024] [file join $b_root results children_hls_20261024] 2>@1]
puts "CHILDREN_RESET_DONE"
