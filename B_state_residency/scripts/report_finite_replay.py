"""Audit terminal finite-ID real-address replay evidence without rerunning it."""
import argparse,json
from pathlib import Path
from replay_finite_page_values import sha


def audit(directory):
    directory=Path(directory);p=directory/'manifest.json';record=json.loads(p.read_text())
    if record['status']!='passed':raise ValueError('Replay incomplete')
    expected={'interval_sample':(1113,2399968),'large_query_tail':(19,13751567)}
    if set(record['groups'])!=set(expected):raise ValueError('Missing/extra trace group')
    if record['performance'] is not None or record['physical_slots']!=4 or record['page_bits']!=6:
        raise ValueError('Unexpected replay scope')
    for name,(queries,accesses) in expected.items():
        r=record['groups'][name]
        if (r['queries'],r['accesses'])!=(queries,accesses):raise ValueError('Trace coverage mismatch')
        if r['fences']!=queries+r['checkpoints']:raise ValueError('Fence/checkpoint mismatch')
        if r['stale_completions_discarded']+r['boundary_probe_skips']!=queries:
            raise ValueError('Cancellation probe accounting mismatch')
        if not r['writebacks'] or not r['refills']:raise ValueError('IO path unused')
    if not record['groups']['large_query_tail']['checkpoints']:
        raise ValueError('Real large-query finite-ID checkpoint path unused')
    for file,digest in record['files'].items():
        path=Path(file)
        if sha(path)!=digest:raise ValueError('Bound source/trace changed: '+file)
        if path.suffix=='.py' and sha(directory/path.name)!=digest:raise ValueError('Snapshot changed')
    return dict(status='passed',manifest_sha256=sha(p),groups=record['groups'],scope='Bound complete selected real addresses, synthetic values; oracle checks executed by frozen driver, not an independent rerun; no hardware/performance claim.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory',type=Path);a=p.parse_args();result=audit(a.directory)
    (a.directory/'completion_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
