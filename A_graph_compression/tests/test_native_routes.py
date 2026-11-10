"""Differential multi-round negotiated routing, without physical/site claims."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from netlist_routing import route_batch
from search_experiment import IncompleteDomain


@unittest.skipUnless(shutil.which('g++'),'g++ required')
class NativeRoutesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.binary=Path(cls.tmp.name)/'routes'
        subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra',
                        str(ROOT/'tests/native_routes_driver.cpp'),'-o',str(cls.binary)],check=True)
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def compare(self,iterations=8,budget=100,unknown=False,cap=8):
        rows=[[] for _ in range(12)]
        for pip,(a,b) in enumerate([(0,2),(2,6),(1,2),(2,7),(1,3),(3,4),(4,5),(5,8),(8,9),(9,7)]):
            rows[a].append(({'src':a,'dst':b,'pip':pip},{'attributes':{}}))
        class Provider:
            def neighbors(self,node):
                if unknown and node==2:raise IncompleteDomain(node)
                return rows[node]
        queries=[{'net':0,'source':0,'sinks':[6]},{'net':1,'source':1,'sinks':[7]}]
        r=route_batch(Provider(),{'nets':{0:{},1:{}}},queries,max_iterations=iterations,
                      max_expansions=budget,present_cap=cap)
        expected={'status':r['status'],'routes':[{'net':n,'complete':v['complete'],
                    'nodes':v['nodes'],'pips':[e['pip'] for e in v['edges']]} for n,v in sorted(r['routes'].items())],
                  'history':[[n,v] for n,v in sorted(r['history'].items())], 'iterations':[]}
        for v in r['iterations']:
            expected['iterations'].append({'present':v['present_factor'],
                'conflicts':[[n,users] for n,users in sorted(v['conflicts'].items())],
                'incomplete':v['incomplete_nets'],'unknown':v['unknown_sources'],
                'connections':[{k:c[k] for k in ['status','cost','expanded','examined','fetched','blocked_edges','unknown_sources']}
                               for o in v['outcomes'] for c in o['connections']]})
        result=subprocess.run([str(self.binary),str(iterations),str(budget),str(int(unknown)),str(cap)],
                              capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(result.stdout),expected)
        return r

    def test_conflicts_release_and_history_converge(self):
        r=self.compare();self.assertEqual(r['status'],'routed');self.assertGreater(len(r['iterations']),1)
    def test_iteration_budget_preserves_conflicts(self):self.assertEqual(self.compare(iterations=1)['status'],'incomplete')
    def test_unknown_boundary_is_not_empty_row(self):self.assertEqual(self.compare(unknown=True)['status'],'incomplete')
    def test_search_budget_does_not_claim_complete(self):self.assertEqual(self.compare(budget=1)['status'],'incomplete')
    def test_capped_present_cost(self):self.compare(cap=1)


if __name__=='__main__':unittest.main()
