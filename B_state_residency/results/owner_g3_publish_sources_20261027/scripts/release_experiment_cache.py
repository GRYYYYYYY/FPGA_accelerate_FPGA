"""Advise Linux to evict clean pages of explicitly selected, audited experiments.

Run after archive/restore verification. This does not delete or rewrite files,
flush dirty data, touch host-wide drop_caches, or promise a given eviction size.
Without --apply it only reports eligible bytes. Each root must have a passing
source-bound audit tied to its current, terminal manifest.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat


def memory_bytes():
    try:
        return int(Path('/sys/fs/cgroup/memory.current').read_text())
    except (OSError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('roots', nargs='+', type=Path)
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    roots = list(dict.fromkeys(p.resolve() for p in args.roots))
    # Validate all roots before advising any file.
    for root in roots:
        audit = json.loads((root / 'source_bound_audit.json').read_text())
        raw = (root / 'manifest.json').read_bytes()
        manifest = json.loads(raw)
        if (audit.get('status') != 'passed'
                or audit.get('manifest_sha256') != hashlib.sha256(raw).hexdigest()
                or manifest.get('status') in (None, 'running', 'pending')):
            raise SystemExit(f'Refusing unaudited, changed or active root: {root}')
    before = memory_bytes()
    count = size = 0
    errors = []
    for root in roots:
        for directory, _, names in os.walk(root, followlinks=False):
            for name in names:
                path = Path(directory) / name
                try:
                    info = path.lstat()
                    if not stat.S_ISREG(info.st_mode) or info.st_size < (1 << 20):
                        continue
                    if args.apply:
                        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
                        try:
                            if not stat.S_ISREG(os.fstat(fd).st_mode):
                                continue
                            os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
                        finally:
                            os.close(fd)
                    count += 1
                    size += info.st_size
                except OSError as exc:
                    errors.append({'path': str(path), 'error': str(exc)})
    print(json.dumps(dict(applied=args.apply, roots=[str(p) for p in roots],
                         files=count, eligible_bytes=size, errors=errors,
                         cgroup_bytes_before=before, cgroup_bytes_after=memory_bytes()),
                     indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
