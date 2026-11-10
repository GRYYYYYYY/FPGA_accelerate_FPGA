#!/usr/bin/env python3
"""Observe shared cgroup memory without using free/cache bytes as an admission gate.

Finite per-process limits are applied by the caller. An actual new cgroup OOM
event stops only the caller's own session; this does not attribute that event.
No estimate of reclaimable cache is used as a guarantee or a decision input.
"""
from pathlib import Path
import time

POLICY = 'no_free_memory_gate_finite_process_as_abort_on_new_oom_v1'


def counters(text):
    result = {}
    for line in text.splitlines():
        key, value = line.split()
        if key in result or int(value) < 0:
            raise ValueError('Invalid memory counter')
        result[key] = int(value)
    return result


def observe(base=Path('/sys/fs/cgroup')):
    maximum = int((base/'memory.max').read_text())
    current_before = int((base/'memory.current').read_text())
    stats = counters((base/'memory.stat').read_text())
    events = counters((base/'memory.events').read_text())
    if maximum <= 0 or not {'oom', 'oom_kill'} <= events.keys():
        raise ValueError('Incomplete cgroup memory accounting')
    current_after = int((base/'memory.current').read_text())
    return dict(policy=POLICY, sampled_monotonic_seconds=time.monotonic(),
                maximum_bytes=maximum, current_bytes=current_after,
                current_before_bytes=current_before,
                raw_free_bytes=maximum-current_after, stats=stats, events=events,
                pressure=(base/'memory.pressure').read_text())


def abort_reason(initial, current):
    """No byte threshold: only new OOM events or invalid/reset event accounting."""
    if initial.get('policy') != POLICY or current.get('policy') != POLICY:
        raise ValueError('Unexpected resource policy')
    for key in ('oom', 'oom_kill'):
        before, after = initial['events'][key], current['events'][key]
        if type(before) is not int or type(after) is not int or min(before, after) < 0:
            raise ValueError('Invalid OOM accounting')
        if after < before:
            return 'oom_accounting_reset'
        if after > before:
            return 'new_cgroup_' + key
    return None
