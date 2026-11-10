"""Control-path fault injection only; does not execute or accept any RTL."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('tree_recovery_control', SCRIPTS / 'run_route_tree_full50_recovery_v1.py')
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)


class RecoveryControl(unittest.TestCase):
    def test_rejected_preflight_creates_nothing(self):
        with tempfile.TemporaryDirectory() as d, patch.object(driver.subprocess, 'run', return_value=Mock(returncode=2)):
            p = Path(d) / 'control'
            with patch.object(driver, 'CONTROL', p), patch.object(driver.subprocess, 'Popen') as launch:
                self.assertEqual(driver.main(), 2)
                launch.assert_not_called()
                self.assertFalse(p.exists())

    def test_guard_abort_even_if_child_exits_zero_is_failure(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            child = Mock(pid=123456, returncode=0)
            child.poll.return_value = None
            with patch.multiple(driver, OUT=base/'out', PROJECT=base/'project', AUDIT=base/'audit', CONTROL=base/'control'), \
                 patch.object(driver.subprocess, 'run', return_value=Mock(returncode=0)), \
                 patch.object(driver.subprocess, 'Popen', return_value=child), \
                 patch.object(driver, 'free_bytes', side_effect=[128 * 2**30, 0]), \
                 patch.object(driver.os, 'killpg') as kill:
                self.assertEqual(driver.main(), 1)
                kill.assert_called_once_with(child.pid, driver.signal.SIGTERM)
            state = json.loads((base/'control/state.json').read_text())
            self.assertEqual(state['status'], 'failed')
            self.assertTrue(state['resource_abort'])
            self.assertFalse((base/'audit').exists())

    def test_zero_exit_without_audit_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            child = Mock(pid=123456, returncode=0)
            child.poll.return_value = 0
            with patch.multiple(driver, OUT=base/'out', PROJECT=base/'project', AUDIT=base/'audit', CONTROL=base/'control'), \
                 patch.object(driver.subprocess, 'run', return_value=Mock(returncode=0)), \
                 patch.object(driver.subprocess, 'Popen', return_value=child), \
                 patch.object(driver, 'free_bytes', return_value=128 * 2**30):
                with self.assertRaisesRegex(RuntimeError, 'without independent audit'):
                    driver.main()
            self.assertEqual(json.loads((base/'control/state.json').read_text())['status'], 'failed')


if __name__ == '__main__':
    unittest.main()
