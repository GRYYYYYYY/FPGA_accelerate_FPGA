"""Classify already-restored 2022.2 reports; do not alter RTL or constraints."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/B_state_residency_offer_20261025')
TARGET = BASE / 'checkpoint_edit_route_recovery_v1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_diagnostics(text):
    summary, details = text.split('2. REPORT DETAILS\n-----------------', 1)
    total = int(re.search(r'Violations found:\s*(\d+)', summary)[1])
    rules = {}
    for line in summary.splitlines():
        fields = [x.strip() for x in line.split('|')]
        if len(fields) == 6 and re.fullmatch(r'[A-Z][A-Z0-9_-]*-\d+', fields[1]):
            name, severity, description, count = fields[1:5]
            assert name not in rules
            rules[name] = dict(severity=severity, description=description, count=int(count))
    headers = list(re.finditer(
        r'^([A-Z][A-Z0-9_-]*-\d+)#(\d+) (Critical Warning|Warning|Error|Advisory|Info)\s*$',
        details, re.M))
    entries = []
    for i, match in enumerate(headers):
        end = headers[i + 1].start() if i + 1 < len(headers) else len(details)
        body = details[match.end():end].strip()
        entries.append(dict(rule=match[1], index=int(match[2]), severity=match[3], details=body))
    assert total == sum(v['count'] for v in rules.values()) == len(entries)
    assert Counter(x['rule'] for x in entries) == Counter({k: v['count'] for k, v in rules.items()})
    for name, rule in rules.items():
        selected = [x for x in entries if x['rule'] == name]
        assert [x['index'] for x in selected] == list(range(1, rule['count'] + 1))
        assert all(x['severity'] == rule['severity'] for x in selected)
        assert all(x['details'].splitlines()[0].strip() == rule['description'] for x in selected)
    return dict(total=total, rules=rules,
                severity_counts=dict(Counter(x['severity'] for x in entries)), entries=entries)


def main():
    owner = BASE / 'checkpoint_edit_route_recovery_followup_v1/manifest.json'
    gate = json.loads(owner.read_text())
    assert gate['status'] == 'observed' and gate['stage'] == 'complete'
    proc = Path('/proc', str(gate['runner_pid']), 'stat')
    if proc.exists():
        assert proc.read_text().split(') ', 1)[1].split()[19] != str(gate['runner_start_ticks'])
    audit_file = TARGET / 'source_bound_audit.json'
    audit = json.loads(audit_file.read_text())
    restore_file = ROOT / 'results/checkpoint_edit_route_recovery_v1_restore_20261025.json'
    restore = json.loads(restore_file.read_text())
    assert audit['status'] == restore['status'] == 'passed' and restore['audit_byte_identical']
    assert restore['audit_sha256'] == sha(audit_file)
    navigation_file = ROOT / 'results/checkpoint_edit_route_recovery_timing_20261030.json'
    navigation = json.loads(navigation_file.read_text())
    assert navigation['audit_sha256'] == sha(audit_file)
    physical_manifest = ROOT / 'results/checkpoint_edit_route_recovery_sources_20261030/manifest.json'
    assert navigation['physical_freeze_manifest_sha256'] == sha(physical_manifest)
    timing_manifest = ROOT / 'results/checkpoint_edit_route_recovery_timing_sources_20261030/manifest.json'
    timing_files = json.loads(timing_manifest.read_text())['files']
    nav_entry = timing_files['observations/' + navigation_file.name]
    assert sha(navigation_file) == nav_entry['sha256']
    assert sha(timing_manifest.parent / 'observations' / navigation_file.name) == nav_entry['sha256']
    parsed = {}
    files = [Path(__file__).resolve(), audit_file, restore_file, owner, navigation_file,
             physical_manifest, timing_manifest]
    for kind, first, second in [
        ('drc', 'drc_routed.rpt', 'inspection/drc.rpt'),
        ('methodology', 'methodology_routed.rpt', 'inspection/methodology.rpt'),
    ]:
        pair = []
        for name in [first, second]:
            report = TARGET / name
            assert sha(report) == audit['artifact_sha256'][name]
            pair.append(parse_diagnostics(report.read_text()))
            files.append(report)
        assert pair[0] == pair[1], (kind, 'routed/reopened detail mismatch')
        parsed[kind] = pair[0]
    assert parsed['drc']['total'] == navigation['drc_violation_count']
    checks = [x for x in parsed['drc']['entries'] if x['rule'] == 'CHECK-2']
    unchecked = []
    for x in checks:
        match = re.search(r'^(.+?) rule not checked: (.+)$', x['details'], re.M)
        assert match
        unchecked.append(dict(rule=match[1], reason=match[2]))
    rt = [x for x in parsed['drc']['entries'] if x['rule'] == 'RTSTAT-10']
    assert len(rt) == 1
    unroutable_loads = int(re.search(r'(\d+) net\(s\) have no routable loads', rt[0]['details'])[1])
    worst = navigation['observations']['routed']['worst']['Setup']
    out = ROOT / 'results/checkpoint_edit_route_diagnostics_20261030.json'
    freeze = ROOT / 'results/checkpoint_edit_route_diagnostics_sources_20261030'
    assert not out.exists() and not freeze.exists()
    result = dict(
        status='restored_reports_classified_no_fix',
        analyzer_sha256=sha(__file__),
        bound={str(p): sha(p) for p in files},
        drc=parsed['drc'], methodology=parsed['methodology'],
        unchecked_rules=unchecked, nets_without_routable_loads=unroutable_loads,
        independent_reopen_details_identical=True,
        timing_checks=audit['timing_checks']['routed'],
        timing_summary=audit['timing_summaries']['routed'],
        worst_setup={k: worst[k] for k in ['source', 'destination', 'slack_ns', 'data_delay_ns',
            'logic_levels', 'logic_delay_ns', 'net_delay_ns', 'primitive_counts',
            'largest_delay_data_nets', 'highest_fanout_data_nets']},
        observations=[
            'DRC contains 37 Warning and 47 Advisory entries; zero reported Error/Critical Warning.',
            'All 47 CHECK-2 entries say Too many IO ports; those checks did not execute.',
            'RTSTAT-10 is one grouped warning describing 4344 nets, not one net.',
            'TIMING-16 and TIMING-18 each contain 1000 printed entries. This is not a claim about the total affected endpoints or ports.',
            'No multiplier primitive appears among the 48 logic levels of the printed worst setup path; DSP pipeline advisories alone do not identify this path bottleneck.',
        ],
        constraints_changed=False, rtl_changed=False, waivers_created=False,
        timing_qualified=False, board_acceptance=False,
        next_investigation='Trace config_restore descriptor write enable and recovery publication guards in the exact 133-source CP baseline. Preserve same-cycle cancellation, drift checks and checkpoint publication.',
        limitations=['Read-only classification of existing 2022.2 reports; no new implementation.',
                     'External I/O delay, physical clock-source and partition-pin locations remain unspecified.',
                     'Routable-net completion and zero reported DRC errors do not establish board readiness.'])
    assert parsed['drc']['severity_counts'] == {'Warning': 37, 'Advisory': 47}
    assert len(unchecked) == 47 and {x['reason'] for x in unchecked} == {'Too many IO ports'}
    assert not any('DSP' in k for k in worst['primitive_counts'])
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    files.append(out)
    freeze.mkdir()
    copied = {}
    for i, source in enumerate(files):
        name = f'{i:02d}_{source.name}'
        shutil.copyfile(source, freeze / name)
        copied[name] = dict(source=str(source), sha256=sha(source))
        assert sha(freeze / name) == copied[name]['sha256']
    (freeze / 'manifest.json').write_text(json.dumps(dict(status='frozen', files=copied,
        scope='Derived report classification only; no new design acceptance.'), indent=2, sort_keys=True) + '\n')
    print('ROUTE_DIAGNOSTICS_FROZEN', len(copied), 'DRC', parsed['drc']['severity_counts'])


if __name__ == '__main__':
    main()
