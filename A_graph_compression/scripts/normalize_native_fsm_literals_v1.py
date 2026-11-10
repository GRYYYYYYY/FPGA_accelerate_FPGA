#!/usr/bin/env python3
"""Normalize only sized, unsigned one-hot parameter literals in a private copy.

Checks exact width/value/name relationships and reconstructs the original bytes.
This is not a simulation verdict or a change to the original RTL input tree.
"""
import argparse
import json
from pathlib import Path
import re
import shlex
import sys

from check_vitis_kernel import digest, require
from run_recovered_native_rtl_v2 import OUT as LIVE
from run_compact_native_stack_recovery_v3 import atomic

PARAM = re.compile(rb'(?m)^(parameter\s+ap_ST_fsm_state([0-9]+)\s*=\s*)([0-9]+)\x27d([0-9]+)(;[ \t]*\r?$)')


def normalize(raw):
    replacements = []
    def convert(match):
        prefix, index, width, number, suffix = match.groups()
        index, bits, value = int(index), int(width), int(number)
        require(0 < index <= bits and value == 1 << (index-1), 'Not the expected sized unsigned one-hot constant')
        literal = width + b"'h" + format(value, 'x').encode()
        require(int(literal.split(b"'h")[1], 16) == value and value.bit_length() <= bits, 'Numeric normalization differs')
        replacement = prefix + literal + suffix
        replacements.append((match.start(), match.end(), replacement, match.group()))
        return replacement
    normalized = PARAM.sub(convert, raw)
    # Independent positional reconstruction checks all text outside substitutions.
    cursor = 0
    rebuilt = bytearray()
    for start, end, new, old in replacements:
        unchanged = raw[cursor:start]
        require(normalized[len(rebuilt):len(rebuilt)+len(unchanged)] == unchanged, 'Nonliteral text changed')
        rebuilt.extend(unchanged)
        rebuilt.extend(new)
        cursor = end
    rebuilt.extend(raw[cursor:])
    require(bytes(rebuilt) == normalized, 'Unexpected substitution')
    # Reverse only recorded replacement spans and demand byte-identical source.
    restored = bytearray()
    src_pos = dst_pos = 0
    for start, end, new, old in replacements:
        n = start-src_pos
        restored.extend(normalized[dst_pos:dst_pos+n])
        dst_pos += n
        require(normalized[dst_pos:dst_pos+len(new)] == new, 'Replacement span differs')
        restored.extend(old)
        dst_pos += len(new)
        src_pos = end
    restored.extend(normalized[dst_pos:])
    require(bytes(restored) == raw, 'Source reconstruction failed')
    return normalized, len(replacements)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sys.set_int_max_str_digits(100000)
    out = args.output.resolve()
    require(not out.exists(), 'Refuse existing normalization output')
    plan = json.loads((LIVE/'plan.json').read_text())
    rtl = LIVE/'sim/verilog'
    project = rtl/'search_batch_trace_top_v2.prj'
    sources = [rtl/shlex.split(line)[2] for line in project.read_text().splitlines() if line.strip()]
    require(len(sources) == 154 and len(set(sources)) == 154, 'Changed full source set')
    out.mkdir(parents=True)
    records = []
    for src in sources:
        require(digest(src) == plan['preserved_inputs'][str(src)], 'Original source changed')
        raw = src.read_bytes()
        normalized, count = normalize(raw)
        dst = out/src.name
        dst.write_bytes(normalized)
        records.append(dict(source=str(src), destination=str(dst), original_sha256=digest(src),
                            normalized_sha256=digest(dst), constants=count,
                            original_bytes=len(raw), normalized_bytes=len(normalized)))
    require(sum(row['constants'] for row in records) > 0, 'No constants normalized')
    atomic(out/'report.json', dict(status='sized_unsigned_onehot_literals_value_and_text_roundtrip_verified',
           files=records, source_count=len(sources), constants=sum(row['constants'] for row in records),
           original_plan_sha256=digest(LIVE/'plan.json'), script_sha256=digest(__file__),
           functional_acceptance=False, original_sources_modified=False,
           rule='Only parameter ap_ST_fsm_stateN = W\'d(2**(N-1)); becomes the same W\'h value.'))
    print(json.dumps(dict(output=str(out), sources=len(sources), constants=sum(row['constants'] for row in records))))


if __name__ == '__main__':
    main()
