import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('lifecycle_replay', Path(__file__).resolve().parents[1] / 'scripts/replay_lifecycle.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReplayEndpointTests(unittest.TestCase):
    def test_normal_sink_excludes_both_terminals(self):
        self.assertEqual(module.resources([8, 4, 2], {'sink': 8, 'has_alt': False}), {4})

    def test_alternate_sink_retains_all_nodes(self):
        self.assertEqual(module.resources([8, 4, 2], {'sink': 8, 'has_alt': True}), {8, 4, 2})
        self.assertEqual(module.resources([7, 4, 2], {'sink': 8, 'has_alt': False}), {7, 4, 2})

    def test_empty_path_has_no_resources(self):
        self.assertEqual(module.resources([], {'sink': 8, 'has_alt': False}), set())

    def test_truncated_trace_count_is_rejected(self):
        config = {'expected_attempts': 100, 'expected_connections': 10, 'expected_occupied_resources': 20}
        with self.assertRaises(ValueError):
            module.validate_counts(config, 99, 10, 20)
        module.validate_counts(config, 100, 10, 20)

    def test_config_rejects_changed_bound_input(self):
        config = {'dataset_kind': 'real_path_protocol_replay', 'expected_attempts': 100,
                  'expected_connections': 10, 'expected_occupied_resources': 20,
                  'input': 'input', 'input_sha256': 'expected'}
        with patch.object(module, 'sha', return_value='changed'):
            with self.assertRaises(ValueError):
                module.validate_config(config)
