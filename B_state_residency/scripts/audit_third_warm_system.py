"""Independently audit G3 warm owner repair, original receipts and q3 retry."""
from pathlib import Path
from collections import Counter
import json
import runpy
import struct
import sys
import zlib
from run_checkpoint_authority import ROOT, sha
from audit_route_fault_axi import replay
from audit_third_warm_records import audit_native_records

p = Path(sys.argv[1]).resolve()
legacy_observer_check = '--legacy-observer-check' in sys.argv
m = json.loads((p / 'manifest.json').read_text())
assert m['status'] == 'observed' and len(m['cases']) == 1
case = next(iter(m['cases']))
c = m['cases'][case]
d = p / case
assert c['status'] == 'observed' and len(c['commands']) == 3
assert all(v['exit_code'] == 0 for v in c['commands'])
ref = p.parent / ('path_capacity_third_' + case + '_v1')
rm = json.loads((ref / 'manifest.json').read_text())
ra = json.loads((ref / 'source_bound_audit.json').read_text())
report = json.loads((ROOT / 'results/path_capacity_third_20261027.json').read_text())
assert ra == report['cases'][ref.name]
assert sha(ref / 'source_bound_audit.json') == report['restores'][ref.name]['audit_sha256']
assert sha(ref / 'manifest.json') == ra['manifest_sha256']
for name, entry in m['sources'].items():
    assert sha(p / 'sources' / name) == entry['sha256'], name
    if name not in ['runner.py', 'tb_query_fault.sv', 'g3_warm_build_tb.py']:
        assert entry['sha256'] == rm['sources'][name]['sha256'], name
assert m['rtl'] == rm['rtl'] and m['binding_sha256'] == rm['binding_sha256']
assert runpy.run_path(str(p / 'sources/g3_warm_build_tb.py'))['make']() == (p / 'sources/tb_query_fault.sv').read_text()
for key in ['scoreboards', 'next_scoreboards', 'third_scoreboards']:
    for name, digest in m[key].items():
        assert sha(p / name) == digest == rm[key][name]
for name, digest in m['third_inputs'].items():
    assert sha(Path(name) / 'source_bound_audit.json') == digest

rows = [s.split() for s in (d / 'natural_trace.txt').read_text().splitlines()]
oldrows = [s.split() for s in (ref / case / 'natural_trace.txt').read_text().splitlines()]
def by(tag, part=None):
    return [t for t in (rows if part is None else part) if t[0] == tag]
def index(tag):
    return next(i for i, t in enumerate(rows) if t[0] == tag)
cut = index('THIRD_BEGIN')
oldcut = next(i for i, t in enumerate(oldrows) if t[0] == 'THIRD_BEGIN')
assert rows[:cut] == oldrows[:oldcut], 'Pre-q3 native protocol/cycles changed'
q3 = rows[cut:]
start = index('THIRD_WARM_START')
owner_done = index('THIRD_WARM_OWNER')
release = index('THIRD_WARM_RELEASE')
retry = index('THIRD_RETRY_BEGIN')
warm = rows[start:release + 1]
fault_search = rows[index('THIRD_FAULT_BEGIN'):index('THIRD_FAULT_DONE') + 1]
retry_search = rows[retry:]
assert cut < start < owner_done < release < retry
assert len(by('THIRD_BEGIN')) == 2 and len(by('THIRD_PREPARED')) == 2
assert all(t[2:] == ['3', '0', '180328'] for t in by('THIRD_BEGIN'))
assert all(t[2:] == ['3', '3', '180328'] for t in by('THIRD_PREPARED'))
assert by('FAILED_QUERY', q3)[0][2:] == ['5', '7', '5', '0', '1', '3']
assert len(by('FI', q3)) == 1
assert [t[2:4] for t in by('SHARED_B', q3)] == [['990179', '0'], ['558358', '2']]
assert len(by('RESET', q3)) == 1 and by('RESET', q3)[0][2:] == ['3']
assert not by('AS_REARM', q3), 'Healthy G3 authority must survive the work-engine fault'
assert not by('JP', q3)
route_ops = [[int(v) for v in t[2:]] for t in by('RO', q3)]
source_tb = (p/'sources/tb_query_fault.sv').read_text()
if legacy_observer_check:
    assert 'wire actual_route_slot=system.inner.backend.f_broute_payload[1];' in source_tb
    observed_slot = 0  # Explicitly only bit0 in the development TB.
else:
    assert 'wire[1:0]actual_route_slot=system.inner.backend.f_broute_payload[2:1];' in source_tb
    observed_slot = 2
