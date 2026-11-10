"""One serial CP matrix owner after recovered physical evidence and path analysis."""
from pathlib import Path
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from run_checkpoint_authority import ROOT, sha

p=Path(sys.argv[1]).resolve();base=p.parent
assert base==Path('/tmp/B_state_residency_offer_20261025') and p.name=='checkpoint_edit_matrix_queue_v1'
gate_path=base/'checkpoint_edit_route_recovery_followup_v1/manifest.json'
gate=json.loads(gate_path.read_text());assert gate['status'] in ['running','observed']
gate_pid=gate['runner_pid'];gate_ticks=gate['runner_start_ticks']
def live(pid,ticks):
    proc=Path('/proc',str(pid),'stat')
    return proc.exists() and proc.read_text().split(') ',1)[1].split()[19]==ticks
if gate['status']=='running':assert live(gate_pid,gate_ticks)
else:assert gate['stage']=='complete'
prepath=ROOT/'results/checkpoint_edit_matrix_preflight_20261030.json';pre=json.loads(prepath.read_text())
assert pre['status']=='seven_cases_source_bound_preflight_only' and len(pre['cases'])==7
assert pre['builder_sha256']==sha(ROOT/'hardware/variants/checkpoint_edit_matrix_v1/build.py')
for name,digest in pre['tools'].items():assert sha(ROOT/name)==digest
assert all(not (base/c['target']).exists() for c in pre['cases'])
assert not (ROOT/'results/checkpoint_edit_matrix_20261030.json').exists()
names=['scripts/run_checkpoint_edit_matrix_case_v1.py','scripts/audit_checkpoint_edit_matrix_case_v1.py',
       'scripts/prepare_checkpoint_edit_monitor.py','scripts/run_checkpoint_authority.py',
       'scripts/archive_offer_result.py','scripts/verify_search_retire_restore.py','scripts/restore_offer_result.py',
       'scripts/release_experiment_cache.py','scripts/freeze_checkpoint_edit_matrix_v1.py',
       'scripts/analyze_state_route_recovery_v1.py','scripts/freeze_state_route_recovery_analysis_v1.py',
       'hardware/variants/checkpoint_edit_matrix_v1/build.py','hardware/variants/checkpoint_edit_matrix_v1/CONTRACT.md',
       'hardware/variants/checkpoint_edit_system_v1/build.py','results/checkpoint_edit_matrix_preflight_20261030.json',
       'results/checkpoint_edit_synth_v1_restore_20261025.json','results/checkpoint_edit_system_crc_pressure_v1_restore_20261025.json']
names += ['hardware/variants/checkpoint_edit_exclusion_v1/'+mode+'/'+name
          for mode in ['baseline','fixed'] for name in ['query_lifecycle.sv','query_residency_system.sv']]
p.mkdir();shutil.copyfile(Path(__file__),p/'runner.py');bound={}
for name in names:
    src=ROOT/name;dest=p/'bound'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
    bound[name]=dict(source=str(src),sha256=sha(dest));assert sha(src)==bound[name]['sha256']
m=dict(status='running',stage='wait_physical_and_analysis',runner_pid=os.getpid(),
       runner_start_ticks=Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19],
       runner_sha256=sha(p/'runner.py'),gate_pid=gate_pid,gate_start_ticks=gate_ticks,bound=bound,cases=[],commands=[],
       memory_admission_fraction=0.75,memory_stable_seconds=60,concurrent_behavioral_jobs=1,
       scope='Run only seven prepared CP cases after the existing physical owner and main-model path-analysis freeze. '
             'One behavioral solver at a time; keep exact stimuli and comparisons. No runtime/tool repair, automatic retry, '
             'candidate selection, constraint change or stopping unrelated processes. Main model performs final matrix freeze.')
def save():
    temp=p/'manifest.pending.json';temp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');temp.replace(p/'manifest.json')
def check_bound():
    for name,entry in bound.items():assert sha(Path(entry['source']))==entry['sha256']==sha(p/'bound'/name),name
def run(stage,args,timeout):
    check_bound();m['stage']=stage;start=time.monotonic();argv=[sys.executable,'-B',*map(str,args)]
    print('START',stage,flush=True)
    with (p/(stage+'.log')).open('w') as handle:
        child=subprocess.Popen(argv,cwd=ROOT,stdout=handle,stderr=subprocess.STDOUT)
        m['active_process']=dict(pid=child.pid,argv=argv);save()
        try:code=child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            m.update(status='observation_timeout',error='Child may still be alive; inspect exact process, do not resubmit');save();raise
    m['commands'].append(dict(stage=stage,argv=argv,pid=child.pid,exit_code=code,
        elapsed_s=time.monotonic()-start,log_sha256=sha(p/(stage+'.log'))))
    m.pop('active_process',None);save();assert code==0,stage
    print('DONE',stage,flush=True)
