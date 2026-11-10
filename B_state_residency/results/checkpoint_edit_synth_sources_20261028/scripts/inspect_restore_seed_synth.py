"""Reopen a terminal OOC checkpoint for read-only Vivado 2022.2 diagnostics.

Produces observations, never declares design acceptance. Does not change the
original synthesis root's source, constraints, checkpoint or manifest. Refuses
to overwrite a previous diagnostic run. Run one root at a time to bound memory.
"""
from pathlib import Path
import json, subprocess, sys, time
from run_checkpoint_authority import sha

p=Path(sys.argv[1]).resolve()
m=json.loads((p/'manifest.json').read_text())
assert m['status']=='observed' and m['exit_code']==0, 'synthesis must be terminal'
assert 'RESTORE_SEED_OOC_DONE' in (p/'vivado.log').read_text()
for name in ['synth.dcp','synth.tcl','clock.xdc']:
    assert (p/name).is_file() and (p/name).stat().st_size>0
out=p/'results'/'methodology_v1'
out.mkdir(parents=True,exist_ok=False)
(out/'runner.py').write_bytes(Path(__file__).read_bytes())
# All paths are local experiment paths, Tcl-braced without substitution.
def path(name):
    value=str(out/name)
    assert not any(c in value for c in '{}\n\r')
    return '{'+value+'}'
assert not any(c in str(p) for c in '{}\n\r')
tcl='set_param general.maxThreads 2\nputs [list VIVADO_VERSION [version -short]]\n'
tcl+='open_checkpoint {'+str(p/'synth.dcp')+'}\n'
tcl+='write_xdc -force -exclude_physical '+path('effective.xdc')+'\n'
tcl+='report_methodology -no_waivers -file '+path('methodology.rpt')+'\n'
tcl+='''proc dump_objects {objects filename} {
 set f [open $filename w]
 foreach obj $objects {
  puts $f [list OBJECT $obj]
  foreach prop [lsort [list_property $obj]] {
   puts $f [list PROPERTY $prop [get_property $prop $obj]]
  }
 }
 close $f
}
'''
tcl+='dump_objects [get_methodology_violations] '+path('methodology_objects.tcllist')+'\n'
tcl+='set loop_checks [get_drc_checks LUTLP-1]\nif {[llength $loop_checks] != 1} {error "LUTLP-1 unavailable"}\n'
tcl+='report_drc -no_waivers -checks $loop_checks -file '+path('loops.rpt')+'\n'
tcl+='dump_objects [get_drc_violations] '+path('loop_objects.tcllist')+'\n'
tcl+='set f [open '+path('loop_elements.tcllist')+' w]\n'
tcl+='''foreach v [get_drc_violations] {
 puts $f [list VIOLATION $v]
 puts $f [list CELLS [get_cells -quiet -of_objects $v]]
 puts $f [list NETS [get_nets -quiet -of_objects $v]]
 puts $f [list PINS [get_pins -quiet -of_objects $v]]
}
close $f
'''
tcl+='check_timing -verbose -file '+path('check_timing.rpt')+'\n'
tcl+='report_clocks -file '+path('clocks.rpt')+'\n'
tcl+='dump_objects [get_timing_paths -delay_type max -max_paths 10 -nworst 1] '+path('timing_path_objects.tcllist')+'\n'
tcl+='puts RESTORE_SEED_DIAGNOSTICS_DONE\n'
(out/'inspect.tcl').write_text(tcl)
inputs={name:sha(p/name)for name in ['manifest.json','synth.dcp','synth.tcl','clock.xdc','vivado.log']}
argv=['/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin/vivado',
      '-mode','batch','-source',str(out/'inspect.tcl'),'-log',str(out/'vivado.log'),'-journal',str(out/'vivado.jou')]
record=dict(status='running',source_root=str(p),input_sha256=inputs,command=argv,
            runner_sha256=sha(out/'runner.py'),tcl_sha256=sha(out/'inspect.tcl'),
            design_acceptance='unresolved',timing_qualified=False,
            scope='Read-only synthesized checkpoint diagnostics with no waivers and no new timing exceptions; command completion does not mean checks pass.')
def save():
    (out/'manifest.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
save();start=time.monotonic()
try:
    with (out/'stdout.log').open('w') as f:
        r=subprocess.run(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=1800)
    record['exit_code']=r.returncode
    assert r.returncode==0,'Vivado command failed; retain original evidence'
    log=(out/'vivado.log').read_text()
    assert 'VIVADO_VERSION 2022.2' in log and 'RESTORE_SEED_DIAGNOSTICS_DONE' in log
    for name in ['effective.xdc','methodology.rpt','methodology_objects.tcllist',
                 'loops.rpt','loop_objects.tcllist','loop_elements.tcllist',
                 'check_timing.rpt','clocks.rpt','timing_path_objects.tcllist']:
        assert (out/name).is_file(),name
    for name,h in inputs.items():
        assert sha(p/name)==h, 'diagnosis changed input: '+name
    record.update(status='observed',artifacts={f.name:sha(f)for f in sorted(out.iterdir())if f.is_file()and f.name!='manifest.json'})
except Exception as error:
    record.update(status='failed',error=repr(error));raise
finally:
    record['elapsed_s']=time.monotonic()-start;save()
print('RESTORE_SEED_DIAGNOSTICS_OBSERVED',out)
