#!/usr/bin/env python3
"""Read existing evidence only; produce a new paper-analysis directory.

No synthesis, simulation, solver, benchmark or legacy auditor is launched.
This validates arithmetic/provenance, not the full historical hardware evidence.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import statistics as st
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'scripts'))
from report_research_matrix import summarize


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), 'Refuse to overwrite an existing analysis'
    inputs = {}

    def bind(path):
        path = ROOT / path
        inputs[str(path.relative_to(ROOT))] = sha(path)
        return path

    def read(path):
        return json.loads(bind(path).read_text())

    base = 'results/research_chain_20261022T183749Z'
    summary = read(base + '/summary.json')
    matrix = read(base + '/matrix/manifest.json')
    audit = read(base + '/completion_audit.json')
    bind('scripts/report_research_matrix.py')
    bind(base + '/matrix/memory_observations.jsonl')
    for p in sorted((ROOT / base / 'matrix').glob('*.labels.json')):
        bind(p)
    assert summarize(ROOT / base / 'matrix') == summary
    assert summary['verified_runs'] == audit['verified_runs'] == len(matrix['runs']) == 78
    assert audit['status'] == 'passed' and summary['status'] == 'complete'
    for run in matrix['runs']:
        assert run['verified'] and run['exit_code'] == 0
        name = run['name']
        files = audit['files'][name]
        for ext in ['log', 'time', 'result']:
            p = bind(base + '/matrix/' + name + '.' + ext)
            assert inputs[str(p.relative_to(ROOT))] == files[ext + '_sha256'], (name, ext)
        raw = (ROOT / base / 'matrix' / (name + '.log')).read_text()
        m = re.search(r'timing: load=(\d+) ms, route=(\d+) ms, write .result=(\d+) ms, total=(\d+) ms', raw)
        assert m and list(map(int, m.groups())) == [run['metrics'][k] for k in ['load_ms', 'route_ms', 'write_ms', 'total_ms']]
        assert run['metrics']['overused'] == 0

    cpu = []
    for row in summary['rows']:
        r = {k: v for k, v in row.items() if k != 'memory_samples'}
        original = next(x for x in summary['rows'] if x['dataset'] == r['dataset'] and x['variant'] == 'original')
        r['runtime_ratio_to_serial_original'] = r['route_ms_median'] / original['route_ms_median']
        r['comparison_scope'] = 'same schedule causal comparison only; batch/original ratio is descriptive'
        cpu.append(r)
    compact = []
    for dataset in sorted({r['dataset'] for r in cpu}):
        for mode in ['serial', 'batch']:
            r = next(x for x in cpu if (x['dataset'], x['mode'], x['variant'], x['page_bits']) == (dataset, mode, 'compact', 9))
            b = next(x for x in cpu if (x['dataset'], x['mode'], x['variant'], x['page_bits']) == (dataset, mode, 'node_epoch', 9))
            compact.append(dict(dataset=dataset, mode=mode, page_nodes=512,
                runtime_change_percent=100 * (r['route_ms_median'] / b['route_ms_median'] - 1),
                label_end_capacity_reduction_percent=100 * (1 - r['end_label_context_capacity_bytes_median'] / b['end_label_context_capacity_bytes_median'])))

    profiles = []
    for i in range(3):
        d = read(f'results/real_trace_20261022T165136Z/profile_{i}.json')
        total = sum(d[k] for k in ['load_ms', 'route_ms', 'write_ms'])
        profiles.append(dict(repetition=i, total_ms=total,
            label_fraction=d['phases']['label_initial_allocation']['ms'] / total,
            mutable_fraction=d['phases']['mutable_state_initialization']['ms'] / total))
    profile = dict(runs=profiles, scope='instrumented CPU profile; initialization phases are nested')
    for k in ['label', 'mutable']:
        f = st.median(r[k + '_fraction'] for r in profiles)
        profile[k + '_percent_median'] = 100 * f
        profile[k + '_ideal_elimination_speedup'] = 1 / (1 - f)

    restore = read('results/restore_seed_20261027.json')
    assert restore['status'] == 'passed'
    recovery = []
    for name, r in restore['comparison'].items():
        assert r['default_off_entire_trace_identical'] and r['enabled_final_ddr_identical']
        label_saved, total_saved = r['label_before'] - r['label_after'], r['total_before'] - r['total_after']
        off = restore['cases']['restore_seed_off_' + name + '_v1']['behavioral_cycles']['events']
        on = restore['cases']['restore_seed_on_' + name + '_v1']['behavioral_cycles']['events']
        segments, prev_off, prev_on = [], 0, 0
        for event in ['FI','FOURTH_WARM_START','FOURTH_WARM_OWNER','FOURTH_WARM_LABELS',
                      'FOURTH_WARM_RELEASE','FOURTH_RETRY_BEGIN','FOURTH_PASS']:
            segments.append(dict(ending_event=event, off_cycles=off[event]-prev_off,
                on_cycles=on[event]-prev_on, saved_cycles=(off[event]-prev_off)-(on[event]-prev_on)))
            prev_off, prev_on = off[event], on[event]
        assert prev_off == r['total_before'] and prev_on == r['total_after']
        assert sum(s['saved_cycles'] for s in segments) == total_saved
        assert -segments[-1]['saved_cycles'] == r['subsequent_retry_phase_increase']
        reduction = 100 * label_saved / r['label_before']
        assert abs(reduction - r['label_reduction_percent']) < 1e-10
        recovery.append(dict(case=name, **r, event_segments=segments, total_fixture_reduction_percent=100 * total_saved / r['total_before'],
            total_fixture_speedup=r['total_before'] / r['total_after'], total_cycles_saved=total_saved,
            scope='controlled RTL fixture cycles; not complete application runtime or board speedup'))

    demand_path = 'results/resident_capacity_demand_20261023/manifest.json'
    demand = read(demand_path)
    da = read('results/resident_capacity_demand_20261023/completion_audit.json')
    assert da['manifest_sha256'] == inputs[demand_path]
    assert demand['status'] == da['status'] == 'passed' and len(demand['queries']) == 38
    capacities = sorted(map(int, demand['totals']))
    curve, perquery = [], []
    baseline = demand['totals']['4']['transfers']
    for c in capacities:
        key = str(c)
        t = demand['totals'][key]
        for field, val in t.items():
            assert val == sum(q['capacities'][key].get(field, 0) for q in demand['queries']), (c, field)
        assert t['transfers'] == t['writebacks'] + t['refills']
        assert t['page_bytes'] == 1344 * t['transfers']
        curve.append(dict(slots=c, resident_payload_bytes=demand['resident_payload_bits_only'][key] / 8,
            **t, transfer_reduction_vs_4_percent=100 * (1 - t['transfers'] / baseline)))
    for q in demand['queries']:
        b, c = q['capacities']['4']['transfers'], q['capacities']['512']['transfers']
        perquery.append(dict(attempt=q['attempt'], accesses=q['accesses'], transfers_4=b, transfers_512=c,
            reduction_percent=100 * (1 - c / b), weight_at_4=b / baseline))
    ranked = sorted(perquery, key=lambda x: x['transfers_4'], reverse=True)
    demand_stats = dict(query_count=38, accesses=sum(q['accesses'] for q in demand['queries']),
        unweighted_query_median_reduction_percent=st.median(q['reduction_percent'] for q in perquery),
        weighted_transfer_reduction_percent=curve[-1]['transfer_reduction_vs_4_percent'],
        top1_transfer_share_percent=100 * ranked[0]['weight_at_4'],
        top5_transfer_share_percent=100 * sum(q['weight_at_4'] for q in ranked[:5]),
        payload_growth_factor=curve[-1]['resident_payload_bytes'] / curve[0]['resident_payload_bytes'],
        scope='address/write demand model, not RTL larger capacities, DDR measurements or speedup; 1344 B transfer page != 1096 B resident payload page')

    phys = read('results/stage_static_cp_physical_v6_main_review_20261104.json')
    bind('results/stage_static_cp_physical_v6_20261104.json')
    bind('results/stage_static_cp_shadow_system_v7_20261103.json')
    bind('results/ka_publication_release_full_rtl_v5_counterexample_review_20261102.json')
    interlock = read('results/publication_start_interlock_slice_v1_review_20261104.json')
    assert phys['physical_artifacts_validated'] and not phys['timing_qualified'] and not phys['board_acceptance']
    assert not interlock['candidate_full_system_validated'] and not interlock['production_repair_accepted']
    p = phys['comparison']
    physical = dict(comparison={k:p[k] for k in ['resources','timing','setup_failing_endpoints','limitations']},
        lut_reduction_percent=100 * (1 - p['resources']['LUT']['candidate'] / p['resources']['LUT']['reference']),
        worst_path_net_delay_share_percent=100 * phys['worst_setup_path']['net_delay_ns'] / phys['worst_setup_path']['data_delay_ns'],
        timing_qualified=False, board_acceptance=False, candidate_interlock_full_system_validated=False)
    pilot = read('results/resident_pilot_20261022T220822Z/summary.json')
    capacity = read('results/resident_capacity_20261022T224734Z/completion_audit.json')
    ca = read('results/command_profile_full_20261024/analysis.json')
    command = {k: ca[k] for k in ['total','fractions_percent','transfer_operations_busy_cycles','transfer_operations_percent_total','scope']}
    result = dict(status='existing_evidence_reanalysis_complete', target='full_architecture_EDA_paper',
        submission_ready=False, new_hardware_experiments_run=False,
        cpu_rows=cpu, compact_same_schedule_comparisons=compact, cpu_initialization=profile,
        recovery=recovery, capacity_demand=demand_stats, physical=physical,
        cpu_single_repeat_pilot=pilot, cpu_single_repeat_capacity=capacity['rows'], command_profile=command,
        verification=dict(matrix_raw_logs_times_results_sha_verified=78, matrix_summary_recomputed_exactly=True,
            demand_38_query_totals_recomputed=True, recovery_cycle_conservation_checked=True,
            scope='raw CPU files and analytical consistency checked; hardware reports consumed, not rerun or independently re-proved'))
    args.output.mkdir(parents=True)
    def write_json(name, obj):
        (args.output / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    write_json('metrics.json', result)
    for name, rows in [('cpu_matrix.csv', cpu), ('compact_comparisons.csv', compact), ('recovery.csv', recovery),
                       ('capacity_curve.csv', curve), ('capacity_queries.csv', perquery)]:
        fields = list(dict.fromkeys(k for row in rows for k in row))
        with (args.output / name).open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    inputs[str(Path(__file__).relative_to(ROOT))] = sha(__file__)
    write_json('analysis_manifest.json', dict(status='passed', inputs_sha256=inputs,
        output_sha256={p.name:sha(p) for p in sorted(args.output.iterdir())},
        command=['python3','-B',str(Path(__file__).relative_to(ROOT)),'--output',str(args.output)],
        overwrite_allowed=False, no_legacy_artifact_written=True))
    print(json.dumps(dict(status='passed', output=str(args.output), verified_raw_cpu_runs=78,
        input_files=len(inputs), recovery_total_reductions=[r['total_fixture_reduction_percent'] for r in recovery],
        demand=demand_stats, initialization=profile), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
