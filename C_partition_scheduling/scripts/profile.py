#!/usr/bin/env python3
"""Reproducible CPU source-adapter diagnostics, separate from the toy scheduler."""
import argparse
import hashlib
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from adapters.instrument_router import build, sha
from adapters.rrt_fixture import create
from src.trace_analysis import summarize
from src.budget_policy import resolve

BASE_ENV = {'RW_MAX_THREADS': '1', 'RW_PAR_PART': '0', 'RW_PAR_ITER1': '0', 'RW_OVERLAP': '0',
            'RW_BATCH_MIN': '0', 'RW_BBOX': '0', 'RW_CORRIDOR': '-1', 'RW_PAR_PIN': '0',
            'RW_PAR_NUMA': '0', 'RW_PAR_REPORT': '1', 'RW_PAR_OVERLAP': '1', 'RW_PAR_MIDLAST': '1',
            'RW_PF_RAMP1': '0', 'RW_ENDGAME': '0', 'RW_GPU_FLOOD': '0'}


def write(path, data):
    with Path(path).open('x') as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')


def clean_environment(partition=False):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(('RW_', 'RWDEV', 'C_TRACE', 'C_CPU_', 'C_METRICS'))}
    knobs = {**BASE_ENV, 'RW_PAR_PART': '1' if partition else '0'}
    env.update(knobs)
    return env


def measurement_context(input_path, binary, budget, partition=False):
    digest = lambda x: hashlib.sha256(json.dumps(x, sort_keys=True).encode()).hexdigest()
    cpu = next((s.split(':', 1)[1].strip() for s in Path('/proc/cpuinfo').read_text().splitlines()
                if s.startswith('model name')), None)
    scheduler = 'existing_partition_one_worker' if partition else 'serial'
    return {'input_sha256': sha(input_path), 'binary_sha256': sha(binary),
            'runner_sha256': digest({p: sha(ROOT/p) for p in
                ['scripts/budget.py', 'scripts/profile.py', 'src/budget_policy.py']}),
            'environment_sha256': digest({'platform': platform.platform(), 'cpu': cpu,
                'affinity': sorted(os.sched_getaffinity(0)), 'environment': clean_environment(partition)}),
            'constraints_sha256': digest({**BASE_ENV, 'RW_PAR_PART': '1' if partition else '0'}),
            'timing_scope': 'whole_process_warm_filesystem_v1',
            'baseline': {'backend': 'cpp_cpu', 'scheduler': scheduler, 'budget_pops': 0},
            'candidate': {'backend': 'cpp_cpu', 'scheduler': scheduler, 'budget_pops': budget}}


