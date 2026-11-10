"""Synthetic validator inputs only: these tests do not establish board execution."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_kernel_router_board import validate_content,OLD_METRICS


def fixture(execution):
    reference={'status':'routed','scope':'tested_site_instances_only',
        'routes':[{'net':i,'nodes':[i],'edges':[[i,i+1,2,3,4,5,6,0]],'demands':[[],[],[]],'complete':True} for i in range(1062)],
        'iterations':[{'conflicts':[],'site_conflicts':[],'incomplete':[],
                       'connections':[[{'status':'found','cost':1,'expanded':1,'blocked':0,'unknown_sources':[],'unknown_pips':[]}]]}],
        **{k:0 for k in OLD_METRICS}}
    batch={k:copy.deepcopy(v) for k,v in reference.items() if k!='logical_bytes'}
    batch.update(route_ms=5,preparation_ms=1,peak_kib=1,kernel_calls=1 if execution=='direct' else 0,
                 cache_misses=1,kernel_payload_bytes=40 if execution=='direct' else 0,
                 xrt_h2d_ms=.1 if execution=='direct' else 0,xrt_kernel_wall_ms=.1 if execution=='direct' else 0,
                 xrt_d2h_ms=.1 if execution=='direct' else 0)
    calls=2 if execution=='direct' else (274732+127)//128
    requests=2 if execution=='direct' else 274732
    transport={'backend':'xrt_hardware','complete':True,'memory':'HBM[0]','device_bdf':'synthetic',
               'device_name':'synthetic','xclbin_uuid':'synthetic','groups':[0]*6,'calls':calls,'requests':requests,
               'h2d_bytes':32784*requests+104*calls,'d2h_bytes':32780*requests+104*calls,
               'h2d_ms':.2,'kernel_wall_ms':.2,'d2h_ms':.2,'setup_ms':1,'graph_h2d_ms':1}
    raw={'backend':'xrt_hardware_adjacency_cpu_search','execution':execution,'batches':[copy.deepcopy(batch),copy.deepcopy(batch)],
         'materialization_ms':1,'export_ms':[.1,.1]}
    return raw,transport,reference


class HybridAuditTests(unittest.TestCase):
    def test_both_execution_protocols_and_corruptions(self):
        for execution in ['direct','expanded']:
            raw,transport,reference=fixture(execution)
            self.assertEqual(len(validate_content(raw,transport,reference,execution,'HBM[0]',274732)),2)
        mutations=[
            lambda r,t:r.update(backend='cpu_vitis_abi_cmodel'),
            lambda r,t:r['batches'].pop(),
            lambda r,t:r['batches'][0]['routes'][0]['edges'][0].__setitem__(6,999),
            lambda r,t:r['batches'][0]['routes'][0]['demands'][0].append(4),
            lambda r,t:r['batches'][0]['iterations'][0]['connections'][0][0].update(cost=2),
            lambda r,t:r['batches'][0]['iterations'][0]['connections'][0][0]['unknown_sources'].append(5),
            lambda r,t:r['batches'][0].update(xrt_kernel_wall_ms=50),
            lambda r,t:r['batches'][0].update(route_ms=float('nan')),
            lambda r,t:r['batches'][0].update(kernel_calls=0),
            lambda r,t:t.update(complete=False),
            lambda r,t:t.update(memory='DDR[0]'),
            lambda r,t:t.update(device_bdf=''),
            lambda r,t:t.update(groups=[False]*6),
            lambda r,t:t.update(calls=1),
            lambda r,t:t.update(requests=3),
            lambda r,t:t.update(h2d_bytes=t['h2d_bytes']+1),
            lambda r,t:t.update(d2h_bytes=t['d2h_bytes']-1),
            lambda r,t:t.update(kernel_wall_ms=1),
            lambda r,t:r.update(export_ms=[-1,.1]),
        ]
        for i,mutate in enumerate(mutations):
            raw,transport,reference=fixture('direct');mutate(raw,transport)
            with self.subTest(mutation=i),self.assertRaises(ValueError):
                validate_content(raw,transport,reference,'direct','HBM[0]',274732)
        raw,transport,reference=fixture('expanded');transport['requests']-=1
        with self.assertRaises(ValueError):validate_content(raw,transport,reference,'expanded','HBM[0]',274732)


if __name__=='__main__':unittest.main()
