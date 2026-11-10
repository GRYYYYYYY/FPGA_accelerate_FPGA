#!/usr/bin/env python3
"""Audit physical clock connectivity independently of IS_USED and logical cells."""
from collections import Counter
import json
from pathlib import Path
import re
from check_source_to_route import digest
from real_experiment import write_new
ROOT = Path(__file__).resolve().parents[1]
SHAPES = {'meta': 3, 'site': 3, 'bel': 4, 'bel_pin': 5, 'site_pin': 4,
          'site_pip': 6, 'config': 4, 'net_link': 5, 'node_link': 4, 'cell_link': 4,
          'count': 3, 'complete': 2}


def parse(text, stage):
    rows = {}; meta = {}; counts = {}; complete = False
    for line in text.splitlines():
        fields = line.split('\t'); kind = fields[0]
        if complete or kind not in SHAPES or len(fields) != SHAPES[kind]: raise ValueError('Malformed capture')
        if kind == 'meta':
            if fields[1] in meta: raise ValueError('Duplicate metadata')
            meta[fields[1]] = fields[2]
        elif kind == 'count':
            if fields[1] in counts: raise ValueError('Duplicate count')
            counts[fields[1]] = int(fields[2])
        elif kind == 'complete':
            if fields[1] != stage: raise ValueError('Wrong completion stage')
            complete = True
        else:
            key = tuple(fields[1:3]) if kind in ('config', 'net_link', 'node_link') else (fields[1],)
            if key in rows.setdefault(kind, {}): raise ValueError('Duplicate/ambiguous resource record')
            rows[kind][key] = fields[1:]
    if not complete or meta != {'schema': 'clock_semantics_capture_v3', 'stage': stage,
                                'tool': '2022.2', 'part': 'xcu280-fsvh2892-2L-e'}:
        raise ValueError('Capture metadata/completion differs')
    expected = {'site': 2, 'bel': 8, 'bel_pin': 33, 'site_pin': 13, 'site_pip': 4, 'config': 21}
    if counts != expected or any(len(rows.get(k, {})) != v for k, v in expected.items()):
        raise ValueError('Incomplete clock resource domain')
    if len(rows.get('node_link', {})) != 13: raise ValueError('Missing physical endpoint nodes')
    return rows


def inspect(baseline, probe, request):
    for kind in ('site', 'bel', 'bel_pin', 'site_pin', 'config', 'site_pip'):
        if set(baseline[kind]) != set(probe[kind]): raise ValueError('Physical resource domain changed')
    if baseline['node_link'] != probe['node_link']: raise ValueError('Physical endpoint identity changed')
    if baseline.get('cell_link') or probe.get('cell_link'): raise ValueError('Unexpected explicit clock cells')
    expected_pins = {'BUFCE_ROW_FSR_X21Y6/CE_PRE_OPTINV', 'BUFCE_ROW_FSR_X21Y6/CLK_OUT',
                     'BUFCE_LEAF_X110Y26/CLK_IN', 'BUFCE_LEAF_X110Y26/CLK_LEAF'}
    if baseline.get('net_link'): raise ValueError('Baseline sites already have physical net owners')
    owners = probe.get('net_link', {})
    if set(owners) != {('site_pin', p) for p in expected_pins}: raise ValueError('Incomplete or unexpected clock net ownership')
    for key, value in owners.items():
        if value != ['site_pin', key[1], request['net'], 'SIGNAL']: raise ValueError('Clock endpoint owner differs')
        if probe['node_link'][key][2] not in request['nodes']: raise ValueError('Endpoint not in verified probe path')
    used = {key[0] for key, value in probe['site_pip'].items() if value[1] == '1'}
    if used != {'BUFCE_ROW_FSR_X21Y6/CEINV:CE_PREINV', 'BUFCE_LEAF_X110Y26/IINV:I_PREINV'}:
        raise ValueError('Actual internal PIP selection differs')
    if any(v[1] != '0' for v in baseline['site_pip'].values()): raise ValueError('Baseline internal PIP already used')
    changes = {key[0]+'/'+key[1]: {'baseline': baseline['config'][key][2], 'probe': value[2]}
               for key, value in probe['config'].items() if value != baseline['config'][key]}
    if changes != {'BUFCE_ROW_FSR_X21Y6/BUFCE/CONFIG.CE_TYPE': {'baseline': 'NOT CONFIGURED', 'probe': 'ASYNC'},
                   'BUFCE_LEAF_X110Y26/LCLK_TEST_DELAY/CONFIG.DELAY': {'baseline': 'NOT CONFIGURED', 'probe': 'VAL0'}}:
        raise ValueError('Configuration changes differ from validated probe')
    false_unused = sorted(p for p in expected_pins if probe['site_pin'][(p,)][2] == '0')
    return {'physical_signal_owners': list(owners.values()), 'used_site_pips': sorted(used),
            'configuration_changes': changes, 'connected_pins_reporting_is_used_zero': false_unused,
            'internal_bel_net_links': sum(key[0] == 'bel_pin' for key in owners),
            'constant_net_links': [v for v in owners.values() if v[-1] in ('POWER', 'GROUND')]}


def main():
    folder = ROOT/'data/netlist/clock_semantics_capture_20261023_v3'
    request_path = ROOT/'results/clock_row_probe_input_20261023_v1.json'
    request = json.loads(request_path.read_text())
    proof_path = ROOT/'data/netlist/clock_row_route_probe_full_20261023_v2/verification.json'
    proof = json.loads(proof_path.read_text())
    if proof['status'] != 'full_context_probe_readback_and_drc_passed' or proof['net'] != request['net']:
        raise ValueError('Full physical probe not verified')
    for path, value in proof['files'].items():
        if digest(path) != value: raise ValueError('Physical proof changed: '+path)
    stages = {name: parse((folder/(name+'.tsv')).read_text(), name) for name in ('baseline', 'probe')}
    findings = inspect(stages['baseline'], stages['probe'], request)
    netlists = {stage: ROOT/f'data/netlist/clock_semantics_capture_20261023_v1/{stage}.timesim.v' for stage in stages}
    findings['explicit_bufce_instances_in_timesim'] = {stage: len(re.findall(r'\bBUFCE_(?:ROW|LEAF)\s*(?:#\s*\(|\\?\w+\s*\()', p.read_text())) for stage, p in netlists.items()}
    paths = [Path(__file__), ROOT/'adapters/capture_clock_semantics_20261023_v3.tcl', request_path, proof_path,
             *netlists.values(), *[folder/(s+'.tsv') for s in stages]]
    write_new(ROOT/'results/clock_semantics_capture_20261023_v1.json',
              {'status': 'physical_clock_connectivity_audited_internal_constant_gap_retained', 'findings': findings,
               'counts_per_stage': {k: len(v) for k, v in stages['probe'].items()},
               'files': {str(p): digest(p) for p in paths},
               'limitations': ['IS_USED=0 is not an availability oracle: four physically connected pins report zero.',
                              'No explicit BUFCE cells or internal constant bindings were exported; empty links do not prove an input constant.',
                              'Site PIP names describe selected arcs, not verified Boolean inversion values.',
                              'No additional pseudo instances are authorized by this observational capture.',
                              'v1 omitted routing BEL pins; v2 was mislabelled by MCP duplicate suppression and is explicitly invalid. v3 is authoritative.']})
    print(json.dumps(findings))


if __name__ == '__main__': main()
