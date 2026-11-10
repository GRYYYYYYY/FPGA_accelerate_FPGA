"""Audit a completed resident push lease repeated experiment; refuse partial or mismatched evidence."""
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
    require(d['status']=='passed' and len(d['runs'])==12 and d['repeats']==3,'Pilot incomplete')
    refp=ROOT/'results/research_chain_20261022T183749Z/matrix/manifest.json'
    require(sha(refp)==d['reference_manifest_sha256'],'Reference changed')
    ref=json.loads(refp.read_text())
    require(sha(directory/'driver_snapshot.py')==d['tool_sha256'],'Driver snapshot changed')
    builds={'field_leases':ROOT/'build/resident_index_lru_v1','push_lease':ROOT/'build/resident_push_lease_v1'}
    for mode,bd in builds.items():
        b=d['builds'][mode];proof=d['semantic_tests'][mode]
        for p,h in b['inputs'].items():require(sha(p)==h,'Input changed: '+p)
        require(sha(bd/'router')==b['binary_sha256'] and sha(bd/'router.cpp')==b['source_sha256'],'Build changed')
        test=ROOT/('tests/resident_index_lru_semantics.cpp' if mode=='field_leases' else 'tests/resident_push_lease_semantics.cpp')
        require(proof['status']=='passed' and proof['router_source_sha256']==b['source_sha256'],'Proof binding mismatch')
        require(sha(test)==proof['test_source_sha256'] and sha(bd/'test_labels')==proof['test_binary_sha256'] and sha(bd/'semantic_tests.log')==proof['log_sha256'],'Native evidence changed')
    datasets={x['id']:x for x in ref['config']['datasets']}
    for ds in datasets.values():require(sha(ROOT/ds['input'])==ds['input_sha256'],'Dataset changed')
    seen=set()
    for r in d['runs']:
        key=(r['dataset'],r['access_mode'],r['repeat']);require(key not in seen,'Duplicate case');seen.add(key)
        prefix=directory/r['name'];g=next(x for x in ref['runs'] if x['dataset']==r['dataset'] and x['mode']=='serial')
        require(r['verified'] and r['exit_code']==0,'Run failed')
        require(sha(prefix.with_suffix('.result'))==r['result_sha256']==g['result_sha256'],'Output mismatch')
        require(parse_log(prefix.with_suffix('.log').read_text())==r['metrics'],'Log mismatch')
        require(r['metrics']['convergence']==g['metrics']['convergence'],'Convergence mismatch')
        require(json.loads(prefix.with_suffix('.labels.json').read_text())==r['labels'],'Label mismatch')
        c=r['labels']['contexts'];require(len(c)==1 and c[0]['physical_pages']==(256 if r['dataset']=='logicnets_jscl' else 4096) and c[0]['page_bits']==6 and c[0]['refills']>0,'Wrong resident configuration')
        require(c[0]['zero_reads']>0,'Bypass unused')
        env=r['environment'];cmd=r['command'];capacity=256 if r['dataset']=='logicnets_jscl' else 4096
        require(r['physical_pages']==capacity and env['B_RESIDENT_PAGES']==str(capacity) and env['RW_BATCH_PBITS']=='6' and env['B_SERIAL_PAGED']=='1','Capacity mismatch')
        require(env['RW_MAX_THREADS']=='1' and all(env[k]=='0' for k in ['RW_PAR_PART','RW_PAR_ITER1','RW_OVERLAP','RW_BATCH_T','RW_GPU_FLOOD']),'Schedule mismatch')
        require(cmd[cmd.index('taskset')+1:cmd.index('taskset')+3]==['-c','8'] and Path(cmd[-3])==builds[r['access_mode']]/'router' and Path(cmd[-2])==ROOT/datasets[r['dataset']]['input'],'Command mismatch')
    require(seen=={(ds,m,rep) for ds in datasets for m in builds for rep in range(1,4)},'Case coverage mismatch')
    require([(r['dataset'],r['access_mode'],r['repeat']) for r in d['runs']]==[(r['dataset'],r['access_mode'],r['repeat']) for r in d['planned_cases']],'Planned order mismatch')
    rows=[]
    for ds in sorted(datasets):
        group=[r for r in d['runs'] if r['dataset']==ds]
        require(all(r['labels']==group[0]['labels'] for r in group),'Repeated counters diverged')
        field=[next(r['metrics']['route_ms'] for r in group if r['access_mode']=='field_leases' and r['repeat']==rep) for rep in range(1,4)]
        push=[next(r['metrics']['route_ms'] for r in group if r['access_mode']=='push_lease' and r['repeat']==rep) for rep in range(1,4)]
        reductions=[100*(1-b/a) for a,b in zip(field,push)]
        rows.append(dict(dataset=ds,field_leases_ms=field,push_lease_ms=push,field_median_ms=median(field),push_median_ms=median(push),paired_reductions_percent=reductions,median_paired_reduction_percent=median(reductions),labels=group[0]['labels']))
    return dict(status='passed',manifest_sha256=sha(directory/'manifest.json'),scope='Three-repeat CPU scoped push lease pairs; no statistical significance or hardware speedup claim.',rows=rows)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('directory',type=Path);args=parser.parse_args()
    result=audit(args.directory)
    (args.directory/'completion_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
