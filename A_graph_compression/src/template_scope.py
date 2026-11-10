"""Change dictionary sharing extent without relearning or changing any graph resource.

None retains global sharing byte-for-byte. Positive spans partition source-anchor
tiles by (SLR, floor(COLUMN/span), floor(ROW/span)); only template RULE storage,
TPL_OFF, and INSTANCE.template are changed. Exceptions and all identities remain.
"""
from pathlib import Path
import struct
from packed_graph import DIRECTORY, HEADER, FORMATS, PackedGraph


def repack(image, replacements):
    """Serialize unchanged sections plus explicit replacements with original ordering."""
    sections = {}
    for name, (offset, size, count, width) in image.layout.items():
        sections[name] = replacements.get(name, (image.data[offset:offset+size], count, width))
    cursor = (HEADER.size+DIRECTORY.size*len(sections)+63)//64*64
    rows = []
    for name, (payload, count, width) in sections.items():
        if len(payload) != count*width:
            raise ValueError('Replacement shape mismatch')
        rows.append((name, cursor, payload, count, width))
        cursor = (cursor+len(payload)+63)//64*64
    data = bytearray(cursor)
    data[:HEADER.size] = image.data[:HEADER.size]
    for index, (name, offset, payload, count, width) in enumerate(rows):
        DIRECTORY.pack_into(data, HEADER.size+index*DIRECTORY.size,
                            name.encode(), offset, len(payload), count, width)
        data[offset:offset+len(payload)] = payload
    return data


def write_scoped(source, output, span=None):
    if span is not None and (type(span) is not int or span <= 0):
        raise ValueError('Span must be a positive integer or None for global')
    image = source if isinstance(source, PackedGraph) else PackedGraph(source)
    if image.mode != 1:
        raise ValueError('Template dictionary scope requires compact input')
    if span is None:
        data = image.data
        templates = len(image.offsets)-1
        rule_count = len(image.rules)
    else:
        keys = []
        for root, instance in zip(image.roots, image.instances):
            tid = instance[0]
            if tid < 0:
                keys.append(None)
            else:
                tile = image.tiles[image.nodes[root[0]][2]]
                keys.append((tile[4], tile[2]//span, tile[3]//span, tid))
        unique = sorted({key for key in keys if key is not None})
        identifiers = {key: i for i, key in enumerate(unique)}
        offsets, rules = [0], bytearray()
        base = image.layout['RULE'][0]
        width = image.layout['RULE'][3]
        for key in unique:
            tid = key[-1]
            lo, hi = image.offsets[tid][0], image.offsets[tid+1][0]
            rules.extend(image.data[base+lo*width:base+hi*width])
            offsets.append(offsets[-1]+hi-lo)
        fmt = struct.Struct('<'+FORMATS['INSTANCE'])
        instances = b''.join(fmt.pack(-1 if key is None else identifiers[key], *old[1:])
                             for key, old in zip(keys, image.instances))
        replacements = {
            'TPL_OFF': (b''.join(struct.pack('<Q', v) for v in offsets), len(offsets), 8),
            'RULE': (bytes(rules), offsets[-1], width),
            'INSTANCE': (instances, len(image.instances), fmt.size)}
        data = repack(image, replacements)
        templates, rule_count = len(unique), offsets[-1]
    with Path(output).open('xb') as stream:
        stream.write(data)
    return {'span_tiles': span, 'file_bytes': len(data), 'templates': templates,
            'rule_records': rule_count, 'sources': len(image.roots), 'nodes': len(image.nodes),
            'fallback_sources': sum(r[0] < 0 for r in image.instances),
            'scope': 'Template dictionary sharing extent only; fixed original rules and per-instance exceptions.'}
