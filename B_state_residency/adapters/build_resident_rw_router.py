"""Read/write leases in a new build; preserve resident_real_v3."""
import json
from pathlib import Path
import re
import subprocess
from prepare_real import ROOT, UPSTREAM, sha
from build_resident_router import generate as resident_source


def generate():
    text, _ = resident_source()
    assert text.count('size_t acquire(int id)') == 1
    text = text.replace('size_t acquire(int id)', 'size_t acquire(int id, bool write = true)')
    text = text.replace('frame.dirty = true;', 'frame.dirty = frame.dirty || write;')
    assert text.count('                frame.page = page;') == 1
    text = text.replace('                frame.page = page;',
                        '                frame.page = page;\n                frame.dirty = false; // new binding starts clean')
    reads, writes = [], []
    for match in re.finditer(r'\bTLD\(', text):
        at, depth = match.end(), 1
        while depth:
            depth += (text[at] == '(') - (text[at] == ')')
            at += 1
        field = re.match(r'->(lb|upstream|hist|prev|visited|target)\b', text[at:])
        if not field:
            continue
        following = text[at+field.end():].lstrip()
        (writes if re.match(r'=(?!=)', following) else reads).append(match.start())
    if (len(reads), len(writes)) != (18, 10):
        raise ValueError('Read/write access audit changed: ' + str((len(reads), len(writes))))
    for start in reversed(reads):
        text = text[:start] + 'TLRead' + text[start+3:]
    anchor = '    SparseLabels bSerialLabels;'
    extra = '''    struct ReadLabelLease {
        LabelLease lease;
        ReadLabelLease(SparseLabels* owner, size_t index, NodeDyn* value) : lease(owner,index,value) {}
        const NodeDyn* operator->() const { return lease.value; }
    };
    static inline ReadLabelLease TLRead(int id) {
        if (!tl_sparse) return ReadLabelLease(nullptr,0,tl_dyn+id);
        size_t index = tl_sparse->acquire(id,false);
        return ReadLabelLease(tl_sparse,index,tl_sparse->frames[index].values.data()+(id&(tl_sparse->PSIZE-1)));
    }
'''
    return text.replace(anchor, extra+anchor), len(reads), len(writes)


def main():
    directory = ROOT / 'build/resident_rw_v2'
    directory.mkdir(parents=True, exist_ok=False)
    text, reads, writes = generate()
    source = directory / 'router.cpp'
    source.write_text(text)
    binary = directory / 'router'
    command = ['g++', '-std=c++17', '-O3', '-g', '-fno-fast-math', '-fno-omit-frame-pointer',
               '-no-pie', '-pthread', '-I', str(UPSTREAM / 'cpp_router/include'), str(source), '-o', str(binary)]
    with (directory / 'build.log').open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=240)
    previous = json.loads((ROOT / 'build/resident_real_v3/build.json').read_text())
    inputs = dict(previous['inputs'])
    inputs[str(Path(__file__).resolve())] = sha(__file__)
    for path, digest in inputs.items():
        if sha(path) != digest:
            raise ValueError('Frozen base changed: ' + path)
    record = dict(layout='resident_rw', source_sha256=sha(source), binary_sha256=sha(binary),
                  command=command, inputs=inputs, read_sites=reads, write_sites=writes)
    (directory / 'build.json').write_text(json.dumps(record, indent=2) + '\n')
    print(directory, flush=True)


if __name__ == '__main__':
    main()
