foreach p [list_param] {if {[regexp -nocase {webtalk|telemetry|hostinfo|registration|licens} $p]} {puts "$p = [get_param $p]"; report_param $p}}
exit
