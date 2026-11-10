#!/usr/bin/env python3
"""Certify a finished read-only Vivado netlist graph export, never partial output."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'adapters')]
from canonical_graph import validate
from heldout import source_slr
from import_vivado import read_export, sha256
from real_experiment import write_new


def main():
    config_path=ROOT/'configs/netlist_u280_v2.json'
    cfg=json.loads(config_path.read_text())
    directory=ROOT/cfg['output_dir']
    log=ROOT/'results/vivado/export_netlist_domain_20261022.stdout'
    text=log.read_text()
    if 'NETLIST_DOMAIN_COMPLETE\n' not in text or 'ERROR:' in text:
        raise ValueError('Vivado export has not completed successfully')
    # Pin the source scripts that produced the rows, rather than silently
    # attributing a later exporter revision to an earlier capture.
    for name, digest in cfg['code_sha256'].items():
        if sha256(ROOT/name)!=digest:raise ValueError('Export code changed: '+name)
    summaries={}
    sources={}
    for label, filename in [('training','training.tsv'),('evaluation','reference_domain.tsv')]:
        graph=read_export(directory/filename);validate(graph)
        if graph['metadata']['part']!=cfg['part']:raise ValueError('Device mismatch')
        sources[label]=set(graph['roots'])
        summaries[label]={key:len(graph[key]) for key in ['roots','nodes','aliases','pips','edges']}
        summaries[label]['source_slrs']=sorted({source_slr(graph,n) for n in graph['roots']})
    if sources['training'] & sources['evaluation']:raise ValueError('Training/evaluation source overlap')
    if sources['evaluation']!=set((ROOT/cfg['reference_sources']).read_text().splitlines()):
        raise ValueError('Incomplete declared reference source domain')
    paths=[config_path,ROOT/cfg['snapshot'],ROOT/cfg['queries'],ROOT/cfg['reference_sources'],
           directory/'training.tsv',directory/'reference_domain.tsv',log]
    result={'created_utc':datetime.now(timezone.utc).isoformat(),'part':cfg['part'],
            'config_sha256':sha256(config_path),'code_sha256':cfg['code_sha256'],
            'scope':cfg['domain_stage'],'summaries':summaries,
            'source_overlap':0,'command':'env LD_PRELOAD=/lib/x86_64-linux-gnu/libudev.so.1 Vivado/2022.2/bin/vivado -mode batch -source adapters/export_netlist_domain.tcl',
            'files':{str(p.relative_to(ROOT)):{'path':str(p.relative_to(ROOT)),'sha256':sha256(p)} for p in paths}}
    write_new(directory/'capture.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
