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
    incident_path=ROOT/'results/native_nonzero_and_tree_guard_abort_20261029_v1.json'
    incident=json.loads(incident_path.read_text())
    for p,h in incident['files'].items(): require(digest(p)==h,'Changed preserved guard-abort evidence')
    control=json.loads((ROOT/'data/derived/route_tree_rtl_recovery_control_20261027_v1/state.json').read_text())
    require(control['status']=='failed' and control['resource_abort'] is True and control['exit_code']==-15,'Different previous tree termination')
    for pid in [4027507,4036512,4036517,4090327,4092413]:
        require(not Path('/proc',str(pid)).exists(),'Previous recovery PID exists; inspect identity')
    print(json.dumps(dict(status='full50_preflight_verified_no_free_memory_gate',verified_bindings=len(bindings),
                         transactions_required=50,recovery_executed=False,rtl_accepted=False),indent=2),flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
