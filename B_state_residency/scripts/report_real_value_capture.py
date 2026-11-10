"""Bind completed actual-value capture evidence and preserve unambiguous source snapshots."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha


def audit(directory):
    directory = Path(directory).resolve()
    manifest = directory/'manifest.json'
    record = json.loads(manifest.read_text())
    if record['status'] != 'passed' or record['route_equivalence'] != 'passed' or record['performance'] is not None:
        raise ValueError('Capture incomplete or wrong scope')
    if record['result_sha256'] != sha(directory/'trace.result') or record['result_sha256'] != '428fa84ffa9e9839965c5000a32a4078f2fc7ea3f787a50cd4f7aff57447aa84':
        raise ValueError('Full real route output changed')
    for path,digest in {**record['files'],**record['artifacts']}.items():
        if sha(path) != digest: raise ValueError('Bound artifact changed: '+path)
    trace = json.loads((directory/'trace.audit.json').read_text())
    if trace['status'] != 'passed' or trace['totals'] != record['trace_totals']:
        raise ValueError('Trace audit mismatch')
    if {row['attempt'] for row in trace['queries']} != set(record['selected_attempts']):
        raise ValueError('Query selection mismatch')
    if not trace['totals']['reads'] or not trace['totals']['writes']:
        raise ValueError('Missing operation kind')
    if record['native_audit']['status'] != 'passed' or record['native_audit']['totals']['queries'] != 2:
        raise ValueError('Native actual proxy test incomplete')
    snapshots = {}
    for path,digest in record['files'].items():
        source = Path(path)
        if source.suffix in ('.py','.hpp','.cpp'):
            # Several frozen builds use router.cpp; flat filenames are ambiguous.
            target = directory/'frozen_sources'/source.relative_to(ROOT)
            target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists(): target.write_bytes(source.read_bytes())
            if sha(target) != digest: raise ValueError('Frozen source snapshot mismatch')
            snapshots[str(target)] = digest
    return dict(status='passed',manifest_sha256=sha(manifest),totals=trace['totals'],snapshots=snapshots,
                scope='Complete real-route SHA and convergence gated actual field capture. Per-read oracle executed by frozen capture driver, not independently rerun here. Global hist observations are not a price-computation proof; no DMA/RTL/performance claim.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path); args = parser.parse_args()
    result = audit(args.directory)
    (args.directory/'completion_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:value for key,value in result.items() if key != 'snapshots'},indent=2))
