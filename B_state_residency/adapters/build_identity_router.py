"""Independent sparse/dense identity variant; frozen compact baseline stays intact."""
import argparse
import json
from pathlib import Path
import subprocess
from prepare_real import ROOT, UPSTREAM, sha
from build_compact_router import generate as compact_source


def generate():
    text = compact_source()
    begin = text.index('    struct SparseLabels {')
    end = text.index('    SparseLabels bSerialLabels;', begin)
    section = text[begin:end]
    def replace(old, new):
        nonlocal section
        if section.count(old) != 1:
            raise ValueError('Identity anchor mismatch: ' + old)
        section = section.replace(old, new)
    replace('        std::vector<uint32_t> bNodeEpoch;',
            '        std::vector<int32_t> bDenseIds; // compact index -> global node ID')
    replace('            bNodeEpoch.resize(pool.size()); bNodeEpoch.shrink_to_fit();', '')
    replace('                bCompactValues.resize(65536); bCompactValues.shrink_to_fit();',
            '                bCompactValues.resize(65536); bCompactValues.shrink_to_fit();\n                bDenseIds.resize(65536); bDenseIds.shrink_to_fit();')
    replace('bNodeEpoch.capacity()*sizeof(uint32_t)', '0')
    replace('"compact\\\",\\\"pool_slot_bytes', '"sparse_identity\\\",\\\"pool_slot_bytes')
    anchor='                << ",\\\"compact_live_nodes\\\":" << bCompactUsed'
    replace(anchor, '                << ",\\\"dense_id_bytes\\\":" << bDenseIds.capacity()*sizeof(int32_t)\n' + anchor)
    replace('            bNodeEpoch.assign(pool.size(), 0);', '            bDenseIds.assign(bCompactValues.size(), -1);')
    replace('            if (bNodeEpoch[slot] == cur)\n                __builtin_prefetch(bCompactValues.data()+pool[slot], 1, 3);',
            '            uint32_t index = pool[slot];\n            if (index < bCompactUsed && bDenseIds[index] == id)\n                __builtin_prefetch(bCompactValues.data()+index, 1, 3);')
    replace('                std::fill(bNodeEpoch.begin(), bNodeEpoch.end(), 0);', '')
    replace('                        bNodeEpoch.resize(pool.size(), 0);', '')
    replace('                if (bNodeEpoch[slot] != cur) {',
            '                uint32_t oldIndex = pool[slot];\n                if (oldIndex >= bCompactUsed || bDenseIds[oldIndex] != id) {')
    replace('                        bPeakCompactNodes = std::max(bPeakCompactNodes, bCompactValues.size());',
            '                        bDenseIds.resize(bCompactValues.size(), -1);\n                        bPeakCompactNodes = std::max(bPeakCompactNodes, bCompactValues.size());')
    replace('                    bNodeEpoch[slot] = cur;', '                    bDenseIds[index] = id;')
    text = text[:begin] + section + text[end:]
    text = text.replace('(B_NODE_EPOCH?"true":"false")', '"false"')
    return '#define B_SPARSE_IDENTITY 1\n' + text


def build(directory):
    directory.mkdir(parents=True, exist_ok=False)
    source = directory / 'router.cpp'
    source.write_text(generate())
    binary = directory / 'router'
    command = ['g++', '-std=c++17', '-O3', '-g', '-fno-fast-math', '-fno-omit-frame-pointer',
               '-no-pie', '-pthread', '-I', str(UPSTREAM / 'cpp_router/include'), str(source), '-o', str(binary)]
    with (directory / 'build.log').open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=240)
    inputs = [Path(__file__), ROOT / 'adapters/build_compact_router.py', ROOT / 'adapters/build_paged_router.py',
              ROOT / 'adapters/build_real_router.py', UPSTREAM / 'cpp_router/src/main.cpp',
              *sorted((UPSTREAM / 'cpp_router/include').glob('*.hpp'))]
    record = {'layout': 'sparse_identity', 'variants': {'sparse_identity': {
        'source': str(source), 'binary': str(binary), 'command': command,
        'source_sha256': sha(source), 'binary_sha256': sha(binary)}},
        'inputs': {str(p): sha(p) for p in inputs}}
    (directory / 'build.json').write_text(json.dumps(record, indent=2) + '\n')
    print('Built', directory, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'build/identity_real_v1')
    args = parser.parse_args()
    build(args.output.resolve())
