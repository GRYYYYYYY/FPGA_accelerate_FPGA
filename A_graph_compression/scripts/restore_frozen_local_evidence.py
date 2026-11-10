#!/usr/bin/env python3
"""Verify persistent backup; optionally relink only missing original local paths."""
import argparse
import hashlib
import json
from pathlib import Path

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(8388608),b''):h.update(block)
    return h.hexdigest()
def restore(manifest,relink=False):
    d=json.loads(manifest.read_text());assert d['status']=='closed_local_evidence_durably_copied_all_bytes_verified'
    source_root=Path(d['source_root']);archive_root=Path(d['archive_root']);assert source_root==Path('/tmp/A_graph_compression_recovery_20261025_v1')
    seen=set()
    for row in d['files']:
        source=Path(row['source']);archive=Path(row['archive']);assert source.is_relative_to(source_root) and archive.is_relative_to(archive_root)
        assert '..' not in source.parts and '..' not in archive.parts
        relative=source.relative_to(source_root);assert relative==archive.relative_to(archive_root) and source not in seen;seen.add(source)
        archive=manifest.resolve().parent/'payload'/relative
        assert archive.is_file() and archive.stat().st_size==row['bytes'] and sha(archive)==row['sha256'],'Changed archive'
        if source.exists():assert sha(source)==row['sha256'],'Original local file changed'
        elif relink:
            assert not source.is_symlink(),'Dangling local alias needs explicit reconciliation'
            source.parent.mkdir(parents=True,exist_ok=True);source.symlink_to(archive)
    print('archive_verified_files',len(seen),'relink_enabled',relink)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest',type=Path);p.add_argument('--relink-missing',action='store_true');a=p.parse_args();restore(a.manifest,a.relink_missing)
