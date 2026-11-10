#!/usr/bin/env python3
"""Run the common real-net router with exact native HLS C-model providers."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'adapters')]
from hls_cmodel import HlsCModel
from import_vivado import read_export,sha256
from netlist import read_snapshot
from netlist_routing import route_batch,validate_routes
from packed_graph import PackedGraph
from real_experiment import write_new


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment',type=Path,default=ROOT/'data/derived/netlist_all_nets_20261022_v1')
    p.add_argument('--models',type=Path,default=ROOT/'data/derived/hls_u280_fixtures_20261022_v1')
    p.add_argument('--config',type=Path,default=ROOT/'configs/netlist_u280_v2.json')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args(argv)
    audit=json.loads((args.experiment/'report.json').read_text())
    cfg=json.loads(args.config.read_text())
    capture_path=ROOT/cfg['output_dir']/'capture.json'
    capture=json.loads(capture_path.read_text())
    if sha256(args.config)!=audit['inputs']['config'] or sha256(capture_path)!=audit['inputs']['capture']:
        raise ValueError('C-model domain differs from audited routing experiment')
    for entry in capture['files'].values():
        if sha256(ROOT/entry['path'])!=entry['sha256']:
            raise ValueError('Captured C-model input changed: '+entry['path'])
    manifest=json.loads((args.models/'manifest.json').read_text())
    for name,digest in manifest['files'].items():
        if sha256(args.models/name)!=digest:raise ValueError('Frozen C-model sources/fixtures changed')
    queries=json.loads((args.experiment/'queries.json').read_text())
    if sha256(args.experiment/'queries.json')!=audit['artifacts']['queries.json']:
        raise ValueError('Audited query selection changed')
    reference_path=args.experiment/'csr_routes.json'
    if sha256(reference_path)!=audit['artifacts']['csr_routes.json']:raise ValueError('Reference changed')
    reference=json.loads(reference_path.read_text())
    snapshot_path=ROOT/cfg['snapshot']
    if sha256(snapshot_path)!=audit['inputs']['snapshot']:raise ValueError('Audited snapshot changed')
    snapshot=read_snapshot(snapshot_path)
    graph_path=(ROOT/capture['graph']['path'] if capture.get('scope_kind')=='independent_endpoint_region'
                else ROOT/cfg['output_dir']/'reference_domain.tsv')
    graph=read_export(graph_path)
    args.output.mkdir(parents=True,exist_ok=False)
    results={};evidence={}
    for mode,name in enumerate(['csr','compact']):
        image=args.experiment/(name+'.agr')
        if sha256(image)!=manifest['image_files'][name]['sha256']:raise ValueError('C-model/software graphs differ')
        if sha256(image)!=audit['artifacts'][image.name]:raise ValueError('Audited C-model image changed')
        if image.stat().st_size>manifest['image_depth_words']*4:
            raise ValueError('Complete graph image exceeds the frozen kernel capacity; regenerate explicit capacity, never truncate')
        library=args.output/(name+'.so');source=args.models/name/'graph_expand.cpp'
        command=['g++','-std=c++14','-O3','-shared','-fPIC','-Wall','-Wextra','-Wno-unknown-pragmas',str(source),'-o',str(library)]
        proc=subprocess.run(command,capture_output=True,text=True,check=True)
        (args.output/(name+'_compile.log')).write_text(proc.stdout+proc.stderr)
        start=perf_counter();provider=HlsCModel(PackedGraph(image),library,mode,manifest['image_depth_words'])
        initialize_ms=(perf_counter()-start)*1000
        def progress(*values):print('CMODEL_ROUTING',name,*values,flush=True)
        settings=audit.get('route_settings',{'max_iterations':20,'max_expansions':200000,'present_cap':1048576})
        result=route_batch(provider,snapshot,queries,max_iterations=settings['max_iterations'],
                           max_expansions=settings['max_expansions'],present_cap=settings['present_cap'],
                           full_trace=False,progress=progress)
        write_new(args.output/(name+'_routes.json'),result)
        valid=validate_routes(graph,snapshot,queries,result)
        normalize=lambda r:{k:v for k,v in r.items() if k!='wall_ms'}
        if normalize(result)!=normalize(reference):raise ValueError('C-model router path/state/search counters differ')
        results[name]={'validation':valid,'identical_to_software_csr_except_time':True,
                       'execution_kind':provider.execution_kind,'initialize_validate_ms':initialize_ms,
                       'native_cpu_cmodel_route_ms':result['wall_ms'],'kernel_calls':provider.calls,
                       'unknown_calls':provider.unknown_calls,'returned_records':provider.returned_records}
        evidence[name]={'source_sha256':sha256(source),'image_sha256':sha256(image),
                        'library_sha256':sha256(library),'compile_command':command}
    report={'status':'equivalent','created_utc':datetime.now(timezone.utc).isoformat(),'nets':len(queries),
            'results':results,'evidence':evidence,'source_experiment_report_sha256':sha256(args.experiment/'report.json'),
            'source_fixture_manifest_sha256':sha256(args.models/'manifest.json'),
            'source_config_sha256':sha256(args.config),'graph_sha256':sha256(graph_path),
            'scope':audit['scope'],
            'host_code_sha256':{str(p.relative_to(ROOT)):sha256(p) for p in
                [Path(__file__),ROOT/'src/hls_cmodel.py',ROOT/'src/netlist_routing.py',ROOT/'hardware/hls/prepare_fixtures.py']},
            'limitations':['CPU execution of HLS C++ providers, not FPGA/XRT execution or board speedup.',
                           'Graph scope follows audited source experiment; external IO and physical board memory unverified.',
                           'One C-model routing run per representation; timings are integration diagnostics, not statistical speedup evidence.']}
    write_new(args.output/'report.json',report);print(json.dumps(report,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
