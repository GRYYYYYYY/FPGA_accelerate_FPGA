#!/usr/bin/env python3
"""Measure inherited fork/exec high-water accounting versus post-exec VmHWM locally."""
import argparse
import json
import platform
import resource
import subprocess
import sys
from pathlib import Path
from real_experiment import write_new


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    payload = bytearray(64*1024*1024)
    child_code = '''import json,resource
from pathlib import Path
hwm=int(next(s.split()[1] for s in Path('/proc/self/status').read_text().splitlines() if s.startswith('VmHWM:')))
print(json.dumps({'self_ru_maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'post_exec_vm_hwm_kib':hwm}))
'''
    child = subprocess.run([sys.executable, '-c', child_code], capture_output=True, text=True,
                           check=True, preexec_fn=lambda: None)
    child_peak = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    parent_peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    report = {'status': 'observed_local_fork_exec_memory_accounting', 'python': sys.version,
              'platform': platform.platform(), 'parent_live_payload_bytes': len(payload),
              'parent_ru_maxrss_kib': parent_peak,
              'waited_child_ru_maxrss_kib': child_peak,
              'child': json.loads(child.stdout),
              'interpretation': 'RUSAGE_CHILDREN ru_maxrss includes fork/pre-exec memory high water; native batch VmHWM describes the executable after exec. They are different scopes, neither is summed with parent peak.',
              'scope': 'One local accounting probe, not an application performance measurement.'}
    write_new(args.output, report)
    print(json.dumps(report))


if __name__ == '__main__': main()
