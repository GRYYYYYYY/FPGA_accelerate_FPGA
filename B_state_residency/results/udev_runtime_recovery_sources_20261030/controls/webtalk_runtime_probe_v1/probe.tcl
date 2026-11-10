# Read and probe process-local WebTalk parameters; do not alter user/install preferences.
if {[version -short] ne "2022.2"} {error "Expected Vivado 2022.2"}
puts "PROBE_VERSION [version -short]"
config_webtalk -info
set probe_names {}
foreach probe_name [list_param] {
    if {[string match -nocase *webtalk* $probe_name]} {
        lappend probe_names $probe_name
        puts "PROBE_PARAM $probe_name=[get_param $probe_name]"
    }
}
foreach probe_name {webtalk.disableTransmit webtalk.disableBeta general.enableWebtalk} {
    if {[lsearch -exact $probe_names $probe_name] >= 0} {
        report_param $probe_name
        set probe_previous [get_param $probe_name]
        set_param $probe_name true
        puts "PROBE_SET $probe_name=[get_param $probe_name]"
        set_param $probe_name $probe_previous
        puts "PROBE_RESET $probe_name=[get_param $probe_name]"
    } else {
        puts "PROBE_NOT_LISTED $probe_name"
    }
}
puts PROBE_WEBTALK_DONE
