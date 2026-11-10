#!/usr/bin/env python3
"""Freeze one algorithmic experiment: insertion sort to bottom-up merge sort."""
import argparse
from datetime import datetime, timezone
import difflib
import json
from pathlib import Path
from check_vitis_kernel import digest, require

ROOT = Path(__file__).resolve().parents[1]
OLD_SORT = '''        for(uint32_t i=1;i<degree;i++) {
            EdgeRecord value=buffer[i];uint32_t j=i;
            while(j>0 && less_edge(value,buffer[j-1])) {buffer[j]=buffer[j-1];j--;}
            buffer[j]=value;
        }'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    baseline = ROOT/'data/derived/vitis_graph_kernel_20261023_v2'
    bp = baseline/'plan.json'
    plan = json.loads(bp.read_text())
    kernel_audit = ROOT/'results/vitis_graph_kernel_audit_20261023_v2.json'
    ooc_audit = ROOT/'results/vitis_ooc_audit_20261023_v1.json'
    kernel = json.loads(kernel_audit.read_text()); ooc = json.loads(ooc_audit.read_text())
    require(kernel['status'] == 'verified_vitis_xo_not_platform_linked' and ooc['all_quality_gates_pass'],
            'Audited baseline not available')
    fixtures = ROOT/'data/derived/vitis_stratified_fixtures_20261023_v1'
    fp = fixtures/'plan.json'; fixture = json.loads(fp.read_text())
    files = {**plan['files'], **plan['generated'], **kernel['artifacts'], **ooc['files'],
             **fixture['files'], **fixture['generated']}
    for name, sha in files.items():
        require(digest(name) == sha, 'Frozen baseline changed: '+name)
    dependencies = [Path(__file__).resolve(), bp, kernel_audit, ooc_audit, fp,
                    ROOT/'hardware/vitis/merge_sort.hpp', ROOT/'hardware/vitis/test_merge_sort.cpp']
    files.update({str(path): digest(path) for path in dependencies})
    old = (baseline/'compact/graph_body.cpp').read_text()
    require(old.count(OLD_SORT) == 1 and old.count('static EdgeRecord expand_rule(') == 1,
            'Unrecognized baseline sorting stage')
    new = old.replace(OLD_SORT, '        sort_edges_merge(buffer,degree);')
    new = new.replace('static EdgeRecord expand_rule(', '#include "merge_sort.hpp"\nstatic EdgeRecord expand_rule(', 1)
    out = a.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    (out/'graph_body.cpp').write_text(new)
    for name in ['graph_body.hpp','graph_accel.cpp','graph_accel.hpp','test_graph_expand.cpp']:
        (out/name).write_bytes((baseline/'compact'/name).read_bytes())
    for name in ['merge_sort.hpp','test_merge_sort.cpp']:
        (out/name).write_bytes((ROOT/'hardware/vitis'/name).read_bytes())
    (out/'algorithm.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),
        fromfile='baseline/graph_body.cpp',tofile='merge/graph_body.cpp')))
    full = (baseline/'compact/full.txt').read_text()
    stratified = (fixtures/'compact/rtl.txt').read_text()
    (out/'full.txt').write_text(full)
    (out/'rtl.txt').write_text(stratified)
    (out/'validation.txt').write_text(full.rstrip()+'\n'+stratified)
    experiment = {'created_utc': datetime.now(timezone.utc).isoformat(), 'files': files,
        'generated': {str(path):digest(path) for path in out.iterdir() if path.is_file()},
        'change': 'Replace only insertion sort with stable bottom-up merge sort using one MAX_DEGREE scratch buffer; no lookup/interface/clock/exception changes.',
        'hypothesis': {'expected': 'Reduce quadratic record shifts on high-degree rows at the cost of a second BRAM buffer and potentially slower low-degree rows.',
                       'confirm': 'Identical full golden records and guards; synthesized merge structure; lower matched high-degree RTL cycles with acceptable internal timing/resources.',
                       'falsify': 'Incorrect output, ignored scratch binding, unexpected schedule, or high-degree cycles not reduced; low-degree regressions must also be reported.'},
        'baseline': {'kernel_audit':str(kernel_audit),'ooc_audit':str(ooc_audit),
                     'stratified_pipeline':str(ROOT/'data/derived/vitis_stratified_cosim_20261023_v1/pipeline.json')},
        'scope': 'Classic HLS2022.2 isolated versioned experiment; not the Unified IDE hls-optimize workflow. No FPGA speedup claim before matched RTL and implementation checks.',
        'initial_status':'prepared_not_executed'}
    with (out/'plan.json').open('x') as stream:
        json.dump(experiment,stream,indent=2); stream.write('\n')
    print(json.dumps({'output':str(out),'status':experiment['initial_status']}))


if __name__ == '__main__':
    main()
