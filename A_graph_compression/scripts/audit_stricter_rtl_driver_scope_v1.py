#!/usr/bin/env python3
"""Verify resource-limited driver/checker versions preserve all functional code."""
import json
from pathlib import Path
from check_vitis_kernel import digest, require
from run_compact_native_stack_recovery_v1 import atomic

ROOT = Path(__file__).resolve().parents[1]


def main():
    output = ROOT/'results/stricter_rtl_driver_scope_audit_20261025_v1.json'
    require(not output.exists(), 'Refuse overwrite')
    pairs = [
        ('run_compressed_bus64_dpi_rtl_v2.py', 'run_compressed_bus64_dpi_rtl_v3.py'),
        ('check_compressed_bus64_dpi_rtl_v2.py', 'check_compressed_bus64_dpi_rtl_v3.py'),
        ('run_snapshot_dpi_rtl_v1.py', 'run_snapshot_dpi_rtl_v2.py'),
        ('check_snapshot_dpi_rtl_v1.py', 'check_snapshot_dpi_rtl_v2.py'),
    ]
    allowed = [
        ('171798691840', '154618822656'),
        ('184*1024**3', '168*1024**3'),
        ('160*1024**3', '144*1024**3'),
        ('compressed_batch_bus64_dpi_rtl_v2', 'compressed_batch_bus64_dpi_rtl_v3'),
        ('snapshot_dpi_rtl_v1', 'snapshot_dpi_rtl_v2'),
    ]
    files = {str(Path(__file__).resolve()): digest(__file__)}
    records = []
    for old, new in pairs:
        before = ROOT/'scripts'/old
        after = ROOT/'scripts'/new
        expected = before.read_text()
        changes = {}
        for source, replacement in allowed:
            changes[source] = expected.count(source)
            expected = expected.replace(source, replacement)
        require(expected == after.read_text(), 'Unapproved functional source change: '+new)
        for path in (before, after):
            files[str(path)] = digest(path)
        records.append(dict(original=str(before), replacement=str(after), allowed_replacement_counts=changes))
    require(184-160 == 168-144 == 24, 'Startup reserve changed')
    atomic(output, dict(status='four_driver_checker_sources_identical_except_stricter_caps_admission_and_trial_paths',
        source_pairs=records, startup_reserve_gib=24, address_space_cap_gib=144,
        admission_raw_free_gib=168, runtime_free_guard_gib=16,
        functional_scope_changed=False, files=files,
        limits=['Source equivalence under an explicit restricted replacement list, not RTL completion',
                '144GiB sufficiency remains unproven until actual execution completes']))
    print(output)


if __name__ == '__main__':
    main()
