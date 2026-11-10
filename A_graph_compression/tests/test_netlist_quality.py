"""Quality gates reject failed timing, routing, new DRC and changed coverage."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_netlist_quality import compare_quality,drc_status,route_status,timing_status


class QualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory=ROOT/'data/netlist/routeracc_cost_u280_20261022_v1'
        cls.baseline={'route':route_status(directory/'route_status.rpt'),
                      'drc':drc_status(ROOT/'results/netlist_baseline_drc_20261022.rpt'),
                      'timing':timing_status(directory/'timing_summary.rpt')}

    def test_existing_ooc_warning_is_retained(self):
        self.assertEqual('Critical Warning',self.baseline['drc']['issues']['HDOOC-4']['severity'])
        self.assertTrue(compare_quality(self.baseline,self.baseline)['quality_gates_pass'])

    def test_route_error_not_a_pass(self):
        after=deepcopy(self.baseline);after['route']['nets with routing errors']=1
        self.assertFalse(compare_quality(self.baseline,after)['quality_gates_pass'])

    def test_hold_failure_not_a_pass(self):
        after=deepcopy(self.baseline)
        after['timing'].update(WHS=-0.001,hold_failing_endpoints=1,constrained_internal_timing_met=False)
        self.assertFalse(compare_quality(self.baseline,after)['quality_gates_pass'])

    def test_new_drc_not_a_pass(self):
        after=deepcopy(self.baseline)
        after['drc']['issues']['RTSTAT-1']={'severity':'Error','count':1}
        self.assertFalse(compare_quality(self.baseline,after)['quality_gates_pass'])

    def test_lost_constraint_coverage_not_a_pass(self):
        after=deepcopy(self.baseline);after['timing']['unconstrained_internal_endpoints']=1
        self.assertFalse(compare_quality(self.baseline,after)['quality_gates_pass'])


if __name__=='__main__':unittest.main()
