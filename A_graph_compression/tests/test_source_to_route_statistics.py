"""Reject false repeat coverage and altered serial execution evidence."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_source_to_route_statistics import check_sequence, summarize


class StatisticsAuditTests(unittest.TestCase):
    def records(self):
        return [{'repeat': r, 'condition': {'mode': m, 'execution': e},
                 'application_wall_ms': factor*(r+1)*100,
                 'worker_process_wall_ms': factor*(r+1)*100+20,
                 'parent_pre_native_peak_kib': 100, 'native_child_peak_kib': 50,
                 'stage_ms': {'native_process_ms': factor*(r+1)*90}}
                for r in range(7) for m, e, factor in
                [('csr', 'direct', 1), ('compact', 'direct', 2), ('compact', 'expanded', 1.5)]]

    def test_paired_measured_totals(self):
        summaries, paired = summarize(list(reversed(self.records())))
        self.assertEqual([r['n'] for r in summaries], [7, 7, 7])
        self.assertEqual([r['median_paired_ratio'] for r in paired], [2, 1.5])
        for change in ('missing', 'duplicate', 'repeat', 'nan', 'zero', 'extra_condition'):
            rows = copy.deepcopy(self.records())
            if change == 'missing': rows.pop()
            elif change == 'duplicate': rows[-1] = rows[0]
            elif change == 'repeat': rows[0]['repeat'] = 7
            elif change == 'nan': rows[0]['application_wall_ms'] = float('nan')
            elif change == 'zero': rows[0]['application_wall_ms'] = 0
            else: rows[0]['condition']['extra'] = True
            with self.subTest(change=change), self.assertRaises(ValueError): summarize(rows)

    def test_execution_sequence_and_timestamps(self):
        order = [2, 0, 1]
        submissions = {i: {'execution_position': n, 'started_monotonic_ns': (n*2+1)*1000000,
                           'owner_pid': 17, 'cpu': 125} for n, i in enumerate(order)}
        receipts = {i: {'finished_monotonic_ns': (n*2+2)*1000000, 'exit_code': 0,
                        'worker_process_wall_ms': 1} for n, i in enumerate(order)}
        self.assertEqual(check_sequence(order, submissions, receipts, 17, 125), 6000000)
        for change in ('position', 'overlap', 'owner', 'cpu', 'wall', 'exit', 'previous_block'):
            s, r = copy.deepcopy(submissions), copy.deepcopy(receipts)
            previous = 0
            if change == 'position': s[2]['execution_position'] = 1
            elif change == 'overlap': s[0]['started_monotonic_ns'] = 1500000
            elif change == 'owner': s[2]['owner_pid'] = 18
            elif change == 'cpu': s[2]['cpu'] = 126
            elif change == 'wall': r[2]['worker_process_wall_ms'] = 100
            elif change == 'exit': r[2]['exit_code'] = 1
            else: previous = 2000000
            with self.subTest(change=change), self.assertRaises(ValueError):
                check_sequence(order, s, r, 17, 125, previous)


if __name__ == '__main__': unittest.main()
