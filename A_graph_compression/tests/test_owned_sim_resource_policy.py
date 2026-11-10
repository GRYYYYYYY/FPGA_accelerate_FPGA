import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from owned_sim_resource_policy_v1 import POLICY, abort_reason


class ResourcePolicyTest(unittest.TestCase):
    def setUp(self):
        self.before = dict(policy=POLICY, raw_free_bytes=120*1024**3,
                           events={'oom': 0, 'oom_kill': 2, 'max': 249})

    def test_low_free_and_reclaim_events_do_not_abort(self):
        after = copy.deepcopy(self.before)
        after.update(raw_free_bytes=0, stats={'file': 160*1024**3})
        after['events']['max'] += 100
        self.assertIsNone(abort_reason(self.before, after))
        after['stats'] = {'file': 0}
        self.assertIsNone(abort_reason(self.before, after))

    def test_new_oom_or_counter_reset_is_rejected(self):
        for key in ('oom', 'oom_kill'):
            after = copy.deepcopy(self.before)
            after['events'][key] += 1
            self.assertEqual(abort_reason(self.before, after), 'new_cgroup_'+key)
        after = copy.deepcopy(self.before)
        after['events']['oom_kill'] = 0
        self.assertEqual(abort_reason(self.before, after), 'oom_accounting_reset')

    def test_missing_or_wrong_policy_accounting_is_rejected(self):
        after = copy.deepcopy(self.before)
        del after['events']['oom']
        with self.assertRaises(KeyError):
            abort_reason(self.before, after)
        after = copy.deepcopy(self.before)
        after['policy'] = 'old_rawfree'
        with self.assertRaises(ValueError):
            abort_reason(self.before, after)


if __name__ == '__main__':
    unittest.main()
