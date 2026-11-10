"""One diagnosed recovery, then independent checkpoint reopen. Never retry a failure."""
from pathlib import Path
import json
import os
import subprocess
import sys
import time
from run_checkpoint_authority import ROOT, sha

p=Path(sys.argv[1]).resolve(); m=json.loads((p/'manifest.json').read_text())
assert m['status']=='prepared' and not os.environ.get('LD_PRELOAD')
assert sha(Path(__file__))==m['runner_sha256']==sha(p/'tools/run_state_route_recovery_v1.py')
assert sha(ROOT/'scripts/prepare_state_route_recovery_v1.py')==m['preparer_sha256']
for name,digest in m['inputs'].items(): assert sha(p/name)==digest,name
assert sha(p/'run.tcl')==m['tcl_sha256'] and sha(p/'inspect.tcl')==m['inspect_tcl_sha256']
assert (p/'run.tcl').read_text()==(p/'tools/resume_state_route_v1.tcl').read_text().replace('@OUT@',str(p))
assert (p/'inspect.tcl').read_text()==(p/'tools/inspect_state_route_v1.tcl').read_text().replace('@OUT@',str(p))
for name,digest in m['runtime_library_sha256'].items(): assert sha(Path(name))==digest
(p/'runner.py').write_bytes(Path(__file__).read_bytes())
m.update(status='running',stage='wait_memory',runner_pid=os.getpid(),
         runner_start_ticks=Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19],commands=[])
def save():
    tmp=p/'manifest.pending.json'; tmp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n'); tmp.replace(p/'manifest.json')
def admit():
    start=None; deadline=time.monotonic()+10800
    while True:
        c=Path('/sys/fs/cgroup'); now=time.monotonic()
        current=int((c/'memory.current').read_text()); limit=int((c/'memory.max').read_text())
        if current*4<=limit*3:
            if start is None: start=now
        else: start=None
        stable=0 if start is None else now-start
        m['memory_observation']=dict(current_bytes=current,limit_bytes=limit,stable_seconds=stable,checked_unix_s=time.time()); save()
        if stable>=60: return
        assert now<deadline,'Memory admission expired; no new process started'
        time.sleep(10)
def run(stage,script,directory,timeout):
    for name,digest in m['runtime_library_sha256'].items(): assert sha(Path(name))==digest
    directory.mkdir(exist_ok=True)
    env=os.environ.copy(); env['LD_PRELOAD']=m['runtime_preload']
    argv=['/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin/vivado',
          '-mode','batch','-source',str(script),'-log',str(directory/'vivado.log'),'-journal',str(directory/'vivado.jou')]
    m['stage']=stage; start=time.monotonic(); print('START',stage,flush=True)
    with (directory/'stdout.log').open('w') as handle:
        child=subprocess.Popen(argv,cwd=p,env=env,stdout=handle,stderr=subprocess.STDOUT)
        m['active_process']=dict(pid=child.pid,argv=argv); save()
        try: code=child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            m.update(status='observation_timeout',error='Original Vivado may still be alive; do not resubmit or restore'); save(); raise
    m['commands'].append(dict(stage=stage,pid=child.pid,exit_code=code,elapsed_s=time.monotonic()-start))
    m.pop('active_process',None); save()
    assert code==0,(stage,code)
    assert not any(l.startswith('ERROR:') for l in (directory/'stdout.log').read_text().splitlines())
    print('DONE',stage,flush=True)
save(); start=time.monotonic()
try:
    admit()
    run('route',p/'run.tcl',p,14400)
    assert 'STATE_ROUTE_RECOVERY_DONE' in (p/'completed.txt').read_text()
    assert (p/'routed.dcp').stat().st_size>0
    m['routed_checkpoint_sha256_before_reopen']=sha(p/'routed.dcp'); save()
    m['stage']='wait_memory_before_reopen'; save(); admit()
    run('inspect',p/'inspect.tcl',p/'inspection',3600)
    assert 'STATE_ROUTE_RECOVERY_REOPENED' in (p/'inspection/stdout.log').read_text()
    assert sha(p/'routed.dcp')==m['routed_checkpoint_sha256_before_reopen']
    for name,digest in m['inputs'].items(): assert sha(p/name)==digest,name
    artifacts=['runtime_maps.txt','milestones.txt','completed.txt','routed.dcp','clocks_resume.rpt',
               'utilization_resume.rpt','timing_resume.rpt','constraints_resume.xdc',
               'route_status.rpt','utilization_routed.rpt','utilization_routed_hier.rpt','methodology_routed.rpt',
               'drc_routed.rpt','loops_routed.rpt','check_timing_routed.rpt','clocks_routed.rpt','timing_routed.rpt',
               'constraints_routed.xdc','internal_paths.tsv','stdout.log','vivado.log','vivado.jou']
    artifacts += ['inspection/'+name for name in ['route_status.rpt','utilization.rpt','timing.rpt','methodology.rpt',
                   'drc.rpt','check_timing.rpt','constraints.xdc','stdout.log','vivado.log','vivado.jou']]
    assert all((p/name).is_file() and (p/name).stat().st_size>0 for name in artifacts)
    m.update(status='observed',stage='complete',exit_code=0,artifact_sha256={name:sha(p/name) for name in artifacts})
except Exception as e:
    if m['status']!='observation_timeout': m.update(status='failed',error=repr(e))
    raise
finally:
    m['elapsed_s']=time.monotonic()-start; save()
