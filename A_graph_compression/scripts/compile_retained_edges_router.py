#!/usr/bin/env python3
"""Build the frozen edge-retention router without changing prior artifacts."""
import hashlib
import json
from pathlib import Path
import subprocess
import os

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    base=Path('data/derived/round_control_router_20261024_v1').resolve()
    out=Path('data/derived/retained_edges_integration_20261024_v1').resolve()
    plan=json.loads((out/'plan.json').read_text())
    for p,h in plan['files'].items():
        if sha(p)!=h:raise ValueError('Input changed '+p)
    cmd=json.loads((base/'compile_router.receipt.json').read_text())['command']
    cmd=[x.replace(str(base/'source'),str(out/'source')).replace(str(base/'router'),str(out/'router')) for x in cmd]
    cmd[2]='120'
    cmd.insert(cmd.index('-o'),str(out/'edge_top_regular.o'))
    first=['taskset','-c','120','g++','-std=c++14','-O2','-Wall','-Wextra','-Werror','-Wno-unknown-pragmas','-I'+str(out/'source'),'-c',str(out/'source/search_retained_edges_top.cpp'),'-o',str(out/'edge_top_regular.o')]
    bindings=dict(plan['files'])
    for x in cmd:
        if x.endswith('.o') and Path(x).exists():bindings[x]=sha(x)
    p=out/'regular_build_plan.json'
    record=dict(owner_pid=os.getpid(),files=bindings,commands=[first,cmd],script_sha256=sha(__file__))
    with p.open('x') as f:json.dump(record,f,indent=2);f.write('\n')
    for name,command in [('compile_edge_regular',first),('compile_router',cmd)]:
        with (out/(name+'.log')).open('x') as f:code=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT).returncode
        receipt=dict(command=command,exit_code=code,log_sha256=sha(out/(name+'.log')),plan_sha256=sha(p))
        with (out/(name+'.receipt.json')).open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
        if code:raise SystemExit(code)
        print(name,'PASS',flush=True)
    for path,h in bindings.items():
        if sha(path)!=h:raise ValueError('Changed build input '+path)
    with (out/'regular_build_complete.json').open('x') as f:json.dump(dict(status='compiled',plan_sha256=sha(p),binary_sha256=sha(out/'router'),object_sha256=sha(out/'edge_top_regular.o')),f,indent=2)
if __name__=='__main__':main()
