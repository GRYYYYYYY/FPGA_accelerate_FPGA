"""Real 2022.2 report parsing plus adversarial gates; no new physical result is implied."""
import copy
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_search_kernel_physical import (coverage, constraints, quality_gates, session_gate,
                                          summary, timing, utilization)
from check_netlist_quality import route_status, drc_status

SOLUTION = ROOT / 'build/vitis_graph_csr_ooc_20261023_v1/solution'
RUN = SOLUTION / 'impl/verilog/project.runs/impl_1'
REPORT = SOLUTION / 'impl/verilog/report'


class PhysicalAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (RUN / 'bd_0_wrapper_timing_summary_routed.rpt').read_text()
        cls.t = timing(cls.text)
        cls.r = route_status(REPORT / 'graph_accel_status_routed.rpt')
        cls.d = drc_status(RUN / 'bd_0_wrapper_drc_routed.rpt')
        cls.m = drc_status(RUN / 'bd_0_wrapper_methodology_drc_routed.rpt')

    def test_real_reports_and_retained_io_warning(self):
        self.assertEqual(self.t['setup']['slack_ns'], 0.998)
        self.assertEqual(self.t['hold']['slack_ns'], 0.011)
        self.assertEqual(self.t['pulse_width']['total_endpoints'], 10321)
        self.assertEqual(self.m['issues']['TIMING-18']['count'], 949)
        gates = quality_gates(self.t, self.r, self.d, self.m)
        self.assertTrue(all(v for k, v in gates.items() if k != 'no_methodology_violations'))
        self.assertFalse(gates['no_methodology_violations'])
        text = (REPORT / 'graph_accel_utilization_hierarchical_routed.rpt').read_text()
        counts = utilization(text, 'bd_0_wrapper')
        self.assertEqual(counts['Total LUTs'], 6708)
        self.assertEqual(counts['FFs'], 9426)
        with self.assertRaises(ValueError): utilization(text)
        with self.assertRaises(ValueError): utilization(text.replace('6708', 'NaN'), 'bd_0_wrapper')

    def test_failed_timing_and_route_gates(self):
        for kind in ('setup', 'hold', 'pulse_width'):
            for key, value in [('slack_ns', -0.001), ('total_negative_slack_ns', -0.001),
                               ('failing_endpoints', 1), ('total_endpoints', 0)]:
                with self.subTest(kind=kind, key=key):
                    bad = copy.deepcopy(self.t); bad[kind][key] = value
                    self.assertFalse(quality_gates(bad, self.r, self.d, {'total': 0})['internal_timing_met'])
        for key in ('no_clock', 'unconstrained_internal_endpoints', 'loops', 'multiple_clock'):
            bad = copy.deepcopy(self.t); bad['coverage'][key] = 1
            self.assertFalse(quality_gates(bad, self.r, self.d, {'total': 0})['internal_constraint_checks_clear'])
        for key, value in [('routable nets', 0), ('fully routed nets', 0), ('nets with routing errors', 1)]:
            bad = dict(self.r); bad[key] = value
            self.assertFalse(quality_gates(self.t, bad, self.d, {'total': 0})['all_nets_routed'])
        self.assertFalse(quality_gates(self.t, self.r, {'total': 1}, {'total': 0})['no_drc_violations'])

    def test_malformed_timing_reports(self):
        bad_reports = [self.text.replace('0.998', 'NaN', 1),
                       self.text.replace('0.998', 'inf', 1),
                       self.text.replace('checking no_clock (0)', 'checking no_clock (1)', 1),
                       self.text.replace('checking no_clock', 'checking removed_check'),
                       self.text.replace('5.000           200.000', '10.000          100.000'),
                       self.text.replace('{0.000 2.500}', '{0.000 1.000}'),
                       re.sub(r'(0\.998\s+0\.000\s+)0', r'\g<1>999999999', self.text, count=1),
                       self.text + self.text]
        row = re.search(r'^\s*WNS\(ns\)[^\n]*\n[ -]+\n([^\n]+)', self.text, re.M)[1]
        bad_reports.append(self.text.replace(row, ' '.join(row.split()[:8]), 1))
        for i, text in enumerate(bad_reports):
            with self.subTest(case=i), self.assertRaises(ValueError): timing(text)

    def test_summary_and_constraint_mismatches(self):
        valid = ('version 2022.2 part xcu280-fsvh2892-2L-e clock_period 5.000 '
                 'setup_slack 0.998 hold_slack 0.011 cells 10000')
        summary(valid, self.t)
        for before, after in [('2022.2', '2026.1'), ('xcu280', 'xcvu13p'), ('5.000', '10.000'),
                              ('0.998', '0.9999'), ('0.011', 'nan'), ('10000', '0')]:
            with self.subTest(before=before), self.assertRaises(ValueError):
                summary(valid.replace(before, after), self.t)
        xdc = ('create_clock -name ap_clk -period 5.000 [get_ports ap_clk]\n'
               'set_clock_uncertainty -setup 1.350 [get_clocks ap_clk]\n')
        constraints(xdc)
        for bad in [xdc.replace('1.350', '0.000'), xdc.replace('-setup', '-hold'), xdc + xdc,
                    xdc + 'set_false_path -from [get_ports ap_rst_n]\n',
                    xdc + 'set_multicycle_path 2 -setup\n', xdc + 'create_waiver -id TIMING-18\n']:
            with self.subTest(xdc=bad), self.assertRaises(ValueError): constraints(bad)

    def test_terminal_session_binding(self):
        # Synthetic completion objects exercise rejection only; they are never written as observations.
        work = Path('/tmp/physical-audit-test/csr')
        command = 'source {' + str(work / 'run_flow.tcl') + '}'
        job = dict(session_id='test', mode='csr', source_command=command)
        state = dict(status='complete', stage='ooc_complete_pending_independent_audit', mode='csr',
                     owner_pid=123, updated_utc='2026-10-24T20:00:00Z')
        started = dict(process_id=123, log=str(work / 'vivado.log'))
        snap = dict(session_id='test', observed_utc='2026-10-24T20:00:01Z', status=dict(
            is_command_running=False, last_completed_code=0, queue_length=0, process_id=123,
            working_dir=str(work), log_file=started['log'], last_completed=command,
            last_completed_output='SEARCH_PHYSICAL_FLOW_COMPLETE'))
        session_gate(snap, job, state, work, started)
        for key, value in [('is_command_running', True), ('last_completed_code', None),
                           ('last_completed_code', 1), ('queue_length', 1), ('process_id', 124),
                           ('working_dir', '/tmp/other'), ('log_file', '/tmp/other.log'),
                           ('last_completed', 'puts ok'), ('last_completed_output', '')]:
            bad = copy.deepcopy(snap); bad['status'][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                session_gate(bad, job, state, work, started)
        for key, value in [('session_id', 'wrong'), ('observed_utc', '2026-10-24T19:59:59Z')]:
            bad = copy.deepcopy(snap); bad[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): session_gate(bad, job, state, work, started)
        for key, value in [('status', 'running'), ('stage', 'synthesis'), ('mode', 'compact')]:
            bad = dict(state); bad[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): session_gate(snap, job, bad, work, started)


if __name__ == '__main__':
    unittest.main()
