#!/usr/bin/env python3
"""Full U280 graph stimuli and fixed-mode explicitly bounded decoder copies."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import struct
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'adapters')]
from canonical_graph import compare
from import_vivado import sha256
from packed_graph import PackedGraph
import prepare_fixtures as stimulus


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--image-capacity-mib',type=int,default=64,
                   help='Explicit image/AXI depth; complete images must fit without truncation')
    args=p.parse_args(argv)
    if args.image_capacity_mib<1 or args.image_capacity_mib>1024:
        raise ValueError('Image capacity must be 1..1024 MiB')
    image_depth=args.image_capacity_mib*1024*1024//4
    report_path=args.experiment/'report.json'
    report=json.loads(report_path.read_text())
    if not report['provider_results_identical_except_time']:raise ValueError('Input experiment did not pass equivalence')
    images={n:args.experiment/(n+'.agr') for n in ['csr','compact']}
    for n,path in images.items():
        if sha256(path)!=report['artifacts'][path.name]:raise ValueError('Audited graph changed')
        if path.stat().st_size>image_depth*4:
            raise ValueError('Complete '+n+' image exceeds declared capacity; increase explicit bound, never truncate')
    readers={n:PackedGraph(path) for n,path in images.items()}
    graphs={n:r.materialize() for n,r in readers.items()}
    if not compare(graphs['csr'],graphs['compact'])['equal']:raise ValueError('CSR/compact semantics differ')
    if any(g['metadata']['part']!='xcu280-fsvh2892-2L-e' for g in graphs.values()):raise ValueError('Expected actual U280 data')
    del graphs
    # Same audited host helpers; enlarge only the declared image bound to match
    # the generated header and AXI depth. All semantic/bounds checks remain.
    stimulus.IMAGE_DEPTH=image_depth
    output=args.output;output.mkdir(parents=True,exist_ok=False)
    base=ROOT/'data/derived/hls_fixed_modes_20261022_v1'
    fixed_manifest=json.loads((base/'manifest.json').read_text())
    for name,digest in fixed_manifest['files'].items():
        if sha256(base/name)!=digest:raise ValueError('Fixed reference source changed')
    degrees={};selected=set();coverage={}
    for n,r in readers.items():
        degree={node:len(r.numeric_neighbors(node)) for node,_,_ in r.roots}
        if max(degree.values())>stimulus.MAX_DEGREE:raise ValueError('Hardware degree capacity exceeded')
        degrees[n]=degree;selected.update([min(degree),max(degree,key=degree.get)])
        categories={}
        for node in degree:
            edges=r.numeric_neighbors(node);labels=[]
            if not edges:labels.append('known_sink')
            if any(e[-1] for e in edges):labels.append('reverse')
            if len({e[0] for e in edges})<len(edges):labels.append('parallel_destination')
            if r.mode:
                tid,rs,rc,ads,adc,ps,pc=r.instances[r.nodes[node][3]]
                if tid<0:labels.append('fallback')
                if rc:labels.append('remove')
                if adc and tid>=0:labels.append('add')
                if pc:labels.append('attribute_patch')
                if tid>=0 and not(rc or adc or pc):labels.append('exact_template')
            for label in labels:
                if label not in categories:categories[label]=node;selected.add(node)
        coverage[n]=categories
    names=[[r.text(node[0]) for node in r.nodes] for r in readers.values()]
    if names[0]!=names[1]:raise ValueError('Numeric node IDs differ')
    unknown=next(i for i,node in enumerate(readers['csr'].nodes) if node[3]<0)
    selected.update([unknown,len(names[0])]);matched=sorted(selected)
    cases={}
    for n,r in readers.items():
        directory=output/n;directory.mkdir()
        source=(base/n/'graph_expand.cpp').read_text()
        header=(base/n/'graph_expand.hpp').read_text()
        if source.count('depth=2097152')!=1 or header.count('IMAGE_DEPTH=2097152')!=1:
            raise ValueError('Unrecognized image declaration')
        (directory/'graph_expand.cpp').write_text(source.replace('depth=2097152','depth='+str(image_depth)))
        (directory/'graph_expand.hpp').write_text(header.replace('IMAGE_DEPTH=2097152','IMAGE_DEPTH='+str(image_depth)))
        (directory/'test_graph_expand.cpp').write_bytes((base/n/'test_graph_expand.cpp').read_bytes())
        cfg=directory/'config.bin';cfg.write_bytes(struct.pack('<32I',*stimulus.descriptor(r)))
        lines={'full':[],'rtl':[]};cases[n]={}
        def add(label,requests,capacity,manifests):
            path=directory/(label+'.bin');info=stimulus.case(path,r,requests,capacity)
            cases[n][label]=info
            line=' '.join(str(p.resolve()) for p in [images[n],cfg,path])
            for key in manifests:lines[key].append(line)
        # Split by BOTH request and output limits; every known row must succeed.
        batch=[];records=0;number=0
        for node in range(len(r.nodes)):
            degree=degrees[n].get(node,0)
            if len(batch)==stimulus.MAX_REQUESTS or records+degree>stimulus.OUTPUT_DEPTH//8:
                add('full_'+str(number),batch,stimulus.OUTPUT_DEPTH,['full'])
                number+=1;batch=[];records=0
            batch.append(node);records+=degree
        if batch:add('full_'+str(number),batch,stimulus.OUTPUT_DEPTH,['full'])
        add('matched',matched,stimulus.OUTPUT_DEPTH,['rtl'])
        capacity_requests=[max(degrees[n],key=degrees[n].get)]
        sink=coverage[n].get('known_sink')
        if sink is not None:capacity_requests.append(sink)
        capacity_requests += [unknown,len(r.nodes)]
        add('capacity',capacity_requests,0,['full','rtl'])
        # Explicit descriptor mismatch must return status 4 for both requests.
        wrong=bytearray(cfg.read_bytes());struct.pack_into('<I',wrong,0,1-r.mode)
        badcfg=directory/'wrong_mode.config.bin';badcfg.write_bytes(wrong)
        bad=directory/'wrong_mode.bin'
        bad.write_bytes(struct.pack('<4I',2,0,0,2)+struct.pack('<2I',0,1)+struct.pack('<6I',0,0,4,0,0,4))
        line=' '.join(str(p.resolve()) for p in [images[n],badcfg,bad])
        for key in lines:
            lines[key].append(line);(directory/(key+'.txt')).write_text('\n'.join(lines[key])+'\n')
        expected=sum(degrees[n].values())
        actual=sum(v['records'] for key,v in cases[n].items() if key.startswith('full_'))
        if expected!=actual:raise ValueError('Full Csim would omit successful edge records')
    metadata={'created_utc':datetime.now(timezone.utc).isoformat(),'part':'xcu280-fsvh2892-2L-e',
        'source_experiment':str(args.experiment.resolve()),'source_report_sha256':sha256(report_path),
        'image_depth_words':stimulus.IMAGE_DEPTH,'host_bytes_per_image_buffer':stimulus.IMAGE_DEPTH*4,
        'image_files':{n:{'path':str(p.resolve()),'sha256':sha256(p),'bytes':p.stat().st_size} for n,p in images.items()},
        'coverage':coverage,'cases':cases,'scope':'Actual U280 graph, complete sampled rows in Csim; matched feature subset in RTL; no real board-memory model.',
        'transformations':'Only image-array declaration and m_axi co-simulation depth change from 8 to '+str(args.image_capacity_mib)+' MiB relative to independently validated fixed-mode sources.',
        'helper_sources':{str(p.relative_to(ROOT)):sha256(p) for p in [Path(__file__),ROOT/'hardware/hls/prepare_fixtures.py']},
        'files':{str(p.relative_to(output)):sha256(p) for p in output.rglob('*') if p.is_file()}}
    (output/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps({'images':metadata['image_files'],'cases':cases,'coverage':coverage},indent=2))


if __name__=='__main__':main()
