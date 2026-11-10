"""Prepare an additive, delayed full-port shadow checker; no simulation launch.

Requires a namespaced netlist top macro at compile time. The host RTL keeps
driving all original agents and running every original internal assertion.
"""
import json
from host_edit_system_common_v1 import ROOT, BASE, read, sha


def render(schema):
    ports = schema['ports']
    assert len(ports) == 563
    assert {p['name'] for p in ports if p['direction'] == 'input'} >= {'clk', 'k_cold_rst'}
    lines = ['`timescale 1ns/1ps', '`default_nettype none',
             'module stage_static_cp_shadow;',
             'localparam integer SHIFT_NS=200;',
             'integer checks=0,reset_edges=0;',
             'time last_checked=0;', 'reg armed=0;',
             '// Nonblocking delayed assignments preserve every transition (transport).']
    for p in ports:
        name, width = p['name'], p['width']
        packed = '' if width == 1 else f'[{width-1}:0] '
        reference = f'tb_candidate_offer.system.{name}'
        if p['direction'] == 'input':
            lines += [f'reg {packed}drive_{name};',
                      f'initial drive_{name} <= #SHIFT_NS {reference};',
                      f'always @({reference}) drive_{name} <= #SHIFT_NS {reference};']
        else:
            lines += [f'wire {packed}actual_{name};', f'reg {packed}expected_{name};',
                      f'initial expected_{name} <= #SHIFT_NS {reference};',
                      f'always @({reference}) expected_{name} <= #SHIFT_NS {reference};']
    lines += ['`SHADOW_NETLIST_TOP shadow_dut (']
    lines += [f" .{p['name']}({'drive_' if p['direction']=='input' else 'actual_'}{p['name']})" +
              (',' if i < len(ports)-1 else '') for i, p in enumerate(ports)]
    lines += [');',
              'always @(posedge drive_clk) begin',
              " if(drive_k_cold_rst===1'b1)reset_edges=reset_edges+1;",
              " else if(drive_k_cold_rst===1'b0&&reset_edges>=5)armed=1;",
              'end',
              'always @(posedge drive_clk or negedge drive_clk) begin',
              ' #1;', ' if(armed)begin', '  checks=checks+1;last_checked=$time;']
    for p in ports:
        if p['direction'] == 'output':
            n = p['name']
            lines += [f'  if(actual_{n}!==expected_{n})',
                      f'   $fatal(1,"FULL_SHADOW_MISMATCH port={n} time=%0t actual=%h expected=%h",$time,actual_{n},expected_{n});']
    lines += [' end', 'end',
              '// Call only at the original normal terminal point, before $finish.',
              'task finish_and_check;', 'time original_end;', 'begin',
              ' original_end=$time;', ' #(SHIFT_NS+2);',
              ' if(!armed||reset_edges<5||checks==0||last_checked<original_end+SHIFT_NS-5)',
              '  $fatal(1,"FULL_SHADOW_INCOMPLETE reset=%0d checks=%0d last=%0t end=%0t",reset_edges,checks,last_checked,original_end);',
              ' $display("FULL_SHADOW_PASS outputs=346 bits=14384 checks=%0d reset_edges=%0d original_end=%0t last_checked=%0t",checks,reset_edges,original_end,last_checked);',
              'end endtask',
              'initial begin #100000000; $fatal(1,"FULL_SHADOW_WATCHDOG"); end',
              'endmodule', '`default_nettype wire']
    return '\n'.join(lines) + '\n'


def main():
    receipt = ROOT / 'results/stage_static_cp_port_schema_20261030.json'
    schema = read(receipt)
    assert sha(schema['source']) == schema['source_sha256']
    assert sha(schema['host_tb']) == schema['host_tb_sha256']
    original = BASE / 'stage_static_cp_system_v1/sources/tb_query_fault.sv'
    tb = original.read_text()
    # Only the known successful host terminal point gets a drain. Negative-case
    # terminal branches are untouched and can never emit FULL_SHADOW_PASS.
    marker = '$display("ITER2_CONTINUOUS_PREP_PASS");$finish;'
    assert tb.count(marker) == 1
    updated = tb.replace(marker, '$display("ITER2_CONTINUOUS_PREP_PASS");stage_static_cp_shadow.finish_and_check;$finish;')
    assert updated.replace('stage_static_cp_shadow.finish_and_check;', '') == tb
    out = ROOT / 'hardware/variants/stage_static_cp_shadow_v1'
    assert not out.exists()
    out.mkdir()
    (out / 'shadow.sv').write_text(render(schema))
    (out / 'tb_query_fault.sv').write_text(updated)
    report = dict(status='full_port_shadow_prepared_not_compiled_or_simulated',
                  source_tb=str(original), source_tb_sha256=sha(original),
                  schema_sha256=sha(receipt), generator_sha256=sha(__file__),
                  outputs=346, output_bits=14384, inputs=217, input_bits=49253,
                  transport_shift_ns=200, all_original_stimuli_and_assertions_retained=True,
                  strict_four_state_output_comparison=True, valid_masks=False,
                  files={n:sha(out/n) for n in ['shadow.sv','tb_query_fault.sv']},
                  full_system_functional_netlist_validated=False,
                  scope='Proposed full host-driven shadow test. Strict all-output/XZ comparison may reveal differences requiring diagnosis; do not mask to manufacture PASS. Needs actual completed namespaced static-stage netlist, original vendor glbl, compile/elaboration, timing controls and full audited run.')
    (out / 'manifest.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    result = ROOT / 'results/stage_static_cp_shadow_preparation_20261030.json'
    assert not result.exists()
    result.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print('FULL_PORT_SHADOW_PREPARED', len(schema['ports']))


if __name__ == '__main__':
    main()
