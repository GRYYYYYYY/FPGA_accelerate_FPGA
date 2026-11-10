#!/usr/bin/env python3
"""Run both real canonical-node native routing modes with frozen provenance."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'adapters'),str(ROOT/'src')]
from import_vivado import sha256
from real_experiment import write_new


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    binary=ROOT/'build/native_netlist_20261023_v1'
    sources=[ROOT/'src/native'/name for name in ('netlist_bench.cpp','netlist_routes.hpp','netlist_connect.hpp','packed_graph.hpp')]
    sources.extend([binary,Path(__file__)])
    frozen={str(path):sha256(path) for path in sources}
    inputs={}
    for mode in ('csr','compact'):
        directory=ROOT/f'data/derived/native_region_{mode}_inputs_20261023_v2'
        manifest=json.loads((directory/'manifest.json').read_text())
        if manifest['mode']!=mode or manifest['status']!='prepared':raise ValueError('Invalid fixture manifest')
        for path,digest in manifest['files'].items():
            if sha256(Path(path))!=digest:raise ValueError('Frozen real input changed: '+path)
        for name,digest in manifest['outputs'].items():
            if sha256(directory/name)!=digest:raise ValueError('Numeric input changed: '+name)
        inputs[mode]={'directory':str(directory),'manifest_sha256':sha256(directory/'manifest.json'),
                      'image':manifest['image'],'canonical_order':manifest['canonical_node_order_sha256']}
    if inputs['csr']['canonical_order']!=inputs['compact']['canonical_order']:raise ValueError('Canonical ordering differs')
    plan={'owner_pid':os.getpid(),'scope':'Full 1062-query canonical-node integration; no site/physical or statistical performance claim.',
          'cache_rows':4096,'max_iterations':80,'max_expansions':200000,'present_cap':8,
          'code_and_binary':frozen,'inputs':inputs}
    write_new(a.output/'plan.json',plan)
    for mode in ('csr','compact'):
        for name,digest in frozen.items():
            if sha256(Path(name))!=digest:raise ValueError('Frozen native source/binary changed: '+name)
        fixture=Path(inputs[mode]['directory'])/'routing.txt'
        command=[str(binary),inputs[mode]['image'],str(fixture),'4096','80','200000','8','direct']
        print('NATIVE_ROUTING_BEGIN',mode,flush=True)
        with (a.output/(mode+'_routes.json')).open('x') as out, (a.output/(mode+'.log')).open('x') as log:
            child=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=log)
            write_new(a.output/(mode+'_submission.json'),{'owner_pid':os.getpid(),'child_pid':child.pid,'command':command})
            code=child.wait()
        write_new(a.output/(mode+'_receipt.json'),{'exit_code':code,
            'output_sha256':sha256(a.output/(mode+'_routes.json')),'log_sha256':sha256(a.output/(mode+'.log'))})
        if code:raise RuntimeError('Native routing failed: '+mode)
        result=json.loads((a.output/(mode+'_routes.json')).read_text())
        print('NATIVE_ROUTING_COMPLETE',mode,result['status'],len(result['routes']),len(result['iterations']),flush=True)
    write_new(a.output/'execution_complete.json',{'status':'await_independent_semantic_validation','plan_sha256':sha256(a.output/'plan.json')})


if __name__=='__main__':main()
