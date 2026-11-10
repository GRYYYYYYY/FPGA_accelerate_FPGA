"""Audit frozen 192-byte page occupancy; reports work counts, never speedup."""
from pathlib import Path
import hashlib
import json
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

def main():
    source = ROOT / 'results/small_checkpoint_vectors_full_20261023'
    out = ROOT / 'results/page_record_density_20261024'
    out.mkdir(exist_ok=False)
    manifest_bytes = (source / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    audit = json.loads((source / 'completion_audit.json').read_text())
    assert audit['status'] == 'passed'
    assert audit['manifest_sha256'] == hashlib.sha256(manifest_bytes).hexdigest()
    assert manifest['status'] == 'passed' and manifest['page_bytes'] == 192
    digest = hashlib.sha256()
    histogram = Counter()
    count = 0
    with (source / 'pages.hex').open('rb') as pages:
        while True:
            first = pages.readline()
            if not first:
                break
            lines = [first, pages.readline(), pages.readline()]
            assert all(len(line) == 129 and line[-1:] == b'\n' for line in lines)
            for line in lines:
                digest.update(line)
            blob = b''.join(int(line, 16).to_bytes(64, 'little') for line in lines)
            bitmap = blob[0]
            assert blob[161:] == bytes(31), count
            for offset in range(8):
                word = int.from_bytes(blob[1 + offset * 20:21 + offset * 20], 'little')
                assert word >> 136 == 0, (count, offset)
                assert bitmap & (1 << offset) or word == 0, (count, offset)
            histogram[bitmap.bit_count()] += 1
            count += 1
    assert count == manifest['transfers']
    assert digest.hexdigest() == manifest['artifacts']['pages.hex']
    present = sum(k * v for k, v in histogram.items())
    total = count * 8
    result = {
        'status': 'passed', 'vector_manifest_sha256': audit['manifest_sha256'],
        'pages_sha256': digest.hexdigest(), 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'queries': manifest['queries'], 'transfers': count,
        'present_records_per_page_histogram': dict(sorted(histogram.items())),
        'represented_records': total, 'present_records': present,
        'absent_records': total - present, 'absent_record_fraction': (total - present) / total,
        'mean_present_records_per_page': present / count,
        'existing_payload_bytes': count * 192,
        'validation': 'All page bytes hashed; all record padding and absent record values checked.',
        'scope': 'Selected 38-query frozen trace, both WB and RF transfer occurrences; not unique pages or all design attempts.',
        'interpretation': 'Absent record count is potential control work only. No sparse adapter implemented or cycle savings measured; byte format and existing AXI traffic remain unchanged.'
    }
    (out / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
