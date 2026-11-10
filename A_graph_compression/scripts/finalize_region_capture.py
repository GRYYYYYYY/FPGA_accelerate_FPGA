#!/usr/bin/env python3
"""Merge completed regional partitions and certify every declared source row."""
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'adapters')]
from import_vivado import read_export,sha256
from merge_exports import merge_graphs,write_tsv
from real_experiment import write_new


def main():
    config_path=ROOT/'configs/region_u280_v1.json';cfg=json.loads(config_path.read_text())
    directory=ROOT/cfg['output_dir'];plan=json.loads((directory/'execution_plan.json').read_text())
    if sha256(config_path)!=plan['config_sha256']:raise ValueError('Config changed')
    for name,digest in plan['code_sha256'].items():
        if sha256(ROOT/name)!=digest:raise ValueError('Capture code changed')
    sources=(directory/'selection/roots.txt').read_text().splitlines()
    bank=json.loads((ROOT/cfg['training_bank']).read_text())
    if set(sources)&set(bank['training_sources']):raise ValueError('Training/evaluation source overlap')
    shards=[ROOT/job['output'] for job in plan['jobs']]
    def graphs():
        for job,path in zip(plan['jobs'],shards):
            graph=read_export(path)
            expected=(ROOT/job['roots']).read_text().splitlines()
            if set(graph['roots'])!=set(expected):raise ValueError('Partition source domain differs')
            if graph['metadata'].get('selection_config_sha256')!=plan['config_sha256']:raise ValueError('Partition config differs')
            yield graph
    metadata={'part':cfg['part'],'purpose':'independent_endpoint_region_complete_rows',
              'scope':'Complete outgoing rows for all canonical nodes touching the preregistered endpoint-tile rectangle; exterior adjacency is unknown.',
              'design':'routed_routeracc_cost_ooc_netlist','selection_config_sha256':plan['config_sha256'],
              'timestamp_utc':datetime.now(timezone.utc).isoformat(),
              'raw_shards_sha256':json.dumps({str(p.relative_to(ROOT)):sha256(p) for p in shards},sort_keys=True)}
    graph=merge_graphs(graphs(),sources,metadata)
    output=directory/'region.tsv';write_tsv(output,graph)
    summary={key:len(graph[key]) for key in ['roots','nodes','aliases','pips','edges']}
    inputs=[config_path,directory/'execution_plan.json',directory/'selection/roots.txt',directory/'selection/metadata.tsv',
            ROOT/cfg['queries'],ROOT/cfg['snapshot'],ROOT/cfg['training_bank'],output,*shards]
    training=ROOT/'data/raw/netlist_u280_20261022_v1/training.tsv';inputs.append(training)
    report={'created_utc':datetime.now(timezone.utc).isoformat(),'part':cfg['part'],'scope_kind':'independent_endpoint_region',
            'scope':cfg['scope'],'config_sha256':plan['config_sha256'],
            'graph':{'path':str(output.relative_to(ROOT)),'sha256':sha256(output),'summary':summary},
            'source_selection':{'path':str((directory/'selection/roots.txt').relative_to(ROOT)), 'sha256':sha256(directory/'selection/roots.txt')},
            'training':{'path':str(training.relative_to(ROOT)),'sha256':sha256(training)},
            'training_bank_sha256':sha256(ROOT/cfg['training_bank']),'source_overlap':0,
            'code_sha256':{str(p.relative_to(ROOT)):sha256(p) for p in [Path(__file__),ROOT/'src/merge_exports.py']},
            'files':{str(p.relative_to(ROOT)):{'path':str(p.relative_to(ROOT)),'sha256':sha256(p)} for p in inputs}}
    write_new(directory/'capture.json',report);print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
