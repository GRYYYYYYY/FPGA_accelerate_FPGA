"""Fixed-slot index LRU, retain exact order and safe pinned victim selection."""
import json
from pathlib import Path
import subprocess
from prepare_real import ROOT,UPSTREAM,sha

def main():
    base=ROOT/'build/resident_zero_v1';b=json.loads((base/'build.json').read_text())
    if sha(base/'router.cpp')!=b['source_sha256']:raise ValueError('Frozen base changed')
    original=(base/'router.cpp').read_text()
    text=original
    def replace(old,new):
        nonlocal text
        if text.count(old)!=1:raise ValueError('LRU anchor changed: '+old)
        text=text.replace(old,new)
    replace('            std::list<size_t>::iterator position;', '            int32_t previous = -1, next = -1;')
    replace('        std::list<size_t> lru;', '        int32_t lruHead = -1, lruTail = -1;')
    replace('                lru.push_back(i);\n                frames[i].position = std::prev(lru.end());',
            '                frames[i].previous = int32_t(i)-1;\n                frames[i].next = (i+1 < frames.size()) ? int32_t(i+1) : -1;')
    replace('            paged = true;', '            lruHead = 0; lruTail = int32_t(frames.size())-1;\n            paged = true;')
    replace('                auto victim = std::find_if(lru.begin(), lru.end(), [&](size_t i) { return frames[i].pins == 0; });\n                if (victim == lru.end()) throw std::runtime_error("All frames pinned; no safe eviction");\n                index = *victim;',
            '                int32_t victim = lruHead;\n                while (victim >= 0 && frames[size_t(victim)].pins) victim = frames[size_t(victim)].next;\n                if (victim < 0) throw std::runtime_error("All frames pinned; no safe eviction");\n                index = size_t(victim);')
    replace('            lru.splice(lru.end(), lru, frame.position);',
            '            touch(index);')
    replace('        void release(size_t index) {', '''        void touch(size_t index) {
            if (int32_t(index) == lruTail) return;
            auto& frame = frames[index];
            if (frame.previous >= 0) frames[size_t(frame.previous)].next = frame.next;
            else lruHead = frame.next;
            if (frame.next >= 0) frames[size_t(frame.next)].previous = frame.previous;
            frames[size_t(lruTail)].next = int32_t(index);
            frame.previous = lruTail; frame.next = -1; lruTail = int32_t(index);
        }
        void release(size_t index) {''')
    directory=ROOT/'build/resident_index_lru_v1';directory.mkdir(exist_ok=False);source=directory/'router.cpp';source.write_text(text)
    binary=directory/'router';cmd=['g++','-std=c++17','-O3','-g','-fno-fast-math','-fno-omit-frame-pointer','-no-pie','-pthread','-I',str(UPSTREAM/'cpp_router/include'),str(source),'-o',str(binary)]
    with (directory/'build.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=240)
    inputs=dict(b['inputs']);inputs[str(base/'router.cpp')]=sha(base/'router.cpp');inputs[str(Path(__file__).resolve())]=sha(__file__)
    for p,h in inputs.items():
        if sha(p)!=h:raise ValueError('Frozen source changed: '+p)
    (directory/'build.json').write_text(json.dumps(dict(layout='resident_index_lru',source_sha256=sha(source),binary_sha256=sha(binary),inputs=inputs,command=cmd,change='Exact LRU via fixed frame indices; prefetch-on and other label semantics unchanged.'),indent=2)+'\n')
    test=ROOT/'tests/resident_index_lru_semantics.cpp';testbinary=directory/'test_labels'
    cmd=['g++','-std=c++17','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie','-pthread','-I',str(directory),'-I',str(UPSTREAM/'cpp_router/include'),str(test),'-o',str(testbinary)]
    with (directory/'test_build.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=240)
    run=['taskset','-c','24',str(testbinary)]
    with (directory/'semantic_tests.log').open('w') as f:subprocess.run(run,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=120)
    (directory/'semantic_tests.json').write_text(json.dumps(dict(status='passed',sanitizers=['address','undefined'],test_source_sha256=sha(test),router_source_sha256=sha(source),test_binary_sha256=sha(testbinary),log_sha256=sha(directory/'semantic_tests.log'),command=run,scope='Actual index-LRU class with independent list-order/pin oracle plus zero/read/write/lease/eviction/reset/wrap suite.'),indent=2)+'\n')
    print(directory)
if __name__=='__main__':main()
