from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from label_index_transform import transform_search
from prepare_search_heap_router import transform_search as heap_search

class LabelIndexIntegration(unittest.TestCase):
    def test_search_and_explicit_capacity_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            w=Path(tmp)
            for p in (ROOT/'src/native').glob('*.hpp'):shutil.copyfile(p,w/p.name)
            for name in ['search_heap.hpp','search_site_state.hpp','search_label_index.hpp']:shutil.copyfile(ROOT/'hardware/vitis'/name,w/name)
            p=w/'site_search.hpp';p.write_text(transform_search(heap_search(p.read_text())))
            driver=(ROOT/'tests/native_site_search_driver.cpp').read_text().replace('../src/native/site_search.hpp','site_search.hpp')
            (w/'driver.cpp').write_text(driver)
            builds=[('reference',ROOT/'tests/native_site_search_driver.cpp',[]),('indexed',w/'driver.cpp',['-DLABEL_INDEX_LABELS=64','-DLABEL_INDEX_SLOTS=128']),('small',w/'driver.cpp',['-DLABEL_INDEX_LABELS=1','-DLABEL_INDEX_SLOTS=2'])]
            for name,src,flags in builds:
                subprocess.run(['g++','-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*flags,str(src),'-o',str(w/name)],check=True)
            def run(name,i):return json.loads(subprocess.run([str(w/name),str(i)],capture_output=True,text=True,check=True).stdout)
            for i in range(12):self.assertEqual(run('indexed',i),run('reference',i))
            for i in [0,5]:
                r=run('small',i);self.assertEqual(r['status'],'capacity_exhausted');self.assertEqual(r['path'],[]);self.assertIsNone(r['cost'])
            self.assertEqual(run('small',2),run('reference',2))

if __name__=='__main__':unittest.main()
