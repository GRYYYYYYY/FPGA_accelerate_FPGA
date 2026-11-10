"""Run twelve controller cases after the existing full-system matrix finishes."""
from pathlib import Path
import importlib.util
import json
import shutil
import subprocess
import sys
import time
from run_checkpoint_authority import ROOT, sha

BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
BASE=Path('/tmp/B_state_residency_offer_20261025')
V=ROOT/'hardware/variants/query_native_exclusion_v1'

def main():
    gate=json.loads((BASE/'native_retirement_matrix_queue_v1/manifest.json').read_text())
    assert gate['status']=='observed' and gate['stage']=='complete', 'existing matrix owns behavioral simulation slot'
    assert int(Path('/sys/fs/cgroup/memory.current').read_text()) <= int(Path('/sys/fs/cgroup/memory.max').read_text())*.75
    out=Path(sys.argv[1]).resolve();out.mkdir()
    spec=importlib.util.spec_from_file_location('query_tb_builder',V/'build_tb.py')
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    variant=json.loads((V/'manifest.json').read_text())
    for name,record in variant['sources'].items():
        assert sha(V/'baseline'/name)==record['baseline']
        assert sha(V/'fixed'/name)==record['candidate']
    m=dict(status='running',cases=[],runner_sha256=sha(Path(__file__)),builder_sha256=sha(V/'build_tb.py'),
           parent_tb_sha256=sha(ROOT/'hardware/variants/query_lifecycle_v1/tb_query_lifecycle.sv'),
           variant_manifest_sha256=sha(V/'manifest.json'),scope='Native query controller with modeled backends; default/full lifecycle and three deliberate same-cycle reply injections. Not full-system or timing proof.')
    tools=out/'tools';tools.mkdir()
    for source in [Path(__file__),V/'build_tb.py',V/'manifest.json',ROOT/'hardware/variants/query_lifecycle_v1/tb_query_lifecycle.sv']:
        shutil.copyfile(source,tools/source.name)
    def save(): (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    save()
    try:
        for mode in ['baseline','default','exclusive']:
            for early in range(4):
                d=out/f'{mode}_{early}';d.mkdir()
                src=V/('baseline' if mode=='baseline' else 'fixed')/'query_lifecycle.sv'
                shutil.copyfile(src,d/'query_lifecycle.sv')
                (d/'tb.sv').write_text(builder.build(ROOT,mode,early))
                (d/'run.tcl').write_text('run 2ms\nquit\n')
                c=dict(mode=mode,early=early,status='running',commands=[],rtl_sha256=sha(d/'query_lifecycle.sv'),tb_sha256=sha(d/'tb.sv'))
                m['cases'].append(c);save()
                commands=[('compile',[BIN/'xvlog','--sv','query_lifecycle.sv','tb.sv']),
                          ('elaborate',[BIN/'xelab','tb_query_lifecycle','-s','query_native','--debug','typical','--mt','2']),
                          ('simulate',[BIN/'xsim','query_native','--tclbatch','run.tcl','--log','simulate.log','--testplusarg','events='+str(d/'events.txt')])]
                for stage,args in commands:
                    t=time.monotonic()
                    with (d/(stage+'.stdout.log')).open('w') as log:
                        proc=subprocess.run(list(map(str,args)),cwd=d,stdout=log,stderr=subprocess.STDOUT,timeout=180)
                    c['commands'].append(dict(stage=stage,argv=list(map(str,args)),exit_code=proc.returncode,elapsed_s=time.monotonic()-t,log_sha256=sha(d/(stage+'.stdout.log'))));save()
                    assert proc.returncode==0,(mode,early,stage)
                log=(d/'simulate.log').read_text()
                assert 'QUERY_LIFECYCLE_PASS checks=' in log and '$finish called' in log
                assert 'Fatal:' not in log and 'ERROR:' not in log
                c.update(status='passed',events_sha256=sha(d/'events.txt'),simulate_log_sha256=sha(d/'simulate.log'));save()
        comparisons=[]
        for early in range(4):
            assert (out/f'baseline_{early}/events.txt').read_bytes()==(out/f'default_{early}/events.txt').read_bytes()
            comparisons.append([f'baseline_{early}',f'default_{early}'])
        assert (out/'baseline_0/events.txt').read_bytes()==(out/'exclusive_0/events.txt').read_bytes()
        comparisons.append(['baseline_0','exclusive_0'])
        m.update(status='observed',exact_event_comparisons=comparisons)
    except Exception as e:
        m.update(status='failed',error=repr(e));raise
    finally: save()
    print('QUERY_NATIVE_TWELVE_CASES_OBSERVED')

if __name__=='__main__': main()
