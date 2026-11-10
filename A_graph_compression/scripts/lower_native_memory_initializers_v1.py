#!/usr/bin/env python3
"""Private simulation-model edit: static zero-init function, unchanged full arrays.

The function is called from a static variable initializer, before initial blocks.
No memory capacity, page count, address mapping or AXI behavior is changed.
Requires separate simulator validation; this script is not a functional checker.
"""
import argparse
import json
from pathlib import Path
import re
from check_vitis_kernel import digest, require
from run_compact_native_stack_recovery_v3 import atomic


def lower(raw, name):
    pattern = re.compile(r"(?m)^reg (\[" + re.escape(name) + r"_DATA_BITWIDTH - 1 : 0\] " + re.escape(name) + r"_mem_([0-3]) \[0: " + re.escape(name) + r"_mem_depth - 1\]) = '\{default : 'h0\}; *$")
    matches = list(pattern.finditer(raw))
    require([m[2] for m in matches] == ['0','1','2','3'], 'Not four exact initialized pages')
    require(all(raw[a.end():b.start()] == '\n' for a,b in zip(matches,matches[1:])), 'Nonadjacent page declarations')
    require('a_initialize_full_pages_v1' not in raw, 'Initialization helper already present')
    replacement = '\n'.join('reg '+m[1]+';' for m in matches) + '\n'
    replacement += 'function automatic a_initialize_full_pages_v1;\n  integer a_page_index;\n  begin\n'
    replacement += f'    for (a_page_index = 0; a_page_index < {name}_mem_depth; a_page_index = a_page_index + 1) begin\n'
    replacement += ''.join(f"      {name}_mem_{i}[a_page_index] = 'h0;\n" for i in range(4))
    replacement += '    end\n    a_initialize_full_pages_v1 = 1\'b1;\n  end\nendfunction\n'
    replacement += 'reg a_full_pages_initialized_v1 = a_initialize_full_pages_v1();'
    start, end = matches[0].start(), matches[-1].end()
    changed = raw[:start]+replacement+raw[end:]
    require(changed.replace(replacement, raw[start:end], 1) == raw, 'Noninitialization text changed')
    return changed, replacement


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source, out = args.source.resolve(), args.output.resolve()
    require(not out.exists(), 'Refuse existing output')
    report = json.loads((source/'report.json').read_text())
    require(report['status'] == 'sized_unsigned_onehot_literals_value_and_text_roundtrip_verified', 'Wrong source report')
    out.mkdir(parents=True)
    records = []
    for row in report['files']:
        src = Path(row['destination'])
        require(src.parent == source and digest(src) == row['normalized_sha256'], 'Changed input')
        raw = src.read_text()
        edited = src.name.startswith('AESL_axi_master_')
        replacement = None
        if edited:
            name = src.stem.removeprefix('AESL_axi_master_')
            raw, replacement = lower(raw, name)
        dst = out/src.name
        dst.write_text(raw)
        records.append(dict(source=str(src), destination=str(dst), original_sha256=digest(src),
                            sha256=digest(dst), memory_initializer_changed=edited, replacement=replacement))
    require(len(records) == 154 and sum(r['memory_initializer_changed'] for r in records) == 30, 'Full source/model set changed')
    atomic(out/'report.json', dict(status='full154_sources_30_models_4pages_static_initializer_candidate_not_accepted',
           files=records, source_report=str(source/'report.json'), source_report_sha256=digest(source/'report.json'),
           script_sha256=digest(__file__), functional_acceptance=False, original_sources_modified=False))
    print(json.dumps(dict(output=str(out), sources=len(records), models=30, pages_per_model=4)))


if __name__ == '__main__':
    main()
