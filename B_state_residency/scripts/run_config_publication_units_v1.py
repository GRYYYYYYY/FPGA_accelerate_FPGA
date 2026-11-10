"""Run five isolated comparison modes, only after the real host-edit pair exits."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import time
from config_publication_units_common_v1 import (ROOT,TARGET,VARIANT,CASES,sha,identity,
    host_pair_evidence,source_evidence,commands)


def main():
    p=Path(sys.argv[1]).resolve();assert p==TARGET and not p.exists()
    gates=host_pair_evidence()  # Refuse before creating a directory or child.
    prep,references,files=source_evidence()
    assert not os.environ.get('LD_PRELOAD'),'Use the verified inherited XSim environment'
    files+=list(map(Path,gates));p.mkdir();(p/'bound').mkdir()
    m=dict(status='running',stage='prepare',runner_pid=os.getpid(),runner_start_ticks=identity(os.getpid()),
        runner_sha256=sha(__file__),predecessors=gates,bound={},references=references,cases={},
        scope='Five verification modes on the same original stimuli; full4810-state/7238-output binary bits and exact event/cycle equality. Default generic and native compatibility, plus native enable only. No full-system equivalence, synthesis, physical timing or board claim.')
    for i,source in enumerate(dict.fromkeys(files)):
        name=f'{i:02d}_{source.name}';shutil.copyfile(source,p/'bound'/name)
        m['bound'][name]=dict(source=str(source),sha256=sha(source));assert sha(p/'bound'/name)==sha(source)
    for name in CASES:
        c=prep['cases'][name];d=p/name;d.mkdir();role='baseline' if name.endswith('_original') else 'fixed'
        shutil.copyfile(VARIANT/role/'config_restore_controller.sv',d/'config_restore_controller.sv')
        shutil.copyfile(c['testbench'],d/'tb.sv');(d/'run.tcl').write_text('run 100us\nquit\n')
        m['cases'][name]=dict(status='prepared',commands=[],top=c['top'],parameter=c['parameter'],
            dut_sha256=sha(d/'config_restore_controller.sv'),tb_sha256=sha(d/'tb.sv'),run_tcl_sha256=sha(d/'run.tcl'))

    def save():
        f=p/'manifest.pending.json';f.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');f.replace(p/'manifest.json')

    def validate():
        for name,e in m['bound'].items():assert sha(e['source'])==e['sha256']==sha(p/'bound'/name),name
        for name,c in m['cases'].items():
            for file,key in [('config_restore_controller.sv','dut_sha256'),('tb.sv','tb_sha256'),('run.tcl','run_tcl_sha256')]:
                assert sha(p/name/file)==c[key]

    save()
    try:
        for name in CASES:
            d=p/name;c=m['cases'][name];m['stage']=name+'_wait_memory';save()
            stable=None;deadline=time.monotonic()+10800
            while True:
                now=time.monotonic();cg=Path('/sys/fs/cgroup')
                current,limit=int((cg/'memory.current').read_text()),int((cg/'memory.max').read_text())
                stable=(now if stable is None else stable) if current*4<=limit*3 else None
                seconds=0 if stable is None else now-stable
                c['memory_admission']=dict(current_bytes=current,limit_bytes=limit,stable_seconds=seconds);save()
                if seconds>=60:break
                assert now<deadline,'Memory observation expired before solver launch'
                time.sleep(10)
            for stage,argv in commands(d,c['top']):
                validate();m['stage']=name+'_'+stage;save();start=time.monotonic()
                with (d/(stage+'.stdout.log')).open('w') as log:
                    child=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT)
                    ticks=identity(child.pid);m['active_process']=dict(case=name,stage=stage,pid=child.pid,start_ticks=ticks,argv=argv);save()
                    try:code=child.wait(timeout=600)
                    except subprocess.TimeoutExpired:
                        m.update(status='observation_timeout',error='Inspect and preserve the existing child; no restart or kill');save();raise
                m.pop('active_process',None)
                c['commands'].append(dict(stage=stage,argv=argv,pid=child.pid,start_ticks=ticks,exit_code=code,
                    elapsed_s=time.monotonic()-start,stdout_sha256=sha(d/(stage+'.stdout.log'))));save()
                assert code==0,(name,stage)
                print('PUBLICATION_UNITS',name,stage,'exit0',flush=True)
            log=(d/'simulate.log').read_text()
            marker='CONFIG_NATIVE_FEEDBACK_PASS' if name.startswith('native_') else 'CONFIG_PUBLICATION_PROBE_PASS'
            assert marker in log and '$finish called' in log and 'Fatal:' not in log and 'ERROR:' not in log
            c.update(status='observed',artifacts={n:sha(d/n) for n in ['events.txt','bank_trace.txt','simulate.log']});save()
        m.update(status='observed',stage='complete')
    except Exception as exc:
        if m['status']!='observation_timeout':m.update(status='failed',error=repr(exc))
        raise
    finally:save()
    print('PUBLICATION_UNITS_OBSERVED',p)


if __name__=='__main__':main()
