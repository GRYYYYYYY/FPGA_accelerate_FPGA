"""Paired sampling-off/on diagnostics, same binary and full routing schedule."""
from datetime import datetime,timezone
import json,os,random,signal,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'adapters'),str(ROOT/'scripts')]
from prepare_real import sha
from profile_real import parse_log

def main():
    bd=ROOT/'build/resident_profile_v1';base=ROOT/'build/resident_zero_v1'
    build=json.loads((bd/'build.json').read_text());proof=json.loads((base/'semantic_tests.json').read_text())
    def bindings():
        for p,h in build['inputs'].items():
            if sha(p)!=h:raise ValueError('Input changed: '+p)
        if sha(bd/'router')!=build['binary_sha256'] or sha(bd/'router.cpp')!=build['source_sha256']:raise ValueError('Diagnostic build changed')
        original=(base/'router.cpp').read_text();region=original[original.index('    struct SparseLabels {'):original.index('    SparseLabels bSerialLabels;')]
        if region not in (bd/'router.cpp').read_text():raise ValueError('Core differs')
        if proof['status']!='passed' or proof['router_source_sha256']!=sha(base/'router.cpp') or proof['test_source_sha256']!=sha(ROOT/'tests/resident_zero_semantics.cpp') or proof['test_binary_sha256']!=sha(base/'test_labels') or proof['log_sha256']!=sha(base/'semantic_tests.log'):raise ValueError('Core proof mismatch')
    bindings()
    refp=ROOT/'results/research_chain_20261022T183749Z/matrix/manifest.json';ref=json.loads(refp.read_text())
    out=ROOT/'results'/('resident_profile_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'));out.mkdir()
    (out/'driver_snapshot.py').write_bytes(Path(__file__).read_bytes())
    cases=[(d,256 if d['id']=='logicnets_jscl' else 4096,interval) for d in ref['config']['datasets'] for interval in [0,1009]]
    random.Random(7821).shuffle(cases)
    record=dict(status='running',runner_pid=os.getpid(),build=build,core_proof=proof,reference_manifest_sha256=sha(refp),tool_sha256=sha(__file__),scope='CPU diagnostic, one off/on pair per design; requested 1009us sampling, actual delivery cadence may differ. No isolated latency inference.',planned_cases=[dict(dataset=d['id'],physical_pages=c,sample_us=i) for d,c,i in cases],runs=[])
    def save():
        tmp=out/'manifest.json.tmp';tmp.write_text(json.dumps(record,indent=2)+'\n');tmp.replace(out/'manifest.json')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('B_','RW_'))}
    try:
        for ds,c,interval in cases:
            if sha(ROOT/ds['input'])!=ds['input_sha256']:raise ValueError('Input changed')
            name=ds['id']+'_c'+str(c)+'_sample'+str(interval);pre=out/name
            env=dict(RW_MAX_THREADS='1',RW_PAR_PART='0',RW_PAR_ITER1='0',RW_OVERLAP='0',RW_BATCH_T='0',RW_GPU_FLOOD='0',RW_BATCH_PBITS='6',B_SERIAL_PAGED='1',B_RESIDENT_PAGES=str(c),B_LABEL_REPORT=str(pre.with_suffix('.labels.json')),B_SAMPLE_US=str(interval),B_PROFILE_PREFIX=str(pre)+'.profile')
            cmd=['/usr/bin/time','-v','-o',str(pre.with_suffix('.time')),'taskset','-c','8',str(bd/'router'),str(ROOT/ds['input']),str(pre.with_suffix('.result'))]
            row=dict(name=name,dataset=ds['id'],physical_pages=c,sample_us=interval,command=cmd,environment=env);record['runs'].append(row)
            with pre.with_suffix('.log').open('w') as log:
                proc=subprocess.Popen(cmd,env=dict(clean,**env),stdout=log,stderr=subprocess.STDOUT,start_new_session=True);row['pid']=proc.pid;save()
                try:proc.wait(timeout=1200)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid,signal.SIGTERM)
                    try:proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
                    raise RuntimeError('Diagnostic timeout')
            if proc.returncode:raise RuntimeError('Diagnostic router failed')
            m=parse_log(pre.with_suffix('.log').read_text());h=sha(pre.with_suffix('.result'));g=next(r for r in ref['runs'] if r['dataset']==ds['id'] and r['mode']=='serial')
            if h!=g['result_sha256'] or m['convergence']!=g['metrics']['convergence']:raise ValueError('Output/convergence changed')
            labels=json.loads(pre.with_suffix('.labels.json').read_text());profile=json.loads(Path(str(pre)+'.profile.json').read_text())
            if labels['contexts'][0]['physical_pages']!=c or profile['samples_dropped'] or (interval and profile['samples']==0) or (not interval and profile['samples']!=0):raise ValueError('Diagnostic not exercised')
            row.update(verified=True,exit_code=proc.returncode,result_sha256=h,metrics=m,labels=labels,profile=profile);save();print(name,m['route_ms'],profile['samples'],flush=True)
        bindings();record['status']='passed'
    except Exception as e:record.update(status='failed',error=repr(e));raise
    finally:save()
    print(out,flush=True)
if __name__=='__main__':main()
