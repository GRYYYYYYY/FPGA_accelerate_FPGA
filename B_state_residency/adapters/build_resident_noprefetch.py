"""Single-change resident label prefetch ablation; preserve frozen originals."""
import json
from pathlib import Path
import subprocess
from prepare_real import ROOT,UPSTREAM,sha

def main():
    base=ROOT/'build/resident_zero_v1';b=json.loads((base/'build.json').read_text())
    if sha(base/'router.cpp')!=b['source_sha256']:raise ValueError('Frozen base changed')
    original=(base/'router.cpp').read_text()
    begin=original.index('        void prefetch(int id) const {');end=original.index('        void bAfterPoolShrink()',begin)
    before=original[begin:end]
    if before.count('__builtin_prefetch')!=1:raise ValueError('Prefetch anchor changed')
    text=original[:begin]+'        void prefetch(int) const {} // isolated resident prefetch ablation\n'+original[end:]
    directory=ROOT/'build/resident_noprefetch_v1';directory.mkdir(exist_ok=False);source=directory/'router.cpp';source.write_text(text)
    binary=directory/'router';cmd=['g++','-std=c++17','-O3','-g','-fno-fast-math','-fno-omit-frame-pointer','-no-pie','-pthread','-I',str(UPSTREAM/'cpp_router/include'),str(source),'-o',str(binary)]
    with (directory/'build.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=240)
    inputs=dict(b['inputs']);inputs[str(base/'router.cpp')]=sha(base/'router.cpp');inputs[str(Path(__file__).resolve())]=sha(__file__)
    for p,h in inputs.items():
        if sha(p)!=h:raise ValueError('Frozen source changed: '+p)
    (directory/'build.json').write_text(json.dumps(dict(layout='resident_noprefetch',source_sha256=sha(source),binary_sha256=sha(binary),inputs=inputs,command=cmd,change='Only SparseLabels::prefetch body replaced by no-op; other prefetch paths unchanged.'),indent=2)+'\n')
    test=ROOT/'tests/resident_zero_semantics.cpp';testbinary=directory/'test_labels'
    cmd=['g++','-std=c++17','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie','-pthread','-I',str(directory),'-I',str(UPSTREAM/'cpp_router/include'),str(test),'-o',str(testbinary)]
    with (directory/'test_build.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=240)
    run=['taskset','-c','24',str(testbinary)]
    with (directory/'semantic_tests.log').open('w') as f:subprocess.run(run,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=120)
    (directory/'semantic_tests.json').write_text(json.dumps(dict(status='passed',sanitizers=['address','undefined'],test_source_sha256=sha(test),router_source_sha256=sha(source),test_binary_sha256=sha(testbinary),log_sha256=sha(directory/'semantic_tests.log'),command=run,scope='Actual no-prefetch class, same zero/read/write, lease, eviction/reset/wrap native suite.'),indent=2)+'\n')
    print(directory)
if __name__=='__main__':main()
