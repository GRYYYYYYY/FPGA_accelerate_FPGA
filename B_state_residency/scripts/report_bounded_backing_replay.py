"""Audit bounded-byte replay completion and its capacity evidence."""
import argparse
import json
from pathlib import Path
from report_finite_control import audit as control_audit
from replay_finite_page_values import ROOT, sha


def audit(directory):
    directory = Path(directory)
    result = control_audit(directory)
    record = json.loads((directory / 'manifest.json').read_text())
    reference_path = ROOT / 'results/finite_control_real_addresses_20261023T020009Z/manifest.json'
    reference = json.loads(reference_path.read_text())
    demand_path = ROOT / 'results/query_page_demand_20261023T022050Z/manifest.json'
    demand = json.loads(demand_path.read_text())
    if reference['status'] != 'passed' or demand['status'] != 'passed':
        raise ValueError('Reference evidence incomplete')
    if record['groups'] != reference['groups'] or record['reference_counter_comparison'] != 'passed':
        raise ValueError('Full control/data event mismatch')
    budget = record['backing_budget_bytes']
    stride = record['synthetic_stride_bytes']
    if budget != demand['selected_raw_budget_bytes'] or stride != demand['synthetic_stride_bytes']:
        raise ValueError('Capacity configuration mismatch')
    for file, digest in demand['files'].items():
        if sha(Path(file)) != digest:
            raise ValueError('Capacity evidence input changed')
        if file.endswith(('.accesses', '.jsonl')) and record['files'].get(file) != digest:
            raise ValueError('Capacity/replay trace mismatch')
    for name, group in demand['groups'].items():
        if budget // stride < group['maximum_unique_pages']:
            raise ValueError('Backing budget below complete-query upper bound')
        if (group['queries'], group['accesses']) != (record['groups'][name]['queries'], record['groups'][name]['accesses']):
            raise ValueError('Capacity/replay coverage mismatch')
    result.update(backing_budget_bytes=budget, backing_page_capacity=budget // stride,
                  capacity_manifest_sha256=sha(demand_path), control_reference_manifest_sha256=sha(reference_path),
                  scope='Complete real addresses with synthetic values decoded from a fixed raw byte pool. Host metadata/checkpoints excluded. Frozen driver executes value oracle; this audit checks evidence bindings and counters, not an independent value rerun. No DMA/RTL/performance proof.')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    result = audit(args.directory)
    (args.directory / 'completion_audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
