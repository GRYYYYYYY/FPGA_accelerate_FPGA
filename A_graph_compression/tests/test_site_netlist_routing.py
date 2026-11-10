import unittest
from test_netlist_routing import fixture
from search_experiment import ExplicitCSR
from netlist_routing import validate_routes
from site_netlist_routing import route_batch, validate_site_routes
from copy import deepcopy


class SiteNetlistRoutingTests(unittest.TestCase):
    def problem(self):
        return fixture([('a','x'),('x','ta'),('a','y'),('y','z'),('z','ta'),
                        ('b','w'),('w','tb')],{'na':('a',['ta']),'nb':('b',['tb'])})

    def test_site_conflict_without_shared_canonical_nodes_is_negotiated(self):
        graph,snapshot,queries=self.problem()
        req={p:{'signal_resources':['site/O']} for p in ('P000','P005')}
        r=route_batch(ExplicitCSR(graph),snapshot,queries,req)
        self.assertEqual(r['status'],'routed')
        self.assertFalse(r['iterations'][0]['conflicts'])
        self.assertTrue(r['iterations'][0]['site_conflicts'])
        self.assertEqual(len(r['iterations']),2)
        self.assertTrue(validate_routes(graph,snapshot,queries,r)['all_nets_routed_without_conflicts'])
        self.assertNotIn('x',r['routes']['na']['nodes'])
        self.assertTrue(validate_site_routes(graph,snapshot,queries,r,req)['all_nets_site_compatible'])

    def test_shared_init_bit_conflict_is_negotiated(self):
        graph,snapshot,queries=self.problem()
        req={'P000':{'configuration_bits':[('INIT',1,0)]},
             'P005':{'configuration_bits':[('INIT',1,1)]}}
        r=route_batch(ExplicitCSR(graph),snapshot,queries,req)
        self.assertEqual(r['status'],'routed')
        self.assertEqual(r['iterations'][0]['site_conflicts'][0]['kind'],1)

    def test_unknown_pseudo_semantics_cannot_claim_complete(self):
        graph,snapshot,queries=fixture([('a','t')],{'n':('a',['t'])})
        graph['pips']['P000']['attributes']['IS_PSEUDO']='1'
        r=route_batch(ExplicitCSR(graph),snapshot,queries,{})
        self.assertEqual(r['status'],'incomplete')
        self.assertEqual(r['iterations'][0]['outcomes'][0]['connections'][0]['status'],'unknown_site_semantics')

    def test_independent_checker_rejects_forged_occupancy(self):
        graph,snapshot,queries=self.problem()
        req={p:{'signal_resources':['site/O']} for p in ('P000','P005')}
        r=route_batch(ExplicitCSR(graph),snapshot,queries,req)
        bad=deepcopy(r);bad['site_demands']['nb']=[[],[],[]]
        with self.assertRaises(ValueError):validate_site_routes(graph,snapshot,queries,bad,req)
        bad=route_batch(ExplicitCSR(graph),snapshot,queries,req,max_iterations=1)
        bad['status']='routed'
        with self.assertRaises(ValueError):validate_site_routes(graph,snapshot,queries,bad,req)
