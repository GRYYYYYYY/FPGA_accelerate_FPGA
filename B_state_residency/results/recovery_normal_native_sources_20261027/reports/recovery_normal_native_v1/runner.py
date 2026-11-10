"""Run the native J0 recovery/label lifecycle with NORMAL admission specialization."""
from pathlib import Path
import json, shutil, subprocess, sys, time
from run_checkpoint_authority import ROOT, sha

p = Path(sys.argv[1]).resolve()
ref = p.parent / 'rearm_loops_component_v2'
rm = json.loads((ref / 'manifest.json').read_text())
ra = json.loads((ref / 'source_bound_audit.json').read_text())
receipt = ROOT / 'results/rearm_loops_component_v2_restore_20261025.json'
rr = json.loads(receipt.read_text())
assert ra['status'] == rr['status'] == 'passed'
assert ra['manifest_sha256'] == sha(ref / 'manifest.json')
assert rr['audit_byte_identical'] and rr['audit_sha256'] == sha(ref / 'source_bound_audit.json')
variant = ROOT / 'hardware/variants/recovery_normal_loops_v1'
assert sha(variant / 'baseline/recovery_coordinator.sv') == rm['sources']['fixed/recovery_coordinator.sv']['sha256']
p.mkdir()
src = p / 'sources'
src.mkdir()
origins = {n: ref / 'sources/fixed' / n for n in ['label_restore_controller.sv', 'rearm_loop_slice.sv']}
origins.update({'tb_rearm_loop.sv': ref / 'sources/tb_rearm_loop.sv',
    'recovery_coordinator.sv': variant / 'fixed/recovery_coordinator.sv',
    'build.py': variant / 'build.py', 'CONTRACT.md': variant / 'CONTRACT.md',
    'identity.json': ROOT / 'results/recovery_normal_identity_20261027.json'})
for n, origin in origins.items():
    shutil.copyfile(origin, src / n)
shutil.copyfile(Path(__file__), p / 'runner.py')
m = dict(status='running', reference=str(ref), reference_audit_sha256=sha(ref / 'source_bound_audit.json'),
    reference_restore_sha256=sha(receipt), sources={n: sha(src / n) for n in origins},
    runner_sha256=sha(p / 'runner.py'), commands=[],
    scope='Native coordinator/label J0 lifecycle only, same RAM/config/retirement models and TB as restored REARM fixed reference. No synthesis, AXI or full-system loop-removal claim.')
def save():
    (p / 'manifest.json').write_text(json.dumps(m, indent=2, sort_keys=True) + '\n')
binpath = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
d = p / 'simulate'
d.mkdir()
(d / 'run.tcl').write_text('run 2ms\nquit\n')
rtl = [src / n for n in ['recovery_coordinator.sv', 'label_restore_controller.sv', 'rearm_loop_slice.sv', 'tb_rearm_loop.sv']]
commands = [('compile', [binpath / 'xvlog', '--sv', *rtl]),
            ('elaborate', [binpath / 'xelab', 'tb_rearm_loop', '-s', 'normal_test', '--debug', 'typical', '--mt', '2']),
            ('simulate', [binpath / 'xsim', 'normal_test', '--tclbatch', 'run.tcl', '--log', 'simulate.log'])]
save()
try:
    for stage, argv in commands:
        argv = list(map(str, argv))
        start = time.monotonic()
        with (d / (stage + '.stdout.log')).open('w') as stream:
            r = subprocess.run(argv, cwd=d, stdout=stream, stderr=subprocess.STDOUT, timeout=120)
        m['commands'].append(dict(stage=stage, argv=argv, exit_code=r.returncode, elapsed_s=time.monotonic()-start))
        save()
        assert r.returncode == 0, stage
        print(stage, 'completed', flush=True)
    log = (d / 'simulate.log').read_text()
    assert 'REARM_LOOP_PASS scenarios=3 successes=3 failures=10 checks=179' in log
    assert '$finish called' in log and 'Fatal:' not in log
    m['status'] = 'observed'
except Exception as error:
    m.update(status='failed', error=repr(error))
    raise
finally:
    m['artifacts'] = {str(f.relative_to(p)): sha(f) for f in sorted(d.rglob('*'))
                      if f.is_file() and f.suffix in ['.log', '.tcl', '.txt']}
    save()
print('RECOVERY_NORMAL_NATIVE_OBSERVED')
