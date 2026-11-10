"""Exercise independent measurement/receipt gates without rerunning long jobs."""
from copy import deepcopy
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_native_site_runtime import audit,sha256,METRICS

class SiteRuntimeAuditTests(unittest.TestCase):
    def test_first_resident_metrics_and_rejections(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            design=[{'repeat':0,'mode':m,'execution':e,'capacity':4096} for m,e in [('csr','direct'),('compact','direct'),('compact','expanded')]]
            random.Random(20261023).shuffle(design);condition=design[0];mode=condition['mode']
            reference={'scope':'tested_site_instances_only','status':'routed','routes':[{} for _ in range(1062)],'iterations':[]}
            ref=directory/'reference.json';ref.write_text(json.dumps(reference))
            inputs={'image':'image.agr','fixture':'routing.txt','sites':'sites.txt'}
            plan={'owner_pid':123,'jobs':design,'seed':20261023,'cpu':127,'code_inputs_and_references':{str(ref):sha256(ref)},
                  'references':{mode:str(ref)},'inputs':{mode:inputs},'limitations':[]}
            (directory/'plan.json').write_text(json.dumps(plan))
            command=[str(ROOT/'build/native_site_runtime_20261023_v1'),inputs['image'],inputs['fixture'],inputs['sites'],'4096','80','200000','8',condition['execution']]
            prefix=directory/'worker_000'
            prefix.with_suffix('.submission.json').write_text(json.dumps({'owner_pid':123,'child_pid':456,'command':command}))
            prefix.with_suffix('.log').write_text('done\n')
            batches=[dict(reference,preparation_ms=2,route_ms=t,peak_kib=100+i,logical_bytes=99,cache_hits=i,cache_misses=1-i) for i,t in enumerate((10,8))]
            raw={'execution':condition['execution'],'batches':batches,'export_ms':[1,1],'materialization_ms':0.5}
            def publish(value,wall=25):
                path=prefix.with_suffix('.raw.json');path.write_text(json.dumps(value));digest=sha256(path)
                record={'condition':condition,'both_complete_batches_verified':True,'batches':[{k:b[k] for k in METRICS} for b in value['batches']],
                        'export_ms':value['export_ms'],'materialization_ms':value['materialization_ms'],'process_wall_ms':wall,'raw_sha256':digest}
                prefix.with_suffix('.json').write_text(json.dumps(record))
                prefix.with_suffix('.receipt.json').write_text(json.dumps({'exit_code':0,'raw_sha256':digest,
                    'log_sha256':sha256(prefix.with_suffix('.log')),'process_wall_ms':wall}))
            publish(raw)
            result=audit(directory,[4096],1,True)
            self.assertEqual((result['completed_workers'],result['planned_workers']),(1,3))
            mutations={}
            r=deepcopy(raw);r['batches'][1]['status']='incomplete';mutations['resident_semantics']=r
            r=deepcopy(raw);r['materialization_ms']=3;mutations['uncharged_preparation']=r
            r=deepcopy(raw);r['batches'][1]['peak_kib']=90;mutations['decreasing_lifetime_peak']=r
            r=deepcopy(raw);r['export_ms'][0]=-1;mutations['negative_export']=r
            r=deepcopy(raw);r['execution']='wrong';mutations['wrong_execution']=r
            for name,value in mutations.items():
                with self.subTest(name=name):
                    publish(value)
                    with self.assertRaises(ValueError):audit(directory,[4096],1,True)
            publish(raw,wall=1)
            with self.assertRaises(ValueError):audit(directory,[4096],1,True)
            publish(raw)
            prefix.with_suffix('.raw.json').write_text('{}')
            with self.assertRaises(ValueError):audit(directory,[4096],1,True)

if __name__=='__main__':unittest.main()
