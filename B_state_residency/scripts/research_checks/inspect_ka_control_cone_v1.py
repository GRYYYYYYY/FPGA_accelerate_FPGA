"""Structural KA fanin inspection. No reachability or equivalence verdict."""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import sys


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    root = Path(sys.argv[1]).resolve()
    output = Path(sys.argv[2]).resolve()
    assert not output.exists(), 'preserve existing evidence'
    receipt = json.loads((root / 'manifest.json').read_text())
    assert receipt['status'] == 'lowered_observed'
    graph = root / 'full.json'
    assert sha(graph) == receipt['json_sha256']
    modules = json.loads(graph.read_text())['modules']
    assert list(modules) == ['query_residency_system'], list(modules)
    module = modules['query_residency_system']
    cells = module['cells']
    drivers = defaultdict(set)
    memory_cells = defaultdict(set)
    inputs = {}
    for name, cell in cells.items():
        directions = cell['port_directions']
        inputs[name] = set()
        for port, bits in cell['connections'].items():
            if directions[port] == 'input':
                inputs[name].update(bit for bit in bits if isinstance(bit, int))
            elif directions[port] == 'output':
                for bit in bits:
                    if isinstance(bit, int):
                        drivers[bit].add(name)
            else:
                raise AssertionError(('unsupported port direction', name, port))
        memid = cell.get('parameters', {}).get('MEMID')
        if memid is not None:
            memory_cells[memid].add(name)

    def inspect(signal, stop_at_state):
        pending = list(module['netnames'][signal]['bits'])
        seen_bits, seen_cells, boundaries = set(), set(), set()
        while pending:
            bit = pending.pop()
            if not isinstance(bit, int) or bit in seen_bits:
                continue
            seen_bits.add(bit)
            for name in drivers[bit]:
                if name in seen_cells:
                    continue
                seen_cells.add(name)
                cell = cells[name]
                typ = cell['type'].lower()
                state = ('dff' in typ or 'latch' in typ or
                         typ in ('$ff', '$sr') or typ.startswith('$mem'))
                if stop_at_state and state:
                    boundaries.add(name)
                    continue
                pending.extend(inputs[name])
                # Memory write ports have implicit dependence on read ports.
                # Include all ports of the same MEMID rather than dropping it.
                memid = cell.get('parameters', {}).get('MEMID')
                if memid is not None:
                    for peer in memory_cells[memid]:
                        if peer not in seen_cells:
                            seen_cells.add(peer)
                            pending.extend(inputs[peer])
        primary = {name: sorted(set(port['bits']) & seen_bits)
                   for name, port in module['ports'].items()
                   if port['direction'] == 'input'}
        return {'cells': sorted(seen_cells), 'bits': len(seen_bits),
                'cell_types': dict(Counter(cells[n]['type'] for n in seen_cells)),
                'state_boundaries': sorted(boundaries),
                'primary_input_bits': {k: v for k, v in primary.items() if v}}

    report = {
        'status': 'full_actual_rtl_structural_ka_fanin_only',
        'input_json': str(graph), 'input_json_sha256': sha(graph),
        'manifest_sha256': sha(root / 'manifest.json'),
        'inspector_sha256': sha(Path(__file__)),
        'parameters': receipt['parameters'],
        'cones': {signal: {'combinational': inspect(signal, True),
                           'transitive': inspect(signal, False)}
                  for signal in ('k_a_valid', 'k_a_ready')},
        'limitations': ['structural bit dependencies overapproximate logic',
                        'state-boundary classification is diagnostic only',
                        'no behavioral abstraction or assumptions have been proved',
                        'not a reachability or functional-equivalence result'],
        'full_system_functional_netlist_validated': False,
        'physical_gate_open': False,
    }
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(output)


if __name__ == '__main__':
    main()