expected_routes = [[observed_slot, 2, n] for n in [990179, 558358, 265324]]
expected_routes += [[observed_slot, 1, n] for n in [990179, 558358]]
expected_routes += [[observed_slot, op, n] for op in [2, 1] for n in [990179, 558358, 265324]]
assert route_ops == expected_routes
journal = by('J', q3)
assert [[int(t[2]), int(t[3]), int(t[4])] for t in journal] == [[t[2], 26422, t[1]] for t in expected_routes]
forwarded = by('BF', q3)
assert [[int(t[2]), int(t[3])] for t in forwarded] == [[t[1], t[2]] for t in expected_routes]
assert all(int(j[1]) < int(b[1]) for j, b in zip(journal, forwarded))

# Both failed and retried searches must independently match the same CPU numbers.
cpu = p.parent / 'followup_iter2_third_plain_v1'
cost = p.parent / 'followup_iter2_third_cost_v1'
cpurows = [s.split() for s in (cpu / 'events.txt').read_text().splitlines()]
polls = [list(map(int, t[1:4])) for t in cpurows if t[0] == 'P']
candidates = [[int(t[1]), int(t[2]), int(t[3]), int(i + 1 < len(cpurows) and cpurows[i+1][0] == 'W')]
              for i, t in enumerate(cpurows) if t[0] == 'C']
costs = [(int(t[1]), sum(int(v, 16) << (32*i) for i, v in enumerate(t[2:25])),
          sum(int(v, 16) << (32*i) for i, v in enumerate(t[25:])))
         for t in map(str.split, (cost / 'cost_vectors.txt').read_text().splitlines())]
assert len(polls) == 114 and len(candidates) == 565 and len(costs) == 302
for part in [fault_search, retry_search]:
    assert [[int(t[2]), int(t[3], 16), int(t[4])] for t in by('P', part)] == polls
    assert [[int(t[3]), int(t[4]), int(t[6]), int(t[5])] for t in by('O', part)] == candidates
    assert [(int(t[2]), int(t[3], 16), int(t[4], 16)) for t in by('C', part)] == costs
    assert [int(t[2]) for t in by('Q', part)] == list(range(100, 213))
assert len(by('LIFECYCLE', q3)) == 1 and by('LIFECYCLE', q3)[0][2:] == ['2', '0', '1', '4', '1', '3', '3']

# Distinct authority rounds and actual working-engine corrections, not TB callbacks.
nodes = [990179, 558358, 265324]
authority = by('KA', warm)
assert [[int(t[2]), int(t[3]), int(t[4])] for t in authority] == [[19, n, 26422] for n in nodes] * 2
assert len({int(t[5]) for t in authority}) == 6
assert [t[2:] for t in by('AS_REPLY', warm)] == [[str(0), str(r), str(o), '0000000100000003'] for r, o in [(2, 2), (4, 2), (5, 1)] * 2]
ops = [(int(t[2]), int(t[3])) for t in by('KO', warm)]
assert ops == [(0, 990179), (0, 558358), (0, 265324), (1, 265324), (0, 990179), (0, 558358), (0, 265324)]
assert [list(map(int, t[2:])) for t in by('KR', warm)] == [[0, r, o] for r, o in [(2, 2), (4, 2), (4, 1), (5, 1), (2, 2), (4, 2), (5, 1)]]
assert by('THIRD_WARM_OWNER')[0][2:] == ['1', '3']

