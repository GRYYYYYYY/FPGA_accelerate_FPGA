import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from native_output_segments_v1 import METRICS, CHUNK, audit_native_output, sha256


class CompleteSegmentAudit(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.reference = self.root/'reference.json'
        self.output = self.root/'output.json'
        self.golden = dict(status='routed', routes=[dict(net=n, nodes=[1, 2], edges=[[1, 2, n]],
            demands=[[], []], nested=dict(route_ms=31), escaped='quote" slash\\ [{]}') for n in range(3)],
            rounds=[dict(conflicts=1, history=[[1, 3], [4, 5]]), dict(conflicts=0)], scope='tested_site_instances_only',
            **{k: 10 for k in METRICS})
        self.reference.write_text(json.dumps(self.golden, separators=(',', ':')))
        self.expected_sha = sha256(self.reference)
        self.raw = dict(execution='direct', materialization_ms=0, batches=[copy.deepcopy(self.golden) for _ in range(2)], export_ms=[1, 2])

    def check(self, raw=None):
        self.output.write_text(json.dumps(self.raw if raw is None else raw, separators=(',', ':')))
        return audit_native_output(self.output, self.reference, self.expected_sha, 'direct', expected_routes=3)

    def test_full_values_with_only_original_metric_exemptions(self):
        for index, batch in enumerate(self.raw['batches']):
            batch.update({key: index+17 for key in METRICS})
        result = self.check()
        self.assertEqual(result['semantic_audit']['batches'], 2)
        self.assertEqual(result['semantic_audit']['routes_per_batch'], 3)
        self.assertEqual(set(result['semantic_audit']['semantic_fields']), set(self.golden)-METRICS)
        self.raw['batches'][1] = dict(reversed(list(self.raw['batches'][1].items())))
        self.check()  # Batch-root key order is not semantic.

    def test_semantic_faults_in_both_batches_and_nested_metric_not_exempt(self):
        for index in range(2):
            for kind in ['late_edge', 'missing_route', 'nested_metric', 'history', 'new_field', 'scope']:
                with self.subTest(batch=index, kind=kind):
                    bad = copy.deepcopy(self.raw); batch = bad['batches'][index]
                    if kind == 'late_edge': batch['routes'][-1]['edges'][-1][-1] += 1
                    if kind == 'missing_route': batch['routes'].pop()
                    if kind == 'nested_metric': batch['routes'][0]['nested']['route_ms'] += 1
                    if kind == 'history': batch['rounds'][-1]['conflicts'] += 1
                    if kind == 'new_field': batch['extra'] = 1
                    if kind == 'scope': batch['scope'] = 'partial'
                    with self.assertRaises(ValueError): self.check(bad)

    def test_bad_framing_counts_metrics_and_reference(self):
        for kind in ['one_batch', 'third_batch', 'wrong_execution', 'nan', 'boolean', 'negative', 'extra_outer']:
            with self.subTest(kind=kind):
                bad = copy.deepcopy(self.raw)
                if kind == 'one_batch': bad['batches'].pop()
                if kind == 'third_batch': bad['batches'].append(copy.deepcopy(self.golden))
                if kind == 'wrong_execution': bad['execution'] = 'expanded'
                if kind == 'nan': bad['batches'][1]['route_ms'] = float('nan')
                if kind == 'boolean': bad['batches'][1]['route_ms'] = True
                if kind == 'negative': bad['export_ms'][1] = -1
                if kind == 'extra_outer': bad['extra'] = 0
                with self.assertRaises(ValueError): self.check(bad)
        self.check(); original = self.output.read_text()
        for bad in [original[:-3], original+'0', original.replace('"execution":', '"execution":"direct","execution":', 1),
                    original.replace('"routes":[{', '"routes":[[', 1), original.replace('"export_ms":[1,2]', '"export_ms":[1,2,]')]:
            self.output.write_text(bad)
            with self.assertRaises(ValueError): audit_native_output(self.output, self.reference, self.expected_sha, 'direct', 3)
        self.reference.write_text('{}')
        with self.assertRaises(ValueError): self.check()

    def test_tail_beyond_comparison_chunk_is_checked(self):
        self.golden['routes'][-1]['tail'] = 'a'*(CHUNK+31)
        self.reference.write_text(json.dumps(self.golden, separators=(',', ':')))
        self.expected_sha = sha256(self.reference)
        self.raw['batches'] = [copy.deepcopy(self.golden) for _ in range(2)]
        self.check()
        self.raw['batches'][1]['routes'][-1]['tail'] = 'a'*(CHUNK+30)+'b'
        with self.assertRaises(ValueError): self.check()

    def test_reference_need_not_contain_later_instrumentation_metrics(self):
        golden = copy.deepcopy(self.golden)
        del golden['peak_kib'], golden['logical_bytes']
        self.reference.write_text(json.dumps(golden, separators=(',', ':')))
        self.expected_sha = sha256(self.reference)
        self.check()
        del self.raw['batches'][1]['peak_kib']
        with self.assertRaises(ValueError): self.check()


if __name__ == '__main__':
    unittest.main()
