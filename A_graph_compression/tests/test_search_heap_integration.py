"""Verify isolated search transformation and explicit root/relaxation overflow."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from prepare_search_heap_router import transform_search

class HeapSearchIntegration(unittest.TestCase):
    def test_search_semantics_and_overflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            work=Path(tmp)
            for p in (ROOT/'src/native').glob('*.hpp'):shutil.copyfile(p,work/p.name)
            shutil.copyfile(ROOT/'hardware/vitis/search_heap.hpp',work/'search_heap.hpp')
            p=work/'site_search.hpp';p.write_text(transform_search(p.read_text()))
            driver=(ROOT/'tests/native_site_search_driver.cpp').read_text().replace('../src/native/site_search.hpp','site_search.hpp')
            (work/'driver.cpp').write_text(driver)
            builds=[('reference',ROOT/'tests/native_site_search_driver.cpp',[]),('heap',work/'driver.cpp',['-DSEARCH_HEAP_CAPACITY=32']),('small',work/'driver.cpp',['-DSEARCH_HEAP_CAPACITY=1'])]
            for name,source,flags in builds:
                subprocess.run(['g++','-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*flags,str(source),'-o',str(work/name)],check=True)
            def run(name,scenario):
                return json.loads(subprocess.run([str(work/name),str(scenario)],capture_output=True,text=True,check=True).stdout)
            for scenario in range(12):self.assertEqual(run('heap',scenario),run('reference',scenario))
            for scenario in [0,5]:
                r=run('small',scenario);self.assertEqual(r['status'],'capacity_exhausted');self.assertEqual(r['path'],[]);self.assertIsNone(r['cost'])
            self.assertEqual(run('small',2),run('reference',2))

if __name__=='__main__':unittest.main()
