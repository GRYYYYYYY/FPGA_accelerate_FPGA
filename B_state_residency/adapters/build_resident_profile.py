"""Build PC-sampling-only diagnostic; freeze resident label implementation."""
import json
from pathlib import Path
import subprocess
from prepare_real import ROOT, UPSTREAM, sha

def main():
    base=ROOT/'build/resident_zero_v1'
    frozen=json.loads((base/'build.json').read_text())
    if sha(base/'router.cpp')!=frozen['source_sha256']:raise ValueError('Frozen source changed')
    original=(base/'router.cpp').read_text()
    text='#include "real_profile.hpp"\n'+original
    anchor='    router.routeIndirectConnectionsIteratively();\n    auto t2 = clk::now();'
    if text.count(anchor)!=1:raise ValueError('Route anchor changed')
    text=text.replace(anchor,'    bprof::startSampling();\n'+anchor+'\n    bprof::stopSampling();')
    anchor='    auto t3 = clk::now();'
    if text.count(anchor)!=1:raise ValueError('Report anchor changed')
    text=text.replace(anchor,anchor+'\n    bprof::report(std::chrono::duration<double,std::milli>(t1-t0).count(), std::chrono::duration<double,std::milli>(t2-t1).count(), std::chrono::duration<double,std::milli>(t3-t2).count());')
    begin=original.index('    struct SparseLabels {');end=original.index('    SparseLabels bSerialLabels;',begin)
    region=original[begin:end]
    if region not in text:raise ValueError('Resident core changed')
    directory=ROOT/'build/resident_profile_v1';directory.mkdir(exist_ok=False)
    source=directory/'router.cpp';source.write_text(text);binary=directory/'router'
    cmd=['g++','-std=c++17','-O3','-g','-fno-fast-math','-fno-omit-frame-pointer','-no-pie','-pthread','-I',str(UPSTREAM/'cpp_router/include'),'-I',str(ROOT/'adapters'),str(source),'-o',str(binary)]
    with (directory/'build.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=240)
    inputs=dict(frozen['inputs']);inputs.update({str(base/'router.cpp'):sha(base/'router.cpp'),str(ROOT/'adapters/real_profile.hpp'):sha(ROOT/'adapters/real_profile.hpp'),str(Path(__file__).resolve()):sha(__file__)})
    (directory/'build.json').write_text(json.dumps(dict(layout='resident_zero_pc_sampling',source_sha256=sha(source),binary_sha256=sha(binary),command=cmd,inputs=inputs,core_identical=True,core_proof=str(base/'semantic_tests.json'),scope='No per-access timers; route CPU PC sampling only; off/on diagnostic pair required.'),indent=2)+'\n')
    print(directory)
if __name__=='__main__':main()
