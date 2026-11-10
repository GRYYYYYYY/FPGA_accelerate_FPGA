"""Reuse complete negotiation tests through a separately named word adapter."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from word_snapshot_routes_transform import transform_routes

class WordSnapshotRoutes(unittest.TestCase):
    def test_native_twelve_scenarios(self):
        # Reuse the frozen integration driver; add only memory/backend names.
        spec=importlib.util.spec_from_file_location('snapshot_driver',ROOT/'tests/test_snapshot_routes_integration.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        original_write=Path.write_text
        def write(path,text,*args,**kwargs):
            if path.name=='candidate.cpp':
                text=text.replace('snapshot_route::','word_snapshot_route::').replace('controller_adapter::','word_controller_adapter::')
                for name in ['search_key_words.hpp','search_controller_words.hpp']:
                    (path.parent/name).write_bytes((ROOT/'hardware/vitis'/name).read_bytes())
            return original_write(path,text,*args,**kwargs)
        with patch.object(module,'transform_routes',transform_routes),patch.object(Path,'write_text',write):
            module.SnapshotRouteIntegration('test_all_negotiation_scenarios').test_all_negotiation_scenarios()

    def test_random_complete_batches(self):
        with tempfile.TemporaryDirectory() as tmp:
            w=Path(tmp)
            generated=transform_routes((ROOT/'src/native/site_routes.hpp').read_text()).replace('namespace site_native {','namespace snapshot_test_native {\nusing namespace site_native;')
            for name in ['site_search.hpp','site_ledger.hpp','netlist_routes.hpp','search_word_snapshot_route_adapter.hpp']:
                generated=generated.replace('#include "'+name+'"','#include "'+str(ROOT/'src/native'/name)+'"')
            (w/'snapshot_test_routes.hpp').write_text(generated)
            driver=(ROOT/'tests/test_snapshot_routes_random.cpp').read_text().replace('../src/native/site_routes.hpp',str(ROOT/'src/native/site_routes.hpp')).replace('snapshot_route::','word_snapshot_route::').replace('controller_adapter::','word_controller_adapter::')
            (w/'driver.cpp').write_text(driver);(w/'sites.txt').write_text('NATIVE_SITES_V1 16 4 4 0 0 0 0 1 1\n')
            subprocess.run(['g++','-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I'+str(ROOT/'hardware/vitis'),'-I'+str(w),str(w/'driver.cpp'),'-o',str(w/'run')],check=True)
            output=subprocess.run([str(w/'run'),str(w/'sites.txt')],capture_output=True,text=True,check=True).stdout
            self.assertIn('SNAPSHOT_ROUTE_FULL_RESULTS_PASS',output)
            print(output,flush=True)

if __name__=='__main__':unittest.main()
