"""Compile/elaborate only: no xsim process, simulation time or functional verdict."""
from pathlib import Path
import importlib.util
import json
import shutil
import subprocess
import sys
import time
from run_checkpoint_authority import ROOT, sha

out=Path(sys.argv[1]).resolve()
assert int(Path('/sys/fs/cgroup/memory.current').read_text()) < int(Path('/sys/fs/cgroup/memory.max').read_text())*.75
out.mkdir()
v=ROOT/'hardware/variants/query_native_exclusion_v1'
bin=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
spec=importlib.util.spec_from_file_location('query_build',v/'build_tb.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
vm=json.loads((v/'manifest.json').read_text())
for name,values in vm['sources'].items():
    assert sha(v/'baseline'/name)==values['baseline']
    assert sha(v/'fixed'/name)==values['candidate']
m=dict(status='running',cases=[],runner_sha256=sha(Path(__file__)),builder_sha256=sha(v/'build_tb.py'),
       variant_manifest_sha256=sha(v/'manifest.json'),scope='Fresh Vivado2022.2 compile and elaboration of twelve native query testbenches; no simulation or functional result.')
tools=out/'tools';tools.mkdir()
for source in [Path(__file__),v/'build_tb.py',v/'manifest.json',ROOT/'hardware/variants/query_lifecycle_v1/tb_query_lifecycle.sv']:
    shutil.copyfile(source,tools/source.name)
def save(): (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
save()
try:
    for mode in ['baseline','default','exclusive']:
        for early in range(4):
            d=out/f'{mode}_{early}';d.mkdir()
            source=v/('baseline' if mode=='baseline' else 'fixed')/'query_lifecycle.sv'
            shutil.copyfile(source,d/'query_lifecycle.sv')
            (d/'tb.sv').write_text(b.build(ROOT,mode,early))
            c=dict(mode=mode,early=early,commands=[],status='running',rtl_sha256=sha(d/'query_lifecycle.sv'),tb_sha256=sha(d/'tb.sv'))
            m['cases'].append(c);save()
            for stage,args in [('compile',[bin/'xvlog','--sv','query_lifecycle.sv','tb.sv']),('elaborate',[bin/'xelab','tb_query_lifecycle','-s','query_native','--debug','typical','--mt','2'])]:
                start=time.monotonic()
                with (d/(stage+'.stdout.log')).open('w') as f:
                    result=subprocess.run(list(map(str,args)),cwd=d,stdout=f,stderr=subprocess.STDOUT,timeout=180)
                log=d/(stage+'.stdout.log')
                c['commands'].append(dict(stage=stage,argv=list(map(str,args)),exit_code=result.returncode,elapsed_s=time.monotonic()-start,log_sha256=sha(log)));save()
                assert result.returncode==0 and 'ERROR:' not in log.read_text(),(mode,early,stage)
            c['status']='elaborated_not_simulated';save()
            print('ELABORATED',mode,early,flush=True)
    m['status']='elaborated_not_simulated'
except Exception as e:
    m.update(status='failed',error=repr(e));raise
finally: save()
