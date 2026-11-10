set b_root [file normalize [file join [file dirname [info script]] ../..]]
puts "EXCLUSION_LABEL_BEGIN version=[version -short]"
puts [exec python3 [file join $b_root scripts/run_exclusion_label_adapter.py] [file join $b_root results/exclusion_label_adapter_20261024] 2>@1]
puts "EXCLUSION_LABEL_END"
