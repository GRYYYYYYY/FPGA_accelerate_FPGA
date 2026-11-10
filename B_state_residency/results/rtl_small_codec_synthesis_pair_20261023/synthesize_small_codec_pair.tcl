set b_root [file normalize [file join [file dirname [info script]] ../..]]
set b_out [file join $b_root results rtl_small_codec_synthesis_pair_20261023]
set_param general.maxThreads 2
puts "SMALL_CODEC_PAIR_BEGIN version=[version -short]"
foreach b_top {scratch_page_codec_small scratch_page_codec_small_static} {
    set b_dir [file join $b_out $b_top]
    file mkdir $b_dir
    create_project -in_memory -part xcu280-fsvh2892-2L-e
    read_verilog -sv [file join $b_out sources ${b_top}.sv]
    read_xdc [file join $b_out research_clock.xdc]
    synth_design -top $b_top -part xcu280-fsvh2892-2L-e -mode out_of_context
    report_utilization -file [file join $b_dir utilization.rpt]
    write_checkpoint -force [file join $b_dir ${b_top}.dcp]
    close_project
}
set b_f [open [file join $b_out completed.txt] w]
puts $b_f "SMALL_CODEC_PAIR_DONE version=[version -short]"
close $b_f
puts "SMALL_CODEC_PAIR_DONE"
