"""Capture selected complete real scratch values; gate on native and full-route equivalence."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'adapters'))
from prepare_real import sha, UPSTREAM
from profile_real import parse_log
from audit_real_value_trace import audit


def main():
    build = ROOT/'build/real_values_trace_v1'
    frozen = json.loads((build/'build.json').read_text())
    for path,digest in frozen['inputs'].items():
        if sha(path) != digest: raise ValueError('Frozen build input changed: '+path)
    for name,key in [('router.cpp','source_sha256'),('router','binary_sha256')]:
        if sha(build/name) != frozen[key]: raise ValueError('Frozen build changed')
    out = ROOT/'results'/('real_field_values_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    out.mkdir()
    selected = set(range(1,9)); expected = {}; iterations = set()
    metadata = ROOT/'results/real_trace_20261022T165136Z/tail/trace.jsonl'
    for line in metadata.open():
        row = json.loads(line)
        if row['iteration'] not in iterations or row['accesses_selected']:
            selected.add(row['attempt']); iterations.add(row['iteration'])
        if row['attempt'] in selected:
            expected[row['attempt']] = {key:row[key] for key in ('iteration','connection_index','connection_id','net_index')}
    selection = out/'selection.txt'; selection.write_text(''.join(str(i)+'\n' for i in sorted(selected)))
    native_selection = out/'native_selection.txt'; native_selection.write_text('1\n2\n')
    input_path = ROOT/'data/derived/logicnets_jscl.rrt'
    if sha(input_path) != 'd03de37af1a4a0b10f8bb29812b0048c4d2dd57ba6dadb70f61853225e39b6f4':
        raise ValueError('Real input changed')
    reference = ROOT/'results/real_trace_20261022T165136Z/original_0.log'
    paths = [Path(__file__).resolve(),ROOT/'scripts/audit_real_value_trace.py',ROOT/'tests/real_values_semantics.cpp',
             ROOT/'src/scratch_page_values.py',ROOT/'tests/test_scratch_page_values.py',build/'router.cpp',build/'router',build/'build.json',
             *map(Path,frozen['inputs']),metadata,selection,input_path,reference]
    hashes = {str(path):sha(path) for path in paths}
    record = dict(status='running',runner_pid=os.getpid(),execution_kind='real_cpu_field_value_trace',performance=None,
                  selected_attempts=sorted(selected),selection_rule='First eight attempts, first attempt of every iteration, and all 19 previously selected large queries.',
                  files=hashes,build=frozen,scope='Frozen serial CPU index-LRU scratch, actual five-field operations with global hist observed separately. Not hardware timing or an end-to-end device implementation.')
    def save():
        temp = out/'manifest.json.tmp'; temp.write_text(json.dumps(record,indent=2)+'\n'); temp.replace(out/'manifest.json')
    for path in paths:
        if path.suffix in ('.py','.hpp','.cpp'):
            (out/path.name).write_bytes(path.read_bytes())
    save(); print(out,flush=True)
    env = {key:value for key,value in os.environ.items() if not key.startswith(('RW_','B_'))}
    env.update(RW_MAX_THREADS='1',RW_PAR_PART='0',RW_PAR_ITER1='0',RW_OVERLAP='0',RW_BATCH_T='0',RW_GPU_FLOOD='0',
               B_SERIAL_PAGED='1',B_RESIDENT_PAGES='256',RW_BATCH_PBITS='6')
    try:
        native = out/'native_test'
        command = ['g++','-std=c++17','-O1','-g0','-fsanitize=address,undefined','-fno-omit-frame-pointer','-pthread',
                   '-I',str(build),'-I',str(ROOT/'adapters'),'-I',str(UPSTREAM/'cpp_router/include'),
                   str(ROOT/'tests/real_values_semantics.cpp'),'-o',str(native)]
        record['native_compile_command']=command; save()
        with (out/'native_build.log').open('w') as log:
            subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
        with (out/'native_test.log').open('w') as log:
            subprocess.run([str(native)],env=dict(env,B_VALUES_PREFIX=str(out/'native'),B_VALUES_SELECTION=str(native_selection)),stdout=log,stderr=subprocess.STDOUT,check=True)
        record['native_audit']=audit(out/'native',1024,{1,2}); save()
        print('Generated native proxies: ASan/UBSan and trace audit passed',flush=True)
        with (out/'tests.log').open('w') as log:
            subprocess.run([sys.executable,'-m','unittest','discover','-s','tests'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        prefix = out/'trace'; result_path = out/'trace.result'
        command = ['taskset','-c','25',str(build/'router'),str(input_path),str(result_path)]
        record.update(command=command,environment=dict(env,B_VALUES_PREFIX=str(prefix),B_VALUES_SELECTION=str(selection))); save()
        with (out/'route.log').open('w') as log:
            subprocess.run(command,env=record['environment'],stdout=log,stderr=subprocess.STDOUT,check=True)
        metrics = parse_log((out/'route.log').read_text()); old_metrics = parse_log(reference.read_text())
        for key in ('iterations','overused','pushes','used_nodes','wire_length','convergence'):
            if metrics[key] != old_metrics[key]: raise ValueError('Instrumentation changed routing: '+key)
        if sha(result_path) != '428fa84ffa9e9839965c5000a32a4078f2fc7ea3f787a50cd4f7aff57447aa84':
            raise ValueError('Instrumentation changed complete route output')
        record.update(result_sha256=sha(result_path),metrics=metrics,route_equivalence='passed'); save()
        print('Full real route output and convergence match original',flush=True)
        field_ids = dict(lb=0,upstream=1,prev=2,visited=3,target=4)
        sites = {(site['line'],field_ids[site['field']],site['write']) for site in frozen['field_sites']}
        trace = audit(prefix,9089009,selected,sites)
        for row in trace['queries']:
            if any(row[key] != value for key,value in expected[row['attempt']].items()):
                raise ValueError('Selected attempt identity changed')
        (out/'trace.audit.json').write_text(json.dumps(trace,indent=2)+'\n')
        record['trace_totals']=trace['totals']
        record['artifacts']={str(path):sha(path) for path in (Path(str(prefix)+'.queries.jsonl'),Path(str(prefix)+'.values'),out/'trace.audit.json',out/'tests.log',native,out/'native_test.log',out/'route.log')}
        if any(sha(path) != digest for path,digest in hashes.items()): raise ValueError('Bound input/source changed')
        record['status']='passed'
        print(json.dumps(trace['totals']),flush=True)
    except Exception as error:
        record.update(status='failed',error=repr(error)); raise
    finally:
        save()


if __name__ == '__main__': main()
