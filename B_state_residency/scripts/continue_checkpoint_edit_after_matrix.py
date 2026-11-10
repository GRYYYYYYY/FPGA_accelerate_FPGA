"""Single owner for matrix freeze and subsequent native query tests; no retries."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import time
from run_checkpoint_authority import ROOT,sha

p=Path(sys.argv[1]).resolve();pid=int(sys.argv[2]);base=p.parent
gate=base/'query_native_matrix_queue_v1';target=base/'checkpoint_edit_units_v1'
proc=Path('/proc')/str(pid)
cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode()
assert 'run_query_native_matrix_queue.py' in cmd and str(gate) in cmd
ticks=(proc/'stat').read_text().split(') ',1)[1].split()[19]
assert not target.exists() and not (ROOT/'results/query_native_matrix_sources_20261028').exists()
p.mkdir();shutil.copyfile(Path(__file__),p/'runner.py')
paths=[ROOT/'scripts'/n for n in ['freeze_query_native_matrix.py','run_checkpoint_edit_units.py',
    'audit_checkpoint_edit_units.py','archive_offer_result.py','verify_search_retire_restore.py','run_checkpoint_authority.py']]
v=ROOT/'hardware/variants/checkpoint_edit_exclusion_v1'
paths += [v/'build.py',v/'build_tb.py',v/'manifest.json',v/'CONTRACT.md',ROOT/'hardware/variants/query_checkpoint_v1/tb_query_checkpoint.sv',ROOT/'hardware/variants/query_warm_rebase_v1/tb_rebase.sv']
paths += [ROOT/'scripts/analyze_checkpoint_edit_exclusion.py',ROOT/'scripts/freeze_checkpoint_edit_units.py']
paths += [v/mode/n for mode in ['baseline','fixed']for n in ['query_lifecycle.sv','query_residency_system.sv']]
bound={}
for src in paths:
    rel=src.relative_to(ROOT);dst=p/'bound'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    bound[str(rel)]=sha(src);assert sha(dst)==bound[str(rel)]
m=dict(status='running',stage='wait_existing_matrix',gate=str(gate),target=str(target),existing_pid=pid,
    existing_start_ticks=ticks,existing_cmdline=cmd,bound=bound,commands=[],runner_sha256=sha(p/'runner.py'),
    scope='Wait for existing matrix without restart; freeze completed matrix, run twelve checkpoint native tests, independently audit, archive, actually restore/re-audit. No parallel behavioral simulations, automatic repair or retry. Timeout does not stop existing matrix.')
def save(): (p/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
def run(stage,args,timeout):
    for rel,h in bound.items():assert sha(ROOT/rel)==h==sha(p/'bound'/rel),('source drift',rel)
    m['stage']=stage;save();argv=[sys.executable,*map(str,args)];start=time.monotonic()
    print('START',stage,flush=True)
    with (p/(stage+'.log')).open('w')as f: result=subprocess.run(argv,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
    m['commands'].append(dict(stage=stage,argv=argv,exit_code=result.returncode,elapsed_s=time.monotonic()-start,log_sha256=sha(p/(stage+'.log'))));save()
    assert result.returncode==0,stage
    print('DONE',stage,flush=True)
save()
try:
    deadline=time.monotonic()+10800;last_live=time.monotonic()
    print('WAIT_EXISTING_MATRIX',pid,flush=True)
    while True:
        try: gm=json.loads((gate/'manifest.json').read_text())
        except json.JSONDecodeError:
            assert time.monotonic()<deadline;time.sleep(1);continue
        if gm['status']=='observed':assert gm['stage']=='complete';break
        assert gm['status']=='running',gm.get('error',gm['status'])
        if proc.exists():
            assert (proc/'stat').read_text().split(') ',1)[1].split()[19]==ticks,'PID identity changed'
            last_live=time.monotonic()
        else:assert time.monotonic()-last_live<30,'matrix handle missing without terminal manifest; no restart'
        assert time.monotonic()<deadline,'observation timeout; existing matrix left untouched'
        time.sleep(10)
    run('freeze_matrix',['scripts/freeze_query_native_matrix.py'],300)
    m['stage']='wait_memory';save();deadline=time.monotonic()+3600
    while int(Path('/sys/fs/cgroup/memory.current').read_text())>int(Path('/sys/fs/cgroup/memory.max').read_text())*.75:
        assert time.monotonic()<deadline,'memory admission wait expired';time.sleep(10)
    run('native_tests',['scripts/run_checkpoint_edit_units.py',target],3600)
    run('native_audit',['scripts/audit_checkpoint_edit_units.py',target],180)
    run('native_archive',['scripts/archive_offer_result.py',target],600)
    run('native_restore',['scripts/verify_search_retire_restore.py',target.name,'audit_checkpoint_edit_units.py'],600)
    run('native_freeze',['scripts/freeze_checkpoint_edit_units.py'],180)
    m.update(status='observed',stage='complete')
except Exception as e:
    m.update(status='failed',error=repr(e));raise
finally: save()
print('CHECKPOINT_EDIT_FOLLOWUP_COMPLETE',flush=True)
