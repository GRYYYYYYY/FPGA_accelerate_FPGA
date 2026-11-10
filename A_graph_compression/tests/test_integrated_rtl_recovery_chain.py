import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import supervise_integrated_rtl_recovery_v1 as chain
from binary_fsm_full44_prerequisites_v2 import REPORTS, validate


class RecoveryChainTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.out = self.root/'supervision'
        self.out.mkdir()
        self.proof = self.root/'proof'
        self.proof.write_text('frozen fixture')
        self.bindings = {str(self.proof): chain.digest(self.proof)}

    def test_new_native_acceptance_required_and_evidence_checked(self):
        reports = self.root/'results'
        reports.mkdir()
        for name, status in REPORTS.items():
            report = dict(status=status, files=self.bindings)
            if name.startswith('compact_native'):
                report.update(rtl_verified=True, snapshots=[{}, {}, {}, {}])
            if name.startswith('fsm_binary_four'):
                report.update(samples=1280, input_level_cases=64, all_seven_states_observed=True)
            (reports/name).write_text(json.dumps(report))
        self.assertIn(str(self.proof), validate(self.root))
        native = reports/'compact_native_stack_recovery_rtl_audit_20261027_v3.json'
        native.rename(reports/'compact_native_stack_recovery_rtl_audit_20261025_v2.json')
        with self.assertRaisesRegex(ValueError, 'prerequisite missing'):
            validate(self.root)
        (reports/'compact_native_stack_recovery_rtl_audit_20261025_v2.json').rename(native)
        self.proof.write_text('changed')
        with self.assertRaisesRegex(ValueError, 'Changed binary-FSM prerequisite'):
            validate(self.root)

    def test_missing_reused_or_failed_upstream_never_releases_wait(self):
        owner = dict(pid=1234, start_ticks='77', command='audit', cwd=str(self.root))
        state = dict(owner_pid=1234, status='running', stage='wait_existing_execution')
        (self.out/'state.json').write_text(json.dumps(state))
        for actual in [None, dict(owner, start_ticks='88')]:
            with self.subTest(actual=actual), self.assertRaisesRegex(ValueError, 'missing or replaced'):
                chain.wait_upstream(self.out, owner, lookup=lambda _: actual)
        state.update(status='failed', stage='independent_audit')
        (self.out/'state.json').write_text(json.dumps(state))
        with self.assertRaisesRegex(ValueError, 'acceptance failed'):
            chain.wait_upstream(self.out, owner, lookup=lambda _: None)
        state.update(status='complete', stage='independently_audited')
        (self.out/'state.json').write_text(json.dumps(state))
        chain.wait_upstream(self.out, owner, lookup=lambda _: None)

    def fake_job(self, name, exit_code=0):
        marker = self.root/(name+'.called')
        driver = self.root/(name+'_driver.py')
        driver.write_text('from pathlib import Path\nPath('+repr(str(marker))+').write_text("called")\nraise SystemExit('+str(exit_code)+')\n')
        checker = self.root/(name+'_checker.py')
        checker.write_text('raise SystemExit(0)\n')
        return dict(name=name, driver=str(driver), checker=str(checker),
                    bundle=str(self.root/(name+'_trial')), report=str(self.root/(name+'_report.json')),
                    accepted_status='accepted', transactions=4, models=30), marker

    def test_failed_execution_does_not_audit_or_start_next(self):
        first, marker = self.fake_job('csr', 23)
        second, next_marker = self.fake_job('compact')
        with self.assertRaisesRegex(ValueError, 'Phase failed'):
            chain.execute_jobs([first, second], self.bindings, self.out, {}, self.root)
        self.assertTrue(marker.exists())
        self.assertFalse(next_marker.exists())
        self.assertFalse((self.out/'csr_independent_audit.log').exists())
        receipt = json.loads((self.out/'csr_execute.receipt.json').read_text())
        self.assertEqual(receipt['exit_code'], 23)

    def test_zero_exits_without_acceptance_do_not_start_next(self):
        first, _ = self.fake_job('csr')
        second, next_marker = self.fake_job('compact')
        with self.assertRaisesRegex(ValueError, 'report missing'):
            chain.execute_jobs([first, second], self.bindings, self.out, {}, self.root)
        self.assertFalse(next_marker.exists())

    def test_source_drift_refuses_before_start(self):
        first, marker = self.fake_job('csr')
        self.proof.write_text('drift')
        with self.assertRaisesRegex(ValueError, 'Changed scheduled input'):
            chain.execute_jobs([first], self.bindings, self.out, {}, self.root)
        self.assertFalse(marker.exists())

    def test_next_driver_runs_only_after_predecessor_audit(self):
        schedule = []
        previous_report = None
        for name in ('csr', 'compact'):
            job, marker = self.fake_job(name)
            job.update(accepted_status='accepted', transactions=4, models=30)
            if previous_report:
                driver = Path(job['driver'])
                driver.write_text('from pathlib import Path\nassert Path('+repr(previous_report)+').is_file()\n'+driver.read_text())
            report = dict(status='accepted', models=30, ports=44, candidate_encoding_changed=True,
                          cycles=[10, 11, 12, 13], snapshots=[dict(transaction=i, bytes=946498280) for i in range(4)],
                          files=self.bindings)
            Path(job['checker']).write_text('from pathlib import Path\nPath('+repr(job['report'])+').write_text('+repr(json.dumps(report))+')\n')
            schedule.append(job)
            previous_report = job['report']
        state = {}
        chain.execute_jobs(schedule, self.bindings, self.out, state, self.root)
        self.assertEqual([item['name'] for item in state['accepted']], ['csr', 'compact'])

    def test_partial_acceptance_and_changed_evidence_rejected(self):
        job, _ = self.fake_job('csr')
        report = dict(status='accepted', models=30, ports=44, candidate_encoding_changed=True,
                      cycles=[10, 11, 12, 13], snapshots=[dict(transaction=i, bytes=946498280) for i in range(4)],
                      files=self.bindings)
        path = Path(job['report'])
        path.write_text(json.dumps(report))
        chain.accept_report(job)
        for key, value in [('cycles', [10]), ('models', 29), ('snapshots', report['snapshots'][:3]),
                           ('candidate_encoding_changed', False), ('files', {})]:
            path.write_text(json.dumps(dict(report, **{key: value})))
            with self.subTest(key=key), self.assertRaises(ValueError):
                chain.accept_report(job)
        path.write_text(json.dumps(report))
        self.proof.write_text('drift')
        with self.assertRaisesRegex(ValueError, 'Changed scheduled input'):
            chain.accept_report(job)


if __name__ == '__main__':
    unittest.main()
