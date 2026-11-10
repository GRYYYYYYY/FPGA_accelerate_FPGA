"""Full component negotiation differential cases; real adapters remain separate."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from site_netlist_routing import route_batch


@unittest.skipUnless(shutil.which('g++'),'g++ required')
class NativeSiteRoutesTests(unittest.TestCase):
    def test_multinet_configuration_negotiation_and_failure_states(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary=Path(tmp)/'routes'
            subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror',
                str(ROOT/'tests/native_site_routes_driver.cpp'),'-o',str(binary)],check=True)
            for scenario in range(12):
                with self.subTest(scenario=scenario):
                    rows={};requirements={};middle=2 if scenario==9 else 3
                    for pip,(a,b) in enumerate([(0,2),(2,6),(1,middle),(middle,7),(1,4),(4,5),(5,8),(8,9),(9,7)]):
                        rows.setdefault(a,[]).append(({'src':a,'dst':b,'pip':pip},{'attributes':{'IS_PSEUDO':'1' if pip in (0,2) else '0'}}))
                    for pip in (0,2):
                        if scenario in (1,4):d={'configuration_bits':[('r1',1,int(pip!=0))]}
                        elif scenario==2:d={'configuration_values':[('r1',1 if pip==0 else 2)]}
                        elif scenario==3:d={'configuration_bits':[('r1',1 if pip==0 else 2,1 if pip==0 else 0)]}
                        else:d={'signal_resources':['r1']}
                        if scenario!=5:requirements[pip]=d
                    class Provider:
                        def neighbors(self,node):return rows.get(node,[])
                    queries=[{'net':0,'source':0,'sinks':[2,6] if scenario==7 else [6]},
                             {'net':1,'source':1,'sinks':[7]}]
                    snapshot={'nets':{0:{},1:{}}}
                    if scenario in (8,10):snapshot['nets']['protected']={'nodes':[4] if scenario==8 else [],'pips':[2] if scenario==10 else [],'site_pins':[]}
                    r=route_batch(Provider(),snapshot,queries,requirements,max_iterations=1 if scenario==11 else 8,
                        max_expansions=1 if scenario==6 else 100,present_cap=8,
                        fixed_bits=[('r1',1,0)] if scenario==4 else ())
                    def converted(d):
                        return [[int(v[1:]) for v in d[0]],[[int(v[0][1:]),*v[1:]] for v in d[1]],
                                [[int(v[0][1:]),v[1]] for v in d[2]]]
                    expected={'status':r['status'],'routes':[{'net':net,'complete':v['complete'],'nodes':v['nodes'],
                        'pips':[e['pip'] for e in v['edges']],'demands':converted(r['site_demands'][net])} for net,v in sorted(r['routes'].items())],
                        'iterations':[]}
                    for v in r['iterations']:
                        expected['iterations'].append({'conflicts':[[n,users] for n,users in sorted(v['conflicts'].items())],
                            'site_conflicts':[[c['kind'],int(c['resource'][1:]),c['nets']] for c in v['site_conflicts']],
                            'incomplete':v['incomplete_nets'],
                            'connections':[[{'status':c['status'],'cost':c.get('cost'),'expanded':c['expanded'],'blocked':c.get('blocked'),
                                'unknown_sources':c['unknown_sources'],'unknown_pips':c['unknown_pips']} for c in o['connections']] for o in v['outcomes']]})
                    actual=subprocess.run([str(binary),str(scenario)],capture_output=True,text=True,check=True)
                    self.assertEqual(json.loads(actual.stdout),expected)


if __name__=='__main__':unittest.main()
