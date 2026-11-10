#!/usr/bin/env python3
"""Read-only recovery admission; never launches or accepts an RTL simulation."""
import json
from pathlib import Path
from check_vitis_kernel import digest, require

ROOT = Path(__file__).resolve().parents[1]


def main():
    bundle = ROOT / 'data/derived/route_tree_rtl_20261024_v1'
    plan_path = bundle / 'plan.json'
    setup_path = bundle / 'setup.json'
    plan = json.loads(plan_path.read_text())
    setup = json.loads(setup_path.read_text())
    execution = json.loads((bundle / 'execution_plan.json').read_text())
    inventory = json.loads((ROOT / 'results/route_tree_rtl_recovery_inventory_20261027_v1.json').read_text())
    setup_audit = json.loads((ROOT / 'results/route_tree_rtl_setup_20261024_v1.json').read_text())
    require(plan['transactions'] == 50 and plan['simulation_bound_ns'] == 10000000000,
            'Changed full50 scope')
    require(setup_audit['status'] == 'production_route_tree_full_capacity_50_transaction_setup_independently_verified_rtl_pending',
            'Missing full-depth setup audit')
    require(execution['plan_sha256'] == digest(plan_path) and
            execution['setup_sha256'] == digest(setup_path), 'Changed preparation')
    bindings = {}
    for group in [plan['files'], plan['synthesis'], setup['files'], execution['files'],
                  inventory['files'], setup_audit['files']]:
        for name, expected in group.items():
            require(name not in bindings or bindings[name] == expected, 'Conflicting binding ' + name)
            bindings[name] = expected
    for name, expected in bindings.items():
        require(digest(name) == expected, 'Changed recovery input ' + name)
    for pid in [2929797, 3001030, 3001920]:
        require(not Path('/proc', str(pid)).exists(), 'Recorded process PID exists; inspect identity before recovery')
    require(not (bundle / 'rtl.receipt.json').exists(), 'Original execution acquired terminal evidence; reassess')
    current = int(Path('/sys/fs/cgroup/memory.current').read_text())
    maximum = int(Path('/sys/fs/cgroup/memory.max').read_text())
    free = maximum - current
    # Conservative admission retained from existing recovery work; not a measured
    # bound on this component. Admission alone never authorizes an unchecked run.
    admitted = free >= 128 * 2**30
    print(json.dumps(dict(status='preflight_verified_memory_admitted' if admitted else
                         'preflight_verified_memory_insufficient',
                         verified_bindings=len(bindings), memory_free_bytes=free,
                         admission_bytes=128 * 2**30, transactions_required=50,
                         recovery_executed=False, rtl_accepted=False), indent=2), flush=True)
    return 0 if admitted else 2


if __name__ == '__main__':
    raise SystemExit(main())
