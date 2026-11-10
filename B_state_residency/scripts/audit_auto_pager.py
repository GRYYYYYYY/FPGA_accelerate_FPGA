"""Independently bind pager regression artifacts and check oracle/counter coverage."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def check_vector(row):
    mode, parent, child, flags, created, lag, prev, cs, ps, excluded, count = row[:11]
    assert mode in (0, 1) and 0 <= parent < 2**24 and 0 <= child < 2**24
    assert parent != child and flags < 256 and created in (0, 1) and lag in (0, 1)
    reads = []
    existing = False
    if created:
        reads.append((1, child))
        if prev != 0xffffffff:
            reads.extend([(2, child), (3, parent)])
            existing = cs != ps and prev == parent and bool(flags & 64)
    if existing:
        expected = False
    elif flags & 64:
        expected = True
    elif flags & 4 and not created and (not lag or not flags & 8):
        expected = True
    elif not lag and flags & 2:
        expected = True
    elif created and flags & 32:
        reads.append((4, child))
        expected = prev != parent
    else:
        expected = False
    assert excluded == int(expected) and count == len(reads)
    assert list(zip(row[11:11 + count*2:2], row[12:12 + count*2:2])) == reads
    assert all(x == 0 for x in row[11 + count*2:])


def main():
    out = ROOT / 'results/auto_pager_20261024'
    manifest = read(out / 'manifest.json')
    assert manifest['status'] == 'passed'
    for name, spec in manifest['sources'].items():
        assert sha(out / 'sources' / name) == spec['sha256'] == sha(Path(spec['path']))
    for path, digest in manifest['gates'].items():
        assert sha(Path(path)) == digest
        assert read(Path(path))['status'] == 'passed'
    base = ROOT / 'results/exclusion_edge_engine_v4_20261024'
    gate = read(base / 'source_bound_audit.json')
    assert gate['manifest_sha256'] == sha(base / 'manifest.json')
    for name, spec in manifest['sources'].items():
        if name.startswith(('backend/', 'adapter/', 'hls32/', 'engine/')):
            assert spec['sha256'] == read(base / 'manifest.json')['sources'][name]['sha256']
    for key, file in [('binary_sha256', 'make_vectors'), ('vectors_sha256', 'vectors.txt'), ('log_sha256', 'oracle_run.stdout.log')]:
        assert manifest['oracle'][key] == sha(out / file)
    assert [c['stage'] for c in manifest['commands']] == ['oracle_build', 'oracle_run']
    assert all(c['exit_code'] == 0 for c in manifest['commands'])
    rows = [[int(v, 16) for v in line.split()] for line in (out / 'vectors.txt').read_text().splitlines()]
    assert len(rows) == manifest['oracle']['lines'] == 27680
    for row in rows:
        assert len(row) == 19
        check_vector(row)
    assert sum(row[10] for row in rows) == 34898
    # Exhaustive nonempty flag/created/lag/previous/sequence cross-product.
    combinations = set()
    for row in rows[:27648]:
        assert row[0] == 1 and row[6] in (0xffffffff, row[1], row[2])
        assert row[7] in (0, 1, 0x80000000) and row[8] in (0, 1, 0x80000000)
        combinations.add((row[3], row[4], row[5], (0xffffffff, row[1], row[2]).index(row[6]), row[7], row[8]))
    assert len(combinations) == 27648
    assert all(row[0] == 0 and row[6:9] == [0, 0, 0] for row in rows[27648:])
    tb = (out / 'sources/pager/tb_paged_exclusion_engine.sv').read_text()
    definitions = {'budget32': 'PAGER_BUDGET', 'single': 'PAGER_SINGLE', 'fault': 'PAGER_FAULT', 'wrap16': 'PAGER_WRAP', 'production32': None}
    assert set(manifest['cases']) == set(definitions)
    results = {}
    for case, define in definitions.items():
        item = manifest['cases'][case]
        assert item['status'] == 'passed' and item['define'] == define
        commands = item['commands']
        assert [c['stage'] for c in commands] == ['compile', 'elaborate', 'simulate']
        assert all(c['exit_code'] == 0 and c['elapsed_s'] > 0 for c in commands)
        argv = commands[0]['argv']
        if define:
            assert argv[argv.index('--define') + 1] == define
        else:
            assert '--define' not in argv
        compiled = {Path(arg).relative_to(out / 'sources').as_posix() for arg in argv if arg.endswith(('.sv', '.v'))}
        expected_sources = {name for name in manifest['sources'] if name.endswith(('.sv', '.v'))}
        assert compiled == expected_sources
        assert 'fixture=' + str(out / 'vectors.txt') in commands[2]['argv']
        for file, digest in item['artifacts'].items():
            assert sha(out / case / file) == digest
        assert (out / case / 'run.tcl').read_text() == 'run 1000ms\nquit\n'
        log = (out / case / 'simulate.log').read_text()
        assert not re.search(r'^(Fatal:|Error:|ERROR:)', log, re.M)
        assert '$finish called' in log and log.count(item['result']) == 1
        values = {k: int(v) for k, v in re.findall(r'(\w+)=(\d+)', item['result'])}
        if case in ('budget32', 'single', 'production32'):
            slots, tx, gen, stride = {'budget32': (32, 6, 16, 97), 'single': (1, 6, 3, 17), 'production32': (32, 16, 16, 1)}[case]
            assert (values['slots'], values['tx_bits'], values['gen_bits'], values['stride']) == (slots, tx, gen, stride)
            assert f'SLOTS={slots},TX_BITS={tx},GEN_BITS={gen},FRAMES=256,INDEX_BITS=8,STRIDE={stride}' in tb
            selected = [row for i, row in enumerate(rows) if i % stride == 0 or i >= 27648]
            labels = sum(row[10] for row in selected)
            assert values['edges'] == len(selected) + 1
            assert values['labels'] == values['responses'] == labels
            assert values['hls_calls'] == values['edges'] + labels
            assert values['checkpoints'] == values['auto_cp'] + 1 and values['auto_cp'] > 0
            assert values['aw'] == values['b'] >= values['wb'] > 0
            assert values['r'] == 3 * values['rf'] and values['ar'] >= values['rf'] > 0
            assert values['empty'] > 0 and 0 < values['max_tx'] <= 2**tx
            if case == 'production32':
                assert values['max_tx'] >= 65502 and values['edges'] == 27681
            if case == 'single':
                assert values['gen_cp'] > 0
        elif case == 'wrap16':
            assert values == {'requests': 65536, 'checkpoints': 1, 'final_binding_before_close': 1, 'checks': 65538}
            assert 'SLOTS=1,TX_BITS=16,GEN_BITS=16,FRAMES=16,INDEX_BITS=4' in tb
        else:
            assert values == {'cases': 3, 'wb_error': 1, 'rf_edge_error': 1, 'directory_full': 1, 'checks': 14}
        results[case] = values
    (out / 'auditor.py').write_bytes(Path(__file__).read_bytes())
    result = {'status': 'passed', 'manifest_sha256': sha(out / 'manifest.json'),
              'auditor_sha256': sha(Path(__file__)), 'oracle_edges': len(rows), 'oracle_reads': 34898,
              'cases': results, 'scope': 'Actual state-reset HLS, automatic page manager, native sparse endpoint and AXI byte-model simulation. Production widths; simulation backing capacity at most 256 frames. No whole-router, board, throughput or speedup claim.'}
    (out / 'source_bound_audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
