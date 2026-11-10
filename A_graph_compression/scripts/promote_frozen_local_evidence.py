#!/usr/bin/env python3
"""Byte-verified durable backup of closed local artifacts, excluding active runs."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile
ROOT=Path(__file__).resolve().parents[1]
LOCAL=Path('/tmp/A_graph_compression_recovery_20261025_v1')
EXCLUDE={'snapshot_rtl_local_recovery','snapshot_rtl_local_project','evidence_promotion','LATEST_HANDOFF.md'}
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(8388608),b''):h.update(block)
    return h.hexdigest()
def atomic(path,value):
    temp=path.with_name(path.name+'.tmp');temp.write_text(json.dumps(value,indent=2)+'\n');temp.replace(path)
def main():
    destination=ROOT/'data/derived/frozen_local_evidence_20261025_v1';destination.mkdir(exist_ok=False)
    progress=LOCAL/'evidence_promotion';progress.mkdir(exist_ok=False)
    # These sources are closed/frozen. Never snapshot live simulator/cache output.
    paths=sorted(p for p in LOCAL.rglob('*') if p.is_file() and p.relative_to(LOCAL).parts[0] not in EXCLUDE)
    total=sum(p.stat().st_size for p in paths)
    if total>256*1024**3 or shutil.disk_usage(ROOT).free<total+128*1024**3:raise RuntimeError('Insufficient safe archival headroom')
    state=dict(owner_pid=os.getpid(),status='running',copied_files=0,copied_bytes=0,total_files=len(paths),total_bytes=total,excluded_active=sorted(EXCLUDE))
    atomic(progress/'state.json',state);atomic(destination/'state.json',state)
    records=[]
    try:
        for index,source in enumerate(paths):
            relative=source.relative_to(LOCAL);target=destination/'payload'/relative;target.parent.mkdir(parents=True,exist_ok=True)
            before=source.stat();h=hashlib.sha256();count=0
            with tempfile.NamedTemporaryFile(dir=target.parent,prefix='.copy_',delete=False) as output:
                temporary=Path(output.name)
                with source.open('rb') as stream:
                    for block in iter(lambda:stream.read(8388608),b''):output.write(block);h.update(block);count+=len(block)
                output.flush();os.fsync(output.fileno())
            after=source.stat()
            if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns) or count!=before.st_size:raise RuntimeError('Source changed during archival: '+str(source))
            digest=h.hexdigest()
            if sha(temporary)!=digest:raise RuntimeError('Archive copy differs: '+str(source))
            os.chmod(temporary,stat.S_IMODE(before.st_mode));temporary.replace(target)
            records.append(dict(source=str(source),archive=str(target),sha256=digest,bytes=count,mode=stat.S_IMODE(before.st_mode)))
            state['copied_files']=index+1;state['copied_bytes']+=count
            if index%25==0:atomic(progress/'state.json',state);atomic(destination/'state.json',state)
        manifest=dict(status='closed_local_evidence_durably_copied_all_bytes_verified',source_root=str(LOCAL),archive_root=str(destination/'payload'),files=records,excluded_active=sorted(EXCLUDE),source_removed=False,limits=['Active snapshot recovery excluded; later final outputs require a new archival revision','Original local paths remain present; restore helper can relink missing paths after a host restart'])
        atomic(destination/'manifest.json',manifest);state['status']='complete';atomic(progress/'state.json',state);atomic(destination/'state.json',state)
        print(manifest['status'],len(records),state['copied_bytes'],flush=True)
    except BaseException as e:state.update(status='failed',error=str(e));atomic(progress/'state.json',state);atomic(destination/'state.json',state);raise
if __name__=='__main__':main()
