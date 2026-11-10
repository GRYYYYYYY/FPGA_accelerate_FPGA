"""Project the frozen field/transaction oracle directly into public AXI vectors.

Only the oracle's serialization sink and query selection are transformed; its
state/value transitions stay identical. No internal-command text intermediate.
"""
from collections import Counter
from pathlib import Path
import argparse
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from audit_large_query_demand import sha


class Projection:
    def __init__(self, host, pages):
        self.host = host; self.pages = pages
        self.owners = {}; self.pending = None; self.labels = []; self.bitmap = 0
        self.counts = Counter(); self.transfers = 0; self.peak = 0; self.queries = 0
        self.max_generation = 0; self.max_transaction = 0

    def public(self, a, frame=0, page_index=0):
        row = (a[0], a[1], a[2], a[3], a[4], a[5], a[9], a[10], a[11],
               a[15], a[16], a[17], a[18], a[19], a[20], frame, page_index)
        self.host.write(' '.join(format(x, 'x') for x in row) + '\n')
        self.counts[str(a[0])] += 1

    def emit_row(self, a):
        if a[15] != 0:
            raise ValueError('Unexpected failing actual command')
        if not 0 <= a[5] < 65536:
            raise ValueError('Generation cannot be represented')
        self.max_generation = max(self.max_generation, a[5])
        op = a[0]
        if self.pending is not None:
            header, frame = self.pending
            reading = header[0] == 6
            if a[1:6] != header[1:6] or a[6] != header[19] or a[7] != reading:
                raise ValueError('Transport descriptor changed')
            if len(self.labels) < 64:
                if op != (7 if reading else 9) or a[9] != len(self.labels):
                    raise ValueError('Transport records reordered')
                present, word = (a[8], a[12]) if reading else (a[17], a[16])
                if word >> 136 or (not present and word):
                    raise ValueError('Noncanonical raw record')
                self.bitmap |= present << len(self.labels)
                self.labels.append(word.to_bytes(20, 'little'))
            else:
                if op != 8:
                    raise ValueError('Missing completion')
                blob = self.bitmap.to_bytes(8, 'little') + b''.join(self.labels) + bytes(56)
                for offset in range(0, 1344, 64):
                    self.pages.write(format(int.from_bytes(blob[offset:offset + 64], 'little'), '0128x') + '\n')
                self.public(header, frame, self.transfers)
                self.transfers += 1; self.pending = None
            return
        if op in (5, 6):
            key = a[4], a[3], a[2]
            if op == 5 and key not in self.owners:
                self.owners[key] = len(self.owners)
            if key not in self.owners or len(self.owners) > 23405:
                raise ValueError('Unknown or oversized backing owner')
            self.peak = max(self.peak, len(self.owners))
            if not 0 <= a[19] < 65536:
                raise ValueError('Transaction cannot be represented')
            self.max_transaction = max(self.max_transaction, a[19])
            self.pending = (a, self.owners[key]); self.labels = []; self.bitmap = 0
        elif op in (7, 8, 9):
            raise ValueError('Orphan internal command')
        else:
            if op == 11:
                self.owners.clear()
            if op == 0:
                self.queries += 1
            self.public(a)


