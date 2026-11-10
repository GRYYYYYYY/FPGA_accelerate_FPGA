"""Replay every real owner mutation with an independent per-node/net ledger."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'adapters'), str(ROOT/'scripts')]
from build_owner_profile_router import generate
from profile_real import parse_log

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def read(path):
    return json.loads(path.read_text())

def main():
    out = ROOT/'results/owner_profile_real_v4_20261024'
    base = ROOT/'results/search_access_real_20261024'
    m, bm = read(out/'manifest.json'), read(base/'manifest.json')
    assert m['status'] == bm['status'] == 'passed'
    assert m['baseline_manifest_sha256'] == sha(base/'manifest.json')
    bg = read(base/'source_bound_audit.json')
    assert bg['status'] == 'passed' and bg['manifest_sha256'] == sha(base/'manifest.json')
    assert m['baseline_audit_sha256'] == sha(base/'source_bound_audit.json')
    assert m['runner_sha256'] == sha(out/'verify_owner_profile_real.py') == sha(ROOT/'scripts/verify_owner_profile_real.py')
    assert m['generator_sha256'] == sha(out/'build_owner_profile_router.py') == sha(ROOT/'adapters/build_owner_profile_router.py')
    for name, digest in m['sources'].items():
        assert sha(out/name) == digest, name
    source, header = generate((base/'sources/trace.cpp').read_text(), (base/'sources/real_trace.hpp').read_text())
    assert source == (out/'sources/trace.cpp').read_text()
    assert header == (out/'sources/real_trace.hpp').read_text()
    assert sha(out/'sources/owner_profile.hpp') == sha(ROOT/'adapters/owner_profile.hpp')
    for name, digest in bm['sources'].items():
        if name not in ['sources/trace.cpp', 'sources/real_trace.hpp']:
            assert sha(out/name) == digest
    assert [c['stage'] for c in m['commands']] == ['build', 'route']
    assert all(c['exit_code'] == 0 for c in m['commands'])
    assert sha(out/'router_owner_profile') == m['binary_sha256']
    metrics = parse_log((out/'trace.log').read_text())
    assert metrics == m['metrics'] and metrics['convergence'] == bm['metrics']['convergence']
    assert metrics['pushes'] == 130334832 and m['attempts'] == 570286
    for name, key in [('trace.result','result_sha256'), ('trace.accesses','accesses_sha256'), ('trace.jsonl','metadata_sha256')]:
        assert sha(out/name) == m[key] == bm[key]
    assert sha(out/'owner.events') == m['owner_events_sha256']
    assert sha(out/'owner.json') == m['owner_profile_sha256']
    expected = read(out/'owner.json')
    assert expected == m['owner_profile'] and expected['initial_nodes'] == 9089009
    ledger, primary = {}, {}
    markers = 0
    counts = Counter(initial_nodes=expected['initial_nodes'])
    def peak(key, value):
        counts[key] = max(counts[key], value)
    with (out/'owner.events').open('rb') as f:
        while chunk := f.read(32*65536):
            assert len(chunk) % 32 == 0
            for op, node, net, count, occ, owner, owner_refs, overflow_size in struct.iter_unpack('<8I', chunk):
                if op == 0:
                    assert markers == 0 and node == expected['initial_nodes']
                    assert net == count == occ == owner == owner_refs == overflow_size == 0
                    markers += 1
                    counts['load_events'] = counts['events']
                    counts['load_owned_nodes'] = len(ledger)
                    continue
                assert op in (1, 2) and node < expected['initial_nodes'] and net < 2**31
                users = ledger.setdefault(node, {})
                before = users.get(net, 0)
                old_size = max(0, len(users)-1)
                old_owner = primary.get(node, 0xffffffff)
                if op == 1:
                    assert before < 65535
                    users[net] = before+1
                    counts['increments'] += 1
                    counts['same_net_increments' if before else 'new_net_increments'] += 1
                else:
                    assert before > 0
                    counts['decrements'] += 1
                    if before == 1:
                        del users[net]
                        counts['net_removals'] += 1
                        if old_owner == net and old_size:
                            counts['promotions'] += 1
                    else:
                        users[net] = before-1
                assert users.get(net, 0) == count
                assert len(users) == occ <= 65535
                assert overflow_size == max(0, len(users)-1)
                if users:
                    assert owner in users and users[owner] == owner_refs
                    # Existing primary is preserved until its final reference is removed.
                    if old_owner in users:
                        assert owner == old_owner
                    primary[node] = owner
                else:
                    assert owner == 0xffffffff and owner_refs == 0
                    del ledger[node]
                    primary.pop(node, None)
                counts['events'] += 1
                counts['live_overflow_entries'] += overflow_size-old_size
                counts['live_overflow_nodes'] += int(overflow_size>0)-int(old_size>0)
                peak('max_overflow_entries', counts['live_overflow_entries'])
                peak('max_overflow_nodes', counts['live_overflow_nodes'])
                peak('max_overflow_per_node', overflow_size)
                peak('max_occupancy', occ)
                peak('max_same_net_refs', count)
                peak('max_primary_refs', owner_refs)
                for other, refs in users.items():
                    if other != owner:
                        peak('max_overflow_refs', refs)
    counts['final_owned_nodes'] = len(ledger)
    assert dict(counts) == expected, (dict(counts), expected)
    assert markers == 1
    assert (out/'owner.events').stat().st_size == (counts['events']+1)*32
    result = {
        'status': 'passed', 'manifest_sha256': sha(out/'manifest.json'),
        'auditor_sha256': sha(Path(__file__)), 'counts': dict(counts),
        'all_mutations_replayed': True, 'whole_route_equal': True,
        'all_metadata_equal': True, 'sampled_label_accesses_equal': True,
        'scope': 'Complete serial CPU workload observation and independent per-net ledger replay; observed peaks do not bound other designs. No owner hardware or acceleration claim.'}
    (out/'auditor.py').write_bytes(Path(__file__).read_bytes())
    (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    main()
