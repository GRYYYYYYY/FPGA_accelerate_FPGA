import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('matrix_report', Path(__file__).resolve().parents[1] / 'scripts/report_research_matrix.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class MatrixReportTests(unittest.TestCase):
    def record(self):
        return {'status': 'running', 'config': {'repetitions': 2,
                'datasets': [{'id': 'real', 'reference_results': {'serial': 'reference'}}],
                'cases': [{'mode': 'serial', 'variant': 'compact', 'page_bits': 9}]},
                'runs': [{'name': 'r0', 'dataset': 'real', 'mode': 'serial', 'variant': 'compact',
                          'page_bits': 9, 'repetition': 0, 'verified': True, 'exit_code': 0,
                          'result_sha256': 'reference', 'metrics': {'route_ms': 12}, 'max_rss_kib': 100}]}

    def summarize(self, record):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / 'manifest.json').write_text(json.dumps(record))
            return module.summarize(path)

    def test_incomplete_does_not_publish_median(self):
        result = self.summarize(self.record())
        self.assertEqual(result['status'], 'partial')
        self.assertNotIn('route_ms_median', result['rows'][0])

    def test_duplicate_cannot_fill_repetition_count(self):
        record = self.record()
        record['runs'].append(dict(record['runs'][0]))
        with self.assertRaises(ValueError):
            self.summarize(record)

    def test_verified_flag_does_not_override_hash_mismatch(self):
        record = self.record()
        record['runs'][0]['result_sha256'] = 'other'
        with self.assertRaises(ValueError):
            self.summarize(record)

    def test_complete_requires_terminal_success(self):
        record = self.record()
        record['runs'].append(dict(record['runs'][0], name='r1', repetition=1, metrics={'route_ms': 14}))
        self.assertEqual(self.summarize(record)['status'], 'partial')
        record['status'] = 'passed'
        result = self.summarize(record)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(result['rows'][0]['route_ms_median'], 13)

    def test_memory_keeps_context_global_and_sampled_scopes_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            labels = {'global_dyn_bytes': 1000, 'contexts': [
                {'pool_capacity_bytes': 100, 'node_epoch_bytes': 20, 'page_table_bytes': 5,
                 'compact_payload_bytes': 30},
                {'pool_capacity_bytes': 200, 'node_epoch_bytes': 40, 'page_table_bytes': 5,
                 'compact_payload_bytes': 60}]}
            (path / 'r0.labels.json').write_text(json.dumps(labels))
            observations = [{'name': 'r0', 'after_load': False, 'rss_kib': 900},
                            {'name': 'r0', 'after_load': True, 'rss_kib': 400},
                            {'name': 'r0', 'after_load': True, 'rss_kib': 500}]
            (path / 'memory_observations.jsonl').write_text('\n'.join(map(json.dumps, observations)) + '\n{"name":')
            result = module.run_memory(path, self.record()['runs'][0], module.read_memory(path))
            self.assertEqual(result['end_label_context_capacity_bytes'], 460)
            self.assertEqual(result['end_global_dyn_capacity_bytes'], 1000)
            self.assertEqual(result['sampled_after_load_peak_rss_kib'], 500)
            self.assertEqual(result['process_peak_rss_kib'], 100)
