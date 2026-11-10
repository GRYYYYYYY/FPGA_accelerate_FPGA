#!/usr/bin/env python3
"""Independently compare host readback files with frozen adjacency fixtures.

This validates readback content and measurement accounting. Hardware provenance
must additionally be bound by the launcher receipt; this alone is not proof of
physical board execution.
"""
import argparse
from array import array
import json
import math
from pathlib import Path
import struct
import sys
from check_vitis_kernel import digest,require

RESULT_WORDS=196608
OUTPUT_WORDS=1048576
SENTINEL=0xdecafbad

def words(data):
    require(len(data)%4==0,'Misaligned word stream')
    result=array('I');result.frombytes(data)
    if sys.byteorder!='little':result.byteswap()
    require(result.itemsize==4,'Unsupported native word size')
    return result

def check_raw(raw,fixture):
    data=words(Path(fixture).read_bytes());require(len(data)>=4,'Short fixture')
    n,capacity,written,failed=data[:4]
    require(0<n<=65536 and capacity<=OUTPUT_WORDS and written<=capacity//8 and failed<=n,'Invalid fixture header')
    require(len(data)==4+4*n+8*written,'Fixture length mismatch')
    got=words(Path(raw).read_bytes())
    require(len(got)==4+RESULT_WORDS+OUTPUT_WORDS,'Incomplete or extra readback words')
    require(list(got[:4])==[written,failed,n,capacity],'Readback header mismatch')
    result=got[4:4+RESULT_WORDS];output=got[4+RESULT_WORDS:]
    require(result[:3*n]==data[4+n:4+4*n],'Status/start/degree mismatch')
    require(output[:8*written]==data[4+4*n:],'Edge identity/direction/attributes mismatch')
    require(all(x==SENTINEL for x in result[3*n:]),'Result tail overwritten')
    require(all(x==SENTINEL for x in output[8*written:]),'Output tail overwritten')
    return {'requests':n,'records':written,'expected_failed_requests':failed}

def audit(directory,manifest,repetitions,mode,memory):
    directory=Path(directory);manifest=Path(manifest)
    require(mode in ('csr','compact') and memory in ('DDR[0]','HBM[0]') and 0<repetitions<=100,'Invalid run parameters')
    entries=[line.split() for line in manifest.read_text().splitlines()]
    require(entries and all(len(e)==3 for e in entries),'Malformed manifest')
    require(len({tuple(e[:2]) for e in entries})==1,'Resident inputs changed')
    summary=json.loads((directory/'summary.json').read_text())
    require(summary['status']=='hardware_batches_readback_verified','Host not complete')
    require(summary['mode']==mode and summary['memory']==memory,'Mode/memory differs')
    require(summary['repetitions']==repetitions and summary['cases_per_repeat']==len(entries),'Repetition count differs')
    count=len(entries)*repetitions;require(summary['completed_batches']==count,'Missing batches')
    require(len(summary['argument_memory_groups'])==6 and all(isinstance(x,int) and x>=0 for x in summary['argument_memory_groups']),'Missing physical mapping record')
    require(all(summary.get(k) for k in ('device_bdf','device_name','xclbin_uuid')),'Device identity missing')
    rows=[json.loads(line) for line in (directory/'batches.jsonl').read_text().splitlines()]
    require(len(rows)==count,'Missing or extra batch measurements')
    require({p.name for p in directory.glob('batch_*.bin')}=={f'batch_{i}.bin' for i in range(count)},'Raw batch set differs')
    hashes={str(manifest.resolve()):digest(manifest)};validated=[]
    timing=['fixture_load_ms','batch_h2d_ms','kernel_wall_ms','d2h_ms','validation_ms','export_ms']
    for i,row in enumerate(rows):
        require((row['repeat'],row['case'])==divmod(i,len(entries)),'Reordered/duplicated measurement')
        raw=directory/f'batch_{i}.bin';fixture=Path(entries[i%len(entries)][2]);result=check_raw(raw,fixture)
        require(row['written']==result['records'] and row['failed']==result['expected_failed_requests'],'Measurement counts differ from raw')
        for key in timing+['batch_wall_ms']:
            require(isinstance(row[key],(int,float)) and math.isfinite(row[key]) and row[key]>=0,'Invalid timing')
        require(sum(row[k] for k in timing)<=row['batch_wall_ms']+1e-6,'Batch phases exceed wall time')
        hashes[str(raw.resolve())]=digest(raw);hashes[str(fixture.resolve())]=digest(fixture)
        validated.append(result)
    prepare=['input_preflight_ms','device_open_load_ms','allocation_ms','graph_h2d_ms']
    for key in prepare+['application_wall_ms']:
        require(isinstance(summary[key],(int,float)) and math.isfinite(summary[key]) and summary[key]>=0,'Invalid application time')
    require(sum(summary[k] for k in prepare)+sum(r['batch_wall_ms'] for r in rows)<=summary['application_wall_ms']+1e-6,'Application accounting does not close')
    for p in [directory/'summary.json',directory/'batches.jsonl',Path(__file__)]+[Path(x) for x in entries[0][:2]]:
        hashes[str(p.resolve())]=digest(p)
    return {'status':'verified_readback_content_and_timing','batches':validated,'mode':mode,'memory':memory,
        'summary':summary,'artifacts':hashes,'limitations':['Content evidence alone does not establish physical board execution; bind launcher, host, xclbin and link receipt.',
            'Kernel launch wall includes XRT overhead; application includes guard transfers, validation and raw export.',
            'Adjacency batches only; not full-router or power evidence.']}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['directory','manifest','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--repetitions',type=int,required=True);p.add_argument('--mode',choices=['csr','compact'],required=True)
    p.add_argument('--memory',choices=['DDR[0]','HBM[0]'],required=True);a=p.parse_args()
    report=audit(a.directory,a.manifest,a.repetitions,a.mode,a.memory)
    with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'status':report['status'],'batches':len(report['batches'])}))

if __name__=='__main__':main()
