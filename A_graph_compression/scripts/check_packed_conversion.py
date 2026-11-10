#!/usr/bin/env python3
"""Independently recheck conversion outputs, trial order and cost summaries."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import struct
from real_experiment import write_new


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('experiment',type=Path);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--partial',action='store_true');a=p.parse_args();root=a.experiment
    plan=json.loads((root/'plan.json').read_text());jobs=[];rng=random.Random(plan['seed'])
    for repeat in range(7):
        block=[{'mode':mode,'repeat':repeat} for mode in ('csr','compact')];rng.shuffle(block);jobs.extend(block)
    if plan['jobs']!=jobs:raise ValueError('Formal paired conversion design differs')
    for path,value in plan['files'].items():
        if digest(path)!=value:raise ValueError('Frozen conversion input/code changed')
    records=[];artifacts={str(root/'plan.json'):digest(root/'plan.json')}
    for index,job in enumerate(jobs):
        prefix=root/f'worker_{index:03d}';record_path=prefix.with_suffix('.json');receipt_path=prefix.with_suffix('.receipt.json')
        if a.partial and not receipt_path.exists():continue
        r=json.loads(record_path.read_text());receipt=json.loads(receipt_path.read_text());image=prefix.with_suffix('.agr')
        submission=json.loads(prefix.with_suffix('.submission.json').read_text())
        if r['condition']!=job or r['status']!='byte_identical_to_verified_image' or receipt['exit_code']:
            raise ValueError('Worker failed or condition differs')
        expected=digest(image)
        if expected!=r['output_sha256'] or expected!=plan['expected_image_sha256'][job['mode']]:raise ValueError('Output image changed')
        if digest(prefix.with_suffix('.log'))!=receipt['log_sha256']:raise ValueError('Worker log changed')
        if submission['cpu']!=plan['cpu'] or submission['owner_pid']!=plan['owner_pid']:raise ValueError('Execution owner/affinity differs')
        command=submission['command']
        if command[-4:]!=['--output',str(root.resolve()),'--worker',str(index)] or not command[2].endswith('/scripts/packed_conversion_benchmark.py'):
            raise ValueError('Executed conversion command differs')
        if r['layout']['file_bytes']!=image.stat().st_size or r['layout']['mode']!=job['mode']:raise ValueError('Output layout differs')
        with image.open('rb') as f:
            magic,version,mode,endian,count=struct.unpack('<8sIIII',f.read(24))
            if magic!=b'AGRAPH01' or version!=1 or mode!=int(job['mode']=='compact') or endian!=0x01020304:raise ValueError('Image header differs')
            sections={}
            for _ in range(count):
                name,offset,size,n,width=struct.unpack('<16sQQII',f.read(40));sections[name.rstrip(b'\0').decode()]={'offset':offset,'bytes':size,'count':n,'record_bytes':width}
        if sections!=r['layout']['sections']:raise ValueError('Reported binary sections differ')
        for name,section in [('nodes','NODE'),('roots','ROOT'),('aliases','ALIAS')]:
            if r['graph_counts'][name]!=sections[section]['count']:raise ValueError('Graph scope differs')
        metrics=['read_export_ms','bank_load_ms','serialize_ms','conversion_ms','validation_ms','peak_child_kib']
        if any(not math.isfinite(r[k]) or r[k]<0 for k in metrics) or r['peak_child_kib']==0:raise ValueError('Invalid metrics')
        phases=sum(r[k] for k in ('read_export_ms','bank_load_ms','serialize_ms'))
        if r['conversion_ms']+0.001<phases:raise ValueError('Conversion phases do not close')
        if not math.isfinite(receipt['process_wall_ms']) or receipt['process_wall_ms']+2<r['conversion_ms']+r['validation_ms']:
            raise ValueError('Process wall excludes measured work')
        records.append((r,receipt))
        for suffix in ('.json','.receipt.json','.submission.json','.agr','.log'):artifacts[str(prefix.with_suffix(suffix))]=digest(prefix.with_suffix(suffix))
    if not records:raise ValueError('No finished conversions')
    summaries={}
    for mode in ('csr','compact'):
        selected=[(r,t) for r,t in records if r['condition']['mode']==mode]
        if not selected:continue
        summaries[mode]={'n':len(selected),**{k:statistics.median(r[k] for r,t in selected) for k in metrics},
                         'process_wall_ms':statistics.median(t['process_wall_ms'] for r,t in selected)}
    if not a.partial:
        report=json.loads((root/'report.json').read_text())
        if report['status']!='all_regenerated_images_byte_identical' or report['workers']!=14 or report['plan_sha256']!=digest(root/'plan.json') or report['summary_medians']!=summaries:
            raise ValueError('Final aggregate differs')
        expected={f'worker_{i:03d}.json':digest(root/f'worker_{i:03d}.json') for i in range(14)}
        if report['worker_sha256']!=expected:raise ValueError('Worker set differs')
        artifacts[str(root/'report.json')]=digest(root/'report.json')
    result={'status':'partial_conversion_workers_audited' if a.partial else 'complete_conversion_matrix_independently_audited',
            'completed_workers':len(records),'planned_workers':14,'summary_medians':summaries,'artifacts':artifacts,
            'auditor_sha256':digest(Path(__file__)),'limitations':plan['limitations']}
    write_new(a.output,result);print(json.dumps({'status':result['status'],'workers':len(records),'summary_medians':summaries}))


if __name__=='__main__':main()
