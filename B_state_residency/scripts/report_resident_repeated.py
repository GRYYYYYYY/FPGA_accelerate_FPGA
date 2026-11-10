"""Audit a completed repeated capacity experiment; refuse partial or mismatched evidence."""
import argparse
import hashlib
import json
from statistics import median
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
    require(d['status']=='passed' and len(d['runs'])==24 and d['repeats']==3 and d['capacities']==[64,256,4096] and d['page_bits']==6,'Pilot incomplete')
    refp=ROOT/'results/research_chain_20261022T183749Z/matrix/manifest.json'
    require(sha(refp)==d['reference_manifest_sha256'],'Reference changed')
    ref=json.loads(refp.read_text())
    require(sha(directory/'driver_snapshot.py')==d['tool_sha256'],'Driver snapshot changed')
    builds={'zero_bypass':ROOT/'build/resident_zero_v1'}
    for mode,bd in builds.items():
        b=d['builds'][mode];proof=d['semantic_tests'][mode]
        for p,h in b['inputs'].items():require(sha(p)==h,'Input changed: '+p)
        require(sha(bd/'router')==b['binary_sha256'] and sha(bd/'router.cpp')==b['source_sha256'],'Build changed')
        test=ROOT/('tests/resident_rw_semantics.cpp' if mode=='explicit_rw' else 'tests/resident_zero_semantics.cpp')
        require(proof['status']=='passed' and proof['router_source_sha256']==b['source_sha256'],'Proof binding mismatch')
        require(sha(test)==proof['test_source_sha256'] and sha(bd/'test_labels')==proof['test_binary_sha256'] and sha(bd/'semantic_tests.log')==proof['log_sha256'],'Native evidence changed')
    datasets={x['id']:x for x in ref['config']['datasets']}
    for ds in datasets.values():require(sha(ROOT/ds['input'])==ds['input_sha256'],'Dataset changed')
    original=ROOT/'build/real_trace'
    require(sha(original/'router_original')==d['original_build']['binary_sha256']==ref['original_binary_sha256'] and sha(original/'original.cpp')==d['original_build']['source_sha256'],'Original control changed')
    seen=set()
    for r in d['runs']:
        key=(r['dataset'],r['physical_pages'],r['repeat']);require(key not in seen,'Duplicate case');seen.add(key)
        prefix=directory/r['name'];g=next(x for x in ref['runs'] if x['dataset']==r['dataset'] and x['mode']=='serial')
        require(r['verified'] and r['exit_code']==0,'Run failed')
        require(sha(prefix.with_suffix('.result'))==r['result_sha256']==g['result_sha256'],'Output mismatch')
        require(parse_log(prefix.with_suffix('.log').read_text())==r['metrics'],'Log mismatch')
        require(r['metrics']['convergence']==g['metrics']['convergence'],'Convergence mismatch')
        if r['access_mode']=='original':
            require(r['labels'] is None and r['physical_pages']==0,'Original label contamination')
        else:
            require(r['access_mode']=='zero_bypass','Unknown variant')
            require(json.loads(prefix.with_suffix('.labels.json').read_text())==r['labels'],'Label mismatch')
            c=r['labels']['contexts'];require(len(c)==1 and c[0]['physical_pages']==r['physical_pages'] and c[0]['page_bits']==6 and c[0]['resident_payload_bytes']==r['physical_pages']*64*r['labels']['node_size'] and c[0]['zero_reads']>0,'Wrong resident configuration')
    require(seen=={(ds,c,rep) for ds in datasets for c in [0]+d['capacities'] for rep in range(1,4)},'Case coverage mismatch')
    planned=[(x['dataset'],x['physical_pages'],x['repeat']) for x in d['planned_cases']]
    require(planned==[(x['dataset'],x['physical_pages'],x['repeat']) for x in d['runs']],'Planned order mismatch')
    for r in d['runs']:
        env=r['environment'];is_original=r['access_mode']=='original'
        require(all(env[k]=='0' for k in ['RW_PAR_PART','RW_PAR_ITER1','RW_OVERLAP','RW_BATCH_T','RW_GPU_FLOOD']) and env['RW_MAX_THREADS']=='1','Schedule mismatch')
        if is_original: require(not any(k.startswith('B_') for k in env),'Original B environment contamination')
        else: require(env['B_SERIAL_PAGED']=='1' and env['B_RESIDENT_PAGES']==str(r['physical_pages']) and env['RW_BATCH_PBITS']=='6','Capacity environment mismatch')
        cmd=r['command'];require(cmd[cmd.index('taskset')+1:cmd.index('taskset')+3]==['-c','8'],'CPU mismatch')
        require(Path(cmd[-3])==(original/'router_original' if is_original else builds['zero_bypass']/'router') and Path(cmd[-2])==ROOT/datasets[r['dataset']]['input'],'Command mismatch')
    rows=[]
    for ds in sorted(datasets):
        for capacity in [0]+d['capacities']:
            group=sorted([r for r in d['runs'] if r['dataset']==ds and r['physical_pages']==capacity],key=lambda r:r['repeat'])
            values=[r['metrics']['route_ms'] for r in group]
            ratios=[r['metrics']['route_ms']/next(x['metrics']['route_ms'] for x in d['runs'] if x['dataset']==ds and x['physical_pages']==0 and x['repeat']==r['repeat']) for r in group]
            counters=None
            if capacity:
                counters=group[0]['labels']['contexts'][0]
                require(all(r['labels']['contexts'][0]==counters for r in group),'Repeated counters diverged')
            rows.append(dict(dataset=ds,physical_pages=capacity,route_ms=values,median_ms=median(values),min_ms=min(values),max_ms=max(values),same_block_original_ratios=ratios,median_original_ratio=median(ratios),counters=counters))
    return dict(status='passed',manifest_sha256=sha(directory/'manifest.json'),scope='Three repeats, synchronous CPU, same-block original control; no statistical significance or hardware speedup claim.',rows=rows)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('directory',type=Path);args=parser.parse_args()
    result=audit(args.directory)
    (args.directory/'completion_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
