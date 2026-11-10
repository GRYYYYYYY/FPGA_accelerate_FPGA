"""Configuration-label search differential cases, not real routing performance."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from site_search import search,merge_demands,EMPTY
from site_resources import SiteState
from search_experiment import IncompleteDomain


@unittest.skipUnless(shutil.which('g++'),'g++ required')
class NativeSiteSearchTests(unittest.TestCase):
    def test_configuration_labels_unknowns_constraints_and_costs(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary=Path(tmp)/'search'
            subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror',
                str(ROOT/'tests/native_site_search_driver.cpp'),'-o',str(binary)],check=True)
            for scenario in range(12):
                with self.subTest(scenario=scenario):
                    rows={};requirements={};roots=[0];initial=EMPTY;state=SiteState()
                    def add(a,b,p,pseudo):
                        rows.setdefault(a,[]).append(({'src':a,'dst':b,'pip':p},{'attributes':{'IS_PSEUDO':'1' if pseudo else '0'}}))
                    if scenario<=1:
                        add(0,1,0,True);add(0,2,1,True);add(2,1,2,False);add(1,3,3,True)
                        requirements={p:{'configuration_bits':[('r0',1,int(p==0))]} for p in (0,1,3)}
                    elif scenario in (2,3):add(0,3,0,True)
                    elif scenario in (5,6):
                        roots=[0,1];initial=merge_demands(EMPTY,{'configuration_values':[('r0',2)]})
                        add(0,3,0,True);add(1,3,1,True)
                        requirements={p:{'configuration_values':[('r0',p+1)]} for p in (0,1)}
                    else:
                        add(0,3,0,True);requirements={0:{'signal_resources':['r1']}}
                        if scenario==4:state=SiteState(fixed_signals=[('r1',99)])
                        if scenario in (7,8):add(0,2,1,False);add(2,3,2,False)
                        if scenario==7:state.replace(1,requirements[0])
                        if scenario==9:requirements[0]['status']='unverified'
                        if scenario==11:requirements[0]['additional_requirements']=['unresolved']
                    class Provider:
                        def neighbors(self,node):
                            if scenario==3 and node==0:raise IncompleteDomain(node)
                            return rows.get(node,[])
                    try:
                        r=search(Provider(),0,3,requirements,tree_nodes=roots,initial_demands=initial,
                            site_state=state,net=0,max_expansions=1 if scenario==1 else 100,
                            blocked_pips={1} if scenario==6 else (),
                            edge_cost=lambda e,p,a,b:-1 if scenario==10 else (10 if scenario==8 and e['pip']==0 else 1))
                        demands=r.get('demands')
                        expected={'status':r['status'],'expanded':r['expanded'],'blocked':r.get('blocked'),
                            'cost':r.get('cost'),'path':[e['pip'] for e in r.get('path',[])],
                            'unknown_sources':r['unknown_sources'],'unknown_pips':r['unknown_pips'],
                            'demands':None if demands is None else [list(demands[0]),[list(v) for v in demands[1]],[list(v) for v in demands[2]]]}
                        if demands is not None:
                            expected['demands'][0]=[int(v[1:]) for v in demands[0]]
                            for component in expected['demands'][1:]:
                                for v in component:v[0]=int(v[0][1:])
                    except ValueError:expected={'error':True}
                    actual=subprocess.run([str(binary),str(scenario)],capture_output=True,text=True,check=True)
                    self.assertEqual(json.loads(actual.stdout),expected)


if __name__=='__main__':unittest.main()
