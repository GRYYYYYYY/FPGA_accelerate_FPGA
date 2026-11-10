from copy import deepcopy
import json
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from check_encoded_physical_execution_v1 import terminal_receipts
from encoded_physical_entry_v1 import watch, validate_bundle
from supervise_search_axi_dpi_v3 import identity
from check_vitis_kernel import digest


class PhysicalEntryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def receipts(self):
        work = self.root/'csr'
        owner = dict(pid=1234)
        state = dict(status='complete', stage='ooc_complete_pending_independent_audit', owner_pid=1234,
                     updated_utc='2026-10-27T00:00:02Z')
        command = 'source {'+str(work/'entry.tcl')+'}'
        observation = dict(observed_utc='2026-10-27T00:00:04Z', status=dict(is_command_running=False,
            last_completed_code=0, queue_length=0, process_id=1234, working_dir=str(work),
            last_completed_elapsed=2.0, last_completed=command))
        history = dict(history=[dict(command=command, code=0, output='SEARCH_PHYSICAL_FLOW_COMPLETE', elapsed=2.0,
                                    timestamp='2026-10-27T00:00:03Z')])
        return observation, history, state, owner, work

    def test_terminal_history_requires_exact_protected_entry(self):
        obs, hist, state, owner, work = self.receipts()
        self.assertFalse(terminal_receipts(obs, hist, state, owner, work)[1])
        for field, value in [('command', 'source {'+str(work/'run_flow.tcl')+'}'), ('code', 1),
                             ('timestamp', '2026-10-27T00:00:01Z'), ('elapsed', 99.0), ('output', 'running')]:
            bad = deepcopy(hist)
            bad['history'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                terminal_receipts(obs, bad, state, owner, work)
        bad = deepcopy(hist); bad['history'] *= 2
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            terminal_receipts(obs, bad, state, owner, work)

    def test_running_stale_and_wrong_owner_receipts_rejected(self):
        obs, hist, state, owner, work = self.receipts()
        for field, value in [('is_command_running', True), ('last_completed_code', 1),
                             ('process_id', 5678), ('queue_length', 1), ('last_completed', 'source wrong')]:
            bad = deepcopy(obs); bad['status'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                terminal_receipts(bad, hist, state, owner, work)
        bad = deepcopy(obs); bad['observed_utc'] = '2026-10-27T00:00:01Z'
        with self.assertRaisesRegex(ValueError, 'Stale'):
            terminal_receipts(bad, hist, state, owner, work)
        state['status'] = 'running'
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            terminal_receipts(obs, hist, state, owner, work)

    def child_fixture(self):
        child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'], start_new_session=True)
        def cleanup():
            if child.poll() is None:
                child.kill()
            child.wait()
        self.addCleanup(cleanup)
        work = self.root/'csr'; control = work/'guard'; control.mkdir(parents=True)
        cg = self.root/'cgroup'; cg.mkdir()
        (cg/'memory.max').write_text('100'); (cg/'memory.current').write_text('100')
        owner = identity(child.pid)
        (control/'plan.json').write_text(json.dumps(dict(owner=owner, work=str(work))))
        return child, work, control, cg, owner

    def test_actual_runtime_abort_kills_only_owned_fixture_and_records_free(self):
        child, work, control, cg, owner = self.child_fixture()
        with self.assertRaisesRegex(RuntimeError, 'memory protection triggered'):
            watch(control, cg)
        self.assertEqual(child.wait(timeout=5), -signal.SIGTERM)
        state = json.loads((control/'state.json').read_text())
        self.assertTrue(state['resource_abort'])
        self.assertEqual(state['triggering_raw_free_bytes'], 0)
        self.assertEqual(state['vivado_owner']['pid'], child.pid)
        self.assertEqual(state['status'], 'failed')

    def test_completed_flow_stops_guard_without_signalling_session(self):
        child, work, control, cg, owner = self.child_fixture()
        (work/'state.json').write_text(json.dumps(dict(owner_pid=child.pid, status='complete')))
        watch(control, cg)
        self.assertIsNone(child.poll())
        state = json.loads((control/'state.json').read_text())
        self.assertEqual(state['status'], 'complete')
        self.assertFalse(state['resource_abort'])

    def test_reused_identity_is_not_signalled(self):
        child, work, control, cg, owner = self.child_fixture()
        owner['start_ticks'] = str(int(owner['start_ticks'])+1)
        (control/'plan.json').write_text(json.dumps(dict(owner=owner, work=str(work))))
        with self.assertRaisesRegex(ValueError, 'missing/reused'):
            watch(control, cg)
        self.assertIsNone(child.poll())

    def test_changed_sources_and_membership_rejected(self):
        jobs = []; files = {}
        for name in ['csr', 'compact', 'read_control']:
            work = self.root/name; source = work/'source'; source.mkdir(parents=True)
            rtl = source/'top.v'; rtl.write_text('module top(); endmodule\n')
            files[str(rtl)] = digest(rtl)
            jobs.append(dict(name=name, work=str(work), source_names=['top.v']))
        plan = dict(status='full_scope_physical_entries_prepared_not_executed', part='xcu280-fsvh2892-2L-e',
                    clock_ns=5, setup_uncertainty_ns=1.35, max_threads=2, startup_wait_removed_by_user=True,
                    runtime_free_bytes=16*1024**3, jobs=jobs, files=files)
        (self.root/'plan.json').write_text(json.dumps(plan))
        validate_bundle(self.root, 'csr')
        extra = self.root/'csr/source/unreviewed.v'; extra.write_text('module bad(); endmodule\n')
        with self.assertRaisesRegex(ValueError, 'membership'):
            validate_bundle(self.root, 'csr')
        extra.unlink(); (self.root/'csr/source/top.v').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'Changed physical input'):
            validate_bundle(self.root, 'csr')


if __name__ == '__main__':
    unittest.main()
