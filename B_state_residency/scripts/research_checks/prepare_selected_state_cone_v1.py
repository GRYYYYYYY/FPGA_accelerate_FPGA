"""Source-bound transition cone with explicitly enumerated retained registers."""
from pathlib import Path
import hashlib
import json
import sys


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    config, out = map(Path, sys.argv[1:])
    assert not out.exists()
    cfg = json.loads(config.read_text())
    source = Path(cfg['source_json'])
    assert sha(source) == cfg['source_json_sha256']
    model = json.loads(source.read_text())
    assert list(model['modules']) == [cfg['module']]
    mod = model['modules'][cfg['module']]
    cells, drivers = mod['cells'], {}
    for name, cell in cells.items():
        for port, bits in cell['connections'].items():
            if cell['port_directions'][port] == 'output':
                for bit in bits:
                    if isinstance(bit, int):
                        assert bit not in drivers
                        drivers[bit] = name
    retain = set()
    for name in cfg['state_names']:
        bits = mod['netnames'][name]['bits']
        names = {drivers[b] for b in bits}
        assert len(names) == 1
        cellname = names.pop()
        cell = cells[cellname]
        assert cell['type'] == '$dff' and cell['connections']['Q'] == bits
        assert cell['connections']['CLK'] == mod['ports'][cfg['clock']]['bits']
        retain.add(cellname)
    pending = [b for n in cfg['state_names'] + cfg['roots']
               for b in mod['netnames'][n]['bits']]
    seen, selected, cuts = set(), {}, {}
    while pending:
        bit = pending.pop()
        if not isinstance(bit, int) or bit in seen:
            continue
        seen.add(bit)
        name = drivers.get(bit)
        if name is None or name in selected:
            continue
        cell = cells[name]
        if cell['type'] in ('$dff', '$memrd', '$memrd_v2') and name not in retain:
            outputs = [(p, bs) for p, bs in cell['connections'].items()
                       if cell['port_directions'][p] == 'output']
            assert len(outputs) == 1
            port, bits = outputs[0]
            assert all(isinstance(b, int) for b in bits)
            assert len(set(bits)) == len(bits)
            selected[name] = {'hide_name': 1, 'type': '$anyseq',
                              'parameters': {'WIDTH': format(len(bits), '032b')},
                              'attributes': {}, 'port_directions': {'Y': 'output'},
                              'connections': {'Y': bits}}
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
                    if p['direction'] == 'input' or n in cfg['roots']}
    for name in cfg['roots']:
        mod['ports'][name] = {'direction': 'output', 'bits': mod['netnames'][name]['bits']}
    for port, net in cfg['observations'].items():
        assert port not in mod['ports']
        mod['ports'][port] = {'direction': 'output', 'bits': mod['netnames'][net]['bits']}
    for net in mod['netnames'].values():
        net.get('attributes', {}).pop('init', None)
    out.mkdir()
    target = out / 'kernel.json'
    target.write_text(json.dumps(model, separators=(',', ':')) + '\n')
    receipt = {'status': 'prepared_transition_overapproximation_not_proved',
               'configuration': cfg, 'configuration_sha256': sha(config),
               'preparer_sha256': sha(Path(__file__)),
               'retained_state_cells': sorted(retain),
               'retained_state_bits': sum(len(cells[n]['connections']['Q']) for n in retain),
               'cuts': cuts, 'selected_cells': len(selected),
               'kernel_json_sha256': sha(target),
               'scope': 'Selected actual transitions retained; other stored/read outputs arbitrary per cycle. Covers are abstraction-only.',
               'full_system_functional_netlist_validated': False,
               'physical_gate_open': False}
    (out / 'preparation.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(out)


if __name__ == '__main__':
    main()
