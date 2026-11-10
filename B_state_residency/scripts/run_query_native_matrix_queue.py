"""One serial owner for the remaining seven cases, gated by the existing structural chain."""
from pathlib import Path
import json,shutil,subprocess,sys,time
from run_checkpoint_authority import ROOT,sha

p=Path(sys.argv[1]).resolve();pid=int(sys.argv[2]);base=p.parent
gate=base/'query_native_synth_followup_v1';proc=Path('/proc')/str(pid)
cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode()
assert 'continue_query_native_synth.py'in cmd and str(gate)in cmd
ticks=(proc/'stat').read_text().split(') ',1)[1].split()[19]
prepath=ROOT/'results/query_native_matrix_preflight_20261028.json'
pre=json.loads(prepath.read_text())
assert pre['builder_sha256']==sha(ROOT/'hardware/variants/query_native_matrix_v1/build.py')
order=['off_full','off_pressure','on_full','on_pressure','retry_cancel_full','retry_cancel_pressure','retry_crc_full']
cases=sorted(pre['cases'],key=lambda c:order.index(c['reference'].removeprefix('native_matrix_').removesuffix('_v1')))
assert len(cases)==7 and len({c['target']for c in cases})==7
for c in cases:assert not(base/c['target']).exists(),c['target']
anchorpath=ROOT/'results/query_native_matrix_crc_anchor_20261028.json'
anchor=json.loads(anchorpath.read_text());assert anchor['status']=='existing_crc_pressure_case_matched_to_original'
assert sha(Path(anchor['existing_run'])/'source_bound_audit.json')==anchor['existing_audit_sha256']
tool_names=['run_query_native_matrix_case.py','audit_query_native_matrix_case.py',
    'archive_offer_result.py','verify_search_retire_restore.py','release_experiment_cache.py']
p.mkdir();shutil.copyfile(Path(__file__),p/'runner.py');(p/'tools').mkdir()
for n in tool_names:shutil.copyfile(ROOT/'scripts'/n,p/'tools'/n)
variant=ROOT/'hardware/variants/query_native_matrix_v1'
extra=[variant/'build.py',variant/'CONTRACT.md',ROOT/'hardware/variants/query_native_system_v1/build.py']
extra += [variant/mode/n for mode in ['baseline','fixed']for n in ['query_lifecycle.sv','query_residency_system.sv']]
bound={}
for src in extra:
    rel=src.relative_to(ROOT);dst=p/'bound'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    bound[str(rel)]=sha(src);assert sha(dst)==bound[str(rel)]
m=dict(bound=bound,status='running',stage='wait_structural_chain',gate=str(gate),gate_pid=pid,gate_start_ticks=ticks,
    gate_cmdline=cmd,runner_sha256=sha(p/'runner.py'),preflight_sha256=sha(prepath),anchor_sha256=sha(anchorpath),
    tools={n:sha(p/'tools'/n)for n in tool_names},commands=[],cases=[],
    memory_admission_fraction=0.75,concurrent_behavioral_jobs=1,
    scope='Seven deterministic matched cases only after same-source CRC and zero-loop structural audits/restoration. One active simulation; clean-cache release only after case archive and actual restoration. 75% cgroup-memory launch threshold is admission control, not a hard cap on other jobs. No automatic retry or restart.')
