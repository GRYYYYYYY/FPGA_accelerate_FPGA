#!/usr/bin/env python3
"""Frozen multi-design/page/layout routing experiments with same-schedule gates."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import platform
import random
import re
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"adapters"))
from prepare_real import sha
from profile_real import parse_log


def save(path,record):
    temporary=path.with_suffix(path.suffix+".tmp")
    temporary.write_text(json.dumps(record,indent=2)+"\n");temporary.replace(path)


def validate_plan(config):
    if config.get("dataset_kind")!="real_placed_netlist":raise ValueError("Only real placed designs are supported")
    if not 1<=config["repetitions"]<=10:raise ValueError("Invalid repetitions")
    if len({d['id'] for d in config['datasets']})!=len(config['datasets']):raise ValueError('Duplicate dataset IDs')
    for case in config['cases']:
        if case['mode'] not in ('serial','batch'):raise ValueError('Invalid mode')
        if case['variant'] not in ('original','paged','node_epoch','compact'):raise ValueError('Invalid label layout')
        if case['variant']=='original':
            if case['mode']!='serial' or case['page_bits'] is not None:raise ValueError('Original baseline is serial without paging')
        elif case['page_bits'] not in (6,9,12):raise ValueError('Page sweep requires 64, 512 or 4096 nodes')
    if len({(c['mode'],c['variant'],c['page_bits']) for c in config['cases']})!=len(config['cases']):raise ValueError('Duplicate cases')


def check_bindings(config,builds):
    for dataset in config['datasets']:
        if sha(ROOT/dataset['input'])!=dataset['input_sha256']:raise ValueError('Real input changed: '+dataset['id'])
        provenance=json.loads((ROOT/dataset['provenance']).read_text())
        if provenance['status']!='exported' or provenance['output_sha256']!=dataset['input_sha256']:raise ValueError('Invalid export provenance')
    for build in builds:
        for path,digest in build['inputs'].items():
            if sha(path)!=digest:raise ValueError('Build input changed: '+path)
        for variant,row in build['variants'].items():
            if sha(row['source'])!=row['source_sha256'] or sha(row['binary'])!=row['binary_sha256']:raise ValueError('Build artifact changed: '+variant)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--config',type=Path,required=True);parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv);config=json.loads(args.config.read_text());validate_plan(config)
    builds=[json.loads((ROOT/path).read_text()) for path in config['builds']];check_bindings(config,builds)
    variants={k:v for b in builds for k,v in b['variants'].items()}
    legacy=json.loads((ROOT/'build/real_trace/build.json').read_text())
    original=ROOT/'build/real_trace/router_original'
    if sha(original)!=legacy['original']['binary_sha256']:raise ValueError('Original baseline changed')
    tests=[]
    for path in config['semantic_tests']:
        test=json.loads((ROOT/path).read_text())
        if test['status']!='passed':raise ValueError('Require passed label semantics')
        tests.append(test)
    compact_test=tests[-1]
    if compact_test.get('test_source_sha256')!=sha(ROOT/'tests/compact_semantics.cpp') or compact_test.get('router_source_sha256')!=variants['compact']['source_sha256']:
        raise ValueError('Compact semantic evidence does not match current source')
    if sha(ROOT/'tests/paged_semantics.cpp')!=tests[0]['source_sha256'] or tests[0]['build']!=builds[0]:raise ValueError('Legacy semantic evidence changed')
    directory=(args.output or ROOT/'results'/('research_matrix_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))).resolve()
    directory.mkdir(parents=True,exist_ok=False);manifest=directory/'manifest.json'
    record={'status':'running','config':config,'config_sha256':sha(args.config),'builds':builds,'semantic_tests':tests,'host':platform.platform(),
            'tool_sha256':sha(__file__),'runner_pid':os.getpid(),'started_utc':datetime.now(timezone.utc).isoformat(),'runs':[],
            'original_binary_sha256':sha(original),'verifier_sha256':sha(ROOT/'build/real_trace/verify_real')}
    save(manifest,record)
    observer_log=(directory/'observer.log').open('w')
    observer=subprocess.Popen(['taskset','-c','24',sys.executable,str(ROOT/'scripts/observe_paged_memory.py'),str(directory),str(os.getpid())],stdout=observer_log,stderr=subprocess.STDOUT)
    record['observer_pid']=observer.pid;save(manifest,record)
    clean={k:v for k,v in os.environ.items() if not k.startswith(('RW_','B_'))}
    expected={(d['id'],mode):d.get('reference_results',{}).get(mode) for d in config['datasets'] for mode in ('serial','batch')}
    convergence={};verified={}
    schedule=[];rng=random.Random(config['seed'])
    for rep in range(config['repetitions']):
        block=[(dataset,case,rep) for dataset in config['datasets'] for case in config['cases']]
        rng.shuffle(block);schedule.extend(block)
    record['schedule']=[{'dataset':d['id'],**c,'repetition':r} for d,c,r in schedule];save(manifest,record)
    try:
        for dataset,case,rep in schedule:
            mode,variant,bits=case['mode'],case['variant'],case['page_bits']
            name=f"{dataset['id']}_{mode}_{variant}_p{bits or 0}_r{rep}";prefix=directory/name
            binary=original if variant=='original' else Path(variants[variant]['binary'])
            env={'RW_MAX_THREADS':'1','RW_PAR_PART':'0','RW_PAR_ITER1':'0','RW_OVERLAP':'0','RW_BATCH_T':'0','RW_GPU_FLOOD':'0'} if mode=='serial' else dict(config['batch_environment'])
            if bits is not None:env['RW_BATCH_PBITS']=str(bits)
            if mode=='serial' and variant!='original':env['B_SERIAL_PAGED']='1'
            if variant!='original':env['B_LABEL_REPORT']=str(prefix.with_suffix('.labels.json'))
            cpus=config['serial_cpu'] if mode=='serial' else config['batch_cpus']
            command=['/usr/bin/time','-v','-o',str(prefix.with_suffix('.time')),'taskset','-c',cpus,str(binary),str(ROOT/dataset['input']),str(prefix.with_suffix('.result'))]
            row={'name':name,'dataset':dataset['id'],'mode':mode,'variant':variant,'page_bits':bits,'repetition':rep,'command':command,'environment':env}
            record['runs'].append(row);save(manifest,record);started=time.monotonic()
            with prefix.with_suffix('.log').open('w') as log:
                process=subprocess.run(command,env=dict(clean,**env),stdout=log,stderr=subprocess.STDOUT,timeout=config['timeout_seconds'])
            row.update(exit_code=process.returncode,process_wall_seconds=time.monotonic()-started);save(manifest,record)
            if process.returncode:raise RuntimeError('Router failed: '+name)
            text=prefix.with_suffix('.log').read_text();row['metrics']=parse_log(text)
            row['result_sha256']=sha(prefix.with_suffix('.result'))
            row['max_rss_kib']=int(re.search(r'Maximum resident set size \(kbytes\): (\d+)',prefix.with_suffix('.time').read_text())[1])
            if variant!='original':
                row['labels']=json.loads(prefix.with_suffix('.labels.json').read_text())
                if mode=='batch' and ('[batch-leaf]' not in text or not row['labels']['contexts']):raise ValueError('Batch paging path not exercised')
            key=(dataset['id'],mode)
            if expected[key] and expected[key]!=row['result_sha256']:raise ValueError('Same-schedule result mismatch: '+name)
            if key in convergence and convergence[key]!=row['metrics']['convergence']:raise ValueError('Same-schedule convergence mismatch: '+name)
            expected[key]=row['result_sha256'];convergence[key]=row['metrics']['convergence']
            proof_key=(dataset['id'],row['result_sha256'])
            if proof_key not in verified:
                cmd=[str(ROOT/'build/real_trace/verify_real'),str(ROOT/dataset['input']),str(prefix.with_suffix('.result'))]
                proof=json.loads(subprocess.check_output(cmd,text=True,env=dict(clean,RW_MAX_THREADS='1'),timeout=180))
                verified[proof_key]={'dataset':dataset['id'],'result_sha256':row['result_sha256'],'command':cmd,'result':proof}
            row['verified']=True;save(manifest,record)
            print(f"{name}: route={row['metrics']['route_ms']}ms, rss={row['max_rss_kib']/1024:.1f}MiB, same-schedule output verified",flush=True)
        check_bindings(config,builds);record['verification']=list(verified.values());record['status']='passed'
    except Exception as error:
        record['status']='failed';record['error']=str(error);raise
    finally:
        record['finished_utc']=datetime.now(timezone.utc).isoformat();save(manifest,record)
        observer.wait(timeout=10);observer_log.close()
    print('Passed matrix:',directory,flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
