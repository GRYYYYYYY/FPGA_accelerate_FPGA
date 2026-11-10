import json
from pathlib import Path
import tempfile
import unittest

from src.trace_analysis import summarize


def partition(task, successors=()):
    return {'record':'partition', 'task_id':task, 'bbox':[task*10,0,task*10+5,5],
            'connection_indices':[task], 'successors':list(successors)}


def attempt(task, number, iteration=1, write=False, truncated=False):
    return {'record':'attempt', 'connection_index':task, 'attempt_id':number, 'parent_attempt_id':0,
            'iteration':iteration, 'status':'routed', 'elapsed_ns':100, 'pops':2, 'truncated':truncated,
            'label_access_resources':['123'], 'label_write_resources':['123'] if write else [],
            'path_resources':[], 'dense_label_pages_512':[0]}


class AuditTests(unittest.TestCase):
    def analyze(self, parts, attempts, total=None):
        footer = {'record':'verification', 'attempts_total':len(attempts) if total is None else total,
                  'attempts_recorded':len(attempts), 'unrouted':0,'bad_paths':0,'final_overused_nodes':0}
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'trace.jsonl'
            p.write_text(''.join(json.dumps(r)+'\n' for r in [*parts,*attempts,footer]))
            return summarize(p)

    def test_read_only_sharing_is_separate_from_read_write_hazard(self):
        r=self.analyze([partition(0),partition(1)],[attempt(0,1),attempt(1,2)])
        self.assertEqual(r['unordered_label_access']['iteration_task_pairs'],1)
        self.assertEqual(r['unordered_label_read_write']['iteration_task_pairs'],0)

    def test_disjoint_boxes_do_not_hide_label_hazard(self):
        r=self.analyze([partition(0),partition(1)],[attempt(0,1,write=True),attempt(1,2)])
        self.assertEqual(r['unordered_label_read_write']['bbox_disjoint_pairs'],1)
        self.assertEqual(r['unordered_path_sharing']['iteration_task_pairs'],0)

    def test_transitive_dependency_orders_tasks(self):
        r=self.analyze([partition(0,[1]),partition(1,[2]),partition(2)],
                       [attempt(0,1,write=True),attempt(2,2)])
        self.assertEqual(r['unordered_label_read_write']['iteration_task_pairs'],0)

    def test_iteration_barrier_separates_accesses(self):
        r=self.analyze([partition(0),partition(1)], [attempt(0,1,write=True),attempt(1,2,iteration=2)])
        self.assertEqual(r['unordered_label_read_write']['iteration_task_pairs'],0)

    def test_sampling_and_truncation_are_not_full_coverage(self):
        for total,truncated in [(2,False),(1,True)]:
            with self.subTest(total=total,truncated=truncated):
                r=self.analyze([partition(0)], [attempt(0,1,truncated=truncated)],total=total)
                self.assertFalse(r['coverage']['all_attempts_and_instrumented_sets_recorded'])

    def test_duplicate_assignment_rejected(self):
        p=partition(1); p['connection_indices']=[0]
        with self.assertRaisesRegex(ValueError,'multiple tasks'):
            self.analyze([partition(0),p],[])

    def test_cycle_rejected(self):
        with self.assertRaisesRegex(ValueError,'DAG'):
            self.analyze([partition(0,[1]),partition(1,[0])],[])

    def test_missing_footer_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'trace.jsonl'; p.write_text(json.dumps(partition(0))+'\n')
            with self.assertRaisesRegex(ValueError,'Incomplete trace'):
                summarize(p)

    def test_duplicate_attempt_ids_rejected(self):
        with self.assertRaisesRegex(ValueError,'count/ID mismatch'):
            self.analyze([partition(0)], [attempt(0,1),attempt(0,1)])


if __name__ == '__main__':
    unittest.main()
