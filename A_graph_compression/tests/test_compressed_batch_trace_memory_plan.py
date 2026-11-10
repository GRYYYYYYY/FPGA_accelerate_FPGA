"""Reject corrupted copies of the actual single-CU candidate without publishing."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from check_compressed_batch_trace_memory_plan import audit
class Reject(unittest.TestCase):
    def test_actual_manifest_corruptions(self):
        original=ROOT/'hardware/vitis/compressed_batch_trace_memory_v1';r=json.loads((original/'plan.json').read_text())
        def wrong_source(x):x['kernels']['search_batch_trace_top_v2'][0]['depth']-=1
        def wrong_width(x):x['kernels']['search_batch_trace_top_v2'][0]['element_bytes']=8
        def wrong_argument(x):x['kernels']['search_batch_trace_top_v2'][0]['name']='different'
        def duplicate(x):x['allocations'][next(iter(x['allocations']))]['endpoints']*=2
        def missing(x):x['allocations'].pop(next(iter(x['allocations'])))
        def wrong_payload(x):next(iter(x['allocations'].values()))['payload_bytes']-=4
        def wrong_alignment(x):next(iter(x['allocations'].values()))['requested_bytes']+=1
        def wrong_total(x):x['total_requested_bytes']-=4096
        def wrong_bundle(x):x['layouts']['hbm_shared_buffers']['search_batch_trace_top_v2.root_nodes']='HBM[31]'
        def wrong_cfg(x):x['configs']['ddr_shared_buffers.cfg']='0'*64
        def missing_layout(x):x['layouts']['hbm_shared_buffers'].pop('search_batch_trace_top_v2.packet')
        def changed_proof(x):x['files'][next(iter(x['files']))]='0'*64
        def wrong_channels(x):x['hbm_channels_used']-=1
        def wrong_summary(x):x['hbm_groups'][-1]['reserve_bytes']=0
        def wrong_alias(x):x['aliases']=[['search_batch_trace_top_v2.trace_meta','search_batch_trace_top_v2.trace_control']]
        def wrong_trace(x):
            for a in x['kernels']['search_batch_trace_top_v2']:
                if a['name']=='trace_data':a['depth']-=1
        for change in [wrong_channels,wrong_summary,wrong_alias,wrong_trace,wrong_source,wrong_width,wrong_argument,duplicate,missing,wrong_payload,wrong_alignment,wrong_total,wrong_bundle,wrong_cfg,missing_layout,changed_proof]:
            with self.subTest(change=change.__name__),tempfile.TemporaryDirectory() as d:
                p=Path(d);value=copy.deepcopy(r);change(value)
                for f in original.glob('*.cfg'):shutil.copyfile(f,p/f.name)
                (p/'plan.json').write_text(json.dumps(value));output=p/'audit.json'
                with self.assertRaises(ValueError):audit(p,output)
                self.assertFalse(output.exists())
if __name__=='__main__':unittest.main()
