"""Build a leased synchronous page-cache reference in an isolated directory."""
import json
import argparse
from pathlib import Path
import subprocess
from prepare_real import ROOT, UPSTREAM, sha
from build_paged_router import generate as paged_source


def generate():
    text = paged_source(False)
    begin = text.index('    struct SparseLabels {')
    end = text.index('    SparseLabels bSerialLabels;', begin)
    text = text[:begin] + (ROOT / 'adapters/resident_labels.inc').read_text() + text[end:]
    old = '    static inline NodeDyn& TLD(int id) { return tl_sparse ? tl_sparse->at(id) : tl_dyn[id]; }'
    assert text.count(old) == 1
    text = text.replace(old, '''    static inline LabelLease TLD(int id) {
        if (!tl_sparse) return LabelLease(nullptr, 0, tl_dyn + id);
        size_t index = tl_sparse->acquire(id);
        return LabelLease(tl_sparse, index, tl_sparse->frames[index].values.data() + (id & (tl_sparse->PSIZE-1)));
    }''')
    # Match balanced call parentheses, including nested TLD/index expressions.
    positions = []
    for start in range(len(text)):
        if not text.startswith('TLD(', start):
            continue
        at, depth = start + 4, 1
        while depth:
            if text[at] == '(':
                depth += 1
            elif text[at] == ')':
                depth -= 1
            at += 1
        if text[at:at+1] == '.':
            positions.append(at)
    if len(positions) != 28:
        raise ValueError('TLD field access audit changed: ' + str(len(positions)))
    for position in reversed(positions):
        text = text[:position] + '->' + text[position+1:]
    return '#include <list>\n' + text, len(positions)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'build/resident_real_v3')
    directory = parser.parse_args().output.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    text, count = generate()
    source = directory / 'router.cpp'
    source.write_text(text)
    binary = directory / 'router'
    command = ['g++', '-std=c++17', '-O3', '-g', '-fno-fast-math', '-fno-omit-frame-pointer',
               '-no-pie', '-pthread', '-I', str(UPSTREAM / 'cpp_router/include'), str(source), '-o', str(binary)]
    with (directory / 'build.log').open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=240)
    inputs = [Path(__file__), ROOT / 'adapters/resident_labels.inc', ROOT / 'adapters/build_paged_router.py',
              ROOT / 'adapters/build_real_router.py', UPSTREAM / 'cpp_router/src/main.cpp',
              *sorted((UPSTREAM / 'cpp_router/include').glob('*.hpp'))]
    (directory / 'build.json').write_text(json.dumps(dict(layout='resident_sync', rewritten_TLD_field_accesses=count,
        source_sha256=sha(source), binary_sha256=sha(binary), command=command,
        inputs={str(p): sha(p) for p in inputs}), indent=2) + '\n')
    print(directory, flush=True)


if __name__ == '__main__':
    main()
