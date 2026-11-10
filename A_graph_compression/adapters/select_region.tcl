# Geometry-only selection. Never queries PIPs, route strings or downhill edges.
namespace eval independent_region {
    proc row {stream args} {puts $stream [join $args "\t"]}
    proc select {site_file directory margin max_sources} {
        if {[file exists $directory]} {error "Refusing existing selection directory"}
        if {[get_property PART [current_design]] ne "xcu280-fsvh2892-2L-e"} {error "Wrong device"}
        file mkdir $directory
        set f [open $site_file];set site_names [split [string trim [read $f]] \n];close $f
        set sites [get_sites $site_names]
        if {[lsort -unique [get_property NAME $sites]] ne [lsort -unique $site_names]} {error "Missing/ambiguous endpoint sites"}
        set endpoint_tiles [get_tiles -of_objects $sites]
        set xs [lsort -integer [get_property COLUMN $endpoint_tiles]]
        set ys [lsort -integer [get_property ROW $endpoint_tiles]]
        set xmin [expr {[lindex $xs 0]-$margin}];set xmax [expr {[lindex $xs end]+$margin}]
        set ymin [expr {[lindex $ys 0]-$margin}];set ymax [expr {[lindex $ys end]+$margin}]
        set filter [format {COLUMN >= %d && COLUMN <= %d && ROW >= %d && ROW <= %d} $xmin $xmax $ymin $ymax]
        set tiles [get_tiles -filter $filter]
        set names [lsort -unique [get_property NAME $tiles]]
        set meta [open [file join $directory metadata.tsv] {WRONLY CREAT EXCL}]
        row $meta schema independent_region_selection_v1
        row $meta part [get_property PART [current_design]]
        row $meta tool [version -short]
        row $meta bbox $xmin $xmax $ymin $ymax
        row $meta endpoint_sites [llength $sites]
        row $meta selected_tiles [llength $names]
        set f [open [file join $directory tiles.txt] {WRONLY CREAT EXCL}]
        puts $f [join $names \n];close $f
        puts "REGION_SELECT_ENUMERATING tiles=[llength $names] bbox=$xmin,$xmax,$ymin,$ymax"
        set roots [lsort -unique [get_property NAME [get_nodes -of_objects $tiles]]]
        set f [open [file join $directory roots.txt] {WRONLY CREAT EXCL}]
        puts $f [join $roots \n];close $f
        row $meta selected_sources [llength $roots]
        if {[llength $roots]>$max_sources} {
            row $meta status source_budget_exceeded;close $meta
            error "Selected source budget exceeded; no clipping allowed"
        }
        row $meta status complete;close $meta
        puts "REGION_SELECTION_COMPLETE tiles=[llength $names] roots=[llength $roots] bbox=$xmin,$xmax,$ymin,$ymax"
    }
}
