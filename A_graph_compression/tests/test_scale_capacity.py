"""Allocation failures must not conceal wrong results or unrelated errors."""
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from scale_capacity_experiment import classify


class CapacityOutcomeTests(unittest.TestCase):
    def test_only_explicit_allocation_failure_is_capacity_result(self):
        expected={'nodes':10,'known_rows':2,'status':'complete_native_adjacency_scan'}
        good={'exit_code':0,'stdout':json.dumps(expected),'stderr':''}
        self.assertEqual(classify(good,expected),'complete_equivalent_scan')
        self.assertEqual(classify({'exit_code':3,'stdout':'','stderr':'ALLOCATION_FAILED\n'},expected),
                         'address_space_allocation_failed')
        for bad in ({**good,'stdout':json.dumps({**expected,'known_rows':1})},
                    {**good,'stderr':'WARNING'}, {'exit_code':-9,'stdout':'','stderr':''},
                    {'exit_code':2,'stdout':'','stderr':'bad graph'},
                    {'exit_code':3,'stdout':'','stderr':'loader failure'}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):classify(bad,expected)


if __name__=='__main__':unittest.main()
