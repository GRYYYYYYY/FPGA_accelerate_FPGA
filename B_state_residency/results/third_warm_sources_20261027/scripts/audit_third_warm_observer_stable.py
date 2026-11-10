"""Deterministic packaging audit of unchanged legacy observations against audited v2."""
from pathlib import Path
import hashlib
import json
import runpy
import sys
from run_checkpoint_authority import ROOT, sha

p = Path(sys.argv[1]).resolve()
m = json.loads((p/'manifest.json').read_text())
origin = Path(m['repackaged_from'])
original_manifest = json.loads((origin/'manifest.json').read_text())
assert sha(origin/'manifest.json') == m['original_manifest_sha256']
assert {k:v for k,v in m.items() if k not in ['repackaged_from','original_manifest_sha256']} == original_manifest
assert m['status'] == 'observed' and len(m['cases']) == 1
case = next(iter(m['cases']))
c = m['cases'][case]
assert c['status'] == 'observed' and len(c['commands']) == 3 and all(x['exit_code'] == 0 for x in c['commands'])
ref = p.parent / ('third_warm_' + case + '_v2')
rm = json.loads((ref/'manifest.json').read_text())
ra = json.loads((ref/'source_bound_audit.json').read_text())
assert ra['status'] == 'passed' and sha(ref/'manifest.json') == ra['manifest_sha256']
assert sha(ROOT/'scripts/audit_third_warm_system.py') == ra['auditor_sha256']
for name, entry in m['sources'].items():
    assert sha(p/'sources'/name) == entry['sha256'], name
    if name not in ['runner.py', 'tb_query_fault.sv', 'g3_warm_build_tb.py']:
        assert entry['sha256'] == rm['sources'][name]['sha256'], name
assert runpy.run_path(str(p/'sources/g3_warm_build_tb.py'))['make']() == (p/'sources/tb_query_fault.sv').read_text()
legacy = (p/'sources/tb_query_fault.sv').read_text()
fixed = legacy.replace('wire actual_route_slot=system.inner.backend.f_broute_payload[1];', 'wire[1:0]actual_route_slot=system.inner.backend.f_broute_payload[2:1];')
fixed = fixed.replace('else begin saved2[count2]<=system.inner.backend.route_join.o_node;count2<=count2+1;end', 'else if(actual_route_slot==1)begin saved2[count2]<=system.inner.backend.route_join.o_node;count2<=count2+1;end')
assert fixed == (ref/'sources/tb_query_fault.sv').read_text()
files = {}
for q in sorted((p/case).iterdir()):
    if q.suffix not in ['.bin', '.txt', '.dat'] or q.name == 'natural_trace.txt':
        continue
    assert sha(q) == sha(ref/case/q.name), q.name
    files[q.name] = sha(q)
assert len([n for n in files if n.endswith('_axi.txt')]) == 12
oldrows = (p/case/'natural_trace.txt').read_text().splitlines()
newrows = (ref/case/'natural_trace.txt').read_text().splitlines()
assert len(oldrows) == len(newrows)
differences = {}
for a, b in zip(oldrows, newrows):
    if a == b:
        continue
    x, y = a.split(), b.split()
    tag = x[0]
    assert tag == y[0] and tag in ['RO', 'RB', 'RL', 'RA', 'RC'], (a, b)
    field = 3 if tag == 'RC' else 2
    assert int(x[field]) == 0 and int(y[field]) == 2
    x[field] = y[field]
    assert x == y, (a, b)
    differences[tag] = differences.get(tag, 0) + 1
log = (p/case/'simulate.log').read_text()
assert 'THIRD_WARM_PASS' in log and 'Fatal:' not in log and '$finish called' in log
result = dict(status='passed', manifest_sha256=sha(p/'manifest.json'), auditor_sha256=sha(Path(__file__)),
              case=case, repackaged_from=str(origin), original_manifest_sha256=m['original_manifest_sha256'], selected_reference=ref.name, reference_audit_sha256=sha(ref/'source_bound_audit.json'),
              identical_files=files, truncated_observer_fields=differences, final_cycle=ra['final_cycle'],
              scope='Development TB only: legacy RO/RB/RL/RA/RC slot observer retained bit0 and routed slot2 into an unused q1 observation array. Exact native cycles except listed slot fields, all12 AXI logs and final images match independently audited corrected v2. Not selected as the full-width slot evidence; not a production RTL counterexample.')
(p/'source_bound_audit.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
print('LEGACY_OBSERVER_EQUIVALENT', case, differences)
