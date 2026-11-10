"""Freeze clock-shell inputs and emit a paired nonproject Vivado implementation."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import tempfile
from make_clock_shell import generate

ROOT = Path(__file__).resolve().parents[2]
COMMON = ['bounded_sync_fifo', 'scratch_frame_store_bram', 'scratch_page_controller',
          'queued_scratch_endpoint', 'scratch_page_axi', 'backing_frame_directory_lookup',
          'backing_page_service_lookup']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = Path(sys.argv[1]).resolve()
    sources = out / 'sources'
    sources.mkdir()
    names = [f'hardware/rtl/{name}.sv' for name in COMMON]
    for variant, suffix in [('baseline', ''), ('wide', '_wide')]:
        names += [f'hardware/rtl/{name}{suffix}.sv' for name in
                  ['scratch_page_codec', 'record_backing_service', 'memory_scratch_endpoint']]
        names += [f'hardware/rtl/clock_shell_{variant}.sv', f'hardware/tb/tb_clock_shell_{variant}.sv',
                  f'hardware/tb/tb_memory_endpoint{suffix}.sv']
    names += ['hardware/rtl/clock_shell.xdc', 'hardware/CLOCK_SHELL_CONTRACT.md',
              'hardware/scripts/make_clock_shell.py', 'hardware/scripts/prepare_clock_shell.py',
              'hardware/scripts/simulate_clock_shell.py']
    with tempfile.TemporaryDirectory() as tmp:
        generate(Path(tmp))
        for p in Path(tmp).rglob('*.sv'):
            if p.read_bytes() != (ROOT / p.relative_to(tmp)).read_bytes():
                raise ValueError('Generated wrapper/TB differs')
    files = {}
    for name in names:
        src = ROOT / name
        dst = sources / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        files[name] = sha(src)
    parents = {}
    for name in ['rtl_wide_codec_20261023/manifest.json', 'rtl_memory_endpoint_20261023/manifest.json',
                 'rtl_codec_timing_20261023/libc_batch/manifest.json']:
        path = ROOT / 'results' / name
        parents[str(path.relative_to(ROOT))] = sha(path)
    inputs = {'files': files, 'parents': parents, 'part': 'xcu280-fsvh2892-2L-e',
              'clock_period_ns': 10, 'input_delay_ns': {'min': 0.5, 'max': 2},
              'output_delay_ns': {'min': -0.5, 'max': 2}, 'reference_pin': 'b_clock/O'}
    (out / 'inputs.json').write_text(json.dumps(inputs, indent=2) + '\n')
    rtl = sources / 'hardware/rtl'
    lines = [f'set b_out {{{out}}}', f'set b_rtl {{{rtl}}}', 'set_param general.maxThreads 2',
             'puts "B_CLOCK_SHELL_BEGIN version=[version -short]"',
             'foreach {b_variant b_suffix} {baseline {} wide _wide} {',
             '    set b_dir [file join $b_out $b_variant]',
             '    if {[file exists $b_dir]} {error "Refuse overwrite $b_dir"}',
             '    file mkdir $b_dir',
             '    create_project -in_memory -part xcu280-fsvh2892-2L-e']
    lines += [f'    read_verilog -sv [file join $b_rtl {name}.sv]' for name in COMMON]
    lines += [f'    read_verilog -sv [file join $b_rtl {name}${{b_suffix}}.sv]' for name in
              ['scratch_page_codec', 'record_backing_service', 'memory_scratch_endpoint']]
    lines += ['    read_verilog -sv [file join $b_rtl clock_shell_${b_variant}.sv]',
              '    read_xdc [file join $b_rtl clock_shell.xdc]',
              '    synth_design -top clock_shell_${b_variant} -part xcu280-fsvh2892-2L-e -mode out_of_context',
              '    if {[llength [get_cells -hier -filter {REF_NAME =~ BUFG*}]] != 1} {error "Expected one BUFG"}',
              '    if {[llength [get_pins b_clock/O]] != 1} {error "Missing reference clock pin"}',
              '    write_checkpoint [file join $b_dir synthesized.dcp]',
              '    report_timing_summary -check_timing_verbose -report_unconstrained -max_paths 5 -file [file join $b_dir timing_synth.rpt]',
              '    opt_design', '    place_design -directive Default', '    route_design -directive Default',
              '    report_methodology -file [file join $b_dir methodology.rpt]',
              '    report_timing_summary -check_timing_verbose -report_unconstrained -max_paths 10 -file [file join $b_dir timing_routed.rpt]',
              '    report_route_status -file [file join $b_dir route_status.rpt]',
              '    report_drc -file [file join $b_dir drc.rpt]',
              '    report_clock_utilization -file [file join $b_dir clock_utilization.rpt]',
              '    report_utilization -file [file join $b_dir utilization.rpt]',
              '    write_xdc [file join $b_dir constraints.xdc]',
              '    write_checkpoint [file join $b_dir routed.dcp]',
              '    set b_file [open [file join $b_dir clock_network.tsv] w]',
              '    puts $b_file "buffer\ttype\tlocation\toutput_net\troute_status"',
              '    foreach b_buf [get_cells -hier -filter {REF_NAME =~ BUFG*}] {',
              '        set b_net [get_nets -of_objects [get_pins $b_buf/O]]',
              '        puts $b_file "$b_buf\t[get_property REF_NAME $b_buf]\t[get_property LOC $b_buf]\t$b_net\t[get_property ROUTE_STATUS $b_net]"',
              '    }', '    close $b_file',
              '    set b_in [get_ports -filter {DIRECTION == IN && NAME != clk}]',
              '    set b_outports [get_ports -filter {DIRECTION == OUT}]',
              '    set b_regs [all_registers]',
              '    set b_file [open [file join $b_dir paths.tsv] w]',
              '    puts $b_file "group\tdelay_type\tslack_ns\tstartpoint\tendpoint\tdatapath_delay_ns\trequirement_ns"',
              '    foreach b_group {internal input output feedthrough} {',
              '        switch $b_group {',
              '            internal {set b_from $b_regs; set b_to $b_regs}',
              '            input {set b_from $b_in; set b_to $b_regs}',
              '            output {set b_from $b_regs; set b_to $b_outports}',
              '            feedthrough {set b_from $b_in; set b_to $b_outports}',
              '        }',
              '        foreach b_delay {max min} {',
              '            report_timing -from $b_from -to $b_to -delay_type $b_delay -max_paths 5 -path_type full_clock_expanded -file [file join $b_dir ${b_group}_${b_delay}.rpt]',
              '            foreach b_path [get_timing_paths -from $b_from -to $b_to -delay_type $b_delay -max_paths 5] {',
              '                puts $b_file "$b_group\t$b_delay\t[get_property SLACK $b_path]\t[get_property STARTPOINT_PIN $b_path]\t[get_property ENDPOINT_PIN $b_path]\t[get_property DATAPATH_DELAY $b_path]\t[get_property REQUIREMENT $b_path]"',
              '            }', '        }', '    }', '    close $b_file',
              '    set b_file [open [file join $b_dir completed.txt] w]',
              '    puts $b_file "B_CLOCK_SHELL_VARIANT_DONE $b_variant version=[version -short]"',
              '    close $b_file', '    puts "B_CLOCK_SHELL_VARIANT_DONE $b_variant"',
              '    close_project', '}', 'puts "B_CLOCK_SHELL_PAIR_DONE"']
    (out / 'implement.tcl').write_text('\n'.join(lines) + '\n')
    print('Frozen', len(files), 'files; implementation script ready')


if __name__ == '__main__':
    main()
