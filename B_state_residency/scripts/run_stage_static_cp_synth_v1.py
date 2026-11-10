"""Run prepared matched OOC; keep real Vivado children alive on observation timeout."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import time
from stage_static_cp_synth_common_v1 import (ROOT,TARGET,REFERENCE,BIN,sha,read,identity,
    evidence,runtime_environment,memory_admission,wait_preserving)


def main():
    p=Path(sys.argv[1]).resolve();assert p==TARGET
    m=read(p/'manifest.json');assert m['status']=='prepared'
    rm,ra,fm,fa,proof=evidence();assert m['stage_static_evidence']==proof
    for name,e in m['bound'].items():assert sha(e['source'])==e['sha256']==sha(p/'bound'/name)
    for name,h in m['sources'].items():assert sha(p/'sources'/name)==h
    assert (p/'synth.tcl').read_text()==(REFERENCE/'synth.tcl').read_text().replace(str(REFERENCE),str(p))
    assert sha(p/'synth.tcl')==m['tcl_sha256'] and sha(p/'clock.xdc')==m['xdc_sha256']
    assert m['rtl']==rm['rtl'] and m['parameters']==rm['parameters'] and m['part']==rm['part']
    env,runtime=runtime_environment();shutil.copyfile(Path(__file__),p/'runner.py')
    m.update(status='running',stage='wait_memory',runner_pid=__import__('os').getpid(),
        runner_start_ticks=identity(__import__('os').getpid()),runner_sha256=sha(p/'runner.py'),
        runtime=runtime,commands=[],execution='local_batch',
        fallback_reason='Existing MCP sessions unusable; local2022.2 source-matched batch and independently reopened diagnostics. Child-only original-library preload from actual restored runtime controls.')
    def save():
        temp=p/'manifest.pending.json';temp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');temp.replace(p/'manifest.json')
    def validate():
        for name,e in m['bound'].items():assert sha(e['source'])==e['sha256']==sha(p/'bound'/name)
        for name,h in m['sources'].items():assert sha(p/'sources'/name)==h
        assert sha(p/'synth.tcl')==m['tcl_sha256'] and sha(p/'clock.xdc')==m['xdc_sha256']
        assert runtime_environment()[1]==runtime
    save();start=time.monotonic()
    try:
        memory_admission(m,save)
        phases=[('version',[str(BIN),'-version'],60),
            ('synthesis',[str(BIN),'-mode','batch','-source',str(p/'synth.tcl'),'-log',str(p/'vivado.log'),'-journal',str(p/'vivado.jou')],7200)]
        for stage,argv,timeout in phases:
            validate();m['stage']=stage;save();stamp=time.monotonic();out=p/('version.stdout.log' if stage=='version' else 'stdout.log')
            with out.open('w') as log:
                child=subprocess.Popen(argv,cwd=p,env=env,stdout=log,stderr=subprocess.STDOUT)
                ticks=identity(child.pid);m['active_process']=dict(stage=stage,pid=child.pid,start_ticks=ticks,argv=argv);save()
                code=wait_preserving(child,timeout,m,save)
            m.pop('active_process',None);m['status']='running'
            m['commands'].append(dict(stage=stage,argv=argv,pid=child.pid,start_ticks=ticks,exit_code=code,
                elapsed_s=time.monotonic()-stamp,stdout_sha256=sha(out)));save();assert code==0,stage
            if stage=='version':assert 'Vivado v2022.2' in out.read_text()
            else:m.update(exit_code=code,command=argv)
            print('STAGE_STATIC_OOC',stage,'exit0',flush=True)
        log=(p/'vivado.log').read_text()
        assert 'RESTORE_SEED_OOC_DONE' in log and 'synth_design completed successfully' in log and 'VIVADO_VERSION 2022.2' in log
        assert not any(line.startswith('ERROR:') for line in log.splitlines())
        for name in ['utilization.rpt','timing_synth.rpt','check_timing.rpt','facts.txt','clocks.rpt','synth.dcp','synth.v']:
            assert (p/name).is_file() and (p/name).stat().st_size>0
        m.update(status='observed',stage='complete')
    except Exception as error:
        m.update(status='failed',error=repr(error));raise
    finally:m['elapsed_s']=time.monotonic()-start;save()
    print('STAGE_STATIC_CP_OOC_OBSERVED',p)


if __name__=='__main__':main()
