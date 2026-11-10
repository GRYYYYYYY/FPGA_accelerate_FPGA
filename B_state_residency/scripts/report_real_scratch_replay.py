"""Audit terminal actual-scratch replay coverage, capacity and frozen evidence."""
import argparse
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha


def audit(directory):
    directory=Path(directory); manifest=directory/'manifest.json'; record=json.loads(manifest.read_text())
    if record['status']!='passed' or record['performance'] is not None:
        raise ValueError('Actual scratch replay incomplete')
    capture=ROOT/'results/real_field_values_20261023T024250Z'
    trace=json.loads((capture/'trace.audit.json').read_text())
    rows=[row for row in trace['queries'] if not record['pilot'] or row['count']<=100000]
    if set(record['selected_attempts'])!={row['attempt'] for row in rows}:raise ValueError('Selection mismatch')
    expected=(len(rows),sum(row['count'] for row in rows),sum(row['reads'] for row in rows),sum(row['writes'] for row in rows))
    totals=record['totals']
    if tuple(totals[key] for key in ('queries','accesses','reads','writes'))!=expected:raise ValueError('Coverage mismatch')
    if (totals['fences']!=totals['queries']+totals['checkpoints'] or totals['duplicate_acks']!=2*totals['fences']
            or totals['stale_completions']!=totals['late_writeback_probes'] or not totals['checkpoints']):
        raise ValueError('Finite lifecycle accounting mismatch or no checkpoint exercised')
    if record['backing_budget_bytes']!=30*(1<<20) or record['stride_bytes']!=1344 or record['physical_slots']!=4:
        raise ValueError('Unexpected capacity configuration')
    capacity=record['backing_budget_bytes']//record['stride_bytes']
    if capacity<max(row['unique_pages'] for row in rows) or totals['peak_backing_pages']>capacity:
        raise ValueError('Capacity mismatch')
    for path,digest in record['files'].items():
        if sha(path)!=digest:raise ValueError('Bound source/trace changed: '+path)
        if Path(path).suffix=='.py' and sha(directory/Path(path).name)!=digest:
            raise ValueError('Frozen replay source changed')
    return dict(status='passed',manifest_sha256=sha(manifest),pilot=record['pilot'],totals=totals,
                backing_page_capacity=capacity,capture_audit_sha256=sha(capture/'completion_audit.json'),
                scope='Actual scratch bits through finite closed transport and fixed raw byte pool. Driver executes per-access and raw final/checkpoint oracles; this audit checks frozen evidence, not an independent replay. No global-history/price computation, actual DMA/RTL, total-memory or performance claim.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('directory',type=Path);args=parser.parse_args()
    result=audit(args.directory)
    (args.directory/'completion_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
