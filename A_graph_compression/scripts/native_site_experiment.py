#!/usr/bin/env python3
"""Frozen full-query native site experiment; independent semantic audit follows."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from real_experiment import write_new


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=False)
    files={};manifests={}
    def bind(path,expected=None):
        path=str(Path(path).resolve())
        actual=files.get(path)
        if actual is None:actual=digest(path);files[path]=actual
        if expected is not None and actual!=expected:raise ValueError('Frozen input mismatch: '+path)
    binary=ROOT/'build/native_site_20261023_v1'
    for path in [Path(__file__),ROOT/'scripts/real_experiment.py',binary,
                 ROOT/'src/native/site_bench.cpp',*sorted((ROOT/'src/native').glob('*.hpp'))]:bind(path)
    for mode in ('csr','compact'):
        folder=ROOT/f'data/derived/native_site_{mode}_inputs_20261023_v1'
        manifest_path=folder/'manifest.json';bind(manifest_path)
        manifest=json.loads(manifest_path.read_text())
        if manifest['status']!='prepared_tested_instances_only' or manifest['mode']!=mode or manifest['queries']!=1062 or manifest['verified_instances']!=14:
            raise ValueError('Unexpected input scope')
        for path,value in manifest['files'].items():bind(path,value)
        for name,value in manifest['outputs'].items():bind(folder/name,value)
        for path in (manifest['image'],manifest['routing_fixture']):
            if str(Path(path).resolve()) not in files:raise ValueError('Unbound image/fixture')
        manifests[mode]=(folder,manifest)
    cpu=max(os.sched_getaffinity(0))
    write_new(a.output/'plan.json',{'status':'frozen','owner_pid':os.getpid(),'files':files,
        'modes':['csr','compact'],'queries':1062,'verified_instances':14,'cpu':cpu,
        'cache_rows':4096,'max_iterations':80,'max_expansions':200000,'present_cap':8,
        'limitations':['Only 14 physically tested instances; other pseudo requirements remain unknown.',
                        'Single runs are semantic validation, not statistical performance measurements.']})
    for mode,(folder,manifest) in manifests.items():
        # Recheck executable closure and immediate inputs after a previous long worker.
        for path,value in files.items():
            if path.startswith(str(ROOT/'src/native')) or path==str(binary) or path in (manifest['image'],manifest['routing_fixture'],str(folder/'sites.txt')):
                if digest(path)!=value:raise ValueError('Execution input changed: '+path)
        command=[str(binary),manifest['image'],manifest['routing_fixture'],str(folder/'sites.txt'),'4096','80','200000','8']
        start=time.monotonic();tmp=a.output/f'{mode}.raw.json.tmp'
        with tmp.open('x') as out,(a.output/f'{mode}.log').open('x') as log:
            process=subprocess.Popen(command,stdout=out,stderr=log,start_new_session=True)
            os.sched_setaffinity(process.pid,{cpu})
            write_new(a.output/f'{mode}.submission.json',{'owner_pid':os.getpid(),'child_pid':process.pid,'command':command,'cpu':cpu})
            code=process.wait()
        receipt={'exit_code':code,'wall_ms':(time.monotonic()-start)*1000,'output_sha256':digest(tmp)}
        write_new(a.output/f'{mode}.receipt.json',receipt)
        if code:raise RuntimeError(f'{mode} failed; partial output retained')
        tmp.rename(a.output/f'{mode}.raw.json')
        print(json.dumps({'mode':mode,'status':'execution_finished_awaiting_independent_audit'}),flush=True)
    write_new(a.output/'execution_complete.json',{'status':'awaiting_independent_semantic_audit','owner_pid':os.getpid()})


if __name__=='__main__':main()
