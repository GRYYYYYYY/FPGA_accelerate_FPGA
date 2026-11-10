"""Execute an already prepared, source-bound local Vivado OOC experiment."""
from pathlib import Path
import json,subprocess,sys,time
from run_checkpoint_authority import sha

p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text())
assert m['status']=='prepared'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h,n
assert sha(p/'synth.tcl')==m['tcl_sha256']and sha(p/'clock.xdc')==m['xdc_sha256']
ref=Path(m['reference']);a=json.loads((ref/'source_bound_audit.json').read_text())
assert a['status']=='passed'and sha(ref/'source_bound_audit.json')==m['reference_audit_sha256']
assert a['manifest_sha256']==sha(ref/'manifest.json')
argv=['/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin/vivado',
      '-mode','batch','-source',str(p/'synth.tcl'),'-log',str(p/'vivado.log'),'-journal',str(p/'vivado.jou')]
(p/'runner.py').write_bytes(Path(__file__).read_bytes());m['runner_sha256']=sha(p/'runner.py')
m.update(status='running',command=argv,execution='local_batch',
         fallback_reason='Existing two MCP sessions report version as out of stack space (infinite loop?); they were not reused or stopped. Fresh local Vivado 2022.2 version and installed command help preflight completed.')
def save():(p/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
save();start=time.monotonic()
try:
    with(p/'stdout.log').open('w')as f:
        r=subprocess.run(argv,cwd=p,stdout=f,stderr=subprocess.STDOUT,timeout=7200)
    m['exit_code']=r.returncode;assert r.returncode==0,'Vivado exit'
    log=(p/'vivado.log').read_text()
    assert 'RESTORE_SEED_OOC_DONE'in log and 'synth_design completed successfully'in log
    assert not any(line.startswith('ERROR:')for line in log.splitlines())
    for n in ['utilization.rpt','timing_synth.rpt','check_timing.rpt','facts.txt','clocks.rpt','synth.dcp','synth.v']:
        assert(p/n).is_file()and(p/n).stat().st_size>0,n
    m['status']='observed'
except Exception as error:
    m.update(status='failed',error=repr(error));raise
finally:
    m['elapsed_s']=time.monotonic()-start;save()
print('RESTORE_SEED_OOC_OBSERVED',p.name)
