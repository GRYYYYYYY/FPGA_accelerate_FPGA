"""Exercise submission and raw-result gates without rerunning the long matrix."""
from copy import deepcopy
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_native_runtime_bound import audit
from check_native_runtime import METRICS
from check_vitis_kernel import digest


class BoundRuntimeTests(unittest.TestCase):
    def test_submission_and_complete_raw_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp);prefix=directory/'worker_000'
            design=[{'repeat':0,'mode':m,'execution':e,'capacity':4096} for m,e in
                    [('csr','direct'),('compact','direct'),('compact','expanded')]]
            random.Random(20261023).shuffle(design);condition=design[0];mode=condition['mode']
            reference={'status':'routed','routes':[{} for _ in range(1062)],'iterations':[]}
            ref=directory/'reference.json';ref.write_text(json.dumps(reference))
            binary=str(ROOT/'build/native_runtime_20261023_v1')
            inputs={'image':'image.agr','fixture':'routing.txt'}
            plan={'owner_pid':123,'jobs':design,'seed':20261023,'cpu':0,
                  'code_inputs_and_references':{str(ref):digest(ref),binary:digest(binary)},
                  'references':{mode:str(ref)},'inputs':{mode:inputs},'limitations':[]}
            (directory/'plan.json').write_text(json.dumps(plan))
            submission={'owner_pid':123,'child_pid':456,'command':[binary,inputs['image'],inputs['fixture'],'4096','80','200000','8',condition['execution']]}
            def submit(s):prefix.with_suffix('.submission.json').write_text(json.dumps(s))
            submit(submission);prefix.with_suffix('.log').write_text('done\n')
            batches=[dict(reference,preparation_ms=2,route_ms=t,peak_kib=100+i,
                          logical_bytes=99,cache_hits=i,cache_misses=1-i) for i,t in enumerate((10,8))]
            raw={'batches':batches,'export_ms':[1,1]}
            def publish(value):
                path=prefix.with_suffix('.raw.json');path.write_text(json.dumps(value));sha=digest(path)
                record={'condition':condition,'both_complete_batches_verified':True,
                        'batches':[{k:b[k] for k in METRICS} for b in value['batches']],
                        'export_ms':value['export_ms'],'process_wall_ms':25,'raw_sha256':sha}
                prefix.with_suffix('.json').write_text(json.dumps(record))
                prefix.with_suffix('.receipt.json').write_text(json.dumps({'exit_code':0,'raw_sha256':sha,
                    'log_sha256':digest(prefix.with_suffix('.log')),'process_wall_ms':25}))
            publish(raw);result=audit(directory,[4096],1,True)
            self.assertEqual(result['submission_commands_verified'],1)
            self.assertIn(str(prefix.with_suffix('.submission.json')),result['artifacts'])
            for index in range(8):
                bad=deepcopy(submission);bad['command'][index]='changed'
                with self.subTest(command_index=index):
                    submit(bad)
                    with self.assertRaises(ValueError):audit(directory,[4096],1,True)
            for key,value in [('owner_pid',321),('child_pid',0),('child_pid',True)]:
                bad=deepcopy(submission);bad[key]=value;submit(bad)
                with self.assertRaises(ValueError):audit(directory,[4096],1,True)
            submit(submission)
            bad=deepcopy(raw);bad['batches'][1]['status']='incomplete';publish(bad)
            with self.assertRaises(ValueError):audit(directory,[4096],1,True)
            publish(raw);prefix.with_suffix('.raw.json').write_text('{}')
            with self.assertRaises(ValueError):audit(directory,[4096],1,True)
            publish(raw);plan['code_inputs_and_references'].pop(binary);(directory/'plan.json').write_text(json.dumps(plan))
            with self.assertRaises(ValueError):audit(directory,[4096],1,True)


if __name__=='__main__':unittest.main()
