#!/usr/bin/env python3
"""Wrap all30 original full-depth models in a checked4096-byte address map."""
import json
from pathlib import Path
import re

from check_vitis_kernel import digest, require

ROOT = Path(__file__).resolve().parents[1]
MARKER = '\n// A_REBASE_WRAPPER_V1: original model above; checked address mapping below.\n'


def interface(text, bundle):
    module = 'AESL_axi_master_'+bundle
    header = re.search(r'\bmodule '+module+r'\s*\((.*?)\);', text, re.S)
    require(header is not None and len(re.findall(r'\bmodule\s+', text)) == 1, 'Unexpected model module')
    ports = [x.strip() for x in header[1].split(',')]
    prefix = text[:text.index('input done;')+len('input done;')]
    parameters = re.findall(r'\bparameter\s+(\w+)\s*=\s*([^;]+);', prefix)
    declarations = re.findall(r'^(?:input|output)\s+[^;]+;', prefix, re.M)
    declared = [re.search(r'(\w+)\s*;$', d)[1] for d in declarations]
    require(len(ports) == len(set(ports)) and set(declared) == set(ports), 'Port declaration mismatch')
    require(len(parameters) == 14 and len({n for n, _ in parameters}) == 14, 'Unexpected parameter interface')
    p = dict(parameters)
    require(p[bundle+'_ADDR_BITWIDTH'].replace(' ', '') == "32'd64" and
            p['mem_page_num'].replace(' ', '') == "32'd4", 'Wrong address width/pages')
    require(p[bundle+'_DATA_BITWIDTH'] == p[bundle+'_C_DATA_BITWIDTH'], 'Packed width conversion not covered')
    return module, ports, parameters, declarations


def wrap(text, bundle):
    module, ports, params, declarations = interface(text, bundle)
    internal = 'A_ZERO_BASE_'+module
    original = re.sub(r'\bmodule '+module+r'\b', 'module '+internal, text, count=1)
    lines = ['module '+module+' (\n    '+',\n    '.join(ports)+'\n);']
    lines += ['parameter '+n+' = '+v+';' for n, v in params]
    lines += declarations
    pre = 'TRAN_'+bundle+'_'
    lines += ['wire [63:0] A_REBASE_AWADDR;', 'wire [63:0] A_REBASE_ARADDR;',
              'assign A_REBASE_AWADDR = '+pre+"AWADDR - 64'd4096;",
              'assign A_REBASE_ARADDR = '+pre+"ARADDR - 64'd4096;",
              internal+' #(\n    '+',\n    '.join('.'+n+'('+n+')' for n, _ in params)+'\n) original_model (']
    connections = [(p, 'A_REBASE_AWADDR' if p == pre+'AWADDR' else 'A_REBASE_ARADDR' if p == pre+'ARADDR' else p) for p in ports]
    lines += ['    '+',\n    '.join('.'+p+'('+v+')' for p, v in connections)+'\n);',
              'a_axi_model_rebase_guard_v1 #(\n    .BASE(64\'d4096), .DEPTH('+bundle+'_mem_depth),',
              '    .DATA_BITS('+bundle+'_DATA_BITWIDTH), .NAME("'+bundle+'")\n) address_guard (',
              '    .clk(clk),']
    lines += ['    '+',\n    '.join('.'+n+'('+pre+n.upper()+')' for n in
                ['awvalid', 'awready', 'awaddr', 'awlen', 'awsize', 'awburst',
                 'arvalid', 'arready', 'araddr', 'arlen', 'arsize', 'arburst'])+'\n);', 'endmodule']
    return original+MARKER+'\n'.join(lines)+'\n'


def main():
    out = ROOT/'data/derived/compact_nonzero_axi_models_20261029_v1'
    report = ROOT/'results/compact_nonzero_axi_models_preparation_20261029_v1.json'
    require(not out.exists() and not report.exists(), 'Refuse overwrite')
    prior_path = ROOT/'results/compact_nonzero_axi_vectors_preparation_20261029_v1.json'
    prior = json.loads(prior_path.read_text())
    require(prior['status'] == 'full44_nonzero_pointer_vectors_prepared_only' and prior['models'] == 30, 'Wrong vector preparation')
    files = dict(prior['files'])
    for p, sha in files.items(): require(digest(p) == sha, 'Changed vector dependency: '+p)
    files[str(prior_path)] = digest(prior_path)
    guard = ROOT/'hardware/vitis/axi_model_rebase_guard_v1.sv'
    files[str(guard)] = digest(guard)
    out.mkdir()
    records = []
    for model in prior['model_mapping_requirements']:
        source = Path(model['original_model']); bundle = model['bundle']; target = out/source.name
        text = source.read_text(); candidate = wrap(text, bundle)
        require(candidate.split(MARKER)[0].replace('module A_ZERO_BASE_AESL_axi_master_'+bundle,
                'module AESL_axi_master_'+bundle, 1) == text, 'Original model was changed')
        target.write_text(candidate)
        files[str(target)] = digest(target)
        records.append(dict(bundle=bundle, source=str(source), source_sha256=digest(source),
                            target=str(target), target_sha256=digest(target),
                            model_body_unchanged_except_module_name=True, address_delta=4096, pages=4))
    files[str(Path(__file__).resolve())] = digest(__file__)
    result = dict(status='all30_full_depth_axi_models_wrapped_for_nonzero_addresses_prepared_only',
                  files=files, models=records, guard_source=str(guard), pointers=44, transactions=4,
                  dut_modified=False, model_storage_unchanged=True, execution_entry_prepared=False, rtl_executed=False,
                  limits=['Wrapper forwards every signal and parameter unchanged except AWADDR/ARADDR minus4096.',
                          'Original memory depth,4pages,input/output files and RO guards remain inside unchanged renamed model.',
                          'Independent structural audit and real model/guard regression are required before any full-kernel run.'])
    with report.open('x') as f: json.dump(result, f, indent=2); f.write('\n')
    print(result['status'], len(records))


if __name__ == '__main__': main()
