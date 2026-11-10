import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('identity_report', Path(__file__).resolve().parents[1] / 'scripts/report_identity.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class IdentityCapacityTests(unittest.TestCase):
    def test_reverse_ids_counted_once_per_context_without_global_state(self):
        labels = {'global_dyn_bytes': 999999, 'contexts': [
            {'pool_capacity_bytes': 100, 'node_epoch_bytes': 0, 'page_table_bytes': 5,
             'compact_payload_bytes': 60, 'dense_id_bytes': 10},
            {'pool_capacity_bytes': 200, 'node_epoch_bytes': 0, 'page_table_bytes': 5,
             'compact_payload_bytes': 120, 'dense_id_bytes': 20}]}
        self.assertEqual(m.capacity(labels), 520)
