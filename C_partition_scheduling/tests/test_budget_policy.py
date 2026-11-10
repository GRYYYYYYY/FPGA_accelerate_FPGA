"""Contract fixtures below are invented timings, never experimental evidence."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.budget_policy import COMPONENTS, evaluate, resolve
from adapters.instrument_router import build
from adapters.rrt_fixture import create
from scripts.profile import profile


def evidence():
    def arm(useful, discarded=0, transfer=0, switches=0):
        return dict(status='passed', legal=True, quality_passed=True,
                    useful_search_ms=useful, discarded_search_ms=discarded,
                    scheduling_and_state_ms=5., transfer_ms=transfer, other_ms=5.,
                    end_to_end_ms=useful+discarded+transfer+10.,
                    backend_switches=switches, reschedules=0)
    return {'schema_version': 1, 'measurement_kind': 'real_routing',
            'context': {'input_sha256': 'input-A', 'binary_sha256': 'binary-A',
                        'runner_sha256': 'runner-A', 'environment_sha256': 'environment-A',
                        'constraints_sha256': 'constraints-A', 'timing_scope': 'end-to-end',
                        'baseline': dict(backend='cpu', scheduler='serial', budget_pops=0),
                        'candidate': dict(backend='cpu_fpga', scheduler='serial', budget_pops=8)},
            'accounting': 'exclusive_wall_components', 'timing_includes_all_costs': True,
            'footprint_collection': False, 'legality_scope': 'source_tool',
            'complete_campaign': True, 'planned_pairs': 10,
            'pairs': [dict(pair_id=i, order=['baseline', 'candidate'] if i%2 == 0 else ['candidate', 'baseline'],
                           baseline=arm(100.), candidate=arm(50., 10., 10., 2)) for i in range(10)]}


class BudgetPolicyTests(unittest.TestCase):
    def test_proven_net_savings_enable_matching_scope_only(self):
        data = evidence()
        result = resolve('auto', 8, data, data['context'])
        self.assertTrue(result['optimization_enabled'])
        stats = result['evaluation']['statistics']
        self.assertEqual(stats['mean_gross_saved_ms'], 50.)
        self.assertEqual(stats['mean_additional_overhead_ms'], 20.)
        self.assertEqual(stats['mean_net_saved_ms'], 30.)
        for key in ['input_sha256', 'binary_sha256', 'runner_sha256', 'environment_sha256', 'constraints_sha256', 'timing_scope']:
            context = copy.deepcopy(data['context']); context[key] += '-changed'
            with self.subTest(key=key):
                self.assertEqual(resolve('auto', 8, data, context)['effective_budget'], 0)
        self.assertEqual(resolve('auto', 9, data, data['context'])['effective_budget'], 0)

    def test_transfers_and_repeated_search_can_erase_kernel_savings(self):
        for component in ['transfer_ms', 'discarded_search_ms', 'scheduling_and_state_ms', 'other_ms']:
            data = evidence()
            for pair in data['pairs']:
                pair['candidate'][component] += 50
                pair['candidate']['end_to_end_ms'] += 50
            with self.subTest(component=component):
                result = evaluate(data)
                self.assertFalse(result['enabled'])
                self.assertLess(result['statistics']['mean_net_saved_ms'], 0)

    def test_same_cpu_restart_is_not_a_backend_change(self):
        data = evidence(); data['context']['candidate']['backend'] = 'cpu'
        for pair in data['pairs']: pair['candidate']['backend_switches'] = 0
        result = evaluate(data)
        self.assertFalse(result['enabled'])
        self.assertIn('same_backend_and_schedule', result['reasons'])

    def test_rescheduling_requires_observed_actions(self):
        data = evidence(); data['context']['candidate'].update(backend='cpu', scheduler='requeue')
        self.assertFalse(evaluate(data)['enabled'])
        for pair in data['pairs']: pair['candidate']['reschedules'] = 2
        self.assertTrue(evaluate(data)['enabled'])

    def test_missing_failed_synthetic_or_instrumented_evidence_never_enables(self):
        for key, value in [('measurement_kind','synthetic_router_fixture'), ('complete_campaign',False),
                           ('timing_includes_all_costs',False), ('footprint_collection',True),
                           ('legality_scope','exported_graph'), ('planned_pairs',11)]:
            data = evidence(); data[key] = value
            with self.subTest(key=key): self.assertFalse(evaluate(data)['enabled'])
        for key, value in [('status','timeout'), ('legal',False), ('quality_passed',False)]:
            data=evidence(); data['pairs'][0]['candidate'][key]=value
            with self.subTest(key=key): self.assertFalse(evaluate(data)['enabled'])
        for data in [None, {}, [], {'schema_version':1,'context':[]}]:
            self.assertFalse(evaluate(data)['enabled'])

    def test_unaccounted_cost_and_invalid_numbers_are_rejected(self):
        for value in [float('nan'), float('inf'), -1., None, True, '5']:
            data=evidence(); data['pairs'][0]['candidate']['transfer_ms']=value
            with self.subTest(value=value): self.assertFalse(evaluate(data)['enabled'])
        data=evidence(); data['pairs'][0]['candidate']['end_to_end_ms'] += 10
        self.assertFalse(evaluate(data)['enabled'])
        data=evidence(); del data['pairs'][0]['candidate']['transfer_ms']
        self.assertFalse(evaluate(data)['enabled'])

    def test_consistency_margin_outliers_and_sample_count(self):
        data=evidence(); data['pairs']=data['pairs'][:2]; data['planned_pairs']=2
        self.assertFalse(evaluate(data)['enabled'])
        # Nine wins cannot hide one very costly fallback in total wall time.
        data=evidence(); data['pairs'][0]['candidate']['other_ms'] += 1000
        data['pairs'][0]['candidate']['end_to_end_ms'] += 1000
        self.assertFalse(evaluate(data)['enabled'])
        # Five large wins and five losses have a positive mean but weak paired evidence.
        data=evidence()
        for pair in data['pairs'][:5]:
            pair['candidate']['other_ms'] += 35; pair['candidate']['end_to_end_ms'] += 35
        self.assertIn('paired_gain_not_consistent', evaluate(data)['reasons'])
        # Sub-margin improvements do not justify enabling the mechanism.
        data=evidence()
        for pair in data['pairs']:
            pair['candidate']['other_ms'] += 29; pair['candidate']['end_to_end_ms'] += 29
        self.assertFalse(evaluate(data)['enabled'])

    def test_duplicate_unbalanced_pairs_cannot_inflate_evidence(self):
        data=evidence(); data['pairs'][0]['pair_id']=1
        self.assertFalse(evaluate(data)['enabled'])
        data=evidence()
        for pair in data['pairs']: pair['order']=['baseline','candidate']
        self.assertFalse(evaluate(data)['enabled'])

    def test_off_and_diagnostic_are_explicit(self):
        self.assertEqual(resolve('off', 8)['effective_budget'], 0)
        self.assertEqual(resolve('auto', 8)['effective_budget'], 0)
        result=resolve('diagnostic', 8)
        self.assertEqual(result['effective_budget'], 8)
        self.assertFalse(result['optimization_enabled'])


class BudgetRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binaries, _ = build()

    def test_default_and_auto_disable_retries_but_diagnostic_preserves_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source=root/'case.rrt'; create(source)
            for mode, aborts in [('off',0),('auto',0),('diagnostic',8)]:
                with self.subTest(mode=mode), patch.dict('os.environ', {'C_CPU_BUDGET':'2',
                        'RW_MAX_THREADS':'8','C_METRICS_PATH':str(root/'unexpected.json')}):
                    result=profile(source, root/(mode+'_0'), self.binaries, budget=2, budget_mode=mode)
                    self.assertEqual(result['status'], 'passed')
                    self.assertEqual(result['analysis']['verification']['budget_aborts_total'], aborts)
                    self.assertEqual(result['budget_policy']['effective_budget'], 2 if aborts else 0)
                    self.assertTrue((root/(mode+'_0')/'trace.jsonl').exists())
                    self.assertFalse((root/'unexpected.json').exists())


if __name__ == '__main__':
    unittest.main()
