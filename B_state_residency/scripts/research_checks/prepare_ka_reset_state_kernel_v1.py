"""Keep four actual state words; overapproximate all other stored outputs."""
from pathlib import Path
import hashlib
import json
import sys


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    root, out = map(Path, sys.argv[1:])
    assert not out.exists()
    receipt = json.loads((root / 'manifest.json').read_text())
    assert receipt['status'] == 'lowered_observed'
    graph = root / 'full.json'
    assert sha(graph) == receipt['json_sha256']
    model = json.loads(graph.read_text())
    mod = model['modules']['query_residency_system']
    cells = mod['cells']
    state_names = ['inner.backend.recovery_ctl.state', 'authority.state',
                   'authority.target', 'authority.active_bank']
    roots = ['k_a_valid', 'k_busy', 'as_initial_safe', 'as_attempt_reset']
    drivers = {}
    for name, cell in cells.items():
        for port, bits in cell['connections'].items():
            if cell['port_directions'][port] == 'output':
                for bit in bits:
                    if isinstance(bit, int):
                        assert bit not in drivers, ('multiple drivers', bit)
                        drivers[bit] = name
    retain = set()
    for name in state_names:
        bits = mod['netnames'][name]['bits']
        matches = {drivers[b] for b in bits}
        assert len(matches) == 1
        cellname = matches.pop()
        assert cells[cellname]['type'] == '$dff'
        assert cells[cellname]['connections']['Q'] == bits
        assert cells[cellname]['connections']['CLK'] == mod['ports']['clk']['bits']
        retain.add(cellname)
    assert len(retain) == 4
    pending = [b for n in roots + state_names for b in mod['netnames'][n]['bits']]
    seen_bits, selected, cuts = set(), {}, {}
    while pending:
        bit = pending.pop()
        if not isinstance(bit, int) or bit in seen_bits:
            continue
        seen_bits.add(bit)
        name = drivers.get(bit)
        if name is None or name in selected:
            continue
        cell = cells[name]
        is_state = cell['type'] in ('$dff', '$memrd', '$memrd_v2')
        if is_state and name not in retain:
            outputs = [(p, b) for p, b in cell['connections'].items()
                       if cell['port_directions'][p] == 'output']
            assert len(outputs) == 1
            port, bits = outputs[0]
            assert all(isinstance(b, int) for b in bits)
            assert len(set(bits)) == len(bits)
            selected[name] = {
                'hide_name': 1, 'type': '$anyseq',
                'parameters': {'WIDTH': format(len(bits), '032b')},
                'attributes': {}, 'port_directions': {'Y': 'output'},
                'connections': {'Y': bits},
            }
            cuts[name] = {'original_type': cell['type'], 'original_port': port,
                          'bits': bits}
        else:
            assert cell['type'] not in ('$memwr_v2', '$meminit', '$meminit_v2')
            selected[name] = cell
            for port, bits in cell['connections'].items():
                if cell['port_directions'][port] == 'input':
                    pending.extend(bits)
    assert retain <= selected.keys()
    mod['cells'] = selected
    mod.pop('memories', None)
    mod['ports'] = {n: p for n, p in mod['ports'].items()
                    if p['direction'] == 'input' or n in roots}
    observations = {}
    for i, name in enumerate(state_names):
        port = 'f_state_' + str(i)
        mod['ports'][port] = {'direction': 'output',
                              'bits': mod['netnames'][name]['bits']}
        observations[port] = name
    for name in roots:
        mod['ports'][name] = {'direction': 'output',
                             'bits': mod['netnames'][name]['bits']}
    init_removed = 0
    for net in mod['netnames'].values():
        if 'init' in net.get('attributes', {}):
            net['attributes'].pop('init')
            init_removed += 1
    out.mkdir()
    target = out / 'kernel.json'
    target.write_text(json.dumps(model, separators=(',', ':')) + '\n')
    report = {
        'status': 'prepared_actual_four_state_transition_overapproximation',
        'source_json': str(graph.resolve()), 'source_json_sha256': sha(graph),
        'preparer_sha256': sha(Path(__file__)),
        'retained_state_cells': sorted(retain), 'retained_state_bits': 9,
        'retained_state_names': state_names, 'observations': observations,
        'cuts': cuts, 'selected_cells': len(selected),
        'removed_init_attributes': init_removed,
        'kernel_json_sha256': sha(target),
        'scope': 'Actual transition logic and shared state bits retained. Other stored/read outputs arbitrary per cycle. Safety overapproximation; covers need full RTL replay for actual reachability.',
        'full_system_functional_netlist_validated': False,
        'physical_gate_open': False,
    }
    (out / 'preparation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out)


if __name__ == '__main__':
    main()
