"""Non-project batch synthesis after two reproducible MCP launch_runs aborts.

Reads already-frozen sources. Does not resubmit or touch any existing synth run.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=Path(sys.argv[1]).resolve();d=out/'synthesis';d.mkdir()
    sources=json.loads((out/'source_manifest.json').read_text())
    for name,h in sources['files'].items():
        snap=out/'sources'/Path(name).relative_to(ROOT)
        if sha(name)!=h or sha(snap)!=h:raise ValueError('Frozen source changed')
    rtl=out/'sources/hardware/rtl'
    lines=['set_param general.maxThreads 2']
    lines += [f'read_verilog -sv {{{rtl/name}}}' for name in ('bounded_sync_fifo.sv','scratch_frame_store_bram.sv','scratch_page_controller.sv','queued_scratch_endpoint.sv')]
    lines += [f'read_xdc {{{rtl/"scratch_frame_store.xdc"}}}',
        'synth_design -top queued_scratch_endpoint -part xcu280-fsvh2892-2L-e -mode out_of_context',
        'report_utilization -file utilization.rpt','write_checkpoint queued_scratch_endpoint.dcp',
        'set b_rams [get_cells -hier -filter {REF_NAME =~ RAMB*}]',
        'set b_file [open ram_cells.txt w]',
        'foreach b_cell $b_rams {puts $b_file "$b_cell [get_property REF_NAME $b_cell]"}',
        'close $b_file','if {[llength $b_rams] != 2} {error "Expected two page block RAMs"}',
        'puts "B_QUEUED_SYNTH_PASS ram_cells=[llength $b_rams]"','exit']
    tcl=d/'synthesize.tcl';tcl.write_text('\n'.join(lines)+'\n')
    cmd=['/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin/vivado','-mode','batch','-source',str(tcl),'-log','synthesize.log','-journal','synthesize.jou']
    record=dict(status='running',command=cmd,driver_sha256=sha(__file__),tcl_sha256=sha(tcl))
    (d/'receipt.json').write_text(json.dumps(record,indent=2)+'\n')
    with (d/'console.log').open('w') as log:r=subprocess.run(cmd,cwd=d,stdout=log,stderr=subprocess.STDOUT)
    record.update(status='exited',exit_code=r.returncode)
    (d/'receipt.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
    raise SystemExit(r.returncode)
if __name__=='__main__':main()