# Raw G3 export is the recovery source; source bytes/CRCs are not rebased by the TB.
path = [int(t[3], 16) for t in by('G3_PATH_WORD')]
query = [int(t[3], 16) for t in by('G3_QUERY_WORD')]
assert len(path) == 117 and path[0] == path[39] == 1 and path[78:] == [0] * 39
assert query == [0x51435031, 1, 0x9abcdef0, 0x12345678, 3, 1, 5, 0x57, 180328, 0]
crc = lambda words: zlib.crc32(struct.pack('<' + 'I'*len(words), *words))
assert [(int(t[2]), int(t[3], 16)) for t in by('THIRD_WARM_PATH')] == list(enumerate(path))
assert [(int(t[2]), int(t[3], 16)) for t in by('THIRD_WARM_QUERY')] == list(enumerate(query))
source_labels = [(int(t[2]), int(t[3], 16)) for t in by('G3_LABEL_RECORD')]
assert len(source_labels) == 781 and len(set(n for n, v in source_labels)) == 781
assert [(int(t[2]), int(t[3], 16)) for t in by('RELOAD', warm)] == source_labels
label_bytes = b''.join(struct.pack('<I', n) + v.to_bytes(20, 'little') for n, v in source_labels)
label_crc = zlib.crc32(label_bytes)
assert by('THIRD_WARM_LABELS')[0][2:] == ['781', '781', f'{label_crc:08x}']
assert by('THIRD_WARM_START')[0][2:] == ['3', '19', f'{label_crc:08x}', f'{crc(path):08x}', f'{crc(query):08x}']
assert [t[2:] for t in by('WL', warm)] == [['0', '781', '781']]
assert [t[2:] for t in by('WPR', warm)] == [['0', f'{crc(path):08x}']]
assert [t[2:] for t in by('WQR', warm)] == [['0', f'{crc(query):08x}']]
assert [(int(t[2]), int(t[3], 16)) for t in by('CHECK', warm)] == source_labels
expected_fields = [[1, n, fi, (v >> (32*fi)) & 0xffffffff] for n, v in source_labels for fi in range(5)]
actual_fields = [[int(t[2]), int(t[3]), int(t[4]), int(t[5], 16)] for t in by('LL', warm) if t[2] == '1']
assert actual_fields == expected_fields
held = by('THIRD_WARM_HELD')
assert len(held) == 8 and all(t[2:] == ['0', '1', '0', '7', '1', '0'] for t in held)
assert int(by('WL', warm)[0][1]) < int(by('WPR', warm)[0][1]) < int(by('WQR', warm)[0][1]) < int(held[0][1]) < int(by('THIRD_WARM_RELEASE')[0][1])
assert by('THIRD_WARM_RELEASE')[0][2:] == ['6', '0', '6', '3', '180328']
final_query = [int(t[3], 16) for t in by('QCM', retry_search)]
assert final_query == query[:6] + [6, 0x58, 180329, 0]
assert by('THIRD_PASS')[0][2:] == ['114', '113', '565', '302', '7', '180329']
final_path = path[:78] + [1, 3, 26422, 66893, 151354, 0x9abcdef0, 0x12345678, *nodes] + [0]*29
assert [int(t[4], 16) for t in by('THIRD_PATH_WORD', retry_search) if t[2] == '1'] == final_path

# All old physical prefixes remain the audited G3 baseline; only live work extends.
g3 = p.parent / ('owner_g3_retired_' + case + '_v3') / case
prefix = {}
for tag in ['graph', 'design', 'table', 'label', 'owner', 'cost', 'qstate', 'snapshot', 'copy', 'labelsnap', 'baseline', 'g3copy']:
    old = (g3 / (tag + '_axi.txt')).read_bytes()
    new = (d / (tag + '_axi.txt')).read_bytes()
    assert new.startswith(old), tag
    if tag in ['copy', 'labelsnap', 'g3copy']:
        assert new == old, tag
    prefix[tag] = len(old.splitlines())
for name in ['owners.bin', 'g3.bin', 'pool.bin', 'snapshot.bin', 'cost.bin', 'design.bin']:
    assert sha(d / name) == sha(ref / case / name), name
binding = json.loads(Path(m['binding']).read_text())
reg = binding['regions']
initial = b''.join(Path(reg[k]['path']).read_bytes() for k in ['owners', 'owner_pool', 'owner_allocator'])
graph = ROOT / 'results/graph_image_20261024'
regions = [
    ('graph', [(0x1fffff000, graph/'offsets.u32le'), (0x10fffff000, graph/'edges.u32le'), (0x20fffff000, graph/'nodes.rrt32')], None),
    ('design', [(0x31fffff000, Path(reg['design']['path']))], d/'design.bin'),
    ('cost', [(0x71fffff000, Path(reg['cost_history_prices_nets']['path']))], d/'cost.bin'),
    ('owner', [(0x61fffff000, initial)], d/'owners.bin'),
    ('label', [(0, bytes(3145728))], d/'labels.bin'),
    ('qstate', [(0x81fffff000, Path(reg['connections']['path']))], None),
    ('table', [(0x41fffff000, Path(reg['rows']['path'])), (0x51fffff000, Path(reg['columns']['path']))], None),
    ('snapshot', [(0x91fffff000, initial), (0xa000000000, d/'pool.bin'), (0xc000000000, d/'g3.bin')], None),
    ('baseline', [(0xb000000000, Path(m['baseline_image'])/'baseline.bin')], None)]
memory = {tag: replay(d/(tag+'_axi.txt'), rr, final) for tag, rr, final in regions}
assert all(v['error_read_beats'] == 0 and v['error_write_replies'] == (2 if tag == 'owner' else 0) for tag, v in memory.items())
writes = []
for t in map(str.split, (d/'owner_axi.txt').read_text().splitlines()[prefix['owner']:]):
    if t[0] != 'W':
        continue
    mask = int(t[2], 16)
    lane = (mask & -mask).bit_length() - 1
    assert lane in [0, 16, 32, 48] and mask == 0xffff << lane
    node = (int(t[1], 16) - 0x61fffff000 + lane) // 16
    value = ((int(t[3], 16) >> (8*lane)) & ((1 << 128) - 1)).to_bytes(16, 'little')
    writes.append((node, struct.unpack('<4I', value)))
