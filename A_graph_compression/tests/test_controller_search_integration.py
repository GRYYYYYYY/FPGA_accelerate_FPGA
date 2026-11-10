from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from controller_search_transform import transform_search

class ControllerSearchIntegration(unittest.TestCase):
    def test_native_interface_all_scenarios(self):
        with tempfile.TemporaryDirectory() as tmp:
            w=Path(tmp)
            for p in (ROOT/'src/native').glob('*.hpp'):shutil.copyfile(p,w/p.name)
            for name in ['search_heap.hpp','search_heap_external.hpp','search_site_state.hpp','search_label_index.hpp','search_label_records.hpp','search_controller.hpp']:shutil.copyfile(ROOT/'hardware/vitis'/name,w/name)
            p=w/'site_search.hpp';p.write_text(transform_search(p.read_text()))
            limits='''struct DriverLimits {
                static constexpr unsigned nodes=32,degree=64,roots=32,unknown_pips=128,path=64,expansions=1000;
                static constexpr unsigned signals=8,bits=8,values=8,slots=128,labels=64,heap=128;
            };
            #define BOUNDED_CONTROLLER_LIMITS DriverLimits
            '''
            driver=(ROOT/'tests/native_site_search_driver.cpp').read_text().replace('../src/native/site_search.hpp','site_search.hpp')
            (w/'driver.cpp').write_text(limits+driver)
            for name,src in [('reference',ROOT/'tests/native_site_search_driver.cpp'),('controller',w/'driver.cpp')]:
                subprocess.run(['g++','-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(src),'-o',str(w/name)],check=True)
            for i in range(12):
                outputs=[json.loads(subprocess.run([str(w/name),str(i)],capture_output=True,text=True,check=True).stdout) for name in ['reference','controller']]
                self.assertEqual(*outputs)

if __name__=='__main__':unittest.main()