def transformed_oracle(path):
    text = path.read_text()
    changes = [
        ("self.stream.write(' '.join(format(x,'x') for x in columns)+'\\n')", 'self.stream.emit_row(columns)'),
        ('def real(o,capture):', 'def real(o,capture,selected_attempts):'),
        ("if row['count']>100000:continue", "if row['attempt'] not in selected_attempts:continue")]
    for before, after in changes:
        if text.count(before) != 1:
            raise ValueError('Ambiguous oracle change: ' + before)
        text = text.replace(before, after)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--large', action='store_true')
    args = parser.parse_args()
    out = args.output.resolve(); out.mkdir()
    demand_path = ROOT / 'results/large_query_demand_20261023/manifest.json'
    if sha(demand_path) != 'cbc1340cf62b89ea6b00e3f1a62a8476857a5ac3c36bc0a0ca78243a16c6fbda':
        raise ValueError('Changed demand audit')
    demand = json.loads(demand_path.read_text())
    rows_path = demand_path.parent / 'queries.json'
    if sha(rows_path) != demand['artifacts']['queries.json']:
        raise ValueError('Changed demand rows')
    rows = json.loads(rows_path.read_text())
    selected = [r['attempt'] for r in rows if (r['accesses'] > 100000 and r['fits_current_epoch']) == args.large
                and (args.large or r['accesses'] <= 100000)]
    if len(selected) != (7 if args.large else 19):
        raise ValueError('Wrong complete-query selection')
    capture = ROOT / 'results/real_field_values_20261023T024250Z'
    for name, expected in demand['inputs'].items():
        if sha(Path(name)) != expected:
            raise ValueError('Changed captured input')
    source = ROOT / 'hardware/scripts/make_controller_vectors.py'
    parent_path = ROOT / 'results/rtl_page_controller_20261023/vectors/vectors_manifest.json'
    parent = json.loads(parent_path.read_text())
    if sha(source) != parent['files'][str(source)]:
        raise ValueError('Changed parent oracle')
    text = transformed_oracle(source)
    (out / 'oracle_transformed.py').write_text(text)
    namespace = {'__name__': 'frozen_projection_oracle', '__file__': str(source)}
    exec(compile(text, str(out / 'oracle_transformed.py'), 'exec'), namespace)
    record = {'status': 'running', 'pid': os.getpid(), 'large': args.large, 'selected_attempts': selected,
              'inputs': {str(p): sha(p) for p in [demand_path, rows_path, parent_path, source]},
              'source': {str(Path(__file__).resolve()): sha(Path(__file__).resolve())}, 'board_performance': None}
    def save():
        (out / 'manifest.json').write_text(json.dumps(record, indent=2) + '\n')
    save()
    try:
        with (out / 'actual.txt').open('w') as host, (out / 'pages.hex').open('w') as pages:
            projection = Projection(host, pages)
            oracle = namespace['Oracle'](projection, tx_bits=16)
            result = namespace['real'](oracle, capture, set(selected))
            if projection.pending is not None:
                raise ValueError('Incomplete transfer suffix')
        chosen = [r for r in rows if r['attempt'] in selected]
        expected_commands = sum(r['public_commands'] for r in chosen)
        expected_transfers = sum(r['transfers'] for r in chosen)
        if sum(projection.counts.values()) != expected_commands or projection.transfers != expected_transfers:
            raise ValueError('Independent demand census mismatch')
        if result['field_accesses'] != sum(r['accesses'] for r in chosen) or result['selected_attempts'] != selected:
            raise ValueError('Incomplete actual trace coverage')
        if not args.large:
            baseline = ROOT / 'results/rtl_memory_endpoint_20261023/vectors'
            for name in ['actual.txt', 'pages.hex']:
                if sha(out / name) != sha(baseline / name):
                    raise ValueError('Streaming projection differs from frozen small vectors')
        record.update(status='passed', queries=projection.queries, public_commands=expected_commands,
                      transfers=projection.transfers, peak_reserved_owners=projection.peak,
                      maximum_generation=projection.max_generation, maximum_transaction=projection.max_transaction,
                      counts=dict(projection.counts), field_replay=result, oracle_commands=oracle.count,
                      small_bitwise_equivalence=not args.large,
                      scope='Complete selected query value/transaction oracle projected to public commands and sequential expected page bytes; no RTL run yet.',
                      artifacts={name: sha(out / name) for name in ['actual.txt', 'pages.hex', 'oracle_transformed.py']})
        save()
        (out / 'completion_audit.json').write_text(json.dumps({'status': 'passed', 'manifest_sha256': sha(out / 'manifest.json')}, indent=2) + '\n')
        print(json.dumps({k: record[k] for k in ['queries', 'public_commands', 'transfers', 'peak_reserved_owners', 'maximum_generation', 'maximum_transaction', 'small_bitwise_equivalence']}, indent=2), flush=True)
    except Exception as exc:
        record.update(status='failed', error=repr(exc)); save(); raise


if __name__ == '__main__':
    main()
