"""Run the port-only export-after-reset probe against the restored CP RTL."""
from pathlib import Path
import json
import os
import shutil
import subprocess
from host_edit_system_common_v1 import ROOT, BASE, sha, read, restored, identity
from config_native_publication_synth_common_v1 import BIN, memory_admission, wait_preserving


def main():
    variant = ROOT/'hardware/variants/stage_static_cp_v1'
    vm = read(variant/'manifest.json')
    for path,digest in vm['bound'].items(): assert sha(path)==digest
    rtl = variant/'fixed.sv'
    assert sha(rtl)==vm['fixed_sha256']
    tb = ROOT/'hardware/tests/tb_stage_export_static_cp_v1.sv'
    prep = ROOT/'results/stage_export_static_cp_rtl_preparation_20261030.json'
    assert read(prep)['tb_sha256'] == sha(tb)
    p = BASE/'stage_export_static_cp_rtl_v1'
    assert not p.exists() and not os.environ.get('LD_PRELOAD')
    p.mkdir()
    shutil.copyfile(rtl, p/'controller.sv'); shutil.copyfile(tb, p/'tb.sv')
    (p/'run.tcl').write_text('run all\nquit\n')
    m = dict(status='running', stage='wait_memory', runner_pid=os.getpid(),
        runner_start_ticks=identity(os.getpid()), runner_sha256=sha(Path(__file__)),
        sources={n:sha(p/n) for n in ['controller.sv','tb.sv','run.tcl']}, commands=[])
    def save():
        tmp = p/'manifest.pending.json'; tmp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n'); tmp.replace(p/'manifest.json')
    save()
    try:
        memory_admission(m, save)
        phases = [('compile', [str(BIN.parent/'xvlog'), '--sv', 'controller.sv', 'tb.sv']),
                  ('elaborate', [str(BIN.parent/'xelab'), 'tb_stage_export_after_reset', '-s', 'probe', '--mt', '2']),
                  ('simulate', [str(BIN.parent/'xsim'), 'probe', '-tclbatch', 'run.tcl'])]
        for stage, argv in phases:
            for n,h in m['sources'].items(): assert sha(p/n)==h
            m['stage']=stage;save()
            with (p/(stage+'.stdout.log')).open('w') as log:
                child=subprocess.Popen(argv,cwd=p,stdout=log,stderr=subprocess.STDOUT)
                m['active_process']=dict(pid=child.pid,start_ticks=identity(child.pid));save()
                code=wait_preserving(child,600,m,save)
            m.pop('active_process',None);m['commands'].append(dict(stage=stage,argv=argv,exit_code=code));save()
            assert code==0,stage
        log=(p/'simulate.stdout.log').read_text()
        assert 'STAGE_EXPORT_AFTER_RESET_PASS imports=30 exports=30' in log
        assert 'Fatal:' not in log
        m.update(status='observed',stage='complete',exit_code=0)
    except Exception as error:
        m.update(status='failed',error=repr(error));raise
    finally:save()
    print('STAGE_EXPORT_RESET_RTL_OBSERVED')


if __name__ == '__main__': main()
