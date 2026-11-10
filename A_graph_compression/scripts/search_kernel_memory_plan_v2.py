"""Strict source ABI parser with explicitly verified max_widen_bitwidth64 support."""
from pathlib import Path
import re
from check_vitis_kernel import require

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
            tokens=re.sub(r'^\s*#pragma HLS INTERFACE m_axi\s+', '',line).split()
            require(all(re.fullmatch(r'\w+=\w+',t) for t in tokens),'Unparsed m_axi option text')
            pairs=[t.split('=',1) for t in tokens]
            require(len({p[0] for p in pairs})==len(pairs),'Duplicate m_axi option')
            fields=dict(pairs)
            required={'port','offset','bundle','depth'}
            require(set(fields) in [required,required|{'max_widen_bitwidth'}] and fields['offset']=='slave','unsupported m_axi pragma')
            require('max_widen_bitwidth' not in fields or fields['max_widen_bitwidth']=='64','Only verified widening cap64 is supported')
            require(fields['port'] not in pragmas, 'duplicate m_axi pragma')
            require(fields['depth'].isdigit() and int(fields['depth']) > 0, 'invalid depth')
            pragmas[fields['port']] = fields
    require(set(pragmas) == {a['name'] for a in args if a['pointer']}, 'm_axi argument mismatch')
    for arg in args:
        if arg['pointer']:
            fields = pragmas[arg['name']]
            arg.update(depth=int(fields['depth']), bundle=fields['bundle'],
                       port='M_AXI_' + fields['bundle'].upper())
            if 'max_widen_bitwidth' in fields:arg['max_widen_bitwidth']=int(fields['max_widen_bitwidth'])
            arg['payload_bytes'] = arg['depth'] * arg['element_bytes']
        else:
            arg['port'] = 'S_AXI_CONTROL'
    return args

