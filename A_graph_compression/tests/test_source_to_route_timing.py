"""Reject incomplete wall-time accounting in the integrated worker."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_source_to_route import check_timing,STAGES

class IntegratedTimingTests(unittest.TestCase):
    def test_accounting_and_rejections(self):
        stages={k:1 for k in STAGES};stages['native_process_ms']=50
        report={'stage_ms':stages,'application_wall_ms':60,'post_route_audit_ms':5,
                'parent_pre_native_peak_kib':200,'native_child_peak_kib':101}
        outer={'worker_process_wall_ms':70};native={'process_wall_ms':50}
        raw={'export_ms':[1,1],'materialization_ms':0.5,'batches':[
            {'preparation_ms':2,'route_ms':10-i*2,'peak_kib':100+i,'logical_bytes':5,'cache_hits':i,'cache_misses':1-i} for i in range(2)]}
        check_timing(report,outer,native,raw)
        for case in ('application','worker','native','materialization','peak','stage','negative'):
            with self.subTest(case=case):
                r,o,n,x=deepcopy((report,outer,native,raw))
                if case=='application':r['application_wall_ms']=1
                elif case=='worker':o['worker_process_wall_ms']=1
                elif case=='native':n['process_wall_ms']=1
                elif case=='materialization':x['materialization_ms']=3
                elif case=='peak':r['native_child_peak_kib']=90
                elif case=='stage':del r['stage_ms']['fixture_write_ms']
                else:x['export_ms'][0]=-1
                with self.assertRaises(ValueError):check_timing(r,o,n,x)

if __name__=='__main__':unittest.main()
