#!/usr/bin/env python3
"""Screen a trusted-occupancy scan bound against existing full CPU artifacts.

This does not modify HLS, execute RTL, or establish functional acceptance.
"""
import array
import collections
import hashlib
import json
from pathlib import Path
import struct
import sys

from read_batch_trace_v4 import decode_file

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_rtl_tb_cpu_v2')
AUDIT = ROOT/'results/collision_safe_bus64_CSR_csim_20261030_v1.json'
OUT = ROOT/'results/native_trace_live_scan_reconstruction_20261102_v1.json'
SLOTS = 2097152


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        while block := f.read(8*1024*1024): h.update(block)
    return h.hexdigest()


def locate(slots, key):
    v = key ^ (key >> 33)
    v = (v*0xff51afd7ed558ccd) & ((1 << 64)-1)
    v ^= v >> 33
    first_free = None
    for i in range(SLOTS):
        at = (v+i) & (SLOTS-1)
        flag, current = slots.get(at, (0, 0))
        if flag == 1 and current == key: return at, True
        if flag != 1 and first_free is None: first_free = at
        if flag == 0: return first_free, False
    return (SLOTS if first_free is None else first_free), False


def snapshot_slots(path):
    with path.open('rb') as f:
        assert struct.unpack('<4Q', f.read(32))[0] == 0x4142534e41503031
        f.seek(24); n = struct.unpack('<Q', f.read(8))[0]; assert n == 44
        offsets = {}
        for _ in range(n):
            port, width, depth = struct.unpack('<3Q', f.read(24))
            assert port not in offsets and width in (4,8)
            offsets[port] = (f.tell(), width, depth); f.seek(width*depth, 1)
        assert f.tell() == path.stat().st_size
        offset, width, depth = offsets[22]; assert (width, depth) == (8,4)
        f.seek(offset); meta = struct.unpack('<4Q', f.read(32))
        offset, width, depth = offsets[26]; assert (width, depth) == (4,SLOTS)
        assert sys.byteorder == 'little'; f.seek(offset)
        flags = array.array('I'); flags.fromfile(f, depth)
        key_offset, width, depth = offsets[25]; assert (width, depth) == (8,SLOTS)
        actual = {}
        for at, flag in enumerate(flags):
            if flag:
                f.seek(key_offset+8*at); actual[at] = (flag, struct.unpack('<Q',f.read(8))[0])
        return meta, actual, dict(collections.Counter(flags))


def main():
    assert not OUT.exists(), 'Refuse report overwrite'
    audit = json.loads(AUDIT.read_text()); assert audit['graph_mode'] == 0
    source = ROOT/'hardware/vitis/test_compressed_batch_rtl_full_depth.cpp'
    text = source.read_text()
    assert 'Node::update(77,nullptr,0,&occupied_node,1' in text and 'uint32_t occupied_node=1;' in text
    paths = [Path(__file__).resolve(), AUDIT, source, ROOT/'hardware/vitis/search_node_occupancy.hpp',
             ROOT/'hardware/vitis/search_trace_records.hpp', ROOT/'scripts/read_batch_trace_v4.py']
    cases = []
    for case in range(3):
        trace = BASE/f'trace_mode_0_case_{case}.bin'; snap = BASE/f'cpu_0_{case}.bin'
        for p in (trace,snap): assert digest(p) == audit['files'][str(p)], 'Changed CPU evidence'
        paths.extend((trace,snap))
        decoded = decode_file(trace,4); slots = {}; routes = {}; records = []
        if case == 1:
            key = (77 << 32) | 1; at, found = locate(slots,key)
            assert not found; slots[at] = (1,key); routes[77] = [1]
        assert decoded['batch_control'][6] == (0 if case == 1 else 1)
        for net in decoded['nets']:
            ident = net['net']
            for node in routes.get(ident,[]):
                at,found = locate(slots,(ident << 32)|node); assert found
                slots[at] = (2,slots[at][1])
            for node in net['roots']:
                key = (ident << 32)|node; at,found = locate(slots,key)
                assert not found and at < SLOTS; slots[at] = (1,key)
            routes[ident] = list(net['roots'])
            active = sorted((at,key) for at,(flag,key) in slots.items() if flag == 1)
            assert len(active) == net['node_meta'][2]
            assert [key for at,key in active if key >> 32 == ident] == net['owned_keys']
            stop = active[-1][0]+1 if active else 0
            records.append({'iteration':net['iteration'],'net':ident,'live_pairs':len(active),
                            'highest_live_slot':active[-1][0] if active else None,
                            'original_iterations_per_scan':SLOTS,'candidate_iterations_per_scan':stop,
                            'candidate_saved_fraction':1-stop/SLOTS})
        meta, actual, counts = snapshot_slots(snap)
        assert meta[2] == sum(flag == 1 for flag,_ in slots.values())
        assert slots == actual, 'Reconstructed flags/keys differ from complete final snapshot'
        cases.append({'case':case,'reset':bool(decoded['batch_control'][6]),
                      'trace_status':decoded['status'],'final_meta':meta,
                      'final_flag_histogram':counts,'net_records':records})
    report = {'status':'trusted_early_stop_reconstructed_3_CPU_cases_no_HLS_or_RTL_acceptance',
              'files':{str(p):digest(p) for p in paths},'slots':SLOTS,'cases':cases,
              'constraints':['Valid only if metadata live count exactly equals the number of flags equal to one.',
                             'Seeded case uses the explicit 77/1 setup from the frozen reference testbench.',
                             'Iteration savings are not measured cycle, synthesis, or board performance.',
                             'No candidate has been implemented; inconsistent/untrusted states are not covered.',
                             'Full original scope, all outputs, error cases and acceptance gates remain required.']}
    with OUT.open('x') as f: json.dump(report,f,indent=2); f.write('\n')
    print(json.dumps({'status':report['status'],'cases':cases,'report_sha256':digest(OUT)},indent=2))


if __name__ == '__main__':
    main()
