
set_param general.maxThreads 2
if {[version -short] ne "2022.2"} {error "Expected Vivado 2022.2"}
open_checkpoint {/tmp/B_state_residency_offer_20261025/config_native_publication_physical_v1/routed.dcp}
set wanted {inner/backend/route_join/controller/cp_stage[154][31]_i_1_n_9}
set selected {}
foreach n [get_nets -hier -filter {NAME =~ *cp_stage*}] {
 if {[get_property NAME $n] eq $wanted} {lappend selected $n}
}
if {[llength $selected]!=1} {error "Expected exactly one reported net"}
set f [open connectivity.tcllist w]
set pins [get_pins -leaf -of_objects $selected]
puts $f [list NET $wanted PINS [llength $pins]]
set drivers {}
foreach pin $pins {
 set cell [get_cells -of_objects $pin]
 puts $f [list PIN [get_property NAME $pin] DIRECTION [get_property DIRECTION $pin] REF_PIN [get_property REF_PIN_NAME $pin] CELL [get_property NAME $cell] REF [get_property REF_NAME $cell]]
 if {[get_property DIRECTION $pin] eq "OUT"} {lappend drivers $cell}
}
set frontier $drivers
for {set depth 0} {$depth<3} {incr depth} {
 set next {}
 foreach cell [lsort -unique $frontier] {
  set init {}
  if {[lsearch -exact [list_property $cell] INIT]>=0} {set init [get_property INIT $cell]}
  puts $f [list DRIVER $depth [get_property NAME $cell] REF [get_property REF_NAME $cell] INIT $init]
  foreach pin [get_pins -of_objects $cell -filter {DIRECTION == IN}] {
   set nets [get_nets -of_objects $pin]
   puts $f [list INPUT $depth [get_property NAME $pin] NETS $nets]
   foreach up [get_pins -leaf -of_objects $nets -filter {DIRECTION == OUT}] {
    set uc [get_cells -of_objects $up]
    puts $f [list UPSTREAM $depth [get_property NAME $up] REF [get_property REF_NAME $uc]]
    if {[string match LUT* [get_property REF_NAME $uc]]} {lappend next $uc}
   }
  }
 }
 set frontier $next
}
close $f
puts NATIVE_STAGE_CE_CONNECTIVITY_DONE
close_project
