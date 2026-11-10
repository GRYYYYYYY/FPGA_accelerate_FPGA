"""Static full-search BO capacity/connectivity plan; never claims board allocation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'hardware/vitis/search_kernel_offsets_v3/search_kernel_top.cpp'
XMLS = {mode: ROOT / f'build/search_kernel_hls_20261024_v3/{mode}/kernel.xml'
        for mode in ('csr', 'compact')}
MIB = 1024 ** 2
KERNEL = 'search_kernel_top'
CU = KERNEL + '_1'
REFERENCES = [
    'https://docs.amd.com/r/en-US/ug1120-alveo-platforms/U280-Gen3x16-XDMA-base_1-Platform',
    'https://xilinx.github.io/Vitis-Tutorials/2021-1/build/html/docs/Hardware_Acceleration/Feature_Tutorials/07-using-hbm/2_Migrating_to_HBM.html',
]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_source(source):
    """Intentionally restricted parser for this frozen production top, not C++."""
    text = Path(source).read_text()
    match = re.search(r'extern "C" void SEARCH_TOP_NAME\((.*?)\)\s*\{', text, re.S)
    require(match is not None, 'unsupported top signature')
    args = []
    for index, decl in enumerate(match.group(1).split(',')):
        ptr = re.fullmatch(r'\s*(const\s+)?uint(32|64)_t\s*\*\s*(\w+)\s*', decl)
        scalar = re.fullmatch(r'\s*unsigned\s+(\w+)\s*', decl)
        require(ptr is not None or scalar is not None, f'unsupported declaration: {decl}')
        if ptr:
            args.append(dict(id=index, name=ptr[3], pointer=True,
                             element_bytes=int(ptr[2]) // 8, const=bool(ptr[1])))
        else:
            args.append(dict(id=index, name=scalar[1], pointer=False, element_bytes=4))
    require(len({a['name'] for a in args}) == len(args), 'duplicate source argument')
    pragmas = {}
    for line in text.splitlines():
        if re.match(r'\s*#pragma HLS INTERFACE m_axi\b', line):
            fields = dict(re.findall(r'(\w+)=(\w+)', line))
            require(set(fields) == {'port', 'offset', 'bundle', 'depth'} and
                    fields['offset'] == 'slave', 'unsupported m_axi pragma')
            require(fields['port'] not in pragmas, 'duplicate m_axi pragma')
            require(fields['depth'].isdigit() and int(fields['depth']) > 0, 'invalid depth')
            pragmas[fields['port']] = fields
    require(set(pragmas) == {a['name'] for a in args if a['pointer']}, 'm_axi argument mismatch')
    for arg in args:
        if arg['pointer']:
            fields = pragmas[arg['name']]
            arg.update(depth=int(fields['depth']), bundle=fields['bundle'],
                       port='M_AXI_' + fields['bundle'].upper())
            arg['payload_bytes'] = arg['depth'] * arg['element_bytes']
        else:
            arg['port'] = 'S_AXI_CONTROL'
    return args


def validate_xml(args, xml):
    kernels = ET.parse(xml).getroot().findall('kernel')
    require(len(kernels) == 1, 'expected one kernel')
    kernel = kernels[0]
    require(kernel.get('name') == KERNEL and kernel.get('hwControlProtocol') == 'ap_ctrl_chain',
            'kernel identity/control mismatch')
    actual = kernel.findall('args/arg')
    require(len(actual) == len(args), 'XML argument count mismatch')
    ports = kernel.findall('ports/port')
    port_map = {p.get('name'): p for p in ports}
    require(len(ports) == len(port_map) and set(port_map) == {a['port'] for a in args},
            'XML port set mismatch')
    abi, control_ranges = [], []
    for expected, observed in zip(args, actual):
        ptr = expected['pointer']
        size = 8 if ptr else 4
        require(int(observed.get('id')) == expected['id'] and observed.get('name') == expected['name'],
                'XML argument order/name mismatch')
        require(observed.get('port') == expected['port'] and
                int(observed.get('addressQualifier')) == int(ptr), 'XML port/qualifier mismatch')
        require(observed.get('type') == ('void*' if ptr else 'unsigned int'), 'XML type mismatch')
        require(all(int(observed.get(f), 0) == size for f in ('hostSize', 'size')) and
                int(observed.get('hostOffset'), 0) == 0, 'XML ABI size mismatch')
        port = port_map[expected['port']]
        require(port.get('mode') == ('master' if ptr else 'slave') and
                port.get('portType') == 'addressable', 'XML port mode mismatch')
        offset = int(observed.get('offset'), 0)
        require(offset >= 16 and offset % 4 == 0, 'invalid control offset')
        require(all(offset + size <= lo or offset >= hi for lo, hi in control_ranges),
                'overlapping control arguments')
        control_ranges.append((offset, offset + size))
        abi.append(dict(id=expected['id'], name=expected['name'], port=expected['port'],
                        control_offset=offset, host_size=size,
                        axi_width=int(port.get('dataWidth'))))
    require(max(hi for _, hi in control_ranges) <= int(port_map['S_AXI_CONTROL'].get('range'), 0),
            'control range too small')
    return abi


def pool(group):
    match = re.fullmatch(r'(HBM|DDR)\[(0|[1-9]\d*)(?::(0|[1-9]\d*))?\]', group)
    require(match is not None, f'invalid memory group: {group}')
    kind, lo, hi = match.groups()
    lo, hi = int(lo), int(hi) if hi is not None else int(lo)
    require(0 <= lo <= hi < (32 if kind == 'HBM' else 2), 'memory channel out of range')
    require(kind != 'DDR' or lo == hi, 'DDR grouping unsupported by this plan')
    channels = frozenset((kind, n) for n in range(lo, hi + 1))
    capacity = len(channels) * (256 * MIB if kind == 'HBM' else 16 * 1024 * MIB)
    return channels, capacity


def validate_layout(args, mapping, alignment=4096, reserve_bytes=16 * MIB):
    require(type(alignment) is int and alignment > 0 and alignment & (alignment - 1) == 0,
            'alignment must be a positive power of two')
    require(type(reserve_bytes) is int and reserve_bytes >= 0, 'invalid reserve')
    buffers = [a for a in args if a['pointer']]
    require(set(mapping) == {a['name'] for a in buffers}, 'missing, extra, or scalar memory mapping')
    pools, bundles, allocations = {}, {}, []
    for arg in buffers:
        group = mapping[arg['name']]
        channels, capacity = pool(group)
        if group not in pools:
            require(all(not channels.intersection(p['channels']) for p in pools.values()),
                    'overlapping memory groups (including aliases)')
            pools[group] = dict(channels=channels, capacity_bytes=capacity, requested_bytes=0,
                                arguments=[])
        previous = bundles.setdefault(arg['bundle'], group)
        require(previous == group, 'shared AXI bundle mapped to different groups')
        size = arg['payload_bytes']
        require(type(size) is int and size > 0, 'invalid buffer size')
        rounded = (size + alignment - 1) // alignment * alignment
        require(rounded <= capacity, f"BO exceeds group capacity: {arg['name']}")
        pools[group]['requested_bytes'] += rounded
        pools[group]['arguments'].append(arg['name'])
        allocations.append(dict(id=arg['id'], name=arg['name'], group=group,
                                payload_bytes=size, requested_bytes=rounded))
    for group, info in pools.items():
        require(info['requested_bytes'] + reserve_bytes <= info['capacity_bytes'],
                f'aggregate requests plus reserve exceed group capacity: {group}')
        info['reserve_bytes'] = reserve_bytes
        info['spare_after_reserve_bytes'] = info['capacity_bytes'] - info['requested_bytes'] - reserve_bytes
        info['channels'] = [f'{kind}[{n}]' for kind, n in sorted(info['channels'])]
    return dict(allocations=allocations, pools=pools,
                total_payload_bytes=sum(a['payload_bytes'] for a in allocations),
                total_requested_bytes=sum(a['requested_bytes'] for a in allocations))


def connectivity(mapping):
    return '\n'.join(['# Static candidate; platform link and real allocation remain required.',
                      '[connectivity]', f'nk={KERNEL}:1:{CU}'] +
                     [f'sp={CU}.{name}:{group}' for name, group in mapping.items()]) + '\n'


def read_connectivity(text):
    lines = [s.strip() for s in text.splitlines() if s.strip() and not s.lstrip().startswith('#')]
    require(lines[:2] == ['[connectivity]', f'nk={KERNEL}:1:{CU}'], 'wrong connectivity kernel')
    mapping = {}
    for line in lines[2:]:
        match = re.fullmatch(r'sp=' + re.escape(CU) + r'\.(\w+):(.+)', line)
        require(match is not None, 'unsupported connectivity line')
        require(match[1] not in mapping, 'duplicate connectivity argument')
        mapping[match[1]] = match[2]
    return mapping


def layouts(args):
    buffers = [a for a in args if a['pointer']]
    split = dict(graph_mem='HBM[0]', input_mem='HBM[1]', heap_mem='HBM[2]',
                 index_mem='HBM[3]', record_mem='HBM[4]', output_mem='HBM[5]', key_mem='HBM[6:7]')
    return {
        'ddr_shared': {a['name']: 'DDR[0]' for a in buffers},
        'hbm_shared': {a['name']: 'HBM[0:3]' for a in buffers},
        'hbm_split': {a['name']: split[a['bundle']] for a in buffers},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='new directory; never overwritten')
    args_cli = parser.parse_args()
    args = parse_source(SOURCE)
    abi = {mode: validate_xml(args, xml) for mode, xml in XMLS.items()}
    require(abi['csr'] == abi['compact'], 'CSR/compact XML ABI differs')
    plans, configs = {}, {}
    for name, mapping in layouts(args).items():
        configs[name] = connectivity(mapping)
        require(read_connectivity(configs[name]) == mapping, 'connectivity roundtrip failed')
        plans[name] = validate_layout(args, read_connectivity(configs[name]))
    out = args_cli.output
    out.mkdir(parents=True, exist_ok=False)
    for name, config in configs.items():
        (out / f'{name}.cfg').write_text(config)
    report = dict(status='static_capacity_and_source_xml_abi_checked_board_unverified',
                  execution_kind='static_memory_plan', kernel=KERNEL, compute_unit=CU,
                  arguments=args, abi=abi, layouts=plans, references=REFERENCES,
                  policy=dict(host_request_alignment_bytes=4096, reserve_bytes_per_pool=16 * MIB,
                              reserve_is_policy_not_measured_free_memory=True,
                              all_thirteen_buffers_simultaneously_resident=True,
                              graph_allocated_at_full_pragma_depth=True),
                  evidence=dict(platform_linked=False, device_allocated=False, hardware_executed=False),
                  limitations=[
                      'Nominal U280 capacities; actual platform memory topology and free capacity must be checked.',
                      'Group connectivity must be validated by v++ link for the installed U280 platform.',
                      'Allocate each BO using kernel.group_id(argument_id); never treat a group ID as a physical MEM_TOPOLOGY bank index.',
                      'HBM split changes topology; it is a separate topology experiment, not a pure DDR/HBM comparison.',
                      'No bandwidth, timing, board availability, performance or power result is established.',
                  ],
                  files={str(p.relative_to(ROOT)): sha(p) for p in
                         [SOURCE, *XMLS.values(), Path(__file__).resolve()]},
                  configs={f'{n}.cfg': sha(out / f'{n}.cfg') for n in configs})
    (out / 'plan.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], output=str(out),
                          total_requested_bytes=plans['ddr_shared']['total_requested_bytes'])))


if __name__ == '__main__':
    main()
