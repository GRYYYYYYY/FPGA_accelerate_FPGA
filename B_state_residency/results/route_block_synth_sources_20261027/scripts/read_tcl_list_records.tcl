# Parse tool-produced Tcl lists as data. Never evaluate a record as Tcl code.
set f [open [lindex $argv 0] r]
set record ""
while {[gets $f line] >= 0} {
 append record $line "\n"
 if {![info complete $record]} {continue}
 set fields $record
 if {[llength $fields] == 0} {set record "";continue}
 if {[lindex $fields 0] in {CELLS NETS PINS}} {
  if {[llength $fields] != 2} {error "invalid element record"}
  set fields [linsert [lindex $fields 1] 0 [lindex $fields 0]]
 }
 set encoded {}
 foreach field $fields {
  lappend encoded [binary encode hex [encoding convertto utf-8 $field]]
 }
 puts [join $encoded "\t"]
 set record ""
}
close $f
if {[string trim $record] ne ""} {error "incomplete record"}
