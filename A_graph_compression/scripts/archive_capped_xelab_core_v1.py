#!/usr/bin/env python3
"""Losslessly archive the failed owned compiler core before releasing its local cache."""
import gzip
import hashlib
import os
from pathlib import Path
from check_vitis_kernel import digest,require
from supervise_search_axi_dpi_v3 import atomic
ROOT=Path(__file__).resolve().parents[1]
def main():
    source=Path('/tmp/A_graph_compression_recovery_20261025_v1/search_axi_dpi_replay_v4/sim/verilog/core.1797616')
    require(not Path('/proc/1797616').exists(),'Compiler still live')
    before=source.stat();out=ROOT/'data/derived/capped_xelab_core_archive_20261025_v1';out.mkdir(exist_ok=False)
    state=dict(owner_pid=os.getpid(),status='running',stage='compressing_closed_core',source=str(source),source_bytes=before.st_size,processed_bytes=0)
    atomic(out/'state.json',state);target=out/'core.1797616.gz';temporary=out/'core.tmp'
    try:
        h=hashlib.sha256();count=0
        with source.open('rb') as src,temporary.open('xb') as raw:
            with gzip.GzipFile(filename='',mode='wb',fileobj=raw,compresslevel=1,mtime=0) as dst:
                for block in iter(lambda:src.read(4*1024*1024),b''):
                    dst.write(block);h.update(block);count+=len(block)
                    if count%(256*1024*1024)==0:state['processed_bytes']=count;atomic(out/'state.json',state)
            raw.flush();os.fsync(raw.fileno())
        after=source.stat();require((before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns) and count==before.st_size,'Core changed during compression')
        state.update(stage='independent_full_decompression_verification',processed_bytes=count);atomic(out/'state.json',state)
        verify=hashlib.sha256();size=0
        with gzip.open(temporary,'rb') as f:
            for block in iter(lambda:f.read(4*1024*1024),b''):verify.update(block);size+=len(block)
        require(size==count and verify.hexdigest()==h.hexdigest(),'Compressed core does not reproduce every original byte')
        os.replace(temporary,target)
        receipt=dict(status='full_original_core_losslessly_preserved_independent_decompression_verified',source=str(source),source_bytes=count,source_sha256=h.hexdigest(),archive=str(target),archive_bytes=target.stat().st_size,archive_sha256=digest(target),script_sha256=digest(__file__),source_removed=False)
        atomic(out/'manifest.json',receipt)
        require((source.stat().st_size,source.stat().st_mtime_ns)==(before.st_size,before.st_mtime_ns),'Source changed before release')
        source.unlink();receipt['source_removed']=True;atomic(out/'manifest.json',receipt)
        state.update(status='complete',stage='verified_lossless_archive_original_core_released');atomic(out/'state.json',state)
        print(receipt['status'],count,receipt['archive_bytes'])
    except BaseException as e:state.update(status='failed',error=str(e));atomic(out/'state.json',state);raise
if __name__=='__main__':main()
