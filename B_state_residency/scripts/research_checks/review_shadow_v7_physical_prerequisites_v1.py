"""Match the accepted shadow to recovered synthesis; do not open a physical gate."""
from pathlib import Path
import datetime
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from shadow_recovered_evidence_v7 import sha, read

BASE = Path('/tmp/B_state_residency_recovery_20261102')
FULL = BASE / 'stage_static_cp_shadow_system_v7'
SYNTH = BASE / 'stage_static_cp_synth_v1'
OUT = ROOT / 'results/stage_static_cp_shadow_v7_physical_prerequisites_20261103.json'


def main():
    assert not OUT.exists()
    accepted_path = ROOT / 'results/stage_static_cp_shadow_system_v7_20261103.json'
    accepted = read(accepted_path)
    assert accepted['status'] == 'full_capacity_fixture_ready_shadow_main_reviewed_frozen_actual_restored'
    assert accepted['full_system_functional_netlist_validated'] and not accepted['physical_gate_open']
    assert sha(accepted['main_review']) == accepted['main_review_sha256']
    freeze = Path(accepted['freeze_root'])
    assert sha(freeze / 'manifest.json') == accepted['freeze_manifest_sha256']
    for name, entry in read(freeze / 'manifest.json')['files'].items():
        assert sha(freeze / name) == entry['sha256'] == sha(Path(accepted['review_actual_restore']) / name)
    fm, fa = read(FULL / 'manifest.json'), read(FULL / 'source_bound_audit.json')
    m, a = read(SYNTH / 'manifest.json'), read(SYNTH / 'source_bound_audit.json')
    assert accepted['audit'] == fa
    assert m['stage'] == 'complete' and m['exit_code'] == 0 and a['status'] == 'passed'
    assert m['parameters'] == fm['parameters'] == fa['parameters'] == a['parameters']
    assert len(m['parameters']) == 13 and m['parameters']['SLOTS'] == 32
    assert m['part'] == 'xcu280-fsvh2892-2L-e'
    assert not a['critical_warnings'] and not a['timing_loop_warnings']
    assert a['check_timing_counts']['loops'] == a['facts']['blackboxes'] == a['facts']['latches'] == 0
    recovery_path = ROOT / 'results/shadow_synthesis_new_host_recovery_review_20261102.json'
    recovery = read(recovery_path)
    recovered = recovery['recovered']['selected_files']
    assert len(recovered) == 192
    for name, digest in recovered.items():
        assert sha(SYNTH / name) == digest
    assert len(m['rtl']) == 133
    for name in m['rtl']:
        assert sha(SYNTH / 'sources' / name) == m['sources'][name] == fm['sources'][name]['sha256'] == sha(FULL / 'sources' / name)
    assert sha(SYNTH / 'synth.dcp') == a['artifact_sha256']['synth.dcp']
    assert sha(SYNTH / 'synth.v') == a['artifact_sha256']['synth.v'] == fm['synthesis_netlist_sha256']
    assert (SYNTH / 'clock.xdc').read_text() == 'create_clock -name core_clk -period 10.000 [get_ports clk]\n'
    assert sha(SYNTH / 'clock.xdc') == a['artifact_sha256']['clock.xdc']
    old_gate = ROOT / 'scripts/check_stage_static_cp_physical_inputs_v5.py'
    old_source = old_gate.read_text()
    assert "FULL=BASE/'stage_static_cp_shadow_system_v6'" in old_source
    assert "['active','stalled','transfers','edges','idle']" in old_source
    files = [accepted_path, Path(accepted['main_review']), freeze / 'manifest.json', recovery_path,
             FULL / 'manifest.json', FULL / 'source_bound_audit.json', SYNTH / 'manifest.json', SYNTH / 'source_bound_audit.json',
             SYNTH / 'synth.dcp', SYNTH / 'synth.v', SYNTH / 'clock.xdc', old_gate,
             ROOT / 'hardware/scripts/implement_state_ooc.tcl']
    report = dict(status='accepted_shadow_and_recovered_synthesis_prerequisites_matched_not_physical_admission',
                  time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), tool_sha256=sha(Path(__file__)),
                  evidence_sha256={str(p): sha(p) for p in files}, production_sources=133, recovered_synthesis_files=192,
                  parameters=m['parameters'], part=m['part'], clock_period_ns=10,
                  synth_dcp_sha256=sha(SYNTH / 'synth.dcp'), synth_netlist_sha256=sha(SYNTH / 'synth.v'),
                  retained_timing_counts=a['check_timing_counts'], full_system_functional_netlist_validated=True,
                  physical_gate_open=False, physical_job_started=False, timing_qualified=False, board_acceptance=False,
                  required_next_work=[
                      'Create a new physical-input gate/prepare/runner/auditor bound to the v7 acceptance and main review, current recovery root and exact synth DCP. Do not execute legacy v5 against failed v6 or old-host paths.',
                      'Retain 342 unconditional/4 qualified outputs, exact 27 files, CP/PW stalls and KA ready1/zero-stall policy; consume actual restored controls without repeating them.',
                      'Copy and independently verify fresh physical inputs/constraints/tools. Query current Vivado sessions and environment; enforce existing continuous 60s dual memory admission before one authorized run.',
                      'Keep the original 10ns OOC clock and no new I/O budgets/exceptions/waivers. opt/place/route and post-route internal timing/DRC remain unmeasured; no board or external-I/O timing claim.',
                      'Publication start/release counterexample and isolated caller-interlock candidate remain a separate source revision; changed production RTL would require new synthesis and functional evidence.'],
                  scope='Read-only preparation inventory, not execution, placement, timing acceptance or opening the physical gate.')
    with OUT.open('x') as f:
        f.write(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print('V7_SYNTHESIS_PHYSICAL_PREREQUISITES_MATCHED', OUT, flush=True)


if __name__ == '__main__':
    main()