assert [n for n, v in writes] == nodes + nodes[:2] + [265324] + nodes * 2
counts = [1, 3, 4, 2, 4, 5, 1, 3, 4, 2, 4, 5]
for (node, words), count in zip(writes, counts):
    with (d/'g3.bin').open('rb') as f:
        f.seek(node*16)
        expected = list(struct.unpack('<4I', f.read(16)))
    expected[1] = (expected[1] & 0xffff0000) | count
    assert list(words) == expected
assert memory['owner']['write_beats'] == 25

# Audit every final page and every native label record transaction, including restore.
misses = {int(t[2]) for t in by('BM')}
pages = {}
with (cpu/'search_final_nodes.u32').open('rb') as f:
    for node in misses:
        f.seek(node*44)
        words = struct.unpack('<11I', f.read(44))
        values = [words[k] for k in [0, 1, 3, 4, 5]]
        if node == 151354:
            values[4] = 0
        page_id, slot = divmod(node, 8)
        page = pages.setdefault(page_id, bytearray(192))
        page[0] |= 1 << slot
        struct.pack_into('<5I', page, 1 + slot*20, *values)
expected = Counter(bytes(v) for v in pages.values())
expected[bytes(192)] += 16384 - len(pages)
data = (d/'labels.bin').read_bytes()
assert len(data) == 3145728 and Counter(data[i:i+192] for i in range(0, len(data), 192)) == expected
native = audit_native_records(rows, d)
log = (d/'simulate.log').read_text()
assert 'THIRD_WARM_PASS polls=114 expands=113 candidates=565 costs=302' in log and '$finish called' in log and 'Fatal:' not in log
result = dict(status='passed', manifest_sha256=sha(p/'manifest.json'), auditor_sha256=sha(Path(__file__)),
              native_auditor_sha256=sha(ROOT/'scripts/audit_third_warm_records.py'), case=case,
              production_sources_match=ref.name, query_sequence=180329, checkpoint=19, source_context=[5,3,5], target_context=[6,0,6],
              polls_per_attempt=114, expansions_per_attempt=113, candidates_per_attempt=565, costs_per_attempt=302,
              journal_keys=nodes, authority_rounds=2, correction_increments=1, corrected_node=265324,
              restored_labels=781, final_labels=len(misses), logical_pages=len(pages), path_words=117,
              source_label_crc=f'{label_crc:08x}', source_path_crc=f'{crc(path):08x}', source_query_crc=f'{crc(query):08x}',
              final_path_crc=f'{crc(final_path):08x}', final_query_crc=f'{crc(final_query):08x}',
              final_sequence=180329, final_slot_mask=7, final_journal=3, physical_memory=memory, native_labels=native,
              owner_sha256=sha(d/'owners.bin'), final_cycle=int(by('THIRD_PASS')[0][1]),
              scope='Actual q3 second commit owner-B error, G3 two-round authority/working-engine INC repair, native781 label validation and original117/10-word receipts, non-cold attempt6 retry with actual historical-path registration/ripup. Fixed price content, initial clones/full baseline externally trusted. No G4 publication, persistent authentication/floor or board/timing proof.')
cycles = {name: int(by(tag, q3)[0][1]) for name, tag in [
    ('fault', 'FI'), ('restore_start', 'THIRD_WARM_START'), ('target_reset', 'RESET'),
    ('owner_verified', 'THIRD_WARM_OWNER'), ('labels_verified', 'THIRD_WARM_LABELS'),
    ('path_receipt', 'WPR'), ('query_receipt', 'WQR'), ('completion_held', 'THIRD_WARM_HELD'),
    ('release', 'THIRD_WARM_RELEASE'), ('retry_start', 'THIRD_RETRY_BEGIN'), ('query_done', 'THIRD_PASS')]}
result['behavioral_cycles'] = dict(events=cycles,
    fault_to_release=cycles['release'] - cycles['fault'],
    owner_phase=cycles['owner_verified'] - cycles['restore_start'],
    label_phase=cycles['labels_verified'] - cycles['owner_verified'],
    retry_including_exports=cycles['query_done'] - cycles['retry_start'])
if legacy_observer_check:
    result['scope'] += ' DEVELOPMENT ONLY: route observation retains bit0; full-width slot evidence requires selected corrected v2. This output cannot satisfy archive_offer_result gating.'
    result['development_observer_check'] = True
output = 'development_warm_audit.json' if legacy_observer_check else 'source_bound_audit.json'
(p/output).write_text(json.dumps(result, indent=2) + '\n')
print('THIRD_WARM_AUDITED', case, result['final_cycle'])