def profile(input_path, directory, binaries, budget=0, partition=False, timeout=60, limit=2000, cap=200000,
            budget_mode='off', budget_evidence=None):
    directory.mkdir()
    env = clean_environment(partition)
    policy = resolve(budget_mode, budget, budget_evidence,
                     measurement_context(input_path, binaries[0], budget, partition))
    budget = policy['effective_budget']
    record = {'input_sha256': sha(input_path), 'budget_pops': budget, 'budget_policy': policy,
              'scheduler': 'existing_partition_one_worker' if partition else 'serial', 'runs': {}}
    # Alternating order across repetitions limits systematic first/second process effects.
    order = [('original_cpu_compat', binaries[1]), ('traced', binaries[0])]
    if int(directory.name.rsplit('_', 1)[-1]) % 2:
        order.reverse()
    for name, binary in order:
        run_env = dict(env)
        if name == 'traced':
            run_env.update(C_TRACE_PATH=str(directory/'trace.jsonl'), C_CPU_BUDGET=str(budget),
                           C_TRACE_LIMIT=str(limit), C_TRACE_CAP=str(cap))
        command = [str(binary), str(input_path.resolve()), str(directory / (name+'.result'))]
        start = time.perf_counter_ns()
        with (directory/(name+'.stdout.log')).open('x') as out, (directory/(name+'.stderr.log')).open('x') as err:
            try:
                p = subprocess.run(command, env=run_env, stdout=out, stderr=err, timeout=timeout)
                code = p.returncode
            except subprocess.TimeoutExpired:
                code = 'timeout'
        record['runs'][name] = {'command': command, 'returncode': code,
                               'process_wall_ms': (time.perf_counter_ns()-start)/1e6,
                               'environment': {k:v for k,v in run_env.items() if k.startswith(('RW_', 'C_TRACE', 'C_CPU_'))}}
    try:
        if any(r['returncode'] != 0 for r in record['runs'].values()):
            raise ValueError('Router process failed or timed out; inspect retained logs')
        record['analysis'] = summarize(directory/'trace.jsonl')
        f = record['analysis']['verification']
        record['checks'] = {'all_connections_routed': f['unrouted'] == 0,
                            'paths_valid_in_exported_graph': f['bad_paths'] == 0,
                            'final_path_capacity_legal': f['final_overused_nodes'] == 0,
                            'output_equal_to_cpu_compat_baseline':
                                sha(directory/'traced.result') == sha(directory/'original_cpu_compat.result')}
        record['status'] = 'passed' if all(record['checks'].values()) else 'failed'
    except (ValueError, OSError, KeyError) as e:
        record.update(status='failed', error=str(e))
    record['artifacts_sha256'] = {p.name: sha(p) for p in directory.iterdir() if p.is_file()}
    write(directory/'summary.json', record)
    return record


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['build', 'trace-smoke', 'profile'])
    p.add_argument('--input', type=Path)
    p.add_argument('--provenance', type=Path, help='Required for real RRT1: input_sha256, target_device, source_version, exporter')
    p.add_argument('--output-dir', type=Path, help='New directory; must not already exist')
    p.add_argument('--repetitions', type=int, default=3)
    p.add_argument('--budget', type=int, default=0)
    p.add_argument('--budget-mode', choices=['off', 'diagnostic', 'auto'], default='off',
                   help='off by default; diagnostic permits probes; auto requires measured evidence')
    p.add_argument('--budget-evidence', type=Path, help='Raw paired measurements, not an evaluation verdict')
    p.add_argument('--partition-one-worker', action='store_true')
    p.add_argument('--timeout', type=float, default=60)
    p.add_argument('--trace-limit', type=int, default=2000)
    p.add_argument('--footprint-cap', type=int, default=200000)
    args = p.parse_args(argv)
    evidence = None
    if args.budget_evidence:
        try:
            evidence = json.loads(args.budget_evidence.read_text())
        except (OSError, ValueError) as exc:
            evidence = {'load_error': str(exc)}
    if min(args.repetitions, args.timeout, args.trace_limit, args.footprint_cap) <= 0 or args.budget < 0:
        p.error('Repetitions, timeout and trace caps must be positive; budget must be nonnegative')
    provenance = None
    if args.action == 'profile':
        if args.input is None or args.provenance is None:
            p.error('profile requires --input and --provenance; use trace-smoke for synthetic checks')
        provenance = json.loads(args.provenance.read_text())
        if not all(provenance.get(k) for k in ('input_sha256', 'target_device', 'source_version', 'exporter')):
            p.error('Incomplete real-data provenance')
        if provenance['input_sha256'] != sha(args.input):
            p.error('Real input hash does not match provenance')
        with args.input.open('rb') as f:
            if f.read(4) != b'RRT1':
                p.error('Only eager RRT1 is supported; JNI RRT2/DCP need a separate adapter')
    binaries, build_record = build()
    if args.action == 'build':
        print(json.dumps({'status':'built', 'binaries':[str(b) for b in binaries]}))
        return 0
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    directory = (args.output_dir or ROOT/'results'/f'{args.action}_{stamp}').resolve()
    directory.mkdir(parents=True, exist_ok=False)
    manifest = {'schema_version':1, 'project_id':'C', 'timestamp_utc':stamp,
                'execution_kind':'synthetic_router_validation' if args.action == 'trace-smoke' else 'real_cpu_diagnostic',
                'backend':'cpp_cpu', 'command':sys.argv, 'repetitions':args.repetitions,
                'platform':platform.platform(), 'python':platform.python_version(),
                'cpu_model':next((line.split(':',1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines()
                                  if line.startswith('model name')), None),
                'cpu_affinity':sorted(os.sched_getaffinity(0)), 'build':build_record, 'provenance':provenance,
                'runner_sha256':sha(__file__), 'analyzer_sha256':sha(ROOT/'src/trace_analysis.py'),
                'fixture_generator_sha256':sha(ROOT/'adapters/rrt_fixture.py'),
                'budget_mode': 'diagnostic' if args.action == 'trace-smoke' else args.budget_mode,
                'budget_policy_sha256': sha(ROOT/'src/budget_policy.py'),
                'limits':'Instrumented CPU diagnostics only; no DCP legality, FPGA/GPU speedup, power or timing claims. '
                         'Elapsed search time includes collection overhead and excludes JSON serialization and recursive retries. '
                         'Budget is upstream pop-count guard (target checked first, abort when pops > budget); '
                         'not a wall-time/memory/recursive-lookahead bound.',
                'measurements':{'routing_ms':None, 'speedup':None, 'transfer_bytes':None, 'pe_idle_ratio':None}}
    write(directory/'manifest.json', manifest)
    rows = []
    if args.action == 'trace-smoke':
        inputs = []
        for case, shared, disconnected in [('disjoint',False,False), ('shared_candidate',True,False),
                                            ('unroutable',False,True), ('same_net',False,False),
                                            ('capacity_conflict',False,False)]:
            path = directory/(case+'.rrt')
            create(path, shared, disconnected, shared_path=case in {'same_net','capacity_conflict'}, same_net=case=='same_net')
            inputs.append((case, path))
        for case, path in inputs:
            settings = [(0,False), (0,True), (2,False), (8,False)] if case in {'disjoint','shared_candidate'} else [(0,False)]
            for budget, partition in settings:
                for rep in range(args.repetitions):
                    name = f'{case}_b{budget}_p{int(partition)}_{rep}'
                    r = profile(path, directory/name, binaries, budget, partition, args.timeout,
                                args.trace_limit, args.footprint_cap, budget_mode='diagnostic')
                    a = r.get('analysis', {})
                    expected = r['status'] == 'passed'
                    if case == 'unroutable':
                        expected = (a.get('verification', {}).get('unrouted') == 1 and r['status'] == 'failed'
                                    and all(v for k,v in r.get('checks',{}).items() if k != 'all_connections_routed'))
                    elif case == 'capacity_conflict':
                        expected = (a.get('verification', {}).get('final_overused_nodes') == 1 and r['status'] == 'failed'
                                    and all(v for k,v in r.get('checks',{}).items() if k != 'final_path_capacity_legal'))
                    elif a:
                        observed = a['unordered_label_read_write']['iteration_task_pairs']
                        expected &= observed > 0 if case == 'shared_candidate' else observed == 0
                        expected &= a['coverage']['all_attempts_and_instrumented_sets_recorded']
                        if budget == 2:
                            expected &= a['verification']['budget_aborts_total'] == 8
                            expected &= a['search']['successful_budget_retries_recorded'] == 8
                    rows.append({'name':name, 'expected_outcome_observed':bool(expected),
                                 'status':r['status'], 'search':a.get('search'),
                                 'unordered_label_read_write_pairs':a.get('unordered_label_read_write',{}).get('iteration_task_pairs')})
    else:
        for rep in range(args.repetitions):
            name = f'real_{rep}'
            r = profile(args.input, directory/name, binaries, args.budget, args.partition_one_worker,
                        args.timeout, args.trace_limit, args.footprint_cap, args.budget_mode, evidence)
            rows.append({'name':name, 'status':r['status'], 'expected_outcome_observed':r['status']=='passed',
                         'budget_policy': r['budget_policy']})
    passed = all(r['expected_outcome_observed'] for r in rows)
    write(directory/'summary.json', {'status':'passed' if passed else 'failed', 'runs':rows,
                                    'execution_kind':manifest['execution_kind']})
    brief = {'status':'passed' if passed else 'failed', 'runs':len(rows), 'output':str(directory)}
    if args.action == 'profile':
        brief['budget_policy'] = rows[0]['budget_policy']
    print(json.dumps(brief, indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