def admit():
    m['stage']='wait_memory';stable_since=None;deadline=time.monotonic()+21600
    while True:
        c=Path('/sys/fs/cgroup');now=time.monotonic()
        used=int((c/'memory.current').read_text());limit=int((c/'memory.max').read_text())
        if used*4<=limit*3:
            if stable_since is None:stable_since=now
        else:stable_since=None
        stable=0 if stable_since is None else now-stable_since
        observation=dict(current_bytes=used,limit_bytes=limit,stable_seconds=stable,checked_unix_s=time.time())
        m['memory_observation']=observation;save()
        if stable>=60:return observation
        assert now<deadline,'Memory admission expired; no new case submitted'
        time.sleep(10)
def restored_case(root):
    a=json.loads((root/'source_bound_audit.json').read_text())
    rp=ROOT/'results'/f'{root.name}_restore_20261025.json';r=json.loads(rp.read_text())
    assert a['status']==r['status']=='passed' and r['audit_byte_identical']
    assert a['manifest_sha256']==sha(root/'manifest.json') and r['audit_sha256']==sha(root/'source_bound_audit.json')
    assert len(a['exact_comparisons'])==27
    return dict(target=root.name,audit_sha256=sha(root/'source_bound_audit.json'),restore_sha256=sha(rp),
        archive_sha256=r['archive_sha256'],finish_time=a['finish_time'],matched_files=27,
        checkpoint_edit_exclusion=a['checkpoint_edit_exclusion'],backend_exclusion=a['backend_exclusion'],
        capture_retirement=a['capture_retirement'],query_interface_exclusion=a['query_interface_exclusion'])
save()
try:
    print('WAIT_EXISTING_PHYSICAL_AND_MAIN_ANALYSIS',gate_pid,flush=True)
    deadline=time.monotonic()+21600;missing_since=None
    analysis=ROOT/'results/checkpoint_edit_route_recovery_timing_20261030.json'
    analysis_freeze=ROOT/'results/checkpoint_edit_route_recovery_timing_sources_20261030'
    while True:
        g=json.loads(gate_path.read_text());assert g['runner_pid']==gate_pid and g['runner_start_ticks']==gate_ticks
        if g['status']=='observed':
            assert g['stage']=='complete'
            if not live(gate_pid,gate_ticks) and analysis.exists() and (analysis_freeze/'manifest.json').exists():break
        else:
            assert g['status']=='running',g.get('error',g['status'])
            if live(gate_pid,gate_ticks):missing_since=None
            elif missing_since is None:missing_since=time.monotonic()
            else:assert time.monotonic()-missing_since<30,'Physical owner missing without successful terminal state'
        assert time.monotonic()<deadline,'Wait expired; physical process untouched and no matrix case submitted'
        time.sleep(10)
    check_bound()
    af=json.loads((analysis_freeze/'manifest.json').read_text());assert af['status']=='frozen'
    for name,entry in af['files'].items():assert sha(analysis_freeze/name)==entry['sha256']==sha(Path(entry['source']))
    ar=json.loads(analysis.read_text());assert ar['status']=='restored_route_recovery_path_navigation'
    assert ar['owner_manifest_sha256']==sha(gate_path)
    assert ar['analyzer_sha256']==sha(ROOT/'scripts/analyze_state_route_recovery_v1.py')
    m['physical_analysis_sha256']=sha(analysis);m['physical_analysis_freeze_sha256']=sha(analysis_freeze/'manifest.json')
    m['anchor']=restored_case(base/'checkpoint_edit_system_crc_pressure_v1');save()
    for c in pre['cases']:
        target=base/c['target'];reference=Path(c['reference']);assert not target.exists()
        memory=admit()
        run(target.name+'_run',['scripts/run_checkpoint_edit_matrix_case_v1.py',target,reference],24000)
        run(target.name+'_audit',['scripts/audit_checkpoint_edit_matrix_case_v1.py',target],600)
        run(target.name+'_archive',['scripts/archive_offer_result.py',target],1800)
        run(target.name+'_restore',['scripts/verify_search_retire_restore.py',target.name,'audit_checkpoint_edit_matrix_case_v1.py'],1800)
        evidence=restored_case(target);evidence.update(reference=reference.name,case=c['case'],memory_admission=memory)
        run(target.name+'_cache',['scripts/release_experiment_cache.py',target,base/'.preserved'/target.name,'--apply'],300)
        m['cases'].append(evidence);save()
    assert len(m['cases'])==7
    report=ROOT/'results/checkpoint_edit_matrix_20261030.json';assert not report.exists()
    report.write_text(json.dumps(dict(status='eight_cp_behavioral_cases_restored',anchor=m['anchor'],cases=m['cases'],
        total_case_file_comparisons=216,physical_analysis_sha256=m['physical_analysis_sha256'],
        queue_runner_sha256=m['runner_sha256'],timing_qualified=False,board_acceptance=False,
        scope='Only the frozen CP specialization and these eight fixed-price four-query cases; exact bytes/cycles '
              'and actual restored audits. Not path/stage matrices, arbitrary parameter equivalence, ordinary-edit '
              'nonempty coverage, physical closure or board acceleration.'),indent=2,sort_keys=True)+'\n')
    m.update(status='observed',stage='complete',result_sha256=sha(report))
except Exception as error:
    if m['status']!='observation_timeout':m.update(status='failed',error=repr(error))
    raise
finally:save()
print('CHECKPOINT_EDIT_MATRIX_QUEUE_COMPLETE',flush=True)
