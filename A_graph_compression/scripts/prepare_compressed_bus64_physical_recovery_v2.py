#!/usr/bin/env python3
"""Freeze an independent recovery trial; require serialized full-batch acceptance."""
import json
import os
import shutil
from pathlib import Path
from check_vitis_kernel import digest,require
from supervise_search_axi_dpi_v3 import atomic,identity

ROOT=Path(__file__).resolve().parents[1]
def main():
    old=ROOT/'data/derived/compressed_batch_bus64_physical_20261025_v1'
    original=json.loads((old/'plan.json').read_text())
    incident=ROOT/'results/compressed_bus64_physical_resource_abort_20261025_v1.json'
    abort=json.loads(incident.read_text())
    require(abort['status']=='owned_incomplete_physical_trial_resource_aborted_process_absence_verified','Original resource incident not reconciled')
    require(identity(1924562) is None,'Original physical process still exists')
    for group in ['inputs','generated']:
        for p,h in original[group].items():require(digest(p)==h,'Changed frozen physical input '+p)
    out=ROOT/'data/derived/compressed_batch_bus64_physical_recovery_20261025_v2'
    out.mkdir(exist_ok=False);work=out/'csr';work.mkdir()
    shutil.copytree(old/'csr/source',work/'source')
    shutil.copyfile(old/'csr/clock.xdc',work/'clock.xdc')
    blockers=[]
    for pid in [2508987,1504642,196239,247521,731182]:
        who=identity(pid);require(who is not None,'Expected current workflow owner missing; reconcile before preparing recovery');blockers.append(who)
    # Admission checks precede state creation so a premature source never claims to run.
    prefix='''# Recovery admission: no concurrent original full-depth workflows.
proc a_read_admission_file {path} {set f [open $path r]; set value [read $f]; close $f; return [string trim $value]}
'''
    for b in blockers:
        prefix+='if {[file exists /proc/'+str(b['pid'])+'/stat]} {\n'
        prefix+='  set a_stat [a_read_admission_file /proc/'+str(b['pid'])+'/stat]\n'
        prefix+='  set a_fields [split [string range $a_stat [expr {[string last ")" $a_stat]+2}] end]]\n'
        prefix+='  if {[lindex $a_fields 19] eq "'+str(b['start_ticks'])+'"} {error "Original workflow still live: '+str(b['pid'])+'"}\n}\n'
    gate=ROOT/'results/compressed_bus64_dpi_rtl_audit_20261025_v1.json'
    prefix+='if {![file exists {'+str(gate)+'}]} {error "Full44 independent functional audit required before physical recovery"}\n'
    prefix+='if {![string match {*"status": "compressed_bus64_full44_four_transaction_dpi_rtl_c_postcheck_and_complete_snapshots_independently_verified"*} [a_read_admission_file {'+str(gate)+'}]]} {error "Full44 functional audit not accepted"}\n'
    prefix+='if {[expr {[a_read_admission_file /sys/fs/cgroup/memory.max]-[a_read_admission_file /sys/fs/cgroup/memory.current]}] < 197568495616} {error "Physical recovery requires184GiB raw cgroup headroom"}\n'
    (work/'run_flow.tcl').write_text(prefix+(old/'csr/run_flow.tcl').read_text())
    generated={str(p):digest(p) for p in (work/'source').iterdir() if p.is_file()}
    for name in ['clock.xdc','run_flow.tcl']:generated[str(work/name)]=digest(work/name)
    require(len(list((work/'source').glob('*.v')))==original['source_rtl_files'],'Different source matrix')
    for p in (work/'source').iterdir():require(digest(p)==original['generated'][str(old/'csr/source'/p.name)],'Changed recovery RTL/ROM')
    inputs={**original['inputs'],str(old/'plan.json'):digest(old/'plan.json'),str(incident):digest(incident),str(Path(__file__).resolve()):digest(Path(__file__).resolve())}
    atomic(out/'plan.json',dict(status='independent_physical_recovery_prepared_not_started',inputs=inputs,generated=generated,
        source_rtl_files=original['source_rtl_files'],top=original['top'],part=original['part'],clock_ns=5,setup_uncertainty_ns=1.35,max_threads=2,
        blockers=blockers,functional_gate=str(gate),minimum_raw_free_bytes=184*1024**3,
        limits=['No Vivado session started or source executed','Same RTL/ROM/constraints and original physical flow after stronger admission prelude','A new terminal source receipt, full reports and independent physical audit remain required']))
    print(out/'plan.json')
if __name__=='__main__':main()
