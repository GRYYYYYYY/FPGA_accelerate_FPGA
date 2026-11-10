"""Compare every semantic value byte against an SHA-bound, previously accepted native JSON.

This is a reader for the frozen native serializer, not a general JSON equivalence
library. Semantic values must have identical serialization. Only the six original
batch-root measurement fields may differ. Large values stay in read-only mmap;
comparison allocates at most two 1 MiB chunks, never whole decoded route trees.
The accepted reference SHA is mandatory: its nested JSON validity is inherited
from the original full semantic audit. New framing and measurement values are
validated here, including duplicate keys, complete consumption and finite numbers.
Virtual mappings scale with file size; this is not a constant-address-space claim.
"""
import hashlib
import json
import math
import mmap
from pathlib import Path
import re

METRICS = {'preparation_ms', 'route_ms', 'peak_kib', 'logical_bytes', 'cache_hits', 'cache_misses'}
STRUCTURAL = re.compile(rb'["{}\[\]]')
STRING = re.compile(rb'"(?:[^"\\\x00-\x1f]|\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4}))*"')
SCALAR = re.compile(rb'(?:true|false|null|-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)')
WS = b' \t\r\n'
CHUNK = 1024 * 1024


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(CHUNK), b''):
            h.update(chunk)
    return h.hexdigest()


def space(data, position, end):
    while position < end and data[position] in WS:
        position += 1
    return position


def value_end(data, start, end):
    """Locate a value without constructing it; nested bytes are checked against golden."""
    if start >= end:
        raise ValueError('Missing JSON value')
    first = data[start]
    if first == 34:
        match = STRING.match(data, start, end)
        if match is None:
            raise ValueError('Invalid JSON string')
        return match.end()
    if first not in (91, 123):
        match = SCALAR.match(data, start, end)
        if match is None:
            raise ValueError('Invalid JSON scalar')
        return match.end()
    stack = [93 if first == 91 else 125]
    position = start + 1
    while stack:
        match = STRUCTURAL.search(data, position, end)
        if match is None:
            raise ValueError('Truncated compound value')
        token = data[match.start()]
        position = match.end()
        if token == 34:
            string = STRING.match(data, match.start(), end)
            if string is None:
                raise ValueError('Invalid nested JSON string')
            position = string.end()
        elif token in (91, 123):
            stack.append(93 if token == 91 else 125)
        elif stack.pop() != token:
            raise ValueError('Mismatched JSON delimiters')
    return position


def object_fields(data, start=0, end=None):
    end = len(data) if end is None else end
    position = space(data, start, end)
    if position >= end or data[position] != 123:
        raise ValueError('Expected object')
    position = space(data, position + 1, end)
    fields = {}
    if position < end and data[position] == 125:
        position += 1
    else:
        while True:
            match = STRING.match(data, position, end)
            if match is None:
                raise ValueError('Expected object key')
            key = json.loads(data[position:match.end()])
            if key in fields:
                raise ValueError('Duplicate object key: ' + key)
            position = space(data, match.end(), end)
            if position >= end or data[position] != 58:
                raise ValueError('Expected colon')
            begin = space(data, position + 1, end)
            stop = value_end(data, begin, end)
            fields[key] = (begin, stop)
            position = space(data, stop, end)
            if position < end and data[position] == 125:
                position += 1
                break
            if position >= end or data[position] != 44:
                raise ValueError('Expected object separator')
            position = space(data, position + 1, end)
    if space(data, position, end) != end:
        raise ValueError('Trailing object data')
    return fields


def array_values(data, span):
    start, end = span
    position = space(data, start, end)
    if position >= end or data[position] != 91:
        raise ValueError('Expected array')
    position = space(data, position + 1, end)
    if position < end and data[position] == 93:
        position += 1
    else:
        while True:
            stop = value_end(data, position, end)
            yield position, stop
            position = space(data, stop, end)
            if position < end and data[position] == 93:
                position += 1
                break
            if position >= end or data[position] != 44:
                raise ValueError('Expected array separator')
            position = space(data, position + 1, end)
    if space(data, position, end) != end:
        raise ValueError('Trailing array data')


def small_value(data, span):
    start, end = span
    if end - start > 4096:
        raise ValueError('Unexpectedly large measurement/metadata')
    return json.loads(data[start:end])


def equal_bytes(left, ls, right, rs):
    if ls[1] - ls[0] != rs[1] - rs[0]:
        return False
    for offset in range(0, ls[1] - ls[0], CHUNK):
        size = min(CHUNK, ls[1] - ls[0] - offset)
        if left[ls[0]+offset:ls[0]+offset+size] != right[rs[0]+offset:rs[0]+offset+size]:
            return False
    return True


def finite_measurement(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def audit_native_output(path, reference, expected_reference_sha256, execution, expected_routes=1062):
    if sha256(reference) != expected_reference_sha256:
        raise ValueError('Accepted reference SHA changed')
    with Path(path).open('rb') as raw_file, Path(reference).open('rb') as reference_file:
        with mmap.mmap(raw_file.fileno(), 0, access=mmap.ACCESS_READ) as raw, \
                mmap.mmap(reference_file.fileno(), 0, access=mmap.ACCESS_READ) as golden:
            wanted = object_fields(golden)
            if 'routes' not in wanted:
                raise ValueError('Incomplete accepted reference schema')
            route_count = sum(1 for _ in array_values(golden, wanted['routes']))
            if route_count != expected_routes:
                raise ValueError('Incomplete accepted reference route count')
            outer = object_fields(raw)
            if set(outer) != {'execution', 'materialization_ms', 'batches', 'export_ms'}:
                raise ValueError('Unexpected native wrapper scope')
            actual_execution = small_value(raw, outer['execution'])
            if actual_execution != execution:
                raise ValueError('Executed representation differs')
            result = dict(execution=actual_execution,
                          materialization_ms=small_value(raw, outer['materialization_ms']),
                          export_ms=small_value(raw, outer['export_ms']), batches=[])
            if (not finite_measurement(result['materialization_ms']) or
                    type(result['export_ms']) is not list or len(result['export_ms']) != 2 or
                    not all(finite_measurement(v) for v in result['export_ms'])):
                raise ValueError('Invalid native measurements')
            semantic_bytes = 0
            for span in array_values(raw, outer['batches']):
                if len(result['batches']) >= 2:
                    raise ValueError('Too many native batches')
                fields = object_fields(raw, *span)
                if set(fields)-METRICS != set(wanted)-METRICS or not METRICS <= fields.keys():
                    raise ValueError('Complete batch field set differs')
                metrics = {key: small_value(raw, fields[key]) for key in METRICS}
                if not all(finite_measurement(v) for v in metrics.values()):
                    raise ValueError('Invalid batch metric')
                for key, reference_span in wanted.items():
                    if key in METRICS:
                        continue
                    else:
                        if not equal_bytes(raw, fields[key], golden, reference_span):
                            raise ValueError('Complete semantic value differs: ' + key)
                        semantic_bytes += reference_span[1] - reference_span[0]
                result['batches'].append(metrics)
            if len(result['batches']) != 2:
                raise ValueError('Incomplete native batches')
            result['semantic_audit'] = dict(method='all_non_metric_value_bytes_equal_to_sha_bound_accepted_reference',
                batches=2, routes_per_batch=route_count, semantic_fields=sorted(set(wanted)-METRICS),
                compared_semantic_value_bytes=semantic_bytes, reference_sha256=expected_reference_sha256,
                raw_bytes=len(raw), reference_bytes=len(golden), comparison_chunk_bytes=CHUNK)
            return result
