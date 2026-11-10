import copy,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from check_vitis_ooc import quality_gates
from check_netlist_quality import timing_status,route_status,drc_status
class OocGateTests(unittest.TestCase):
    def test_real_positive_and_false_closure_rejected(self):
        solution=ROOT/'build/hls_region_csr_20261023_v1/solution'
        runs=solution/'impl/verilog/project.runs/impl_1'
        t=timing_status(runs/'bd_0_wrapper_timing_summary_routed.rpt')
        r=route_status(solution/'impl/verilog/report/graph_expand_status_routed.rpt')
        d=drc_status(runs/'bd_0_wrapper_drc_routed.rpt')
        self.assertTrue(all(quality_gates(t,r,d).values()))
        for key,value in [('constrained_internal_timing_met',False),('setup_total_endpoints',0),('hold_total_endpoints',0),('no_clock',1),('unconstrained_internal_endpoints',1)]:
            bad=dict(t);bad[key]=value;self.assertFalse(all(quality_gates(bad,r,d).values()))
        for key,value in [('routable nets',0),('fully routed nets',0),('nets with routing errors',1)]:
            bad=dict(r);bad[key]=value;self.assertFalse(all(quality_gates(t,bad,d).values()))
        self.assertFalse(all(quality_gates(t,r,{'total':1}).values()))
if __name__=='__main__':unittest.main()
