from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from label_index_transform import transform_search as indexed
from label_records_transform import transform_search
from prepare_search_heap_router import transform_search as heap_search

class LabelRecordIntegration(unittest.TestCase):
    def test_full_search_synthetic_semantics(self):
        with tempfile.TemporaryDirectory() as tmp:
            w=Path(tmp)
            for p in (ROOT/'src/native').glob('*.hpp'):shutil.copyfile(p,w/p.name)
            for name in ['search_heap.hpp','search_site_state.hpp','search_label_index.hpp','search_label_records.hpp']:shutil.copyfile(ROOT/'hardware/vitis'/name,w/name)
            p=w/'site_search.hpp';p.write_text(transform_search(indexed(heap_search(p.read_text()))))
            driver=(ROOT/'tests/native_site_search_driver.cpp').read_text().replace('../src/native/site_search.hpp','site_search.hpp')
            (w/'driver.cpp').write_text(driver)
            for name,src in [('reference',ROOT/'tests/native_site_search_driver.cpp'),('bounded',w/'driver.cpp')]:
                subprocess.run(['g++','-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-DLABEL_INDEX_LABELS=64','-DLABEL_INDEX_SLOTS=128',str(src),'-o',str(w/name)],check=True)
            for i in range(12):
                outputs=[json.loads(subprocess.run([str(w/name),str(i)],capture_output=True,text=True,check=True).stdout) for name in ['reference','bounded']]
                self.assertEqual(*outputs)

if __name__=='__main__':unittest.main()
