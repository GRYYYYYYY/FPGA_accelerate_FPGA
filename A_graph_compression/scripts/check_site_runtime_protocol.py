#!/usr/bin/env python3
"""Small real-input protocol check; not a full-query performance experiment."""
import json
import subprocess
from pathlib import Path
from native_site_runtime_benchmark import METRICS,sha256
from real_experiment import write_new
ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'data/derived/native_site_runtime_protocol_20261023_v1';out.mkdir(parents=True,exist_ok=False)
    results=[];files={}
    def bind(path):files[str(path)]=sha256(path)
    for mode in ('csr','compact'):
        folder=ROOT/f'data/derived/native_site_{mode}_inputs_20261023_v1'
        manifest=json.loads((folder/'manifest.json').read_text())
        fixture=Path(manifest['routing_fixture']);words=fixture.read_text().split();index=2
        for width in (1,2,1):count=int(words[index]);index+=1+count*width
        query_start=index+1;query_end=query_start+3+int(words[query_start+2])
        short=out/f'{mode}.routing.txt';short.write_text('\n'.join(words[:index]+['1']+words[query_start:query_end])+'\n')
        base=[manifest['image'],str(short),str(folder/'sites.txt'),'4096','80','200000','8']
        reference_file=out/f'{mode}.reference.json'
        with reference_file.open('x') as stream:
            subprocess.run([str(ROOT/'build/native_site_20261023_v1'),*base],stdout=stream,stderr=subprocess.PIPE,check=True)
        reference=json.loads(reference_file.read_text());expected={k:v for k,v in reference.items() if k not in METRICS}
        for execution in (('direct',) if mode=='csr' else ('direct','expanded')):
            path=out/f'{mode}.{execution}.json'
            with path.open('x') as stream:
                subprocess.run([str(ROOT/'build/native_site_runtime_20261023_v1'),*base,execution],stdout=stream,stderr=subprocess.PIPE,check=True)
            raw=json.loads(path.read_text())
            assert raw['execution']==execution and len(raw['batches'])==len(raw['export_ms'])==2
            for batch in raw['batches']:
                assert {k:v for k,v in batch.items() if k not in METRICS}==expected
                assert all(batch[k]>=0 for k in METRICS)
                assert batch['peak_kib']>0
            assert raw['batches'][1]['peak_kib']>=raw['batches'][0]['peak_kib']
            assert all(v>=0 for v in raw['export_ms'])
            if execution=='direct':
                assert raw['batches'][0]['cache_misses']>0
                assert raw['batches'][1]['cache_misses']==0
                assert raw['batches'][1]['cache_hits']==raw['batches'][0]['cache_hits']+raw['batches'][0]['cache_misses']
            else:
                assert raw['materialization_ms']>0
                assert all(batch['cache_hits']==0 for batch in raw['batches'])
            results.append({'mode':mode,'execution':execution,'complete_batches_equal':True,
                'batches':[{k:b[k] for k in METRICS} for b in raw['batches']],'export_ms':raw['export_ms'],
                'materialization_ms':raw['materialization_ms']})
            bind(path)
        for path in (short,reference_file,fixture,folder/'sites.txt',Path(manifest['image'])):bind(path)
    for path in [Path(__file__),ROOT/'scripts/native_site_runtime_benchmark.py',ROOT/'src/native/site_runtime.cpp',
                 ROOT/'build/native_site_runtime_20261023_v1',ROOT/'build/native_site_20261023_v1']:bind(path)
    write_new(ROOT/'results/native_site_runtime_protocol_20261023_v1.json',{'status':'three_conditions_first_resident_protocol_verified',
        'scope':'One real query only; not full workload or statistical evidence.','conditions':results,'files':files})
    print('SITE_RUNTIME_PROTOCOL_VERIFIED',len(results))


if __name__=='__main__':main()
