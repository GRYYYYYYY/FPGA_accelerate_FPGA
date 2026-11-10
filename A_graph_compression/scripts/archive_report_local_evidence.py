#!/usr/bin/env python3
"""Persist only exact local file bindings from closed, audited reports."""
import argparse,json,os,shutil,stat,tempfile
from pathlib import Path
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
LOCAL=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def atomic(p,value):
    fd,tmp=tempfile.mkstemp(dir=p.parent)
    with os.fdopen(fd,'w') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,p)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('reports',type=Path,nargs='+');a=p.parse_args();out=a.output_dir.resolve();out.mkdir(exist_ok=False)
    expected={};reports={}
    for path in a.reports:
        path=path.resolve();r=json.loads(path.read_text());require(isinstance(r.get('files'),dict),'Report has no exact file bindings')
        reports[str(path)]=digest(path)
        for name,h in r['files'].items():
            source=Path(name);require(source.is_absolute() and '..' not in source.parts,'Invalid source binding')
            require(name not in expected or expected[name]==h,'Conflicting report hashes '+name);expected[name]=h
    local={p:h for p,h in expected.items() if Path(p).is_relative_to(LOCAL)};persistent={p:h for p,h in expected.items() if p not in local}
    total=sum(Path(p).stat().st_size for p in local);require(shutil.disk_usage(ROOT).free>total+128*1024**3,'Insufficient archival headroom')
    state=dict(owner_pid=os.getpid(),status='running',copied_files=0,copied_bytes=0,total_files=len(local),total_bytes=total)
    atomic(out/'state.json',state);atomic(out/'plan.json',dict(reports=reports,local_files=local,persistent_files=persistent,script_sha256=digest(__file__)))
    records=[]
    try:
        for name,h in persistent.items():require(digest(name)==h,'Changed persistent evidence '+name)
        for name,h in sorted(local.items()):
            source=Path(name);target=out/'payload'/source.relative_to(LOCAL);target.parent.mkdir(parents=True,exist_ok=True);before=source.stat()
            fd,tmp=tempfile.mkstemp(dir=target.parent)
            with os.fdopen(fd,'wb') as f,source.open('rb') as stream:
                import hashlib
                computed=hashlib.sha256();count=0
                for block in iter(lambda:stream.read(8388608),b''):f.write(block);computed.update(block);count+=len(block)
                f.flush();os.fsync(f.fileno())
            after=source.stat();require((before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),'Evidence changed during copy')
            require(count==before.st_size and computed.hexdigest()==h and digest(tmp)==h,'Copied file hash differs '+name)
            os.chmod(tmp,stat.S_IMODE(before.st_mode));os.replace(tmp,target)
            records.append(dict(source=name,archive=str(target),sha256=h,bytes=count,mode=stat.S_IMODE(before.st_mode)))
            state['copied_files']+=1;state['copied_bytes']+=count
            if state['copied_files']%25==0:atomic(out/'state.json',state)
        for name,h in reports.items():require(digest(name)==h,'Report changed during archival')
        manifest=dict(status='closed_local_evidence_durably_copied_all_bytes_verified',source_root=str(LOCAL),archive_root=str(out/'payload'),files=records,reports=reports,persistent_files=persistent,source_removed=False,limits=['Only exact report bindings copied; active unbound caches/logs intentionally excluded','Original local paths preserved; compatible restore_frozen_local_evidence.py can relink missing originals'])
        atomic(out/'manifest.json',manifest);state['status']='complete';atomic(out/'state.json',state);print(manifest['status'],len(records),state['copied_bytes'])
    except BaseException as e:state.update(status='failed',error=str(e));atomic(out/'state.json',state);raise
if __name__=='__main__':main()
