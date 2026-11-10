#!/usr/bin/env python3
"""Freeze exact contiguous source partitions; no adjacency-based selection."""
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'adapters')]
from import_vivado import sha256
from real_experiment import write_new


def main():
    config_path=ROOT/'configs/region_u280_v1.json';cfg=json.loads(config_path.read_text())
    directory=ROOT/cfg['output_dir'];selection=directory/'selection'
    check=json.loads((selection/'check.json').read_text())
    if check['training_overlap_count'] or check['missing_query_terminals']:raise ValueError('Training/terminal selection check failed')
    roots=(selection/'roots.txt').read_text().splitlines()
    if roots!=sorted(set(roots)) or len(roots)>cfg['max_sources']:raise ValueError('Invalid source domain')
    for key in ['snapshot','checkpoint','queries','endpoint_sites','training_bank']:
        if sha256(ROOT/cfg[key])!=cfg[key+'_sha256']:raise ValueError('Frozen input changed: '+key)
    selector=json.loads((directory/'selector_receipt.json').read_text())
    for path,digest in selector['files'].items():
        if sha256(ROOT/path)!=digest:raise ValueError('Selector/config changed')
    parts=directory/'partitions';parts.mkdir(exist_ok=False)
    jobs=[]
    for i in range(cfg['workers']):
        rows=roots[len(roots)*i//cfg['workers']:len(roots)*(i+1)//cfg['workers']]
        path=parts/f'{i:02d}.txt';path.write_text('\n'.join(rows)+'\n')
        jobs.append({'id':f'{i:02d}','sources':len(rows),'roots':str(path.relative_to(ROOT)),
                     'roots_sha256':sha256(path),'output':str((directory/f'shard_{i:02d}.tsv').relative_to(ROOT))})
    # Pilot only checks the adapter on already observed rows; not a source subset
    # of the final evaluation, which still requires every partition to complete.
    old=(ROOT/'data/raw/netlist_u280_20261022_v1/reference_sources.txt').read_text().splitlines()
    common=sorted(set(old)&set(roots));pilot=common[::max(1,len(common)//24)][:24]
    (directory/'pilot_roots.txt').write_text('\n'.join(pilot)+'\n')
    code=['adapters/export_region_shard.tcl','adapters/export_regions.tcl','adapters/export_vivado.tcl']
    receipt={'created_utc':datetime.now(timezone.utc).isoformat(),'config_sha256':sha256(config_path),
        'total_sources':len(roots),'workers':cfg['workers'],'vivado_threads_per_worker':cfg['vivado_threads_per_worker'],
        'partition_rule':'Contiguous canonical-name order, balanced source counts, union exact and disjoint.',
        'jobs':jobs,'code_sha256':{p:sha256(ROOT/p) for p in code}}
    write_new(directory/'execution_plan.json',receipt)
    print(json.dumps({'sources':len(roots),'jobs':len(jobs),'pilot':len(pilot)},indent=2))


if __name__=='__main__':main()
