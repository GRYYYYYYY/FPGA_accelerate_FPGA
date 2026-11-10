"""Preserve an actual verification-driver failure and its read-only diagnosis."""
from pathlib import Path
import json,re,sys
from run_checkpoint_authority import ROOT,sha

p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text())
original=p.parent/'rearm_loops_component_v1';probe=p.parent/'rearm_loops_probe_v1'
dev=ROOT/'results/rearm_loop_development_20261027.json';record=json.loads(dev.read_text())
assert sha(original/'manifest.json')==record['failed_manifest_sha256']
assert sha(probe/'manifest.json')==record['probe_manifest_sha256']
for n,e in m['sources'].items():assert sha(p/'sources'/n)==(e['sha256']if isinstance(e,dict)else e),n
if p==original:
    assert m['status']=='failed'and len(m['commands'])==4 and all(c['exit_code']==0 for c in m['commands'])
    for n,h in m['artifacts'].items():assert sha(p/n)==h,n
    assert sha(p/'runner.py')==m['runner_sha256']
    tb=(p/'sources/tb_rearm_loop.sv').read_text()
    assert sha(p/'sources/tb_rearm_loop.sv')==record['old_tb_sha256']
    assert 'reg  l_start_offer=0;'in tb and 'always @*l_start_offer=!started;'in tb
    log=(p/'baseline/simulate/simulate.log').read_text()
    assert 'Fatal: watchdog'in log and '$finish called at time : 1 ms'in log
    assert not re.search(r'^(RESULT|WRITE|RESET) ',log,re.M)
    verdict='original TB never offered label start; observed watchdog is not a production RTL counterexample'
elif p==probe:
    assert m['status']=='diagnostic_observed'and len(m['commands'])==3 and all(c['exit_code']==0 for c in m['commands'])
    for n in ['recovery_coordinator.sv','label_restore_controller.sv','rearm_loop_slice.sv']:
        assert sha(p/'sources'/n)==sha(original/'sources/baseline'/n)
    assert sha(p/'sources/tb_rearm_loop.sv')==sha(original/'sources/tb_rearm_loop.sv')
    code=(p/'sources/tb_rearm_probe.sv').read_text();assert 'force'not in code and 't.dut.k.state'in code
    log=(p/'simulate.log').read_text();rows=[l for l in log.splitlines()if l.startswith('DBG ')]
    assert len(rows)==19 and 'PROBE_DONE'in log and 'Fatal:'not in log
    assert all('ks=9 ls=0'in l and 'lbl=1/0/1'in l and 'lr=0/0/0'in l and 'started=0'in l for l in rows)
    verdict='read-only monitor confirms coordinator waiting for labels, idle ready label leaf, but TB offer remains0 while started0'
else:raise AssertionError('unexpected development root')
r=dict(status='passed',audit_kind='failure/diagnostic evidence integrity, not functional pass',
    manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),development_record_sha256=sha(dev),
    diagnostic_log_sha256=sha(probe/'simulate.log'),verdict=verdict)
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
print('REARM_DEVELOPMENT_AUDITED',p.name,verdict)
