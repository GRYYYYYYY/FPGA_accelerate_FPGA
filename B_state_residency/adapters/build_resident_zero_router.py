"""Independent read-zero bypass; leave prior resident builds frozen."""
import json
from pathlib import Path
import subprocess
from prepare_real import ROOT, UPSTREAM, sha
from build_resident_rw_router import generate as rw_source


def generate():
    text, reads, writes = rw_source()
    anchor = '        size_t acquire(int id, bool write = true) {'
    extra = '''        uint64_t zeroReads = 0;
        bool readIsZero(int id) {
            if (id < 0 || (size_t(id) >> PBITS) >= pageEp.size()) throw std::runtime_error("Bad label node");
            int page = id >> PBITS;
            if (pageEp[size_t(page)] == cur || backing.find(page) != backing.end()) return false;
            ++zeroReads;
            return true;
        }
'''
    assert text.count(anchor) == 1
    text = text.replace(anchor, extra + anchor)
    anchor = '        size_t index = tl_sparse->acquire(id,false);'
    assert text.count(anchor) == 1
    text = text.replace(anchor, '''        // No resident or saved page: all fields have the query's default value.
        // Independent storage stays stable even if another operand allocates a page.
        static NodeDyn zero{};
        if (tl_sparse->readIsZero(id)) return ReadLabelLease(nullptr,0,&zero);
''' + anchor)
    anchor = '<< ",\\\"first_pages\\\":" << firstPages'
    assert text.count(anchor) == 1
    text = text.replace(anchor, '<< ",\\\"zero_reads\\\":" << zeroReads\n                ' + anchor)
    return text, reads, writes


def main():
    directory = ROOT / 'build/resident_zero_v1'
    directory.mkdir(parents=True, exist_ok=False)
    text, reads, writes = generate()
    source = directory / 'router.cpp'; source.write_text(text)
    binary = directory / 'router'
    command = ['g++','-std=c++17','-O3','-g','-fno-fast-math','-fno-omit-frame-pointer','-no-pie','-pthread','-I',str(UPSTREAM/'cpp_router/include'),str(source),'-o',str(binary)]
    with (directory/'build.log').open('w') as log:
        subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
    base = json.loads((ROOT/'build/resident_rw_v2/build.json').read_text())
    inputs = dict(base['inputs']);inputs[str(Path(__file__).resolve())] = sha(__file__)
    for p,h in inputs.items():
        if sha(p)!=h: raise ValueError('Frozen base changed: '+p)
    (directory/'build.json').write_text(json.dumps(dict(layout='resident_zero',source_sha256=sha(source),binary_sha256=sha(binary),command=command,inputs=inputs,read_sites=reads,write_sites=writes),indent=2)+'\n')
    print(directory)

if __name__ == '__main__': main()
