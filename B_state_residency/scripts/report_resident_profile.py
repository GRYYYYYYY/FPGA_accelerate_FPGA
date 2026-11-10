"""Audit completed CPU sampling pairs, including profiler disturbance."""
import argparse,json
from pathlib import Path
from profile_real import parse_log
from report_resident_capacity import sha,require,ROOT

def audit(directory):
    p=Path(directory);d=json.loads((p/'manifest.json').read_text());require(d['status']=='passed' and len(d['runs'])==4,'Diagnostic incomplete')
    bd=ROOT/'build/resident_profile_v1';b=d['build'];base=ROOT/'build/resident_zero_v1';proof=d['core_proof']
    for f,h in b['inputs'].items():require(sha(f)==h,'Build input changed: '+f)
    require(sha(bd/'router')==b['binary_sha256'] and sha(bd/'router.cpp')==b['source_sha256'],'Build changed')
    source=(base/'router.cpp').read_text();region=source[source.index('    struct SparseLabels {'):source.index('    SparseLabels bSerialLabels;')]
    require(region in (bd/'router.cpp').read_text(),'Core changed')
    require(proof['status']=='passed' and proof['router_source_sha256']==sha(base/'router.cpp') and proof['test_source_sha256']==sha(ROOT/'tests/resident_zero_semantics.cpp') and proof['test_binary_sha256']==sha(base/'test_labels') and proof['log_sha256']==sha(base/'semantic_tests.log'),'Core proof changed')
    require(sha(p/'driver_snapshot.py')==d['tool_sha256'],'Driver changed')
    refp=ROOT/'results/research_chain_20261022T183749Z/matrix/manifest.json';require(sha(refp)==d['reference_manifest_sha256'],'Reference changed');ref=json.loads(refp.read_text());datasets={x['id']:x for x in ref['config']['datasets']}
    for ds in datasets.values():require(sha(ROOT/ds['input'])==ds['input_sha256'],'Dataset changed')
    seen=set()
    for r in d['runs']:
        key=(r['dataset'],r['sample_us']);require(key not in seen,'Duplicate case');seen.add(key)
        pre=p/r['name'];g=next(x for x in ref['runs'] if x['dataset']==r['dataset'] and x['mode']=='serial')
        require(r['verified'] and r['exit_code']==0 and sha(pre.with_suffix('.result'))==r['result_sha256']==g['result_sha256'],'Result mismatch')
        require(parse_log(pre.with_suffix('.log').read_text())==r['metrics'] and r['metrics']['convergence']==g['metrics']['convergence'],'Log mismatch')
        require(json.loads(pre.with_suffix('.labels.json').read_text())==r['labels'] and json.loads(Path(str(pre)+'.profile.json').read_text())==r['profile'],'Counters mismatch')
        c=256 if r['dataset']=='logicnets_jscl' else 4096;e=r['environment'];cmd=r['command']
        require(r['physical_pages']==c and e['B_RESIDENT_PAGES']==str(c) and e['B_SAMPLE_US']==str(r['sample_us']) and e['B_SERIAL_PAGED']=='1' and e['RW_BATCH_PBITS']=='6','Diagnostic parameters changed')
        require(e['RW_MAX_THREADS']=='1' and all(e[k]=='0' for k in ['RW_PAR_PART','RW_PAR_ITER1','RW_OVERLAP','RW_BATCH_T','RW_GPU_FLOOD']),'Schedule changed')
        require(cmd[cmd.index('taskset')+1:cmd.index('taskset')+3]==['-c','8'] and Path(cmd[-3])==bd/'router' and Path(cmd[-2])==ROOT/datasets[r['dataset']]['input'],'Command changed')
        profile=r['profile'];require(profile['samples_dropped']==0 and profile['sample_interval_requested_us']==r['sample_us'],'Sampling failed')
        if r['sample_us']:
            pcs=Path(str(pre)+'.profile.pcs');require(sum(1 for _ in pcs.open())==profile['samples'] and profile['samples']>0,'Samples mismatch')
        else:require(profile['samples']==0,'Off run sampled')
    require(seen=={(ds,i) for ds in datasets for i in [0,1009]},'Coverage mismatch')
    rows=[]
    for ds in sorted(datasets):
        off=next(r for r in d['runs'] if r['dataset']==ds and r['sample_us']==0);on=next(r for r in d['runs'] if r['dataset']==ds and r['sample_us']!=0)
        require(off['labels']==on['labels'],'Sampling changed label counters')
        rows.append(dict(dataset=ds,off_route_ms=off['metrics']['route_ms'],on_route_ms=on['metrics']['route_ms'],observed_on_vs_off_percent=100*(on['metrics']['route_ms']/off['metrics']['route_ms']-1),samples=on['profile']['samples'],scope='One pair; timing difference includes run variation and sampler overhead.'))
    return dict(status='passed',manifest_sha256=sha(p/'manifest.json'),rows=rows)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory',type=Path);args=p.parse_args();result=audit(args.directory);(args.directory/'completion_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
