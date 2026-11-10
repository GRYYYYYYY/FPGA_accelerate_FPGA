"""Read-only routed net connectivity measurement, with no timing/source edits."""
from pathlib import Path
import json
import os
import subprocess
import time
from host_edit_system_common_v1 import ROOT, BASE, read, sha, restored, identity, verify_freeze
from config_native_publication_synth_common_v1 import BIN, runtime_environment, memory_admission, wait_preserving

TCL = r'''
set_param general.maxThreads 2
if {[version -short] ne "2022.2"} {error "Expected Vivado 2022.2"}
open_checkpoint {@DCP@}
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
'''


def main():
    accepted = ROOT/'results/config_native_publication_physical_20261030.json'
    assert read(accepted)['status'] == 'fresh_native_physical_artifacts_actual_restored'
    verify_freeze(ROOT/'results/config_native_publication_physical_sources_20261030')
    source = BASE/'config_native_publication_physical_v1'
    m, a, files = restored(source)
    assert a['independent_reopened_dcp_matches']
    dcp = source/'routed.dcp'
    assert sha(dcp) == a['artifact_sha256']['routed.dcp']
    out = BASE/'native_stage_ce_connectivity_v1'
    assert not out.exists()
    env, runtime = runtime_environment()
    out.mkdir()
    script = out/'inspect.tcl'
    script.write_text(TCL.replace('@DCP@', str(dcp)))
    record = dict(status='running', stage='wait_memory', source_root=str(source),
        runner_pid=os.getpid(), runner_start_ticks=identity(os.getpid()),
        runner_sha256=sha(Path(__file__)), tcl_sha256=sha(script), dcp_sha256=sha(dcp),
        source_audit_sha256=sha(source/'source_bound_audit.json'), runtime=runtime)
    def save():
        tmp = out/'manifest.pending.json'
        tmp.write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
        tmp.replace(out/'manifest.json')
    save()
    start = time.monotonic()
    try:
        memory_admission(record, save)
        assert runtime_environment()[1] == runtime
        argv = [str(BIN), '-mode', 'batch', '-source', str(script),
                '-log', str(out/'vivado.log'), '-journal', str(out/'vivado.jou')]
        record.update(stage='connectivity_query', command=argv)
        with (out/'stdout.log').open('w') as log:
            child = subprocess.Popen(argv, cwd=out, env=env, stdout=log, stderr=subprocess.STDOUT)
            record['active_process'] = dict(pid=child.pid, start_ticks=identity(child.pid))
            save()
            code = wait_preserving(child, 3600, record, save)
        record.pop('active_process', None)
        record['exit_code'] = code
        assert code == 0
        assert 'NATIVE_STAGE_CE_CONNECTIVITY_DONE' in (out/'stdout.log').read_text()
        assert sha(dcp) == record['dcp_sha256']
        record.update(status='observed', stage='complete',
            artifact_sha256={n: sha(out/n) for n in ['inspect.tcl', 'connectivity.tcllist', 'stdout.log', 'vivado.log', 'vivado.jou']})
    except Exception as error:
        record.update(status='failed', error=repr(error))
        raise
    finally:
        record['elapsed_s'] = time.monotonic()-start
        save()
    print('NATIVE_STAGE_CE_CONNECTIVITY_OBSERVED')


if __name__ == '__main__': main()
