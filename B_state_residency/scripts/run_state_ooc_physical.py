"""Run one prepared full-system OOC implementation; preserve every failed attempt."""
from pathlib import Path
import json
import subprocess
import sys
import time
from run_checkpoint_authority import ROOT, sha

p = Path(sys.argv[1]).resolve()
m = json.loads((p/'manifest.json').read_text())
assert m['status'] == 'prepared'
gate = json.loads((p.parent/'route_stage_synth_followup_v1/manifest.json').read_text())
assert gate['status'] == 'observed' and gate['stage'] == 'complete'
c = Path('/sys/fs/cgroup')
assert int((c/'memory.current').read_text())*4 <= int((c/'memory.max').read_text())*3
for name, digest in m['inputs'].items():
    assert sha(p/name) == digest, name
assert sha(p/'run.tcl') == m['tcl_sha256']
assert sha(ROOT/'scripts/prepare_state_ooc_physical.py') == m['preparer_sha256']
assert sha(ROOT/'hardware/scripts/implement_state_ooc.tcl') == m['template_sha256']
ref = Path(m['reference'])
assert sha(ref/'source_bound_audit.json') == m['synthesis_audit_sha256']
assert sha(Path(m['full_system_reference'])/'source_bound_audit.json') == m['full_system_audit_sha256']
argv = ['/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin/vivado',
        '-mode', 'batch', '-source', str(p/'run.tcl'),
        '-log', str(p/'vivado.log'), '-journal', str(p/'vivado.jou')]
(p/'runner.py').write_bytes(Path(__file__).read_bytes())
m.update(status='running', command=argv, execution='local_batch', runner_sha256=sha(p/'runner.py'))


def save():
    tmp = p/'manifest.pending.json'
    tmp.write_text(json.dumps(m, indent=2, sort_keys=True)+'\n')
    tmp.replace(p/'manifest.json')


save()
start = time.monotonic()
try:
    with (p/'stdout.log').open('w') as log:
        result = subprocess.run(argv, cwd=p, stdout=log, stderr=subprocess.STDOUT, timeout=14400)
    m['exit_code'] = result.returncode
    assert result.returncode == 0, 'Vivado implementation failed; preserve attempt'
    log = (p/'vivado.log').read_text()
    assert 'STATE_FULL_PHYSICAL_DONE' in log
    assert not any(line.startswith('ERROR:') for line in log.splitlines())
    outputs = ['optimized.dcp', 'placed.dcp', 'routed.dcp', 'completed.txt', 'milestones.txt',
               'clocks_input.rpt', 'utilization_input.rpt', 'methodology_input.rpt',
               'check_timing_input.rpt', 'loops_input.rpt', 'constraints_input.xdc',
               'utilization_placed.rpt', 'timing_placed.rpt', 'route_status.rpt',
               'utilization_routed.rpt', 'utilization_routed_hier.rpt',
               'methodology_routed.rpt', 'drc_routed.rpt', 'loops_routed.rpt',
               'check_timing_routed.rpt', 'clocks_routed.rpt', 'timing_routed.rpt',
               'constraints_routed.xdc', 'internal_paths.tsv', 'vivado.log', 'vivado.jou', 'stdout.log']
    for name in outputs:
        assert (p/name).is_file() and (p/name).stat().st_size > 0, name
    for name, digest in m['inputs'].items():
        assert sha(p/name) == digest, 'Implementation changed an input: '+name
    m.update(status='observed', artifact_sha256={name:sha(p/name) for name in outputs})
except Exception as error:
    m.update(status='failed', error=repr(error))
    raise
finally:
    m['elapsed_s'] = time.monotonic()-start
    save()
print('STATE_FULL_PHYSICAL_OBSERVED', p.name)
