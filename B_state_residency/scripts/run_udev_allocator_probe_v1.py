"""Reproduce libudev/allocator interactions without invoking license or FPGA flows."""
from pathlib import Path
import hashlib
import json
import os
import resource
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
out = Path(sys.argv[1]).resolve()
out.mkdir()
source = ROOT/'hardware/tests/probe_udev_allocator_v1.c'
tcmalloc = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/lib/lnx64.o/libtcmalloc.so.4')
udev = Path('/lib/x86_64-linux-gnu/libudev.so.1')
assert not os.environ.get('LD_PRELOAD'), 'Preserve and diagnose inherited loader settings first'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
(out/source.name).write_bytes(source.read_bytes())
(out/'runner.py').write_bytes(Path(__file__).read_bytes())
command = ['gcc','-std=c11','-Wall','-Wextra','-Werror','-O2',str(out/source.name),'-ldl','-o',str(out/'probe')]
compile_result = subprocess.run(command, capture_output=True, text=True)
(out/'compile.log').write_text(compile_result.stdout+compile_result.stderr)
assert compile_result.returncode == 0
record = dict(status='running', compile_command=command, cases=[],
              source_sha256=sha(source), runner_sha256=sha(Path(__file__)), binary_sha256=sha(out/'probe'),
              libraries={str(p): dict(realpath=str(p.resolve()),sha256=sha(p)) for p in [udev,tcmalloc]},
              scope='Real libudev enumeration; no license API or host identifier spoofing; only subprocess loader environment changes.')

def no_core():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

for label, preload in [('system_allocator',''),('tcmalloc_deepbind',str(tcmalloc)),
                       ('tcmalloc_preloaded_udev',str(tcmalloc)+':'+str(udev))]:
    for repeat in range(2):
        env = os.environ.copy()
        if preload:
            env['LD_PRELOAD'] = preload
        r = subprocess.run([str(out/'probe')],cwd=out,env=env,capture_output=True,text=True,
                           timeout=60,preexec_fn=no_core)
        log = out/f'{label}_{repeat}.log'
        log.write_text(r.stdout+r.stderr)
        record['cases'].append(dict(label=label,repeat=repeat,exit_code=r.returncode,
                                    preload=preload,log=log.name,sha256=sha(log)))
        print(label,repeat,'exit',r.returncode,flush=True)
        print(r.stdout+r.stderr,flush=True)
        (out/'manifest.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
record['status'] = 'observed'
(out/'manifest.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
