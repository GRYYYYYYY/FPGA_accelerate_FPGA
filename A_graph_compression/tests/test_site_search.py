import unittest
from site_search import search, EMPTY, merge_demands, verified_requirements
from search_experiment import IncompleteDomain
from site_resources import SiteState


class Provider:
    def __init__(self, edges):self.edges=edges
    def neighbors(self,node):
        return [({'src':node,'dst':dst,'pip':pip},{'attributes':{'IS_PSEUDO':'1' if pseudo else '0'}})
                for dst,pip,pseudo in self.edges.get(node,[])]


class SiteSearchTests(unittest.TestCase):
    def test_other_net_site_state_and_congestion_cost(self):
        p=Provider({'s':[('t','short',True),('a','free',False)],'a':[('t','finish',False)]})
        req={'short':{'signal_resources':['site/O']}}
        state=SiteState();state.replace('other',req['short'])
        r=search(p,'s','t',req,site_state=state,net='candidate')
        self.assertEqual([x['pip'] for x in r['path']],['free','finish'])
        state.release('other')
        self.assertEqual(search(p,'s','t',req,site_state=state,net='candidate')['cost'],1)
        r=search(p,'s','t',req,edge_cost=lambda e,p,a,b:10 if e['pip']=='short' else 1)
        self.assertEqual([x['pip'] for x in r['path']],['free','finish'])

    def test_invalid_cost_is_rejected(self):
        p=Provider({'s':[('t','p',False)]})
        for value in (0,-1,float('inf'),float('nan')):
            with self.subTest(value=value),self.assertRaises(ValueError):
                search(p,'s','t',{},edge_cost=lambda *args:value)

    def test_unverified_records_never_become_unconstrained_pips(self):
        records={'p':{'status':'unverified'},'q':{'status':'sampled','signal_resources':['site/O']}}
        self.assertEqual(verified_requirements(records,{}),{})
        good={'q':{'signal_resources':['site/O']}}
        self.assertIn('q',verified_requirements(records,good))
        with self.assertRaises(ValueError):verified_requirements(records,{'q':{'signal_resources':['wrong/O']}})
        records['q']['additional_requirements']=['constant clock input']
        with self.assertRaises(ValueError):verified_requirements(records,good)
        with self.assertRaises(ValueError):search(Provider({'s':[('t','p',True)]}),'s','t',records)

    def test_unknown_adjacency_is_not_sink(self):
        class Partial:
            def neighbors(self,node):raise IncompleteDomain(node)
        r=search(Partial(),'s','t',{})
        self.assertEqual(r['status'],'incomplete_domain')
        self.assertEqual(r['unknown_sources'],['s'])

    def test_protected_resources_and_existing_tree_demands(self):
        p=Provider({'a':[('t','p',True)],'b':[('t','q',True)]})
        req={'p':{'configuration_values':[('mux','A')]},'q':{'configuration_values':[('mux','B')]}}
        initial=merge_demands(EMPTY,{'configuration_values':[('mux','B')]})
        r=search(p,'a','t',req,tree_nodes=['a','b'],initial_demands=initial)
        self.assertEqual([x['pip'] for x in r['path']],['q'])
        r=search(p,'a','t',req,tree_nodes=['a','b'],initial_demands=initial,blocked_pips={'q'})
        self.assertEqual(r['status'],'no_path')

    def test_preserves_alternative_configuration_at_same_node(self):
        p=Provider({'s':[('m','bad',True),('a','good',True)],
                    'a':[('m','ordinary',False)],'m':[('t','finish',True)]})
        r=search(p,'s','t',{'bad':{'configuration_bits':[('LUT',1,1)]},
                          'good':{'configuration_bits':[('LUT',1,0)]},
                          'finish':{'configuration_bits':[('LUT',1,0)]}})
        self.assertEqual(r['status'],'found')
        self.assertEqual([e['pip'] for e in r['path']],['good','ordinary','finish'])

    def test_fixed_resource_and_unknown_semantics_are_explicit(self):
        p=Provider({'s':[('t','p',True)]})
        self.assertEqual(search(p,'s','t',{})['status'],'unknown_site_semantics')
        self.assertEqual(search(p,'s','t',{'p':{'signal_resources':['site/O']}},fixed_signals={'site/O'})['status'],'no_path')

    def test_budget_is_not_no_path(self):
        p=Provider({'s':[('a','p',False)],'a':[('t','q',False)]})
        self.assertEqual(search(p,'s','t',{},max_expansions=1)['status'],'budget_exhausted')
