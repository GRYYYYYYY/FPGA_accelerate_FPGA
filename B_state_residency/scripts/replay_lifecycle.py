"""Replay actual path events through the CPU protocol specification; no timing claim."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from lifecycle import Authority, Context, Replica


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def resources(path, meta):
    if path and path[0] == meta['sink'] and not meta['has_alt']:
        return frozenset(path[1:-1])
    return frozenset(path)


def validate_config(config):
    if config.get('dataset_kind') != 'real_path_protocol_replay':
        raise ValueError('Require an explicit real trace replay configuration')
    for key in ('expected_attempts', 'expected_connections', 'expected_occupied_resources'):
        if type(config.get(key)) is not int or config[key] <= 0:
            raise ValueError('Invalid expected count: ' + key)
    for key in ('input', 'trace', 'metadata_binary'):
        if sha(ROOT / config[key]) != config[key + '_sha256']:
            raise ValueError('Frozen input changed: ' + key)


def validate_counts(config, attempts, connections, occupied):
    actual = (attempts, connections, occupied)
    expected = tuple(config[k] for k in ('expected_attempts', 'expected_connections', 'expected_occupied_resources'))
    if actual != expected:
        raise ValueError('Trace completeness/count mismatch: ' + str((actual, expected)))


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: replay invariant assertions must remain enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT / 'configs/lifecycle_replay.json')
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    validate_config(config)
    trace, dataset = ROOT / config['trace'], ROOT / config['input']
    binary = ROOT / config['metadata_binary']
    out = ROOT / 'results' / ('lifecycle_real_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    out.mkdir()
    record = {'status': 'running', 'execution_kind': 'real_path_protocol_replay',
              'performance': None, 'scope': 'Sequential protocol replay, not router/device integration. No real historical-price events in this trace.',
              'config': config, 'config_sha256': sha(args.config),
              'files': {str(p): sha(p) for p in [trace, dataset, Path(__file__).resolve(),
                         ROOT / 'src/lifecycle.py', ROOT / 'adapters/export_lifecycle_metadata.cpp',
                         ROOT / 'build/real_trace/export_lifecycle_metadata', ROOT / 'build/real_trace/original.cpp']}}
    def save():
        (out / 'manifest.json').write_text(json.dumps(record, indent=2) + '\n')
    save()
    (out / 'replay_snapshot.py').write_bytes(Path(__file__).read_bytes())
    (out / 'lifecycle_snapshot.py').write_bytes((ROOT / 'src/lifecycle.py').read_bytes())
    try:
        with (out / 'export.log').open('w') as log:
            subprocess.run([str(binary), str(dataset), str(out / 'metadata.jsonl')],
                           stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
        meta, initial_occ = {}, {}
        for line in (out / 'metadata.jsonl').open():
            row = json.loads(line)
            if 'connection' in row:
                meta[row['connection']] = row
            else:
                initial_occ[row['resource']] = row['occupancy']
        nets = {c: row['net'] for c, row in meta.items()}
        nets.update({-c-1: row['net'] for c, row in meta.items() if not row['has_alt']})
        authority = Authority(nets)
        replica = Replica(authority.design)
        context = Context(authority, replica, 0, epoch_bits=8)
        raw_paths = {c: row['path'] for c, row in meta.items()}
        for c, row in meta.items():
            if not row['has_alt']:
                replica.apply(context.commit(context.begin(), -c-1, [row['sink']]))
            if row['path']:
                replica.apply(context.commit(context.begin(), c, resources(row['path'], row)))
        assert {r: len(owners) for r, owners in authority.references.items()} == initial_occ, 'Initial loader occupancy mismatch'
        attempts = recoveries = 0
        for line in trace.open():
            row = json.loads(line)
            attempts += 1
            assert row['attempt'] == attempts
            c = row['connection_index']
            assert meta[c]['id'] == row['connection_id'] and meta[c]['net'] == row['net_index']
            assert raw_paths[c] == row['previous_path'], 'Previous path mismatch'
            # Expose rip-up as its own version before the next search/commit.
            replica.apply(context.commit(context.begin(), c, []))
            delta = context.commit(context.begin(), c, resources(row['path'], meta[c]))
            raw_paths[c] = row['path']
            if attempts % 50000 == 0:
                # Model a lost delivery and recover from an authoritative snapshot.
                try:
                    context.begin()
                except ValueError:
                    pass
                else:
                    raise AssertionError('Stale replica accepted a query')
                replica.install(authority.snapshot())
                recoveries += 1
            else:
                replica.apply(delta)
                replica.apply(delta)
            if attempts % 50000 == 0:
                record.update(attempts=attempts, recoveries=recoveries)
                save()
                print('Replayed', attempts, flush=True)
        # Independent reconstruction from final raw paths, without Authority references.
        owners = defaultdict(set)
        for c, row in meta.items():
            if not row['has_alt']:
                owners[row['sink']].add(row['net'])
            for resource in resources(raw_paths[c], row):
                owners[resource].add(row['net'])
        for resource in owners.keys() | replica.values.keys() | authority.references.keys():
            expected = len(owners.get(resource, ()))
            assert authority.occupancy(resource) == expected
            assert replica.values.get(resource, (0, 0)) == (expected, 0)
        validate_counts(config, attempts, len(meta), len(owners))
        validate_config(config)
        record.update(status='passed', attempts=attempts, recoveries=recoveries,
                      connections=len(meta), occupied_resources=len(owners), final_version=authority.version,
                      checks=['initial_loader_occupancy', 'previous_path_chain', 'final_distinct_net_occupancy',
                              'replica_matches_authority', 'duplicate_delivery', 'lost_delta_snapshot_recovery'])
    except Exception as error:
        record.update(status='failed', error=repr(error))
        raise
    finally:
        record['finished_utc'] = datetime.now(timezone.utc).isoformat()
        save()
    print(out, flush=True)


if __name__ == '__main__':
    main()
