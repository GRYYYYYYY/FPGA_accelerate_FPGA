#!/usr/bin/env python3
"""Audit the complete retained native output after the v1 Python MemoryError."""
import json
from pathlib import Path
import resource
import time

from native_output_segments_v1 import audit_native_output, sha256
from real_experiment import write_new

ROOT = Path(__file__).resolve().parents[1]


def main():
    resource.setrlimit(resource.RLIMIT_AS, (4*1024**3, 4*1024**3))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    incident = ROOT/'results/source_to_route_training_postcheck_memory_failure_20261027_v1.json'
    evidence = json.loads(incident.read_text())
    assert evidence['accepted'] is False and evidence['native']['exit_code'] == 0
    assert evidence['worker']['exit_code'] == 1 and evidence['supervisor']['resource_abort'] is False
    assert all(not Path('/proc', str(pid)).exists() for pid in [2061291, 2061603, 2065413, 2087151])
    for name, digest in evidence['files'].items():
        if sha256(name) != digest:
            raise ValueError('Frozen failure evidence changed: '+name)
    directory = ROOT/'data/derived/source_to_route_training_validation_20261027_v1'
    plan = json.loads((directory/'plan.json').read_text())
    reference = plan['references']['csr']
    started = time.monotonic()
    summary = audit_native_output(directory/'worker_000/native.raw.json', reference,
        plan['files'][reference], 'direct')
    elapsed = time.monotonic()-started
    files = dict(evidence['files'])
    for path in [incident, Path(reference), Path(__file__), Path(__file__).with_name('native_output_segments_v1.py'),
                 ROOT/'tests/test_native_output_segments.py',
                 ROOT/'data/derived/source_to_route_training_recovery_20261027_v2/segments_tests_v2.log']:
        files[str(path)] = sha256(path)
    write_new(ROOT/'results/source_to_route_preserved_full_output_audit_20261027_v1.json', dict(
        status='preserved_native_two_complete1062_net_batches_match_original_reference',
        scope='Output equality only; failed v1 application timings were not preserved and are not reconstructed',
        summary=summary, elapsed_seconds=elapsed, address_space_limit_bytes=resource.getrlimit(resource.RLIMIT_AS)[0],
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        old_experiment_accepted=False, timing_reconstructed=False, files=files))
    print(json.dumps(dict(status='full_output_verified', batches=2, routes_per_batch=1062,
                         elapsed_seconds=elapsed, peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)), flush=True)


if __name__ == '__main__':
    main()
