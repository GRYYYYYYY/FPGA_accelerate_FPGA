"""Continue the diagnosed runtime control with preserved baseline and unchanged real libraries."""
from pathlib import Path
import hashlib
import json
import os
import resource
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
out = Path(sys.argv[1]).resolve()
assert not os.environ.get('LD_PRELOAD')
old=out.parent/'udev_route_probe_v1'
previous=json.loads((old/'manifest.json').read_text())
assert previous['status']=='failed' and previous['stage']=='baseline'
assert not Path('/proc',str(previous['pid'])).exists()
assert len(previous['cases'])==1 and previous['cases'][0]['exit_code']==134
assert 'realloc(): invalid old size' in (old/'baseline/stdout.log').read_text()
crashes=list((old/'baseline').glob('hs_err_pid*.log')); assert len(crashes)==1
assert 'udev_enumerate_scan_devices' in crashes[0].read_text() and 'prepAndTransmitWebtalkData' in crashes[0].read_text()
assert not (old/'baseline/routed.dcp').exists()
out.mkdir()
shutil.copytree(old/'baseline',out/'baseline')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
tcl = ROOT/'hardware/scripts/probe_udev_route_v1.tcl'
fixture = ROOT/'hardware/tests/udev_route_probe_v1.v'
libs = [Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/lib/lnx64.o/libtcmalloc.so.4'),
        Path('/lib/x86_64-linux-gnu/libudev.so.1')]
(out/'runner.py').write_bytes(Path(__file__).read_bytes())
m = dict(status='running',stage='wait_memory',pid=os.getpid(),cases=previous['cases'].copy(),
         predecessor=str(old),predecessor_manifest_sha256=sha(old/'manifest.json'),
         baseline_files_sha256={str(f.relative_to(old/'baseline')):sha(f) for f in sorted((old/'baseline').rglob('*')) if f.is_file()},
         runner_sha256=sha(Path(__file__)),tcl_sha256=sha(tcl),fixture_sha256=sha(fixture),
         libraries={str(p):sha(p) for p in libs},
         scope='Tool runtime probe only; tiny independent fixture is not full-system equivalence or timing evidence.')
def save():
    tmp=out/'manifest.pending.json'
    tmp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
    tmp.replace(out/'manifest.json')
def admit():
    start=None; deadline=time.monotonic()+10800
    while True:
        c=Path('/sys/fs/cgroup'); now=time.monotonic()
        current=int((c/'memory.current').read_text()); limit=int((c/'memory.max').read_text())
        if current*4 <= limit*3:
            if start is None: start=now
        else: start=None
        stable=0 if start is None else now-start
        m['memory']=dict(current=current,limit=limit,stable_seconds=stable); save()
        if stable>=60: return
        assert now<deadline
        time.sleep(10)
def no_core():
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
save()
try:
    admit()
    for label, preload in [('preloaded_udev',':'.join(map(str,libs)))]:
        assert sha(tcl)==m['tcl_sha256'] and sha(fixture)==m['fixture_sha256']
        assert all(sha(p)==m['libraries'][str(p)] for p in libs)
        p=out/label; p.mkdir()
        (p/'run.tcl').write_bytes(tcl.read_bytes()); (p/'fixture.v').write_bytes(fixture.read_bytes())
        env=os.environ.copy()
        if preload: env['LD_PRELOAD']=preload
        argv=['/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin/vivado',
              '-mode','batch','-source',str(p/'run.tcl'),'-log',str(p/'vivado.log'),'-journal',str(p/'vivado.jou')]
        m['stage']=label; save(); print('START',label,flush=True)
        with (p/'stdout.log').open('w') as f:
            child=subprocess.Popen(argv,cwd=p,env=env,stdout=f,stderr=subprocess.STDOUT,preexec_fn=no_core)
            m['active_pid']=child.pid; save()
            code=child.wait(timeout=900)
        m.pop('active_pid',None)
        m['cases'].append(dict(label=label,exit_code=code,preload=preload,
                               stdout_sha256=sha(p/'stdout.log'),reopened=(p/'completed.txt').exists()))
        save(); print('DONE',label,code,flush=True)
        if label=='baseline':
            assert code in [0,134,-6], 'Unexpected baseline failure; diagnose before next case'
            if code!=0:
                assert 'realloc(): invalid pointer' in (p/'stdout.log').read_text()
        else:
            assert code==0 and (p/'completed.txt').read_text().strip()=='UDEV_ROUTE_PROBE_REOPENED'
    m.update(status='observed',stage='complete')
except Exception as e:
    m.update(status='failed',error=repr(e)); raise
finally:
    save()
