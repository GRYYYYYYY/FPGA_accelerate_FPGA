"""Scope/runtime audit bindings and complete-workload rejection checks."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from check_template_scope_runtime import check_worker


class ScopeRuntimeAuditTests(unittest.TestCase):
    def example(self):
        plan = {'binary': '/binary', 'owner_pid': 7, 'cpu': 126, 'inputs': {'span4': {'image': '/span4.agr', 'fixture': '/routing', 'sites': '/sites'}}}
        job = {'repeat': 0, 'scope': 'span4'}
        submission = {'owner_pid': 7, 'cpu': 126, 'condition': job, 'command': ['/binary', '/span4.agr', '/routing', '/sites', '4096', '80', '200000', '8', 'direct']}
        reference = {'status': 'routed', 'routes': list(range(1062)), 'iterations': [{'conflicts': [], 'site_conflicts': [], 'incomplete': []}], 'scope': 'tested_site_instances_only'}
        metrics = {'preparation_ms': 3, 'route_ms': 10, 'peak_kib': 100, 'logical_bytes': 50, 'cache_hits': 2, 'cache_misses': 3}
        raw = {'execution': 'direct', 'batches': [{**copy.deepcopy(reference), **metrics} for _ in range(2)], 'export_ms': [1, 1], 'materialization_ms': 0}
        record = {'condition': job, 'status': 'two_full_scope_batches_equivalent', 'process_wall_ms': 30, 'raw_sha256': 'hash', 'batches': [metrics.copy(), metrics.copy()], 'export_ms': [1, 1], 'materialization_ms': 0}
        receipt = {'exit_code': 0, 'process_wall_ms': 30, 'raw_sha256': 'hash'}
        return plan, job, submission, receipt, record, raw, reference

    def test_binding_semantics_and_timing_rejections(self):
        check_worker(*self.example())
        for change in ('wrong_image', 'wrong_scope', 'cpu', 'missing_route', 'conflict', 'demand', 'wall', 'peak', 'metrics'):
            data = self.example(); plan, job, sub, receipt, record, raw, reference = data
            if change == 'wrong_image': sub['command'][1] = '/global.agr'
            elif change == 'wrong_scope': record['condition'] = {'repeat': 0, 'scope': 'global'}
            elif change == 'cpu': sub['cpu'] = 125
            elif change == 'missing_route': raw['batches'][0]['routes'].pop()
            elif change == 'conflict': raw['batches'][1]['iterations'][0]['site_conflicts'] = [1]
            elif change == 'demand': raw['batches'][0]['demands'] = ['extra']
            elif change == 'wall': record['process_wall_ms'] = receipt['process_wall_ms'] = 1
            elif change == 'peak': raw['batches'][1]['peak_kib'] = record['batches'][1]['peak_kib'] = 1
            else: record['batches'][0]['route_ms'] = 11
            with self.subTest(change=change), self.assertRaises(ValueError): check_worker(*data)


if __name__ == '__main__': unittest.main()
