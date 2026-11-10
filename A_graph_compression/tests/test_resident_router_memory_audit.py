"""Mutate isolated copies of the actual candidate; never edits frozen evidence."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_resident_router_memory_plan import audit


class RejectCorruption(unittest.TestCase):
    def test_bad_shared_buffers_and_configs_never_publish(self):
        original=ROOT/'hardware/vitis/resident_router_memory_v1'
        source=json.loads((original/'plan.json').read_text())
        def alter_alias(r):r['layouts']['hbm_shared_buffers']['search_route_tree_top.roots']='HBM[31]'
        def alter_bundle(r):r['layouts']['hbm_shared_buffers']['search_kernel_top.config']='HBM[31]'
        def alter_alignment(r):next(iter(r['allocations'].values()))['requested_bytes']+=1
        def alter_accounting(r):r['total_requested_bytes']-=4096
        def alter_missing(r):r['allocations'].pop(next(iter(r['allocations'])))
        def alter_source(r):r['files'][next(iter(r['files']))]='0'*64
        def alter_cfg(r):r['configs']['ddr_shared_buffers.cfg']='0'*64
        def alter_keys(r):r['layouts']['hbm_shared_buffers']['search_kernel_top.keys']='HBM[5]'
        for change in [alter_alias,alter_bundle,alter_alignment,alter_accounting,alter_missing,alter_source,alter_cfg,alter_keys]:
            with self.subTest(change=change.__name__),tempfile.TemporaryDirectory() as directory:
                folder=Path(directory);r=copy.deepcopy(source);change(r)
                for p in original.glob('*.cfg'):shutil.copyfile(p,folder/p.name)
                (folder/'plan.json').write_text(json.dumps(r))
                output=folder/'audit.json'
                with self.assertRaises(ValueError):audit(folder,output)
                self.assertFalse(output.exists())


if __name__=='__main__':unittest.main()
