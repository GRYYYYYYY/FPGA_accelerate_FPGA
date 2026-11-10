#!/usr/bin/env python3
"""Exhaustive real-graph verification of the HLS C ABI and common BFS integration."""
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
from import_vivado import sha256
from packed_graph import PackedGraph
from real_experiment import write_new
from search_experiment import ExplicitCSR,IncompleteDomain,edge_order,make_queries,search


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--graphs',type=Path,required=True)
    p.add_argument('--compact-name',default='compact')
    p.add_argument('--sources',type=Path,default=ROOT/'data/derived/hls_fixed_modes_20261022_v1')
    p.add_argument('--image-capacity-words',type=int,default=2097152)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args(argv);args.output.mkdir(parents=True,exist_ok=False)
    checks={};artifacts={}
    for name,file_stem,mode in [('csr','csr',0),('compact',args.compact_name,1)]:
        image=args.graphs/(file_stem+'.agr');reader=PackedGraph(image)
        library=args.output/(name+'.so');source=args.sources/name/'graph_expand.cpp'
        command=['g++','-std=c++14','-O3','-shared','-fPIC','-Wall','-Wextra','-Wno-unknown-pragmas',str(source),'-o',str(library)]
        proc=subprocess.run(command,capture_output=True,text=True,check=True)
        (args.output/(name+'_compile.log')).write_text(proc.stdout+proc.stderr)
        started=perf_counter();provider=HlsCModel(reader,library,mode,args.image_capacity_words)
        initialize_ms=(perf_counter()-started)*1000
        known=unknown=records=0
        for node,row in enumerate(reader.nodes):
            canonical=reader.text(row[0])
            if row[3]<0:
                try:provider.neighbors(canonical)
                except IncompleteDomain:unknown+=1
                else:raise ValueError('Unknown row accepted as sink')
            else:
                actual=provider.neighbors(canonical)
                expected=sorted(reader.decoded_neighbors(node),key=edge_order)
                if actual!=expected:raise ValueError('C-model edge/property/direction differs: '+canonical)
                known+=1;records+=len(actual)
        graph=reader.materialize();baseline=ExplicitCSR(graph)
        seeds=[n for n in graph['metadata'].get('bfs_seeds','').split(',') if n in graph['roots']]
        if not seeds:
            # Route-conditioned captures have no traversal seeds. Choose actual
            # rows with a verified three-hop closure, rather than sink/boundary rows.
            for candidate in sorted(graph['roots']):
                levels={candidate:0};todo=[candidate]
                for node in todo:
                    if levels[node]>=3:continue
                    try:edges=baseline.neighbors(node)
                    except IncompleteDomain:continue
                    for edge,_ in edges:
                        if edge['dst'] not in levels:
                            levels[edge['dst']]=levels[node]+1;todo.append(edge['dst'])
                if any(depth==3 for depth in levels.values()):seeds.append(candidate)
                if len(seeds)==3:break
        if not seeds:raise ValueError('No three-hop search closure in this graph')
        queries=make_queries(graph,seeds,3,200000)
        for q in queries:
            a=search(baseline,q['source'],q['target'],q['max_expansions'],trace=True)
            b=search(provider,q['source'],q['target'],q['max_expansions'],trace=True)
            if a!=b:raise ValueError('C-model common-search path/status/trace differs')
        checks[name]={'known_rows':known,'unknown_rows':unknown,'edge_records':records,'common_bfs_queries':len(queries),
                      'initialize_validate_ms':initialize_ms,'execution_kind':provider.execution_kind,'compile_command':command}
        artifacts[name]={'source_sha256':sha256(source),'image_sha256':sha256(image),'library_sha256':sha256(library)}
    report={'status':'passed','created_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'artifacts':artifacts,
            'limitations':['Native CPU C-model execution, not FPGA or XRT; initialization validates the full packed graph.',
                           'String/attribute conversion and buffers are host allocations; no board speedup or memory-traffic claim.']}
    write_new(args.output/'report.json',report);print(json.dumps(report,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
