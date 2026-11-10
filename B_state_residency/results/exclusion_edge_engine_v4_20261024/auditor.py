"""Check generated RTL lineage, original oracle, exact stimuli and all run receipts."""
from pathlib import Path
from collections import Counter
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
    out=ROOT/'results/exclusion_edge_engine_v4_20261024';m=read(out/'manifest.json')
    assert m['status']=='passed',m['status']
    for name,spec in m['sources'].items():assert sha(out/'sources'/name)==spec['sha256']==sha(Path(spec['path'])),name
    for path,digest in m['gates'].items():assert sha(Path(path))==digest,path
    ha=read(ROOT/'results/exclusion_hls_reset_20261024/source_bound_audit.json')
    la=read(ROOT/'results/exclusion_label_adapter_v2_20261024/source_bound_audit.json')
    ba=read(ROOT/'results/sparse_records_20261024/source_bound_audit.json')
    for gate,folder in [(ha,'exclusion_hls_reset_20261024'),(la,'exclusion_label_adapter_v2_20261024'),(ba,'sparse_records_20261024')]:
        assert gate['status']=='passed' and gate['manifest_sha256']==sha(ROOT/'results'/folder/'manifest.json')
    for bits in (32,3):
        for name,digest in ha['cases'][str(bits)]['generated_rtl_artifacts'].items():assert sha(out/'sources'/f'hls{bits}'/name)==digest
    assert sha(out/'sources/adapter/exclusion_label_adapter.sv')==sha(ROOT/'results/exclusion_label_adapter_v2_20261024/sources/exclusion_label_adapter.sv')
    original=ROOT/'results/frontier_real_20261024/original_trace.cpp';s=original.read_text()
    a=s.index('    bool isPartOfExistingRoute(int parent, int child) const {');b=s.index('    // ----------------------------------------------------------------- getChildren',a)
    assert (out/'sources/engine/original_functions.inc').read_text()==s[a:b]
    assert all(r['exit_code']==0 for r in m['commands']) and [r['stage'] for r in m['commands']]==['oracle_build','oracle_run']
    assert sha(out/'make_vectors')==m['oracle']['binary_sha256']
    assert sha(out/'vectors.txt')==m['oracle']['vectors_sha256']
    assert sha(out/'oracle_run.stdout.log')==m['oracle']['log_sha256']
    rows=[[int(v,16) for v in line.split()] for line in (out/'vectors.txt').read_text().splitlines()]
    assert len(rows)==m['oracle']['lines']==27680 and all(len(row)==19 for row in rows)
    assert all(row[0]==1 for row in rows[:27648]) and all(row[0]==0 for row in rows[27648:])
    seen=set();topologies=Counter();total_reads=0
    for row in rows:
        mode,parent,child,flags,created,lag,prev,cs,ps,decision,n=row[:11]
        assert parent<2**24 and child<2**24 and parent!=child and n<=4 and decision in (0,1)
        if mode:
            relation=0 if prev==0xffffffff else 1 if prev==parent else 2
            if relation==2:assert prev==child
            seen.add((flags,created,lag,relation,cs,ps))
            topologies['high' if child==0xffffff else 'same_page' if parent>>3==child>>3 else 'cross_page']+=1
        else:assert parent==28 and child==29 and prev==cs==ps==0
        for i in range(n):
            phase,node=row[11+i*2:13+i*2]
            assert 1<=phase<=4 and node==(parent if phase==3 else child)
        assert all(v==0 for v in row[11+n*2:])
        total_reads+=n
    assert len(seen)==27648 and topologies=={'same_page':9216,'cross_page':9216,'high':9216}
    assert total_reads==34898
    assert (out/'oracle_run.stdout.log').read_text()=='EDGE_VECTORS_PASS edges=27680 reads=34898\n'
    expected={
        'collector':'HLS_CALL_PASS permutations=720 coherent_calls=721 fault_cases=9',
        'engine32':'EDGE_ENGINE_PASS edges=27680 error_cases=13 checks=110686 label_requests=34911 native_reads=34906 hls_calls=62592 responses=34904',
        'engine3':'EDGE_GEN3_PASS accepted=14 exhausted=2 hls_calls=16',
    }
    assert set(m['cases'])==set(expected)
    for case,cm in m['cases'].items():
        assert cm['status']=='passed' and cm['result']==expected[case],cm
        assert [r['stage'] for r in cm['commands']]==['compile','elaborate','simulate'] and all(r['exit_code']==0 for r in cm['commands'])
        compile=cm['commands'][0]['argv'];assert compile[1]=='--sv'
        assert ('HLS_GEN3' in compile)==(case=='engine3')
        compiled={str(Path(arg).relative_to(out/'sources')) for arg in compile if arg.endswith(('.sv','.v'))}
        if case=='collector':assert compiled=={'engine/exclusion_hls_call.sv','engine/tb_exclusion_hls_call.sv'}
        else:
            bits='32' if case=='engine32' else '3'
            wanted={name for name in m['sources'] if name.startswith(('backend/','adapter/','hls'+bits+'/')) and name.endswith(('.sv','.v'))}
            wanted|={'engine/'+n for n in ['exclusion_hls_call.sv','exclusion_edge_controller.sv','exclusion_edge_engine.sv','tb_exclusion_edge_engine.sv']}
            assert compiled==wanted,(case,compiled^wanted)
        assert len(compiled)==sum(arg.endswith(('.sv','.v')) for arg in compile)
        sim=cm['commands'][2]['argv']
        assert ('--testplusarg' in sim)==(case=='engine32')
        if case=='engine32':assert sim[-1]=='fixture='+str(out/'vectors.txt')
        for name,digest in cm['artifacts'].items():assert sha(out/case/name)==digest
        for name in ['compile.stdout.log','elaborate.stdout.log','simulate.log']:
            log=(out/case/name).read_text();assert not re.search(r'^(ERROR:|Fatal:|Error:)',log,re.M)
        log=(out/case/'simulate.log').read_text();assert log.splitlines().count(expected[case])==1 and '$finish called' in log
    # v2 changes the timeout test, not the collector/controller/engine RTL.
    first=ROOT/'results/exclusion_edge_engine_20261024';fm=read(first/'manifest.json');assert fm['status']=='failed'
    for name in ['exclusion_edge_controller.sv','exclusion_edge_engine.sv']:
        assert sha(first/'sources/engine'/name)==sha(out/'sources/engine'/name)
    failure=(first/'collector/simulate.log').read_text()
    assert 'Fatal: collector fault not visible before sampling' in failure and 'Time: 166951 ns' in failure
    assert 'HLS_CALL_PASS ' not in failure
    reset_evidence={}
    for folder,negative in [('exclusion_reset_negative_20261024',True),('exclusion_reset_positive_20261024',False)]:
        d=ROOT/'results'/folder;rm=read(d/'manifest.json')
        assert rm['negative']==negative and rm['status']==('expected_failure_verified' if negative else 'passed')
        for name,spec in rm['sources'].items():assert sha(d/'sources'/name)==spec['sha256']==sha(Path(spec['path']))
        for name,digest in rm['artifacts'].items():assert sha(d/name)==digest
        assert all(r['exit_code']==0 for r in rm['commands'])
        log=(d/'simulate.log').read_text()
        assert ('Fatal: RESET_CONTRACT_FAIL expected_generation=1 actual_generation=2' in log) if negative else ('RESET_CONTRACT_PASS calls=4 resets=3' in log and 'Fatal:' not in log)
        reset_evidence[folder]={'manifest_sha256':sha(d/'manifest.json'),'log_sha256':sha(d/'simulate.log')}
    neg=ROOT/'results/exclusion_reset_negative_20261024';pos=ROOT/'results/exclusion_reset_positive_20261024'
    for name in ['exclusion_hls_call.sv','tb_reset_generation.sv']:assert sha(neg/'sources'/name)==sha(pos/'sources'/name)
    reset_failed=ROOT/'results/exclusion_edge_engine_v2_20261024'
    assert read(reset_failed/'manifest.json')['status']=='failed'
    assert 'Fatal: engine watchdog edge=27680' in (reset_failed/'engine32/simulate.log').read_text()
    reset_diagnosis=(reset_failed/'engine32/diagnose.log').read_text()
    assert 'STATE edges=27680' in reset_diagnosis and 'STATE errors_tested=5' in reset_diagnosis and 'STATE dut/controller/stopped=1' in reset_diagnosis
    prior=ROOT/'results/exclusion_edge_engine_v3_20261024'
    for name in ['tb_exclusion_hls_call.sv','tb_exclusion_edge_engine.sv','exclusion_edge_controller.sv','exclusion_edge_engine.sv']:
        assert sha(out/'sources/engine'/name)==sha(prior/'sources/engine'/name)
    fixed=(out/'sources/engine/exclusion_hls_call.sv').read_text()
    assert 'assign ap_start=!rst && !stopped && !abort && state==ACTIVE && !accepted;' in fixed
    assert 'assign ap_start=!rst && !fault' not in fixed
    (out/'auditor.py').write_bytes(Path(__file__).read_bytes())
    result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),
        'reset_evidence':reset_evidence,'reset_failure_manifest_sha256':sha(reset_failed/'manifest.json'),'reset_diagnosis_sha256':sha(reset_failed/'engine32/diagnose.log'),'cases':expected,'oracle_edges':len(rows),'oracle_reads':total_reads,'topologies':dict(topologies),
        'first_failure_manifest_sha256':sha(first/'manifest.json'),'first_failure_log_sha256':sha(first/'collector/simulate.log'),
        'diagnostic_wave_sha256':sha(first/'collector/debug.vcd'),'scope':m['scope']}
    (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
