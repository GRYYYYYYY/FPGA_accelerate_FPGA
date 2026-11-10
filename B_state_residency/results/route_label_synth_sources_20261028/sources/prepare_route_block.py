"""Prepare matched full-root synthesis of the two-file idle blocking candidate."""
from pathlib import Path
import importlib.util, json, shutil, sys
from run_checkpoint_authority import ROOT, sha

p = Path(sys.argv[1]).resolve()
ref = p.parent / 'combined_loops_synth_v1'
rm = json.loads((ref / 'manifest.json').read_text())
ra = json.loads((ref / 'source_bound_audit.json').read_text())
assert rm['status'] == 'observed' and ra['status'] == 'passed'
assert ra['manifest_sha256'] == sha(ref / 'manifest.json')
receipt = ROOT / 'results/combined_loops_synth_v1_restore_20261025.json'
rr = json.loads(receipt.read_text())
assert rr['status'] == 'passed' and rr['audit_byte_identical']
assert rr['audit_sha256'] == sha(ref / 'source_bound_audit.json')
variant = ROOT / 'hardware/variants/route_block_loops_v1'
builder = variant / 'build.py'
spec = importlib.util.spec_from_file_location('route_block_builder', builder)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
baseline, fixed = b.sources(False), b.sources(True)
assert set(fixed) == {'route_commit_controller.sv', 'route_commit_host_adapter.sv'}
changes = {}
for n in fixed:
    assert (ref / 'sources' / n).read_text() == baseline[n]
    assert (variant / 'baseline' / n).read_text() == baseline[n]
    assert (variant / 'fixed' / n).read_text() == fixed[n]
    changes[n] = dict(original_sha256=sha(ref / 'sources' / n),
                      candidate_sha256=sha(variant / 'fixed' / n),
                      path=str(variant / 'fixed' / n))
p.mkdir()
src = p / 'sources'
src.mkdir()
sources = {}
for n, h in rm['sources'].items():
    origin = ref / 'sources' / n
    assert sha(origin) == h
    dest = src / n
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(origin, dest)
    sources[n] = h
for n, c in changes.items():
    shutil.copyfile(c['path'], src / n)
    sources[n] = sha(src / n)
for f in src.rglob('*.dat'):
    shutil.copyfile(f, p / f.name)
(p / 'synth.tcl').write_text((ref / 'synth.tcl').read_text().replace(str(ref), str(p)))
shutil.copyfile(ref / 'clock.xdc', p / 'clock.xdc')
shutil.copyfile(Path(__file__), src / 'prepare_route_block.py')
sources['prepare_route_block.py'] = sha(src / 'prepare_route_block.py')
evidence = dict(builder_sha256=sha(builder),
    identity_sha256=sha(ROOT / 'results/route_block_identity_20261027.json'),
    analyzer_sha256=sha(ROOT / 'scripts/analyze_route_block_identity.py'),
    reference_restore_sha256=sha(receipt))
m = dict(status='prepared', sources=sources, rtl=rm['rtl'], parameters=rm['parameters'],
    part=rm['part'], reference=str(ref), reference_audit_sha256=sha(ref / 'source_bound_audit.json'),
    tcl_sha256=sha(p / 'synth.tcl'), xdc_sha256=sha(p / 'clock.xdc'), clock_period_ns=10,
    production_changes=changes, route_block_evidence=evidence,
    scope='Two-source route idle blocking candidate on restored five-source combined baseline; seven cumulative source changes relative to restore_seed_synth_on_v1. Same full 133 RTL list, part, parameters and10ns clock. Boolean identity is not native RTL validation. Full behavior, remaining loops, physical timing and board validation pending.')
(p / 'manifest.json').write_text(json.dumps(m, indent=2, sort_keys=True) + '\n')
print('ROUTE_BLOCK_SYNTH_PREPARED', len(m['rtl']), len(changes))
