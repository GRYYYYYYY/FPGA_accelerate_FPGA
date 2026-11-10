"""Same delayed port stimulus on original RTL and standalone functional netlist."""
from pathlib import Path
import json
import os
import shutil
import subprocess
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity
from config_native_publication_synth_common_v1 import BIN,memory_admission,wait_preserving


def main():
    ref=BASE/'stage_export_reset_synth_v1';sm=read(ref/'manifest.json')
    assert sm['status']=='observed' and sm['stage']=='complete' and sm['exit_code']==0
    assert identity(sm['runner_pid'])!=str(sm['runner_start_ticks']) and not sm.get('active_process')
    for n,h in {**sm['sources'],**sm['artifact_sha256']}.items():assert sha(ref/n)==h
    tb=ROOT/'hardware/tests/tb_stage_export_after_reset_v3.sv'
    old=(ROOT/'hardware/tests/tb_stage_export_after_reset_v2.sv').read_text()
    assert tb.read_text()==old.replace(' initial begin\n  for(x=0;x<30;x=x+1)saved[x]=0;',
        ' initial begin\n  #200; // Both modes wait beyond the unmodified glbl 100ns startup.\n  for(x=0;x<30;x=x+1)saved[x]=0;',1)
    glbl=BIN.parent.parent/'data/verilog/src/glbl.v';assert glbl.exists()
    p=BASE/'stage_export_functional_pair_v1';assert not p.exists() and not os.environ.get('LD_PRELOAD')
    p.mkdir()
    m=dict(status='running',stage='prepare',runner_pid=os.getpid(),runner_start_ticks=identity(os.getpid()),
        runner_sha256=sha(Path(__file__)),synthesis_manifest_sha256=sha(ref/'manifest.json'),
        reference_sources={str(ref/n):h for n,h in {**sm['sources'],**sm['artifact_sha256']}.items()},
        tb_sha256=sha(tb),glbl_sha256=sha(glbl),cases={},
        scope='2-slot/MAX_PATH8 standalone original controller, RTL versus post-synthesis functional, identical v3 port stimulus and vendor glbl; not full-system netlist or timing simulation.')
    def save():
        tmp=p/'manifest.pending.json';tmp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');tmp.replace(p/'manifest.json')
    save()
    try:
        for mode,source in [('rtl',ref/'controller.sv'),('functional',ref/'functional.v')]:
            d=p/mode;d.mkdir();shutil.copyfile(source,d/'design.v');shutil.copyfile(tb,d/'tb.sv');shutil.copyfile(glbl,d/'glbl.v')
            (d/'run.tcl').write_text('run all\nquit\n')
            case=dict(commands=[],inputs={n:sha(d/n) for n in ['design.v','tb.sv','glbl.v','run.tcl']});m['cases'][mode]=case
            m['stage']=mode+'_wait_memory';save();memory_admission(m,save)
            compile=[str(BIN.parent/'xvlog'),'--sv']+(['-d','NETLIST'] if mode=='functional' else [])+['design.v','tb.sv','glbl.v']
            phases=[('compile',compile),('elaborate',[str(BIN.parent/'xelab'),'-L','unisims_ver','tb_stage_export_after_reset','glbl','-s','probe','--mt','2']),
                    ('simulate',[str(BIN.parent/'xsim'),'probe','-tclbatch','run.tcl'])]
            for stage,argv in phases:
                for n,h in case['inputs'].items():assert sha(d/n)==h
                m['stage']=mode+'_'+stage;save()
                with (d/(stage+'.stdout.log')).open('w') as log:
                    child=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT)
                    m['active_process']=dict(pid=child.pid,start_ticks=identity(child.pid));save()
                    code=wait_preserving(child,600,m,save)
                m.pop('active_process',None);case['commands'].append(dict(stage=stage,argv=argv,exit_code=code));save();assert code==0,(mode,stage)
            log=(d/'simulate.stdout.log').read_text()
            assert 'STAGE_EXPORT_AFTER_RESET_PASS imports=30 exports=30 crc=395d7a27' in log
            assert 'Fatal:' not in log
            case['status']='observed';save();print('STAGE_EXPORT_PAIR_CASE',mode,'observed',flush=True)
        m.update(status='observed',stage='complete',exit_code=0)
    except Exception as error:
        m.update(status='failed',error=repr(error));raise
    finally:save()
    print('STAGE_EXPORT_FUNCTIONAL_PAIR_OBSERVED')


if __name__=='__main__':main()
