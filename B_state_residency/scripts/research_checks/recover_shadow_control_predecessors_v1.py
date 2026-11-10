"""Recover previously accepted control evidence; do not rerun or rewrite historical verdicts."""
from pathlib import Path
import datetime
import json
from recover_probe_inputs_new_host_v2 import ROOT, DEST, recover, sha


def main():
    selected = []
    for stem in ['shadow_payload_contract_controls', 'shadow_payload_monitor_controls',
                 'shadow_cp_protocol_controls', 'shadow_cp_transfer_monitor_controls']:
        p = ROOT / 'results' / (stem + '_20261030.json')
        r = json.loads(p.read_text())
        selected.append((p, r))
    clock_path = ROOT / 'results/shadow_clock_sampling_controls_20261030.json'
    clock = json.loads(clock_path.read_text())
    assert clock['status'] == 'shadow_clock_sampling_controls_actual_restored'
    selected += [(clock_path, r) for r in clock['controls'].values()]
    recovered = {}
    for p, r in selected:
        receipt = r['restoration']
        index_path = Path(receipt['archive_index'])
        index = json.loads(index_path.read_text())
        assert index['archive_sha256'] == receipt['archive_sha256']
        name = Path(receipt['restored_root']).name
        evidence = recover(name, sorted(index['members']))
        actual = DEST / name
        audit = json.loads((actual / 'source_bound_audit.json').read_text())
        assert audit == r['audit'] and sha(actual / 'source_bound_audit.json') == receipt['audit_sha256']
        assert audit['manifest_sha256'] == sha(actual / 'manifest.json')
        assert not audit['full_system_functional_netlist_validated']
        recovered[name] = dict(evidence, accepted_report=str(p), accepted_report_sha256=sha(p),
                               audit_sha256=sha(actual / 'source_bound_audit.json'))
        print('HISTORICAL_CONTROL_BYTES_RECOVERED', name, len(index['members']), flush=True)
    report = {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'status': 'seven_historical_control_roots_recovered_byte_identical',
              'recovered': recovered, 'tool_sha256': sha(Path(__file__)),
              'scope': 'Actual extraction and complete indexed hashes plus accepted-report/audit/manifest binding. No new simulation or independent functional re-audit; historical verdicts unchanged. Includes the intentionally failing v1 NBA diagnostic.',
              'full_system_functional_netlist_validated': False, 'physical_gate_open': False}
    assert len(recovered) == 7
    out = ROOT / 'results/shadow_control_predecessors_recovery_20261102.json'
    assert not out.exists()
    out.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
