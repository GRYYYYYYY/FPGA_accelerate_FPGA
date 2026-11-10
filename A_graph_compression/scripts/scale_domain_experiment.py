#!/usr/bin/env python3
"""Build nested real domains and exhaustively audit CSR/compact storage semantics."""
import argparse
import gc
import json
import os
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/p) for p in ('src','adapters')]
from import_vivado import read_export
from packed_graph import write_packed
from scale_domain import make_domain
from heldout import object_digest
from real_experiment import write_new
from check_scale_domain import check_image, check_selection
from check_template_scope import digest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--cpu',type=int,default=124)
    args=p.parse_args();args.output=args.output.resolve()
    if args.cpu not in os.sched_getaffinity(0):raise ValueError('CPU unavailable')
    os.sched_setaffinity(0,{args.cpu})
    source=ROOT/'data/raw/region_u280_20261022_v1/region.tsv'
    bank_path=ROOT/'data/derived/netlist_u280_bank_20261022_v1/bank.json'
    prior_path=ROOT/'data/derived/native_site_routing_20261023_v2/plan.json'
    config_path=ROOT/'configs/region_u280_v1.json'
    reference=ROOT/'data/derived/region_all_nets_cap8_20261022_v1'
    prior=json.loads(prior_path.read_text());cfg=json.loads(config_path.read_text())
    for path in (source,config_path,reference/'report.json',reference/'csr.agr',reference/'compact.agr'):
        if digest(path)!=prior['files'][str(path)]:raise ValueError('Verified source changed: '+str(path))
    bank=json.loads(bank_path.read_text())
    if digest(bank_path)!=cfg['training_bank_sha256'] or object_digest(bank)!=json.loads((reference/'report.json').read_text())['frozen_bank_sha256']:
        raise ValueError('Frozen bank changed')
    regression=ROOT/'results/regression_scale_domain_20261023_v1.log'
    if not regression.read_text().rstrip().endswith('OK'):raise ValueError('Regression not passed')
    args.output.mkdir(parents=True,exist_ok=False)
    binary=args.output/'native_scan'
    command=['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror',str(ROOT/'src/native/scale_domain_scan.cpp'),'-o',str(binary)]
    with (args.output/'compile.log').open('x') as stream:
        subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,check=True)
    dependencies=[source,bank_path,prior_path,config_path,reference/'report.json',reference/'csr.agr',reference/'compact.agr',
        Path(__file__),ROOT/'scripts/check_scale_domain.py',ROOT/'scripts/check_template_scope.py',ROOT/'scripts/real_experiment.py',
        ROOT/'adapters/import_vivado.py',ROOT/'src/native/scale_domain_scan.cpp',ROOT/'src/native/packed_graph.hpp',binary,regression,
        *[ROOT/'src'/name for name in ('scale_domain.py','heldout.py','canonical_graph.py','packed_graph.py','template_codec.py')]]
    files={str(path):digest(path) for path in dependencies}
    limits=['Nested spatial prefixes of one captured device region; not independent devices or larger-than-capture graphs.',
        'All outgoing edges and endpoint aliases retained. Unselected endpoint adjacency remains unknown, not empty.',
        'Frozen training bank, no query-path selection, no new site legality authorization.',
        'Single-build timings are diagnostics, not repeated performance or full-router capacity.',
        'No hardware DDR/HBM, wall-clock speedup, or routing success claim from graph size.']
    plan={'owner_pid':os.getpid(),'cpu':args.cpu,'source':str(source),'bank':str(bank_path),'denominators':[16,4,2,1],
        'selection_order':['SLR_REGION_ID','COLUMN','ROW','tile_name'],'files':files,'compile_command':command,'limitations':limits}
    write_new(args.output/'plan.json',plan)
    graph=read_export(source);records=[]
    for denominator in plan['denominators']:
        directory=args.output/f'fraction_1_{denominator}';directory.mkdir()
        domain,selection=make_domain(graph,denominator)
        check_selection(graph,domain,selection);write_new(directory/'selection.json',selection)
        record={'denominator':denominator,'source_tiles':len(selection['source_tiles']),
            'counts':{k:len(domain[k]) for k in ('nodes','roots','tiles','aliases','pips','edges')},'modes':{}}
        for mode in ('csr','compact'):
            image=directory/(mode+'.agr');dump=directory/(mode+'.edges.bin')
            start=time.perf_counter();layout=write_packed(image,domain,mode,bank if mode=='compact' else None)
            build_ms=(time.perf_counter()-start)*1000
            if denominator==1 and digest(image)!=files[str(reference/(mode+'.agr'))]:raise ValueError('Full control not byte identical')
            command=[str(binary),str(image),str(dump)];start=time.perf_counter()
            result=subprocess.run(command,capture_output=True,text=True)
            write_new(directory/(mode+'.receipt.json'),{'command':command,'exit_code':result.returncode,
                'process_wall_ms':(time.perf_counter()-start)*1000,'stdout':result.stdout,'stderr':result.stderr})
            if result.returncode:raise RuntimeError('Native scan failed')
            native=json.loads(result.stdout);counts=check_image(domain,image,dump,native)
            audit={'status':'complete_source_static_python_native_equivalence','counts':counts,'native':native,
                'image_sha256':digest(image),'dump_sha256':digest(dump),'layout':layout,'build_diagnostic_ms':build_ms}
            write_new(directory/(mode+'.audit.json'),audit);record['modes'][mode]=audit
            print('SCALE_VERIFIED',denominator,mode,json.dumps(counts),layout['file_bytes'],flush=True)
            gc.collect()
        write_new(directory/'report.json',record);records.append(record)
        del domain,selection;gc.collect()
    for name,value in files.items():
        if digest(name)!=value:raise ValueError('Frozen dependency changed: '+name)
    artifacts={str(path):digest(path) for path in args.output.glob('fraction_*/*') if path.is_file()}
    write_new(args.output/'report.json',{'status':'all_four_nested_real_domains_verified','plan_sha256':digest(args.output/'plan.json'),
        'domains':records,'artifacts':artifacts,'limitations':limits})


if __name__=='__main__':main()
