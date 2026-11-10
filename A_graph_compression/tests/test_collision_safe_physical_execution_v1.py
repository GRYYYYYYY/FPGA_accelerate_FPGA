from copy import deepcopy
import json
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from check_collision_safe_physical_execution_v1 import terminal_receipts
import collision_safe_physical_entry_v1 as entry
from collision_safe_physical_entry_v1 import watch, validate_bundle, validate_accepted_sources, validate_functional, PHYSICAL_AS_BYTES
from owned_sim_resource_policy_v1 import POLICY, observe
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
        (cg/'memory.stat').write_text('anon 50\nfile 50\n')
        (cg/'memory.events').write_text('oom 0\noom_kill 2\n')
        (cg/'memory.pressure').write_text('fixture-only\n')
        owner = identity(child.pid)
        (control/'plan.json').write_text(json.dumps(dict(owner=owner, work=str(work), resource_policy=POLICY,physical_as_bytes=PHYSICAL_AS_BYTES,entry_memory=observe(cg))))
        return child, work, control, cg, owner

    def test_new_oom_stops_owned_fixture_without_touching_unrelated_child(self):
        child, work, control, cg, owner = self.child_fixture()
        unrelated = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])
        try:
            (cg/'memory.events').write_text('oom 1\noom_kill 2\n')
            with self.assertRaisesRegex(RuntimeError, 'New cgroup OOM'):
                watch(control, cg)
            self.assertEqual(child.wait(timeout=5), -signal.SIGTERM)
            self.assertIsNone(unrelated.poll())
            state = json.loads((control/'state.json').read_text())
            self.assertTrue(state['resource_abort'])
            self.assertEqual(state['resource_abort_reason'], 'new_cgroup_oom')
            self.assertEqual(state['resource_abort_observation']['raw_free_bytes'], 0)
            self.assertEqual(state['vivado_owner']['pid'], child.pid)
            self.assertEqual(state['status'], 'failed')
        finally:
            unrelated.terminate(); unrelated.wait(timeout=5)

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
                    runtime_rawfree_gate_removed_by_user=True,resource_policy=POLICY,physical_as_bytes=PHYSICAL_AS_BYTES,jobs=jobs,files=files)
        (self.root/'plan.json').write_text(json.dumps(plan))
        validate_bundle(self.root, 'csr')
        extra = self.root/'csr/source/unreviewed.v'; extra.write_text('module bad(); endmodule\n')
        with self.assertRaisesRegex(ValueError, 'membership'):
            validate_bundle(self.root, 'csr')
        extra.unlink(); (self.root/'csr/source/top.v').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'Changed physical input'):
            validate_bundle(self.root, 'csr')

    def test_physical_sources_require_current_same_mode_actual_bindings(self):
        jobs=[]; files={}
        for name, trial in [('csr','collision_safe_bus64_full_rtl_v1/mode_0'),
                            ('compact','collision_safe_bus64_full_rtl_v1/mode_1'),
                            ('read_control','search_read_control_staging_dpi_rtl_v5')]:
            work=self.root/name; source=work/'source'; source.mkdir(parents=True)
            p=source/'top.v'; p.write_text('module '+name+'(); endmodule\n')
            accepted=entry.SIM_BASE/trial/'sim/verilog/top.v'
            files[str(accepted)]=digest(p)
            jobs.append(dict(name=name,work=str(work),source_names=['top.v']))
        plan=dict(jobs=jobs)
        self.assertEqual(set(validate_accepted_sources(plan,files)),{'csr','compact','read_control'})
        for kind in ['missing','wrong_mode','changed']:
            bad=dict(files); keys=list(bad)
            if kind=='missing':bad.pop(keys[0])
            elif kind=='wrong_mode':bad[keys[0]],bad[keys[1]]=bad[keys[1]],bad[keys[0]]
            else:bad[keys[2]]='0'*64
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError,'actual accepted same-mode'):
                validate_accepted_sources(plan,bad)

    def test_read_acceptance_requires_full_current_report_and_snapshot_binding(self):
        results=self.root/'results';results.mkdir()
        snapshot=results/entry.SNAPSHOT;snapshot.write_text('full30 fixture')
        evidence=self.root/'accepted_output'; evidence.write_bytes(b'original full output fixture')
        inherited={str(snapshot):digest(snapshot)}
        read=dict(status='read_control_staging_full2tx_dpi_rtl_all_output_bytes_and_original_c_oracle_independently_verified',
                  rtl_verified=True,transactions=2,pointers=13,models=7,pages=4,output_files=5,cycles=[1,2],
                  resource_policy=POLICY,original_address_environment_unchanged=True,original_cycle_parity_claimed=False,
                  files={**inherited,str(evidence):digest(evidence)})
        path=results/entry.READ
        with patch.object(entry,'validate_read',side_effect=lambda root:dict(inherited)):
            with self.assertRaisesRegex(ValueError,'missing'):
                validate_functional(self.root)
            path.write_text(json.dumps(read));validate_functional(self.root)
            for field,value in [('status','prepared'),('transactions',1),('pointers',12),('pages',1),('output_files',4),
                                ('cycles',[1,0]),('resource_policy','old_rawfree'),('original_cycle_parity_claimed',True)]:
                bad=deepcopy(read);bad[field]=value;path.write_text(json.dumps(bad))
                with self.subTest(field=field), self.assertRaises(ValueError):validate_functional(self.root)
            bad=deepcopy(read);bad['files'].pop(str(snapshot));path.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError,'different full30'):validate_functional(self.root)
            path.write_text(json.dumps(read));evidence.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'Changed predecessor'):validate_functional(self.root)


if __name__ == '__main__':
    unittest.main()
