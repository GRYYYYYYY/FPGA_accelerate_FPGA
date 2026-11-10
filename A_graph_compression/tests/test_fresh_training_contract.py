from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from fresh_training_contract_v1 import prepare_training, validate_training, TRAINING_STAGES
from check_vitis_kernel import digest


class FreshTrainingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.tmp.name)
        source = ROOT/'data/raw/netlist_u280_20261022_v1/training.tsv'
        meta = json.loads((ROOT/'data/derived/netlist_u280_bank_20261022_v1/manifest.json').read_text())
        cls.plan = dict(training_inclusive=True, training_source=str(source), files={str(source):digest(source)},
                        training_bank_file_sha256=meta['bank_file_sha256'], training_bank_object_sha256=meta['bank_object_sha256'])
        times = {}
        def timed(name, fn):
            start = time.monotonic(); value = fn(); times[name] = (time.monotonic()-start)*1000
            return value
        training = prepare_training(cls.plan, 'compact', cls.output, timed)
        training['evaluation_read_start_ns'] = time.monotonic_ns()
        cls.report = dict(training=training, stage_ms=times, artifacts={'bank.json':digest(cls.output/'bank.json')})
        cls.bank_bytes = (cls.output/'bank.json').read_bytes()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_complete_original_training_rebuilt_before_evaluation(self):
        validate_training(self.plan, {'mode':'compact'}, self.output, self.report)
        self.assertEqual(self.report['training']['sources'], 3761)
        self.assertEqual(self.report['training']['templates'], 440)

    def test_training_order_and_partial_counts_rejected(self):
        for key, value in [('evaluation_read_start_ns', 1), ('sources', 3760), ('templates', 439),
                           ('applied', False), ('source_sha256', 'wrong')]:
            report = deepcopy(self.report); report['training'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_training(self.plan, {'mode':'compact'}, self.output, report)

    def test_training_must_be_measured_and_consumed_bank_bound(self):
        for key in TRAINING_STAGES:
            report = deepcopy(self.report); report['stage_ms'][key] = 0
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_training(self.plan, {'mode':'compact'}, self.output, report)
        report = deepcopy(self.report); report['artifacts'] = {}
        with self.assertRaisesRegex(ValueError, 'not bound'):
            validate_training(self.plan, {'mode':'compact'}, self.output, report)

    def test_changed_bank_rejected(self):
        path = self.output/'bank.json'; path.write_bytes(self.bank_bytes+b' ')
        try:
            with self.assertRaisesRegex(ValueError, 'Changed consumed trained bank'):
                validate_training(self.plan, {'mode':'compact'}, self.output, self.report)
        finally:
            path.write_bytes(self.bank_bytes)

    def test_csr_does_not_read_or_fit_a_template_bank(self):
        with tempfile.TemporaryDirectory() as directory:
            times = {}
            def timed(name, fn):
                self.assertIsNone(fn); times[name] = 0
            with patch('fresh_training_contract_v1.read_export', side_effect=AssertionError('CSR read training')), \
                 patch('fresh_training_contract_v1.fit_bank', side_effect=AssertionError('CSR fitted templates')):
                record = prepare_training(self.plan, 'csr', Path(directory), timed)
            record['evaluation_read_start_ns'] = time.monotonic_ns()
            report = dict(training=record, stage_ms=times, artifacts={})
            validate_training(self.plan, {'mode':'csr'}, Path(directory), report)
            report['stage_ms']['training_fit_ms'] = 1
            with self.assertRaisesRegex(ValueError, 'unnecessary/zero'):
                validate_training(self.plan, {'mode':'csr'}, Path(directory), report)


if __name__ == '__main__':
    unittest.main()
