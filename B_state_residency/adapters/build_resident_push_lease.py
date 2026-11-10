"""Scoped same-node push lease; preserve frozen index LRU baseline."""
import json
from pathlib import Path
import subprocess
from prepare_real import ROOT,UPSTREAM,sha

def main():
    base=ROOT/'build/resident_index_lru_v1';b=json.loads((base/'build.json').read_text())
    if sha(base/'router.cpp')!=b['source_sha256']:raise ValueError('Frozen base changed')
    original=(base/'router.cpp').read_text()
    old = '        TLD(child)->lb = newTotal;\n        TLD(child)->upstream = newPartial;\n        TLD(child)->visited = st.sequence;'
    new = '        { // Release before recursive expansion or queue work.\n            auto label = TLD(child);\n            label->lb = newTotal;\n            label->upstream = newPartial;\n            label->visited = st.sequence;\n        }'
    if original.count(old)!=1:raise ValueError('Push write audit changed')
    text=original.replace(old,new)
    directory=ROOT/'build/resident_push_lease_v1';directory.mkdir(exist_ok=False);source=directory/'router.cpp';source.write_text(text)
    binary=directory/'router';cmd=['g++','-std=c++17','-O3','-g','-fno-fast-math','-fno-omit-frame-pointer','-no-pie','-pthread','-I',str(UPSTREAM/'cpp_router/include'),str(source),'-o',str(binary)]
    with (directory/'build.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=240)
    inputs=dict(b['inputs']);inputs[str(base/'router.cpp')]=sha(base/'router.cpp');inputs[str(Path(__file__).resolve())]=sha(__file__)
    for p,h in inputs.items():
        if sha(p)!=h:raise ValueError('Frozen source changed: '+p)
    (directory/'build.json').write_text(json.dumps(dict(layout='resident_push_lease',source_sha256=sha(source),binary_sha256=sha(binary),inputs=inputs,command=cmd,change='Only push three adjacent same-node writes share one scoped lease, destroyed before recursion/queue.'),indent=2)+'\n')
    test=ROOT/'tests/resident_push_lease_semantics.cpp';testbinary=directory/'test_labels'
    cmd=['g++','-std=c++17','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie','-pthread','-I',str(directory),'-I',str(UPSTREAM/'cpp_router/include'),str(test),'-o',str(testbinary)]
    with (directory/'test_build.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=240)
    run=['taskset','-c','24',str(testbinary)]
    with (directory/'semantic_tests.log').open('w') as f:subprocess.run(run,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=120)
    (directory/'semantic_tests.json').write_text(json.dumps(dict(status='passed',sanitizers=['address','undefined'],test_source_sha256=sha(test),router_source_sha256=sha(source),test_binary_sha256=sha(testbinary),log_sha256=sha(directory/'semantic_tests.log'),command=run,scope='Actual push function, field and queue behavior, lease release; inherited exact index LRU and value/reset/wrap suite.'),indent=2)+'\n')
    print(directory)
if __name__=='__main__':main()
