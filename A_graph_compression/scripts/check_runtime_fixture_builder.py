#!/usr/bin/env python3
"""Rebuild complete native inputs from regenerated images and physical evidence."""
from copy import deepcopy
import gc
import hashlib
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'adapters')]
from import_vivado import read_export
from netlist import read_snapshot
from packed_graph import PackedGraph
from runtime_fixture_builder import build_runtime_payloads
from real_experiment import write_new


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def main():
    output=ROOT/'data/derived/runtime_fixture_rebuild_20261023_v1';output.mkdir(parents=True,exist_ok=False)
    frozen={};manifests={};files={}
    for mode in ('csr','compact'):
        folder=ROOT/f'data/derived/native_site_{mode}_inputs_20261023_v1';path=folder/'manifest.json'
        manifest=json.loads(path.read_text());manifests[mode]=manifest
        files[str(path)]=digest(path);frozen.update(manifest['files'])
        for name,value in manifest['outputs'].items():frozen[str(folder/name)]=value
    for path,value in frozen.items():
        if digest(path)!=value:raise ValueError('Frozen evidence changed: '+path)
    files.update(frozen)
    base=ROOT/'data/derived/region_all_nets_cap8_20261022_v1'
    graph=read_export(ROOT/'data/raw/region_u280_20261022_v1/region.tsv')
    snapshot=read_snapshot(ROOT/'data/netlist/routeracc_cost_u280_20261022_v1/snapshot.tsv')
    queries=json.loads((base/'queries.json').read_text());fixed=json.loads((base/'fixed_site_state_v2.json').read_text())
    proofs=[json.loads((ROOT/f'data/netlist/lut_route_probes_20261023_v{v}/verification.json').read_text()) for v in (1,2)]
    required={r['pip'] for r in proofs[1]['checks']};pip_records={name:graph['pips'][name] for name in required}
    del graph;gc.collect()
    results={};negatives=[]
    for mode,index in [('csr',0),('compact',1)]:
        worker=ROOT/f'data/derived/packed_conversion_statistics_20261023_v1/worker_{index:03d}'
        record=json.loads(worker.with_suffix('.json').read_text());image_path=worker.with_suffix('.agr')
        expected_image=manifests[mode]['files'][manifests[mode]['image']]
        if record['condition']['mode']!=mode or record['output_sha256']!=expected_image or digest(image_path)!=expected_image:
            raise ValueError('Regenerated image differs')
        files[str(image_path)]=expected_image;files[str(worker.with_suffix('.json'))]=digest(worker.with_suffix('.json'))
        started=time.perf_counter();image=PackedGraph(image_path);image_load_ms=(time.perf_counter()-started)*1000
        started=time.perf_counter();payload=build_runtime_payloads(image,snapshot,queries,fixed,proofs,pip_records)
        build_ms=(time.perf_counter()-started)*1000
        directory=output/mode;directory.mkdir()
        (directory/'routing.txt').write_text(payload['routing_text']);(directory/'sites.txt').write_text(payload['sites_text'])
        write_new(directory/'queries.json',payload['queries']);write_new(directory/'symbols.json',payload['symbols'])
        original_routing=Path(manifests[mode]['routing_fixture']).parent
        original_sites=ROOT/f'data/derived/native_site_{mode}_inputs_20261023_v1'
        artifacts={}
        for name in ('routing.txt','queries.json','sites.txt','symbols.json'):
            original=(original_routing if name in ('routing.txt','queries.json') else original_sites)/name
            if digest(directory/name)!=digest(original):raise ValueError('Rebuilt input bytes differ: '+mode+'/'+name)
            artifacts[name]=digest(directory/name)
        results[mode]={'status':'four_runtime_artifacts_byte_identical','image_load_ms_diagnostic':image_load_ms,
                       'fixture_build_ms_diagnostic':build_ms,'counts':payload['counts'],'artifacts':artifacts}
        if mode=='csr':
            bad=deepcopy(proofs);bad[1]['checks'].append(deepcopy(bad[1]['checks'][0]))
            variants=[('duplicate_evidence',fixed,bad,pip_records)]
            bad_fixed=deepcopy(fixed);bad_fixed['fixed_functional_luts'][0]['configuration_bits'][2]=1<<64
            variants.append(('invalid_mask_value',bad_fixed,proofs,pip_records))
            bad_pips=deepcopy(pip_records);bad_pips[sorted(required)[0]]['attributes']['IS_PSEUDO']='0'
            variants.append(('changed_physical_pip',fixed,proofs,bad_pips))
            for label,fx,pf,pips in variants:
                try:build_runtime_payloads(image,snapshot,queries,fx,pf,pips)
                except ValueError:negatives.append(label)
                else:raise ValueError('Invalid input was accepted: '+label)
        del image;gc.collect()
    for path in (Path(__file__),ROOT/'src/runtime_fixture_builder.py',ROOT/'src/packed_graph.py',ROOT/'src/netlist.py',ROOT/'src/lut_equation.py'):
        files[str(path)]=digest(path)
    report={'status':'complete_query_and_site_fixtures_rebuilt_byte_identically','modes':results,'negative_cases':negatives,'files':files,
            'limitations':['Integration test only, not statistical fixture costs or complete source-to-route timing.',
                'Physical evidence remains the same14 tested instances; no inferred resource family promoted.',
                'Reusable builder requires caller-validated provenance; this driver revalidates all frozen evidence first.']}
    write_new(output/'report.json',report);print(json.dumps({'status':report['status'],'modes':results,'negative_cases':negatives}))


if __name__=='__main__':main()
