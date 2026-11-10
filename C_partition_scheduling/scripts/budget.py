#!/usr/bin/env python3
"""Measure CPU budget overhead; evaluate evidence for budget admission."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from adapters.instrument_router import build, sha
from adapters.rrt_fixture import create
from scripts.profile import clean_environment, measurement_context, write
from src.budget_policy import evaluate


def run_arm(binary, input_path, directory, budget, partition, timeout):
    directory.mkdir()
    env = clean_environment(partition)
    env.update(C_CPU_BUDGET=str(budget), C_METRICS_PATH=str(directory/'metrics.json'))
    command = [str(binary), str(input_path), str(directory/'route.result')]
    result = {'status': 'failed', 'legal': False, 'quality_passed': False,
              'backend_switches': 0, 'reschedules': 0, 'command': command,
              'budget_pops': budget, 'artifact_directory': str(directory)}
    with (directory/'stdout.log').open('x') as out, (directory/'stderr.log').open('x') as err:
        start = time.perf_counter_ns()
        try:
            result['returncode'] = subprocess.run(command, env=env, stdout=out, stderr=err,
                                                  timeout=timeout).returncode
        except subprocess.TimeoutExpired:
            result['returncode'] = 'timeout'
        result['end_to_end_ms'] = (time.perf_counter_ns() - start)/1e6
    try:
        if result['returncode'] != 0:
            raise ValueError('Process failed or timed out')
        metrics = json.loads((directory/'metrics.json').read_text())
        route, search, discarded = (metrics[k]/1e6 for k in
                                    ['route_ns', 'search_ns', 'discarded_search_ns'])
        if not 0 <= discarded <= search <= route <= result['end_to_end_ms']:
            raise ValueError('Non-exclusive or incomplete serial accounting')
        result.update(useful_search_ms=search-discarded, discarded_search_ms=discarded,
                      scheduling_and_state_ms=route-search, transfer_ms=0.,
                      other_ms=result['end_to_end_ms']-route, metrics=metrics,
                      result_sha256=sha(directory/'route.result'))
        result['legal'] = all(metrics['verification'][k] == 0 for k in
                              ['unrouted', 'bad_paths', 'final_overused_nodes'])
        result['status'] = 'passed' if result['legal'] else 'failed'
    except (OSError, ValueError, KeyError) as exc:
        result['error'] = str(exc)
    result['artifacts_sha256'] = {p.name: sha(p) for p in directory.iterdir() if p.is_file()}
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    bench = sub.add_parser('budget-bench', help='Same-CPU paired overhead diagnostic')
    source = bench.add_mutually_exclusive_group(required=True)
    source.add_argument('--fixture', choices=['disjoint', 'shared_candidate'])
    source.add_argument('--input', type=Path)
    bench.add_argument('--provenance', type=Path)
    bench.add_argument('--budget', type=int, required=True)
    bench.add_argument('--repetitions', type=int, default=10)
    bench.add_argument('--timeout', type=float, default=60)
    bench.add_argument('--partition-one-worker', action='store_true')
    bench.add_argument('--output-dir', type=Path)
    assess = sub.add_parser('budget-evaluate', help='Recompute a verdict from raw paired evidence')
    assess.add_argument('--evidence', type=Path, required=True)
    assess.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    if args.action == 'budget-evaluate':
        try:
            evidence = json.loads(args.evidence.read_text())
        except (OSError, ValueError) as exc:
            evidence = {'load_error': str(exc)}
        decision = evaluate(evidence)
        if args.output:
            write(args.output, decision)
        print(json.dumps(decision, indent=2, ensure_ascii=False))
        return 0  # disabling the budget is a valid outcome
    if args.budget <= 0 or args.repetitions <= 0 or args.timeout <= 0:
        parser.error('Budget, repetitions and timeout must be positive')
    provenance = None
    if args.input:
        if not args.provenance:
            parser.error('Real input requires --provenance; use --fixture for synthetic diagnostics')
        provenance = json.loads(args.provenance.read_text())
        if not all(provenance.get(k) for k in ['input_sha256', 'target_device', 'source_version', 'exporter']):
            parser.error('Incomplete provenance')
        if provenance['input_sha256'] != sha(args.input):
            parser.error('Input hash does not match provenance')
        with args.input.open('rb') as f:
            if f.read(4) != b'RRT1':
                parser.error('Only eager RRT1 is supported')
    binaries, build_record = build()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    directory = (args.output_dir or ROOT/'results'/f'budget-bench_{stamp}').resolve()
    directory.mkdir(parents=True, exist_ok=False)
    input_path = args.input.resolve() if args.input else directory/(args.fixture+'.rrt')
    if args.fixture:
        create(input_path, shared_candidate=args.fixture == 'shared_candidate')
    evidence = {'schema_version': 1, 'timestamp_utc': stamp,
                'measurement_kind': 'synthetic_router_fixture' if args.fixture else 'real_routing',
                'context': measurement_context(input_path, binaries[0], args.budget, args.partition_one_worker),
                'accounting': 'exclusive_wall_components', 'timing_includes_all_costs': True,
                'footprint_collection': False, 'legality_scope': 'exported_graph',
                'complete_campaign': False, 'planned_pairs': args.repetitions, 'pairs': [],
                'provenance': provenance, 'build': build_record,
                'limitations': 'Same CPU/scheduler, immediate retry; serial timers remain in both arms. '
                    'Scheduling/state includes all non-search routing time. Other includes process launch, '
                    'load, verification, output and observer wait. No host/device transfer. Fresh processes '
                    'after one retained warm-up pair. Graph checks are not source-tool signoff.'}
    # No early stopping or discarded failed measurements. Warm-up artifacts are retained.
    for pair_id in range(-1, args.repetitions):
        pair = {'pair_id': pair_id,
                'order': ['candidate', 'baseline'] if pair_id % 2 else ['baseline', 'candidate']}
        for name in pair['order']:
            run_dir = directory/f'{"warmup" if pair_id == -1 else pair_id}_{name}'
            pair[name] = run_arm(binaries[0], input_path, run_dir, args.budget if name == 'candidate' else 0,
                                 args.partition_one_worker, args.timeout)
        equal = bool(pair['baseline'].get('result_sha256')) and (
            pair['baseline'].get('result_sha256') == pair['candidate'].get('result_sha256'))
        for name in ['baseline', 'candidate']:
            pair[name]['quality_passed'] = equal
            if not equal:
                pair[name]['status'] = 'failed'
            write(Path(pair[name]['artifact_directory'])/'run.json', pair[name])
        if pair_id == -1:
            evidence['warmup'] = pair
        else:
            evidence['pairs'].append(pair)
        write(directory/f'pair_{pair_id}.json', pair)
    evidence['complete_campaign'] = all(evidence['warmup'][n]['status'] == 'passed' for n in ['baseline', 'candidate'])
    write(directory/'evidence.json', evidence)
    decision = evaluate(evidence)
    write(directory/'decision.json', decision)
    success = evidence['complete_campaign'] and all(p[n]['status'] == 'passed' for p in evidence['pairs']
                                                   for n in ['baseline', 'candidate'])
    print(json.dumps({'status': 'passed' if success else 'failed', 'pairs': len(evidence['pairs']),
                      'budget_enabled': decision['enabled'], 'reasons': decision['reasons'],
                      'output': str(directory)}, indent=2))
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(main())
