#!/usr/bin/env python3
"""Freeze Vitis-compatible wrappers while preserving the verified decode algorithm."""
import argparse
import json
from pathlib import Path
import struct
from check_template_scope import digest
from real_experiment import write_new
ROOT=Path(__file__).resolve().parents[1]


def transform(source,header,test):
    interfaces=[line for line in source.splitlines() if line.startswith('#pragma HLS INTERFACE ')]
    if len(interfaces)!=15 or source.count('void graph_expand(')!=1 or header.count('void graph_expand(')!=1:
        raise ValueError('Unexpected verified source interface')
    body='\n'.join(line for line in source.splitlines() if not line.startswith('#pragma HLS INTERFACE '))+'\n'
    body=body.replace('#include "graph_expand.hpp"','#include "graph_body.hpp"').replace('void graph_expand(','void graph_expand_body(')
    new_header=header.replace('void graph_expand(','void graph_expand_body(')
    new_test=test.replace('#include "graph_expand.hpp"','#include "graph_accel.hpp"')
    if new_test==test:raise ValueError('Testbench include missing')
    return body,new_header,new_test,interfaces


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args();a.output=a.output.resolve()
    bundle=ROOT/'data/derived/hls_region_fixtures_20261023_v1'
    manifest_path=bundle/'manifest.json';manifest=json.loads(manifest_path.read_text())
    prior_path=ROOT/'results/hls_region_check_20261023_v1.json';prior=json.loads(prior_path.read_text())
    if digest(manifest_path)!=prior['source_bundle_manifest_sha256'] or not prior['both_fully_routed'] or not prior['both_internal_timing_met']:
        raise ValueError('Prior regional HLS evidence missing or changed')
    for name,value in manifest['files'].items():
        if digest(bundle/name)!=value:raise ValueError('Frozen HLS source/stimulus changed')
    for value in manifest['image_files'].values():
        if digest(value['path'])!=value['sha256']:raise ValueError('Verified image changed')
    a.output.mkdir(parents=True,exist_ok=False)
    files={str(p):digest(p) for p in [Path(__file__),manifest_path,prior_path,ROOT/'hardware/vitis/run.tcl',
        ROOT/'hardware/vitis/graph_accel.cpp',ROOT/'hardware/vitis/graph_accel.hpp']}
    modes={}
    for name,mode in [('csr',0),('compact',1)]:
        original=bundle/name;target=a.output/name;target.mkdir()
        body,header,test,interfaces=transform((original/'graph_expand.cpp').read_text(),
            (original/'graph_expand.hpp').read_text(),(original/'test_graph_expand.cpp').read_text())
        (target/'graph_body.cpp').write_text(body);(target/'graph_body.hpp').write_text(header)
        (target/'test_graph_expand.cpp').write_text(test)
        for filename in ('graph_accel.cpp','graph_accel.hpp'):(target/filename).write_bytes((ROOT/'hardware/vitis'/filename).read_bytes())
        for filename in ('full.txt','rtl.txt'):(target/filename).write_bytes((original/filename).read_bytes())
        board=[]
        for line in (original/'full.txt').read_text().splitlines():
            image,config,case=map(Path,line.split())
            if struct.unpack_from('<I',config.read_bytes())[0]==mode:board.append(line)
            for path in (image,config,case):files[str(path)]=digest(path)
        (target/'board.txt').write_text('\n'.join(board)+'\n')
        for filename in ('graph_expand.cpp','graph_expand.hpp','test_graph_expand.cpp'):
            files[str(original/filename)]=digest(original/filename)
        modes[name]={'mode':mode,'source':str(target),'full_cases':len((target/'full.txt').read_text().splitlines()),
            'rtl_cases':len((target/'rtl.txt').read_text().splitlines()),'board_cases':len(board),'removed_interfaces':interfaces}
    generated={str(p):digest(p) for p in a.output.rglob('*') if p.is_file()}
    write_new(a.output/'plan.json',{'status':'prepared_not_hls_validated','modes':modes,'files':files,'generated':generated,
        'top':'graph_accel','part':'xcu280-fsvh2892-2L-e','period_ns':5,'image_capacity_bytes':134217728,
        'transformation':'Remove old top-only interface directives from renamed decode body; preserve all algorithm statements, static modes and BRAM scope. New top maps two output counters into a two-word memory buffer.',
        'limitations':['New wrapper requires its own Csim/csynth/RTL checks; prior implementation timing is not inherited.',
            'Kernel object export is not a platform-linked xclbin or board measurement.']})
    print(json.dumps(modes))


if __name__=='__main__':main()
