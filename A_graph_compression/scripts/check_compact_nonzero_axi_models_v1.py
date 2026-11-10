#!/usr/bin/env python3
"""Independently inspect model bodies, complete wiring and address-only mapping."""
import argparse
import json
from pathlib import Path
import re

from check_vitis_kernel import digest, require

ROOT = Path(__file__).resolve().parents[1]
MARKER = '\n// A_REBASE_WRAPPER_V1: original model above; checked address mapping below.\n'


def compact(text): return re.sub(r'\s+', '', text)


def bindings(text):
    found = re.findall(r'\.(\w+)\s*\(\s*([^()]*)\s*\)', text)
    require(len(found) == len({k for k, _ in found}), 'Duplicate connection')
    remainder = re.sub(r'\.(\w+)\s*\(\s*([^()]*)\s*\)', '', text)
    require(not remainder.replace(',', '').strip(), 'Unsupported connection expression')
    return {k: compact(v) for k, v in found}


def audit_model(original, candidate, bundle):
    public = 'AESL_axi_master_'+bundle; private = 'A_ZERO_BASE_'+public
    require(candidate.count(MARKER) == 1, 'Missing/unexpected wrapper boundary')
    internal, wrapper = candidate.split(MARKER)
    restored, count = re.subn(r'\bmodule\s+'+private+r'\b', 'module '+public, internal, count=1)
    require(count == 1 and restored == original, 'Original storage/guard logic changed')
    old_header = re.search(r'\bmodule\s+'+public+r'\s*\((.*?)\);', original, re.S)
    new_header = re.match(r'module\s+'+public+r'\s*\((.*?)\);', wrapper, re.S)
    require(old_header is not None and new_header is not None and compact(old_header[1]) == compact(new_header[1]), 'Public interface changed')
    ports = [p.strip() for p in old_header[1].split(',')]
    require(len(set(ports)) == len(ports), 'Duplicate original port')
    original_interface = original[:original.index('input done;')+len('input done;')]
    params = re.findall(r'\bparameter\s+(\w+)\s*=\s*([^;]+);', original_interface)
    require(len(params) == 14, 'Missing original parameter')
    tail = wrapper[new_header.end():]
    actual_params = re.findall(r'\bparameter\s+(\w+)\s*=\s*([^;]+);', tail)
    require([(n, compact(v)) for n, v in params] == [(n, compact(v)) for n, v in actual_params], 'Parameters/defaults changed')
    tail = re.sub(r'\bparameter\s+\w+\s*=\s*[^;]+;', '', tail)
    old_decl = re.findall(r'^(?:input|output)\s+[^;]+;', original_interface, re.M)
    new_decl = re.findall(r'^(?:input|output)\s+[^;]+;', tail, re.M)
    require(list(map(compact, old_decl)) == list(map(compact, new_decl)), 'Port type/width/direction changed')
    tail = re.sub(r'^(?:input|output)\s+[^;]+;', '', tail, flags=re.M)
    for channel in ['AW', 'AR']:
        wire = 'A_REBASE_'+channel+'ADDR'
        tail, n = re.subn(r'wire\s+\[63:0\]\s+'+wire+r';', '', tail)
        require(n == 1, 'Translation wire changed')
        tail, n = re.subn(r'assign\s+'+wire+r'\s*=\s*TRAN_'+bundle+'_'+channel+r"ADDR\s*-\s*64'd4096\s*;", '', tail)
        require(n == 1, 'Address translation changed')
    instance = re.search(private+r'\s*#\((.*?)\)\s*original_model\s*\((.*?)\);', tail, re.S)
    require(instance is not None, 'Missing original instance')
    require(bindings(instance[1]) == {n: n for n, _ in params}, 'Original parameters not forwarded')
    expected_ports = {p: ('A_REBASE_AWADDR' if p == 'TRAN_'+bundle+'_AWADDR' else
                          'A_REBASE_ARADDR' if p == 'TRAN_'+bundle+'_ARADDR' else p) for p in ports}
    require(bindings(instance[2]) == expected_ports, 'A non-address signal changed or port omitted')
    tail = tail[:instance.start()]+tail[instance.end():]
    guard = re.search(r'a_axi_model_rebase_guard_v1\s*#\((.*?)\)\s*address_guard\s*\((.*?)\);', tail, re.S)
    require(guard is not None, 'Missing address guard')
    require(bindings(guard[1]) == {'BASE': "64'd4096", 'DEPTH': bundle+'_mem_depth',
                                 'DATA_BITS': bundle+'_DATA_BITWIDTH', 'NAME': '"'+bundle+'"'}, 'Guard parameters changed')
    guard_ports = {n: 'TRAN_'+bundle+'_'+n.upper() for n in
                   ['awvalid', 'awready', 'awaddr', 'awlen', 'awsize', 'awburst',
                    'arvalid', 'arready', 'araddr', 'arlen', 'arsize', 'arburst']}
    guard_ports['clk'] = 'clk'
    require(bindings(guard[2]) == guard_ports, 'Guard bypassed/miswired')
    tail = tail[:guard.start()]+tail[guard.end():]
    require(tail.strip() == 'endmodule', 'Unreviewed wrapper logic')
    return dict(bundle=bundle, preserved_parameters=len(params), preserved_ports=len(ports),
                address_translations=2, original_model_body_exact=True)


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    require(not args.output.exists(), 'Refuse overwrite')
    preparation = ROOT/'results/compact_nonzero_axi_models_preparation_20261029_v1.json'
    plan = json.loads(preparation.read_text())
    require(plan['status'] == 'all30_full_depth_axi_models_wrapped_for_nonzero_addresses_prepared_only', 'Wrong preparation')
    require(len(plan['models']) == 30 and len({m['bundle'] for m in plan['models']}) == 30
            and plan['pointers'] == 44 and plan['transactions'] == 4, 'Incomplete interface scope')
    for name, sha in plan['files'].items(): require(digest(name) == sha, 'Changed model preparation evidence: '+name)
    records = [audit_model(Path(m['source']).read_text(), Path(m['target']).read_text(), m['bundle']) for m in plan['models']]
    files = {**plan['files'], str(preparation): digest(preparation), str(Path(__file__).resolve()): digest(__file__)}
    result = dict(status='all30_original_model_bodies_and_complete_address_wrapper_connections_independently_verified',
                  files=files, models=records, rtl_executed=False, full_kernel_verified=False,
                  limits=['Structural proof only: model contents, parameters and non-address signals unchanged; guard behavior requires simulation.',
                          'Four-transaction full44 acceptance and all original C output checks remain mandatory.'])
    with args.output.open('x') as f: json.dump(result, f, indent=2); f.write('\n')
    print(result['status'], len(records))


if __name__ == '__main__': main()
