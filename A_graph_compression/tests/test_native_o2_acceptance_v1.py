"""Synthetic gate tests only; these are not RTL acceptance evidence."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import validate_native_o2_acceptance_v1 as gate


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name)
        self.report = self.out / 'report.json'
        self.checker = self.out / 'checker.py'
        for key, value in [('OUT', self.out), ('REPORT', self.report), ('CHECKER', self.checker)]:
            p = patch.object(gate, key, value)
            p.start()
            self.addCleanup(p.stop)
        self.accepted = dict(status=gate.STATUS, rtl_verified=True, transactions=4,
                             pointers=44, models=30, files={})
        self.save('state.json', dict(status='complete', stage='full4_RTL_C_independent_audit_pending',
                                    owner_pid=1, owner_start_ticks='1'))
        self.save('report.json', self.accepted)
        (self.out / 'audit.log').write_text(gate.STATUS + '\n')
        self.save('terminal.json', dict(status='full4_O2_RTL_independently_verified',
                                       report=str(self.report), report_sha256=gate.digest(self.report),
                                       downstream_gates_rewired=False, physical_verified=False,
                                       board_verified=False))
        command = ['prlimit', '--as=17179869184:17179869184', '--stack=67108864:67108864',
                   '--core=0:0', '--', 'python3', str(self.checker)]
        self.save('audit.receipt.json', dict(command=command, exit_code=0, abort_reason=None,
                                           elapsed_seconds=1, report_sha256=gate.digest(self.report),
                                           log_sha256=gate.digest(self.out / 'audit.log')))
        p = patch.object(gate, 'owner_exited')
        self.owner = p.start()
        self.addCleanup(p.stop)
        p = patch.object(gate, 'audit', return_value=copy.deepcopy(self.accepted))
        self.audit = p.start()
        self.addCleanup(p.stop)

    def save(self, name, value):
        (self.out / name).write_text(json.dumps(value))

    def modify(self, name, **changes):
        data = json.loads((self.out / name).read_text())
        data.update(changes)
        self.save(name, data)

    def test_pass_requires_full_reaudit_and_no_transfer(self):
        result = gate.validate()
        self.audit.assert_called_once_with()
        self.assertEqual(self.owner.call_count, 2)
        self.assertFalse(result['downstream_gates_rewired'])

    def test_running_rejected_before_expensive_audit(self):
        self.modify('state.json', status='running')
        with self.assertRaises(Exception):
            gate.validate()
        self.audit.assert_not_called()

    def test_live_owner_rejected(self):
        self.owner.side_effect = RuntimeError('live owner')
        with self.assertRaisesRegex(RuntimeError, 'live owner'):
            gate.validate()
        self.audit.assert_not_called()

    def test_missing_terminal_rejected(self):
        (self.out / 'terminal.json').unlink()
        with self.assertRaises(Exception):
            gate.validate()
        self.audit.assert_not_called()

    def test_receipt_failures(self):
        original = (self.out / 'audit.receipt.json').read_text()
        for changes in [dict(exit_code=1), dict(abort_reason='oom'), dict(command=['true']),
                        dict(log_sha256='0'*64), dict(report_sha256='0'*64),
                        dict(elapsed_seconds=0)]:
            with self.subTest(changes=changes):
                (self.out / 'audit.receipt.json').write_text(original)
                self.modify('audit.receipt.json', **changes)
                with self.assertRaises(Exception):
                    gate.validate()
        self.audit.assert_not_called()

    def test_full_reaudit_difference_rejected(self):
        self.audit.return_value['transactions'] = 3
        with self.assertRaises(Exception):
            gate.validate()

    def test_changed_binding_during_reaudit_rejected(self):
        def changed():
            (self.out / 'audit.log').write_text('changed')
            return copy.deepcopy(self.accepted)
        self.audit.side_effect = changed
        with self.assertRaises(Exception):
            gate.validate()


class OwnerIdentityTests(unittest.TestCase):
    def test_current_process_rejected(self):
        ticks = Path('/proc/self/stat').read_text().rsplit(')', 1)[1].split()[19]
        with self.assertRaises(Exception):
            gate.owner_exited(dict(owner_pid=os.getpid(), owner_start_ticks=ticks))

    def test_reused_pid_does_not_identify_old_owner(self):
        ticks = Path('/proc/self/stat').read_text().rsplit(')', 1)[1].split()[19]
        gate.owner_exited(dict(owner_pid=os.getpid(), owner_start_ticks=str(int(ticks)-1)))


if __name__ == '__main__':
    unittest.main()
