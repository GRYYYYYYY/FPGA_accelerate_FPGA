#!/usr/bin/env python3
"""Run explicit empty-occupancy source/sink probes, not negotiated full routing."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from prepare_search_heap_router import ROOT,digest

OUT=ROOT/'data/derived/search_snapshot_probes_20261024_v1'

def save(path,obj):
    with path.open('x') as f:json.dump(obj,f,indent=2);f.write('\n')

def main():
    baseline_path=ROOT/'data/derived/native_site_runtime_validation_20261023_v1/plan.json'
    baseline=json.loads(baseline_path.read_text())
    OUT.mkdir(exist_ok=False);binary=OUT/'probe'
    shutil.copyfile('/tmp/a_search_snapshot_real_search_20261024',binary);binary.chmod(0o755)
    paths=list((ROOT/'src/native').glob('*.hpp'))+[ROOT/'tests/test_search_snapshot_real_search.cpp',Path(__file__).resolve()]
    paths += [ROOT/'hardware/vitis'/name for name in ['search_heap.hpp','search_heap_external.hpp','search_site_state.hpp','search_label_index.hpp','search_label_records.hpp','search_controller.hpp','search_cost_snapshot.hpp','search_snapshot_provider.hpp']]
    files={str(p):digest(p) for p in paths};files[str(binary)]=digest(binary)
    for inputs in baseline['inputs'].values():
        for p in inputs.values():
            if digest(p)!=baseline['code_inputs_and_references'][p]:raise ValueError('Changed real fixture '+p)
            files[p]=digest(p)
    plan={'owner_pid':os.getpid(),'files':files,'binary':str(binary),'inputs':baseline['inputs'],
          'scope':'16 independent real source/sink queries per mode, every 67th net, first sink, empty dynamic node/site occupancy and history, actual fixed/protected/reserved resources.',
          'compiler_flags':['-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined'],
          'limitations':['CPU native adjacency decoder, bounded static semantic/cost provider; no HLS/RTL/board result.',
                         'Not a complete 1062-net negotiated route and not a performance comparison.']}
    save(OUT/'plan.json',plan)
    for mode in ['csr','compact']:
        inp=baseline['inputs'][mode]
        command=['taskset','-c','120',str(binary),inp['image'],inp['fixture'],inp['sites']]
        with (OUT/(mode+'.log')).open('x') as log:
            start=time.monotonic();p=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
            save(OUT/(mode+'.submission.json'),{'command':command,'pid':p.pid,'plan_sha256':digest(OUT/'plan.json')})
            code=p.wait()
        save(OUT/(mode+'.receipt.json'),{'exit_code':code,'wall_seconds':time.monotonic()-start,'command':command,'log_sha256':digest(OUT/(mode+'.log'))})
        if code:raise RuntimeError(mode+' snapshot probe failed')
        print((OUT/(mode+'.log')).read_text(),flush=True)

if __name__=='__main__':main()
