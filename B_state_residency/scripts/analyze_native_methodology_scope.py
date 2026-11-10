"""Classify restored OOC diagnostics without treating report caps as design totals."""
from collections import Counter
from pathlib import Path
import json
import re
from run_checkpoint_authority import ROOT, sha

base = Path('/tmp/B_state_residency_offer_20261025')
gate = json.loads((base / 'native_retirement_synth_followup_v1/manifest.json').read_text())
assert gate['status'] == 'observed' and gate['stage'] == 'complete'
p = base / 'native_retirement_synth_v1'
ap = p / 'source_bound_audit.json'
a = json.loads(ap.read_text())
rp = ROOT / 'results/native_retirement_synth_v1_restore_20261025.json'
r = json.loads(rp.read_text())
assert a['status'] == r['status'] == 'passed' and r['audit_byte_identical']
assert sha(ap) == r['audit_sha256']
dp = p / 'results/methodology_v1/manifest.json'
d = json.loads(dp.read_text())
assert sha(dp) == a['diagnostic_manifest_sha256']
report = dp.parent / 'methodology.rpt'
assert sha(report) == d['artifacts']['methodology.rpt']
text = report.read_text()
headers = list(re.finditer(r'^(SYNTH-10|TIMING-16|TIMING-18)#(\d+) Warning\s*$', text, re.M))
counts = Counter(h[1] for h in headers)
assert dict(counts) == a['methodology_counts']
rows = []
for i, h in enumerate(headers):
    end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
    lines = [s.strip() for s in text[h.end():end].splitlines() if s.strip()]
    rows.append(dict(rule=h[1], index=int(h[2]), title=lines[0], description=lines[1]))
timing = []
for row in rows:
    if row['rule'] != 'TIMING-16':
        continue
    m = re.fullmatch(r'There is a large setup violation of (-?[\d.]+) ns between (\S+) \(clocked by ([^)]+)\) and (\S+) \(clocked by ([^)]+)\).*', row['description'])
    assert m, row
    timing.append(dict(slack_ns=float(m[1]), source=m[2], destination=m[4], source_clock=m[3], destination_clock=m[5]))
multipliers = []
for row in rows:
    if row['rule'] != 'SYNTH-10':
        continue
    m = re.fullmatch(r'Detected multiplier at (\S+) of size (\d+x\d+), it is decomposed from a wide multipler into (\d+) DSP blocks\.', row['description'])
    assert m, row
    multipliers.append(dict(cell=m[1], size=m[2], decomposition_dsp_blocks=int(m[3])))
summary = a['synthesis_timing_summary']
m = re.search(r'^\s*(-?[\d.]+)\s+(-?[\d.]+)\s+(\d+)\s+(\d+)\s+', summary, re.M)
assert m and float(m[1]) == a['preplacement_wns_ns']
result = dict(
    status='source_bound_diagnostic_navigation', analyzer_sha256=sha(Path(__file__)),
    audit_sha256=sha(ap), restore_receipt_sha256=sha(rp), report_sha256=sha(report),
    report_counts=dict(counts), rule_titles={row['rule']: row['title'] for row in rows},
    setup_summary=dict(wns_ns=float(m[1]), tns_ns=float(m[2]), failing_endpoints=int(m[3]), total_endpoints=int(m[4])),
    unconstrained_io_counts={k:a['check_timing_counts'][k] for k in ['no_input_delay','no_output_delay']},
    listed_setup_sources=dict(Counter(x['source'] for x in timing)),
    listed_setup_destinations_by_top_hierarchy=dict(Counter(x['destination'].split('/')[0] for x in timing)),
    listed_setup_slack_range_ns=[min(x['slack_ns'] for x in timing),max(x['slack_ns'] for x in timing)],
    listed_setup_paths=timing, listed_multiplier_cells=multipliers,
    multiplier_hierarchies=dict(Counter(x['cell'].rsplit('/',1)[0] for x in multipliers)),
    scope='Read-only classification of restored OOC diagnostics. The 1000 listed TIMING-16/18 warnings are not full-design endpoint totals or a representative sample. Multiplier decomposition counts overlap and must not be summed as utilization. Setup/net delays are preplacement estimates. No constraints, waivers, RTL or running jobs changed.')
out = ROOT / 'results/native_methodology_scope_20261027.json'
assert not out.exists()
out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['listed_setup_paths','listed_multiplier_cells','scope']},indent=2))
