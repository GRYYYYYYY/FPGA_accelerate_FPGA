"""Retain actual KA combinational cells; overapproximate state outputs."""
from pathlib import Path
import hashlib
import json
import sys


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    root, cone_path, out = map(Path, sys.argv[1:])
    assert not out.exists()
    receipt = json.loads((root / 'manifest.json').read_text())
    assert receipt['status'] == 'lowered_observed'
    graph = root / 'full.json'
    assert sha(graph) == receipt['json_sha256']
    cone = json.loads(cone_path.read_text())
    assert cone['input_json_sha256'] == sha(graph)
    model = json.loads(graph.read_text())
    module = model['modules']['query_residency_system']
    selected = cone['cones']['k_a_ready']['combinational']
    keep = set(selected['cells'])
    boundary = set(selected['state_boundaries'])
    assert set(cone['cones']['k_a_valid']['combinational']['cells']) <= keep
    original_cells = module['cells']
    cells, cuts = {}, {}
    for name in sorted(keep):
        cell = original_cells[name]
        if name not in boundary:
            assert cell['type'] not in ('$dff', '$memrd')
            cells[name] = cell
            continue
        assert cell['type'] in ('$dff', '$memrd'), cell['type']
        outputs = [(port, bits) for port, bits in cell['connections'].items()
                   if cell['port_directions'][port] == 'output']
        assert len(outputs) == 1
        port, bits = outputs[0]
        assert all(isinstance(b, int) for b in bits)
        assert len(set(bits)) == len(bits)
        cells[name] = {
            'hide_name': 1, 'type': '$anyseq',
            'parameters': {'WIDTH': format(len(bits), '032b')},
            'attributes': {'ka_cut_original_type': cell['type']},
            'port_directions': {'Y': 'output'}, 'connections': {'Y': bits},
        }
        cuts[name] = {'original_type': cell['type'], 'original_output': port,
                      'bits': bits}
    module['cells'] = cells
    module.pop('memories', None)
    roots = ['k_a_valid', 'k_a_ready', 'k_busy', 'ap_offer', 'ap_owned',
             'as_initial_safe', 'as_attempt_reset', 'as_cfg_lease', 'pc_owned']
    module['ports'] = {n: p for n, p in module['ports'].items()
                       if p['direction'] == 'input' or n in roots}
    for name in roots:
        if name not in module['ports']:
            module['ports'][name] = {'direction': 'output',
                                    'bits': module['netnames'][name]['bits']}
    # Initial state is intentionally unconstrained in this combinational cut.
    removed_init = 0
    for net in module['netnames'].values():
        if 'init' in net.get('attributes', {}):
            del net['attributes']['init']
            removed_init += 1
    out.mkdir()
    target = out / 'cut.json'
    target.write_text(json.dumps(model, separators=(',', ':')) + '\n')
    report = {
        'status': 'prepared_actual_comb_logic_arbitrary_state_outputs',
        'scope': 'Two-state combinational overapproximation, not a sequential model',
        'source_graph': str(graph.resolve()), 'source_graph_sha256': sha(graph),
        'cone_report_sha256': sha(cone_path),
        'preparer_sha256': sha(Path(__file__)),
        'retained_comb_cells': len(keep - boundary), 'cuts': cuts,
        'removed_initial_attributes': removed_init,
        'cut_json_sha256': sha(target), 'roots': roots,
        'limitations': ['all state and memory-read outputs arbitrary',
                        'no consistency between separate memory reads imposed',
                        'SAT witness may be unreachable in actual RTL',
                        'neither full-system equivalence nor physical acceptance'],
        'full_system_functional_netlist_validated': False,
        'physical_gate_open': False,
    }
    (out / 'preparation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out)


if __name__ == '__main__':
    main()
