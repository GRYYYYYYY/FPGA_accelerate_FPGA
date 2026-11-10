"""Conservative, scope-bound admission of a budget policy using paired measurements.

Times are disjoint wall-clock components, never summed worker/device busy times.
The evidence is a trusted measurement-harness record, not a security certificate.
"""
import math
from statistics import mean

POLICY_VERSION = 1
MIN_PAIRS = 10
MIN_GAIN = .02
MAX_P_VALUE = .05
COMPONENTS = ('useful_search_ms', 'discarded_search_ms', 'scheduling_and_state_ms',
              'transfer_ms', 'other_ms')
CONTEXT_KEYS = ('input_sha256', 'binary_sha256', 'runner_sha256', 'environment_sha256',
                'constraints_sha256', 'timing_scope', 'baseline', 'candidate')


def _number(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError('Timings must be finite nonnegative numbers')
    return value


def evaluate(evidence, expected_context=None):
    """Missing, stale, failed, incomplete or non-beneficial evidence disables budgets."""
    reasons, rows = [], []
    decision = {'policy_version': POLICY_VERSION, 'enabled': False, 'effective_budget': 0,
                'diagnostics_available': True, 'reasons': reasons, 'statistics': None,
                'thresholds': {'min_pairs': MIN_PAIRS, 'min_gain_fraction': MIN_GAIN,
                               'max_one_sided_sign_test_p': MAX_P_VALUE}}
    try:
        if not isinstance(evidence, dict) or evidence.get('schema_version') != 1:
            raise ValueError('Missing or unsupported evidence schema')
        context = evidence['context']
        if any(not context.get(k) for k in CONTEXT_KEYS):
            raise ValueError('Incomplete measurement identity')
        if expected_context is not None and context != expected_context:
            reasons.append('evidence_context_mismatch')
        if evidence.get('measurement_kind') != 'real_routing':
            reasons.append('not_real_routing_evidence')
        if evidence.get('accounting') != 'exclusive_wall_components':
            raise ValueError('Require non-overlapping wall-time accounting')
        if evidence.get('timing_includes_all_costs') is not True:
            reasons.append('incomplete_timing_boundary')
        if evidence.get('footprint_collection') is not False:
            reasons.append('footprint_instrumentation_not_suitable_for_admission')
        if evidence.get('legality_scope') != 'source_tool':
            reasons.append('source_tool_legality_missing')
        if evidence.get('complete_campaign') is not True:
            reasons.append('incomplete_campaign')
        baseline, candidate = context['baseline'], context['candidate']
        if baseline['budget_pops'] != 0 or type(candidate['budget_pops']) is not int or candidate['budget_pops'] <= 0:
            raise ValueError('Require zero-budget control and positive-budget candidate')
        changed_backend = baseline['backend'] != candidate['backend']
        changed_schedule = baseline['scheduler'] != candidate['scheduler']
        if not (changed_backend or changed_schedule):
            reasons.append('same_backend_and_schedule')
        pairs = evidence['pairs']
        if not isinstance(pairs, list) or not pairs:
            raise ValueError('Missing paired measurements')
        if len(pairs) < MIN_PAIRS:
            reasons.append('insufficient_pairs')
        if evidence.get('planned_pairs') != len(pairs):
            reasons.append('missing_planned_pairs')
        ids, actions, orders = set(), 0, set()
        for pair in pairs:
            pair_id = pair['pair_id']
            if type(pair_id) is not int or pair_id < 0 or pair_id in ids:
                raise ValueError('Invalid or duplicate pair ID')
            ids.add(pair_id)
            order = pair['order']
            if order not in (['baseline', 'candidate'], ['candidate', 'baseline']):
                raise ValueError('Invalid paired execution order')
            orders.add(tuple(order))
            arms = []
            for name in ('baseline', 'candidate'):
                arm = pair[name]
                if arm.get('status') != 'passed' or arm.get('legal') is not True or arm.get('quality_passed') is not True:
                    reasons.append('failed_or_unverified_pair')
                wall = _number(arm['end_to_end_ms'])
                if wall == 0:
                    raise ValueError('End-to-end time must be positive')
                parts = [_number(arm[k]) for k in COMPONENTS]
                if not math.isclose(sum(parts), wall, rel_tol=1e-6, abs_tol=1e-6):
                    raise ValueError('Components do not cover end-to-end wall time exactly once')
                arms.append(arm)
            b, c = arms
            for name, changed in [('backend_switches', changed_backend), ('reschedules', changed_schedule)]:
                count = c[name]
                if type(count) is not int or count < 0:
                    raise ValueError('Invalid mechanism execution count')
                if changed:
                    actions += count
            saved = b['useful_search_ms'] - c['useful_search_ms']
            extra = sum(c[k] - b[k] for k in COMPONENTS[1:])
            net = b['end_to_end_ms'] - c['end_to_end_ms']
            rows.append({'gross_saved_ms': saved, 'additional_overhead_ms': extra,
                         'net_saved_ms': net, 'gain_fraction': net / b['end_to_end_ms'],
                         'baseline_ms': b['end_to_end_ms'], 'candidate_ms': c['end_to_end_ms']})
        if not actions:
            reasons.append('no_backend_switch_or_reschedule_observed')
        first_baseline = sum(p['order'][0] == 'baseline' for p in pairs)
        if ids != set(range(len(pairs))) or len(orders) != 2 or abs(2*first_baseline-len(pairs)) > 1:
            reasons.append('incomplete_or_unbalanced_pairs')
        wins = sum(r['gain_fraction'] > MIN_GAIN for r in rows)
        # Exact one-sided sign test against a 2% improvement; ties count as losses.
        p_value = sum(math.comb(len(rows), k) for k in range(wins, len(rows)+1)) / 2**len(rows)
        net = mean(r['net_saved_ms'] for r in rows)
        gross = mean(r['gross_saved_ms'] for r in rows)
        extra = mean(r['additional_overhead_ms'] for r in rows)
        fraction = net / mean(r['baseline_ms'] for r in rows)
        if gross <= 0 or gross <= extra or fraction <= MIN_GAIN:
            reasons.append('savings_do_not_exceed_overhead_and_margin')
        if p_value > MAX_P_VALUE:
            reasons.append('paired_gain_not_consistent')
        decision['statistics'] = {'pairs': len(rows), 'wins_above_margin': wins,
                                  'one_sided_sign_test_p': p_value,
                                  'mean_gross_saved_ms': gross, 'mean_additional_overhead_ms': extra,
                                  'mean_net_saved_ms': net, 'aggregate_gain_fraction': fraction,
                                  'mean_baseline_ms': mean(r['baseline_ms'] for r in rows),
                                  'mean_candidate_ms': mean(r['candidate_ms'] for r in rows)}
        if not reasons:
            decision.update(enabled=True, effective_budget=candidate['budget_pops'])
    except (AttributeError, KeyError, TypeError, ValueError, OverflowError) as exc:
        reasons.append('invalid_evidence: ' + str(exc))
    decision['reasons'] = list(dict.fromkeys(reasons))
    return decision


def resolve(mode, requested_budget, evidence=None, expected_context=None):
    if mode not in ('off', 'diagnostic', 'auto') or type(requested_budget) is not int or requested_budget < 0:
        raise ValueError('Invalid budget mode or pop count')
    result = {'mode': mode, 'requested_budget': requested_budget, 'effective_budget': 0,
              'optimization_enabled': False, 'diagnostics_available': True}
    if mode == 'diagnostic':
        result.update(effective_budget=requested_budget, reason='explicit_diagnostic_only')
    elif mode == 'auto' and requested_budget:
        if expected_context is None:
            result['reason'] = 'missing_execution_identity'
        else:
            decision = evaluate(evidence, expected_context)
            # A valid result for another threshold must never enable this request.
            if decision['enabled'] and decision['effective_budget'] != requested_budget:
                decision.update(enabled=False, effective_budget=0)
                decision['reasons'].append('requested_budget_mismatch')
            result.update(effective_budget=decision['effective_budget'],
                          optimization_enabled=decision['enabled'], evaluation=decision)
    else:
        result['reason'] = 'default_off' if mode == 'off' else 'zero_budget_requested'
    return result
