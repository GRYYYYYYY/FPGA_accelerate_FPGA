"""Bind the existing module physical flow and the restored full-system timing anchor."""
from pathlib import Path
import json
from run_checkpoint_authority import ROOT, sha

base = Path('/tmp/B_state_residency_offer_20261025')
module = base/'parent_physical_v2'
summary_path = ROOT/'results/parent_physical_20261025.json'
summary = json.loads(summary_path.read_text())
mm = json.loads((module/'manifest.json').read_text())
ma = json.loads((module/'source_bound_audit.json').read_text())
assert mm['status'] == ma['status'] == summary['status'] == 'passed'
assert ma['manifest_sha256'] == sha(module/'manifest.json')
assert summary['audit_sha256'] == sha(module/'source_bound_audit.json')
assert summary['cases'] == ma['cases'] and summary['delta'] == ma['delta']
assert mm['top'] == 'postprev_inputs'
for name in ['baseline', 'cached']:
    for file in ['route_status.rpt', 'timing_routed.rpt', 'constraints_routed.xdc',
                 'methodology_routed.rpt', 'utilization_routed.rpt']:
        relative = f'{name}/{file}'
        assert sha(module/relative) == mm['artifacts'][relative], relative
    assert ma['cases'][name]['route']['nets with routing errors'] == 0

anchor = base/'checkpoint_edit_synth_v1'
am = json.loads((anchor/'manifest.json').read_text())
aa = json.loads((anchor/'source_bound_audit.json').read_text())
receipt_path = ROOT/'results/checkpoint_edit_synth_v1_restore_20261025.json'
receipt = json.loads(receipt_path.read_text())
assert am['status'] == 'observed' and am['exit_code'] == 0
assert aa['status'] == receipt['status'] == 'passed' and receipt['audit_byte_identical']
assert aa['manifest_sha256'] == sha(anchor/'manifest.json')
assert receipt['audit_sha256'] == sha(anchor/'source_bound_audit.json')
assert aa['check_timing_counts']['loops'] == 0 and not aa['timing_loop_warnings']
assert not aa['critical_warnings']
assert len(am['rtl']) == 133 and am['part'] == mm['part']
assert (anchor/'clock.xdc').read_text() == 'create_clock -name core_clk -period 10.000 [get_ports clk]\n'
assert sha(anchor/'synth.dcp') == aa['artifact_sha256']['synth.dcp']
for name in am['rtl']:
    assert sha(anchor/'sources'/name) == am['sources'][name], name

template = ROOT/'hardware/scripts/implement_parent_pair.tcl'
text = template.read_text()
assert 'opt_design\n' in text
assert 'place_design -directive Default' in text and 'route_design -directive Default' in text
assert '-mode out_of_context' in text and 'set_param general.maxThreads 2' in text
assert not any(cmd in text for cmd in ['set_false_path', 'set_input_delay', 'set_output_delay', 'HD.CLK_SRC'])
record = dict(
    status='source_bound_readiness_observation_no_full_system_physical_run',
    analyzer_sha256=sha(Path(__file__)),
    existing_module_flow=dict(top=mm['top'], part=mm['part'], period_ns=mm['period_ns'],
        summary_sha256=sha(summary_path), audit_sha256=sha(module/'source_bound_audit.json'),
        template_sha256=sha(template), current_template_matches_executed_script=(
            text.replace('@OUT@', str(module)) == (module/'run.tcl').read_text()),
        routed_observations={name:dict(
            wns_ns=ma['cases'][name]['reported_WNS_ns'],
            whs_ns=ma['cases'][name]['reported_WHS_ns'],
            unconstrained_IO=ma['cases'][name]['unconstrained_IO_checks'])
            for name in ['baseline','cached']}),
    full_system_anchor=dict(name=anchor.name, part=am['part'], production_sources=133,
        manifest_sha256=sha(anchor/'manifest.json'), audit_sha256=sha(anchor/'source_bound_audit.json'),
        restoration_sha256=sha(receipt_path), dcp_sha256=sha(anchor/'synth.dcp'),
        xdc_sha256=sha(anchor/'clock.xdc'), clock_period_ns=10,
        preplacement_wns_ns=aa['preplacement_wns_ns'],
        port_bits=aa['facts']['port_bits'], timing_checks=aa['check_timing_counts']),
    proposed_measurement_scope='Isolated full-system OOC internal placement/routing under the existing research clock; not platform timing closure.',
    required_before_execution=[
        'Finish the current stage synthesis/audit/actual restoration and compare candidates; preserve the CP timing anchor.',
        'Create a new full-system implementation root from the audited DCP without changing its RTL or XDC.',
        'Prepare independent runner/auditor/freezer for synthesized, placed and routed checkpoints and report hashes.',
        'Check memory admission and serialize the physical run with the current synthesis/inspection owner.',
        'Record full route completion/errors, DRC, methodology, setup/hold/pulse minima and unconstrained paths; preserve failures.',
        'Archive, actually restore and independently re-audit before freezing physical observations.'],
    limitations=[
        'Existing postprev/center physical results do not establish full-system place/route feasibility or quality.',
        'No external I/O budget or physical clock-source location is supplied; do not invent constraints or waive warnings.',
        'Internal OOC measurements cannot establish board frequency, whole-accelerator speedup or the missing new behavior matrix.',
        'No full-system physical tools or jobs were created by this analysis.'])
out = ROOT/'results/state_full_physical_readiness_20261029.json'
assert not out.exists()
out.write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
print('STATE_PHYSICAL_READINESS_RECORDED', record['full_system_anchor']['port_bits'], 'port bits')
print('MODULE_TEMPLATE_MATCH', record['existing_module_flow']['current_template_matches_executed_script'])
