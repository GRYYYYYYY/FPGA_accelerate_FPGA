"""Run preserved/default/native route tests and a generic overlap counterexample."""
from pathlib import Path
import importlib.util
import json
import shutil
import subprocess
import sys
import time
from run_checkpoint_authority import ROOT, BIN, sha

p = Path(sys.argv[1]).resolve()
assert not p.exists()
assert int(Path('/sys/fs/cgroup/memory.current').read_text()) <= int(Path('/sys/fs/cgroup/memory.max').read_text())*.75
v = ROOT/'hardware/variants/route_path_write_v1'
spec = importlib.util.spec_from_file_location('route_label_tb', v/'build_tb.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
vm = json.loads((v/'manifest.json').read_text())
ref = p.parent/'route_checkpoint_unit_v8'
ra = json.loads((ref/'source_bound_audit.json').read_text())
rp = ROOT/'results/route_checkpoint_unit_v8_restore_20261025.json'
rr = json.loads(rp.read_text())
assert ra['status'] == rr['status'] == 'passed' and rr['audit_byte_identical']
assert rr['audit_sha256'] == sha(ref/'source_bound_audit.json')
assert ra['manifest_sha256'] == sha(ref/'manifest.json')
p.mkdir()
bound = ['scripts/run_route_path_units.py', 'scripts/run_checkpoint_authority.py',
         'scripts/analyze_route_label_exclusion.py',
         'hardware/variants/route_commit_v1/tb_route_commit.sv',
         'hardware/variants/route_checkpoint_v1/tb_route_commit.sv',
         'hardware/variants/route_checkpoint_v1/build_tb.py',
         'hardware/variants/route_label_exclusion_v2/build_tb.py']
bound += [str(x.relative_to(ROOT)) for x in v.rglob('*') if x.is_file() and '__pycache__' not in x.parts]
m = dict(status='running', cases=[], bound={n:sha(ROOT/n) for n in bound},
         reference_audit_sha256=sha(ref/'source_bound_audit.json'),
         reference_restore_sha256=sha(rp), labels_sha256=sha(ref/'labels.txt'),
         scope='Three controller modes, original route and checkpoint8/32 plus generic overlap; per-word path-bank event cycles recorded. '
               'No native readiness masking or label specialization. Generic overlap '
               'preserves original same-cycle reply behavior in all modes. '
               'No full-system, adapter RTL composition or timing acceptance.')
for name in bound:
    q = p/'tools'/name
    q.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT/name, q)
shutil.copyfile(ref/'labels.txt', p/'labels.txt')


def save():
    (p/'manifest.json').write_text(json.dumps(m, indent=2, sort_keys=True)+'\n')


save()
try:
    for mode in ['baseline', 'default', 'factored']:
        for suite in ['route', 'checkpoint', 'checkpoint32', 'generic_overlap']:
            for name, digest in m['bound'].items():
                assert sha(ROOT/name) == sha(p/'tools'/name) == digest, name
            d = p/f'{mode}_{suite}'
            d.mkdir()
            source = v/('baseline' if mode == 'baseline' else 'fixed')/'route_commit_controller.sv'
            assert sha(source) == vm['sources']['route_commit_controller.sv']['baseline' if mode == 'baseline' else 'fixed']
            shutil.copyfile(source, d/'route_commit_controller.sv')
            tb, marker = b.build(ROOT, mode, suite)
            (d/'tb.sv').write_text(tb)
            (d/'run.tcl').write_text('run 1ms\nquit\n')
            c = dict(mode=mode, suite=suite, status='running', commands=[],
                     rtl_sha256=sha(source), tb_sha256=sha(d/'tb.sv'))
            m['cases'].append(c)
            save()
            commands = [
                ('compile', [BIN/'xvlog', '--sv', d/'route_commit_controller.sv', d/'tb.sv']),
                ('elaborate', [BIN/'xelab', 'tb_route_commit', '-s', 'route', '--debug', 'typical', '--mt', '2']),
                ('simulate', [BIN/'xsim', 'route', '--tclbatch', 'run.tcl', '--log', 'simulate.log',
                              '--testplusarg', 'labels='+str(p/'labels.txt'),
                              '--testplusarg', 'events='+str(d/'events.txt'),
                              '--testplusarg', 'bank_events='+str(d/'bank_events.txt')])]
            for stage, args in commands:
                start = time.monotonic()
                argv = list(map(str, args))
                with (d/(stage+'.stdout.log')).open('w') as log:
                    result = subprocess.run(argv, cwd=d, stdout=log, stderr=subprocess.STDOUT, timeout=240)
                c['commands'].append(dict(stage=stage, argv=argv, exit_code=result.returncode,
                                          elapsed_s=time.monotonic()-start,
                                          log_sha256=sha(d/(stage+'.stdout.log'))))
                save()
                assert result.returncode == 0, (mode, suite, stage)
            log = (d/'simulate.log').read_text()
            assert marker in log and '$finish called' in log and 'Fatal:' not in log and 'ERROR:' not in log
            c.update(status='passed', trace_sha256=sha(d/'events.txt'), simulate_log_sha256=sha(d/'simulate.log'), bank_trace_sha256=sha(d/'bank_events.txt'))
            save()
            print(mode, suite, 'passed', flush=True)
    m['status'] = 'observed'
except Exception as error:
    m.update(status='failed', error=repr(error))
    raise
finally:
    save()
print('ROUTE_PATH_UNITS_OBSERVED', flush=True)
