"""Audit a completed read-zero pilot; refuse partial or mismatched evidence."""
import argparse
import hashlib
import json
from pathlib import Path
from profile_real import parse_log

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()

def require(ok,message):
    if not ok: raise ValueError(message)

def audit(directory):
    directory=Path(directory).resolve()
    d=json.loads((directory/'manifest.json').read_text())
    require(d['status']=='passed' and len(d['runs'])==4,'Pilot incomplete')
    refp=ROOT/'results/research_chain_20261022T183749Z/matrix/manifest.json'
    require(sha(refp)==d['reference_manifest_sha256'],'Reference changed')
    ref=json.loads(refp.read_text())
    require(sha(directory/'driver_snapshot.py')==d['tool_sha256'],'Driver snapshot changed')
    builds={'explicit_rw':ROOT/'build/resident_rw_v2','zero_bypass':ROOT/'build/resident_zero_v1'}
    for mode,bd in builds.items():
        b=d['builds'][mode];proof=d['semantic_tests'][mode]
        for p,h in b['inputs'].items():require(sha(p)==h,'Input changed: '+p)
        require(sha(bd/'router')==b['binary_sha256'] and sha(bd/'router.cpp')==b['source_sha256'],'Build changed')
        test=ROOT/('tests/resident_rw_semantics.cpp' if mode=='explicit_rw' else 'tests/resident_zero_semantics.cpp')
        require(proof['status']=='passed' and proof['router_source_sha256']==b['source_sha256'],'Proof binding mismatch')
        require(sha(test)==proof['test_source_sha256'] and sha(bd/'test_labels')==proof['test_binary_sha256'] and sha(bd/'semantic_tests.log')==proof['log_sha256'],'Native evidence changed')
    datasets={x['id']:x for x in ref['config']['datasets']}
    for ds in datasets.values():require(sha(ROOT/ds['input'])==ds['input_sha256'],'Dataset changed')
    seen=set()
    for r in d['runs']:
        key=(r['dataset'],r['access_mode']);require(key not in seen,'Duplicate case');seen.add(key)
        prefix=directory/r['name'];g=next(x for x in ref['runs'] if x['dataset']==r['dataset'] and x['mode']=='serial')
        require(r['verified'] and r['exit_code']==0,'Run failed')
        require(sha(prefix.with_suffix('.result'))==r['result_sha256']==g['result_sha256'],'Output mismatch')
        require(parse_log(prefix.with_suffix('.log').read_text())==r['metrics'],'Log mismatch')
        require(r['metrics']['convergence']==g['metrics']['convergence'],'Convergence mismatch')
        require(json.loads(prefix.with_suffix('.labels.json').read_text())==r['labels'],'Label mismatch')
        c=r['labels']['contexts'];require(len(c)==1 and c[0]['physical_pages']==64 and c[0]['page_bits']==6 and c[0]['refills']>0,'Wrong resident configuration')
        if r['access_mode']=='zero_bypass': require(c[0]['zero_reads']>0,'Bypass unused')
    require(seen=={(ds,m) for ds in datasets for m in builds},'Case coverage mismatch')
    rows=[]
    for ds in sorted(datasets):
        a=next(r for r in d['runs'] if r['dataset']==ds and r['access_mode']=='explicit_rw')
        b=next(r for r in d['runs'] if r['dataset']==ds and r['access_mode']=='zero_bypass')
        rows.append(dict(dataset=ds,explicit_rw_ms=a['metrics']['route_ms'],zero_bypass_ms=b['metrics']['route_ms'],time_reduction_percent=100*(1-b['metrics']['route_ms']/a['metrics']['route_ms']),explicit_rw_counters=a['labels']['contexts'][0],zero_bypass_counters=b['labels']['contexts'][0]))
    return dict(status='passed',manifest_sha256=sha(directory/'manifest.json'),scope='Single-repeat synchronous CPU paired discovery; no hardware speedup claim.',rows=rows)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('directory',type=Path);args=parser.parse_args()
    result=audit(args.directory)
    (args.directory/'completion_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
