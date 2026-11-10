"""Fault injection for protected resources, selected route identity and placement."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from check_netlist_readback import check
from netlist import read_snapshot, routing_queries


class ReadbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot=read_snapshot(ROOT/'data/netlist/routeracc_cost_u280_20261022_v1/snapshot.tsv')
        cls.name=routing_queries(cls.snapshot)[0]['net']
        net=cls.snapshot['nets'][cls.name]
        cls.routes={cls.name:{'nodes':net['nodes'],'edges':[{'pip':p} for p in net['pips']]}}

    def test_reference_and_endpoint_order(self):
        after=deepcopy(self.snapshot)
        after['nets'][self.name]['site_pins'].reverse()
        self.assertEqual(1,check(self.snapshot,after,self.routes)['selected_route_readback_exact'])

    def test_unknown_candidate_net_rejected(self):
        with self.assertRaisesRegex(ValueError,'Unknown selected'):
            check(self.snapshot,self.snapshot,{'missing':self.routes[self.name]})

    def test_protected_clock_resource_change_rejected(self):
        after=deepcopy(self.snapshot)
        name=next(n for n,v in after['nets'].items() if v['type']=='GLOBAL_CLOCK')
        after['nets'][name]['pips'].pop()
        with self.assertRaisesRegex(ValueError,'Protected net resources'):
            check(self.snapshot,after,self.routes)

    def test_selected_parallel_pip_identity_rejected(self):
        after=deepcopy(self.snapshot)
        after['nets'][self.name]['pips'][0]='different_physical_pip'
        with self.assertRaisesRegex(ValueError,'Applied node/PIP'):
            check(self.snapshot,after,self.routes)

    def test_placement_change_rejected(self):
        after=deepcopy(self.snapshot)
        next(iter(after['cells'].values()))['loc']='different_site'
        with self.assertRaisesRegex(ValueError,'LOC/BEL'):
            check(self.snapshot,after,self.routes)

    def test_endpoint_remapping_rejected(self):
        after=deepcopy(self.snapshot)
        after['nets'][self.name]['site_pins'][0]['node']='different_canonical_node'
        with self.assertRaisesRegex(ValueError,'connectivity/terminals'):
            check(self.snapshot,after,self.routes)


if __name__=='__main__':unittest.main()