def save():(p/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
def run(stage,script,args,timeout):
    assert sha(prepath)==m['preflight_sha256'],'preflight drift'
    for rel,h in bound.items():assert sha(ROOT/rel)==h==sha(p/'bound'/rel),('bound source drift',rel)
    assert sha(ROOT/'scripts'/script)==m['tools'][script],'tool source drift'
    m['stage']=stage;save();argv=[sys.executable,str(ROOT/'scripts'/script),*map(str,args)]
    print('START',stage,flush=True);start=time.monotonic()
    with(p/(stage+'.log')).open('w')as f:
        r=subprocess.run(argv,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
    m['commands'].append(dict(stage=stage,argv=argv,exit_code=r.returncode,elapsed_s=time.monotonic()-start,log_sha256=sha(p/(stage+'.log'))));save()
    assert r.returncode==0,stage
    print('DONE',stage,flush=True)
def admit_memory():
    m['stage']='wait_memory';save();deadline=time.monotonic()+3600
    while True:
        current=int(Path('/sys/fs/cgroup/memory.current').read_text())
        limit=int(Path('/sys/fs/cgroup/memory.max').read_text())
        if current*4<=limit*3:return dict(current_bytes=current,limit_bytes=limit)
        assert time.monotonic()<deadline,'memory admission timeout; no case submitted'
        time.sleep(10)
save()
try:
    print('WAIT_EXISTING_STRUCTURAL_CHAIN',pid,flush=True)
    deadline=time.monotonic()+7200;last_live=time.monotonic()
    while True:
        try:gm=json.loads((gate/'manifest.json').read_text())
        except json.JSONDecodeError:
            assert time.monotonic()<deadline;time.sleep(1);continue
        if gm['status']=='observed':
            assert gm['stage']=='complete';break
        assert gm['status']=='running',gm.get('error',gm['status'])
        if proc.exists():
            assert (proc/'stat').read_text().split(') ',1)[1].split()[19]==ticks
            last_live=time.monotonic()
        else:assert time.monotonic()-last_live<30,'gate owner exited without terminal manifest'
        assert time.monotonic()<deadline,'observer timeout; existing chain not stopped'
        time.sleep(10)
    struct=base/'query_native_synth_v1'
    sa=json.loads((struct/'source_bound_audit.json').read_text())
    srpath=ROOT/'results/query_native_synth_v1_restore_20261025.json';sr=json.loads(srpath.read_text())
    assert sa['status']==sr['status']=='passed'and sr['audit_byte_identical']
    assert sa['manifest_sha256']==sha(struct/'manifest.json')and sr['audit_sha256']==sha(struct/'source_bound_audit.json')
    assert not sa['timing_loop_warnings'],'automatic loop cuts require diagnosis'
    assert sa['check_timing_counts']['loops']==0,'remaining loops require main-model diagnosis; no matrix run submitted'
    m['structural_audit_sha256']=sha(struct/'source_bound_audit.json');m['structural_restore_sha256']=sha(srpath);save()
    for c in cases:
        target=base/c['target'];reference=base/c['reference'];name=c['target']
        assert not target.exists(),name
        memory=admit_memory()
        run(name+'_run','run_query_native_matrix_case.py',[target,reference],7500)
        run(name+'_audit','audit_query_native_matrix_case.py',[target],240)
        run(name+'_archive','archive_offer_result.py',[target],600)
        run(name+'_restore','verify_search_retire_restore.py',[name,'audit_query_native_matrix_case.py'],600)
        a=json.loads((target/'source_bound_audit.json').read_text())
        receipt=ROOT/'results'/f'{name}_restore_20261025.json';r=json.loads(receipt.read_text())
        assert a['status']==r['status']=='passed'and r['audit_byte_identical']
        assert r['audit_sha256']==sha(target/'source_bound_audit.json')and len(a['exact_comparisons'])==27
        run(name+'_cache','release_experiment_cache.py',[target,base/'.preserved'/name,'--apply'],180)
        m['cases'].append(dict(target=name,reference=c['reference'],case=c['case'],memory_admission=memory,
            audit_sha256=sha(target/'source_bound_audit.json'),restore_sha256=sha(receipt),archive_sha256=r['archive_sha256'],
            finish_time=a['finish_time'],backend_exclusion=a['backend_exclusion'],capture_retirement=a['capture_retirement'],query_interface_exclusion=a['query_interface_exclusion'],
            matched_files=len(a['exact_comparisons'])));save()
    assert len(m['cases'])==7
    out=ROOT/'results/query_native_matrix_20261028.json';assert not out.exists()
    out.write_text(json.dumps(dict(status='eight_behavioral_cases_passed',anchor=anchor,cases=m['cases'],
        total_case_file_comparisons=216,structural_audit_sha256=m['structural_audit_sha256'],
        structural_restore_sha256=m['structural_restore_sha256'],queue_runner_sha256=m['runner_sha256'],
        scope='Eight specific fixed-price reference cases; all native/AXI/final-memory bytes and cycles matched, with actual archive restoration. Not general equivalence, timing closure or board benefit.'),indent=2,sort_keys=True)+'\n')
    m.update(status='observed',stage='complete',result_sha256=sha(out))
except Exception as e:
    m.update(status='failed',error=repr(e));raise
finally:save()
print('QUERY_NATIVE_MATRIX_QUEUE_COMPLETED',flush=True)
