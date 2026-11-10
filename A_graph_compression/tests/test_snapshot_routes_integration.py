import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from snapshot_routes_transform import transform_routes

def site_fixture(scenario):
    out=['NATIVE_SITES_V1','32','4','2']
    out += ['1','1','1','0'] if scenario==4 else ['0']
    out += ['0','0',str(0 if scenario==5 else 2)]
    if scenario!=5:
        for pip in [0,2]:
            signals=[];bits=[];values=[]
            if scenario in [1,4]:bits=[(1,1,int(pip!=0))]
            elif scenario==2:values=[(1,1 if pip==0 else 2)]
            elif scenario==3:bits=[(1,1 if pip==0 else 2,1 if pip==0 else 0)]
            else:signals=[1]
            out += ['0',str(pip),str(len(signals)),*map(str,signals),str(len(bits))]
            for item in bits:out.extend(map(str,item))
            out.append(str(len(values)))
            for item in values:out.extend(map(str,item))
    out += ['1','1']
    return ' '.join(out)+'\n'

class SnapshotRouteIntegration(unittest.TestCase):
    def test_all_negotiation_scenarios(self):
        with tempfile.TemporaryDirectory() as tmp:
            w=Path(tmp)
            for p in (ROOT/'src/native').glob('*.hpp'):shutil.copyfile(p,w/p.name)
            for name in ['search_heap.hpp','search_heap_external.hpp','search_site_state.hpp','search_label_index.hpp','search_label_records.hpp','search_controller.hpp','search_cost_snapshot.hpp','search_snapshot_provider.hpp']:shutil.copyfile(ROOT/'hardware/vitis'/name,w/name)
            p=w/'site_routes.hpp';p.write_text(transform_routes(p.read_text()))
            original=(ROOT/'tests/native_site_routes_driver.cpp').read_text().replace('0,pip,0,0,0,0','0,pip,0,0,unsigned(pip==0||pip==2),0')
            reference=original.replace('../src/native/site_routes.hpp',str(ROOT/'src/native/site_routes.hpp'))
            (w/'reference.cpp').write_text(reference)
            candidate=original.replace('../src/native/site_routes.hpp','site_routes.hpp').replace('argc!=2','argc!=3')
            limits='''struct DriverLimits:snapshot_route::RegionLimits {
                static constexpr unsigned nodes=32,roots=32,degree=8,path=128,expansions=1000;
                static constexpr unsigned signals=4,bits=4,values=4,labels=128,slots=256,heap=256;
            };
'''
            candidate=candidate.replace('int main(',limits+'int main(')
            start=candidate.index('    site_native::Demands fixed;')
            end=candidate.index('    std::vector<netlist_native::NetQuery> queries=')
            candidate=candidate[:start]+'''    site_native::SiteInputs sites(argv[2]);
    std::set<std::pair<uint32_t,uint32_t>> protected_pips;
    if(scenario==10)protected_pips.emplace(0,2);
    snapshot_inputs::SiteBuffers<DriverLimits> metadata(sites,protected_pips);
'''+candidate[end:]
            start=candidate.index('    auto r=site_native::route_batch(')
            end=candidate.index('    std::cout<<',start)
            candidate=candidate[:start]+'''    auto r=site_native::route_snapshot_batch<DriverLimits>(graph,queries,scenario==8?std::set<uint32_t>{4}:std::set<uint32_t>{},metadata,
        scenario==11?1:8,scenario==6?1:100,8);
    const auto c=snapshot_route::counters;
    std::cerr<<"SNAPSHOT_TEST_COUNTS "<<c.snapshots<<' '<<c.node_occupied<<' '<<c.node_history<<' '<<c.site_occupied<<' '<<c.site_history<<' '<<c.site_found_paths<<' '<<c.failures<<' '<<controller_adapter::counters.searches<<'\\n';
'''+candidate[end:]
            (w/'candidate.cpp').write_text(candidate)
            for name in ['reference','candidate']:
                subprocess.run(['g++','-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(w/(name+'.cpp')),'-o',str(w/name)],check=True)
            for scenario in range(12):
                with self.subTest(scenario=scenario):
                    fixture=w/f'sites_{scenario}.txt';fixture.write_text(site_fixture(scenario))
                    a=subprocess.run([str(w/'reference'),str(scenario)],check=True,capture_output=True,text=True)
                    b=subprocess.run([str(w/'candidate'),str(scenario),str(fixture)],check=True,capture_output=True,text=True)
                    expected=json.loads(a.stdout);self.assertEqual(expected,json.loads(b.stdout))
                    counts=list(map(int,b.stderr.strip().split()[1:]));self.assertEqual(len(counts),8)
                    self.assertEqual(counts[0],2*len(expected['iterations']));self.assertEqual(counts[6],0)
                    self.assertEqual(counts[7],sum(len(c) for r in expected['iterations'] for c in r['connections']))
                    if scenario==0:self.assertGreater(counts[4],0);self.assertGreater(counts[5],0)
                    if scenario==9:self.assertGreater(counts[2],0)

if __name__=='__main__':unittest.main()
