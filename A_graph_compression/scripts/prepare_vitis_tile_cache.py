#!/usr/bin/env python3
"""Prepare one per-node tile-cache variant; preserve baseline ABI and sorting."""
import argparse
import difflib
import json
from pathlib import Path
from check_vitis_kernel import digest, require
from profile_vitis_decoder import once

ROOT = Path(__file__).resolve().parents[1]
HELPER = '''struct TileCache { bool valid; int32_t x,y; uint32_t tile; };
static uint32_t cached_tile_lookup(const uint32_t *im, const uint32_t *c,
        int32_t x, int32_t y, bool &ok, TileCache &cache) {
    if(cache.valid && cache.x==x && cache.y==y)return cache.tile;
    bool local_ok=true;
    uint32_t tile=tile_lookup(im,c,x,y,local_ok);
    cache.valid=local_ok;
    if(local_ok) {cache.x=x;cache.y=y;cache.tile=tile;}
    if(!local_ok)ok=false;
    return tile;
}
'''


def transform(old):
    new = once(old, 'static uint32_t alias_lookup(', HELPER+'static uint32_t alias_lookup(')
    new = once(new, 'bool patch, uint32_t attr, bool &ok) {',
               'bool patch, uint32_t attr, bool &ok, TileCache &tile_cache) {')
    new = once(new, 'uint32_t tile=tile_lookup(im,c,(int32_t)tx,(int32_t)ty,ok);',
               'uint32_t tile=cached_tile_lookup(im,c,(int32_t)tx,(int32_t)ty,ok,tile_cache);')
    new = once(new, '        uint32_t anchor=im[nbase+2];',
               '        TileCache tile_cache={false,0,0,0};\n        uint32_t anchor=im[nbase+2];')
    new = once(new, 'c[RULE_BASE]+7*i,patch,attr,ok);', 'c[RULE_BASE]+7*i,patch,attr,ok,tile_cache);')
    return once(new, 'c[ADD_BASE]+7*(as+i),false,0,ok);', 'c[ADD_BASE]+7*(as+i),false,0,ok,tile_cache);')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    baseline=ROOT/'data/derived/vitis_graph_kernel_20261023_v2'
    fixtures=ROOT/'data/derived/vitis_stratified_fixtures_20261023_v1'
    audit=ROOT/'results/vitis_graph_kernel_audit_20261023_v2.json'
    require(json.loads(audit.read_text())['status']=='verified_vitis_xo_not_platform_linked','Baseline audit missing')
    files={}
    for plan_path in [baseline/'plan.json',fixtures/'plan.json']:
        plan=json.loads(plan_path.read_text())
        files.update(plan['files']);files.update(plan['generated'])
        files[str(plan_path)]=digest(plan_path)
    for path in [Path(__file__).resolve(),ROOT/'scripts/profile_vitis_decoder.py',
                 ROOT/'scripts/check_vitis_kernel.py',ROOT/'hardware/vitis/test_tile_cache.cpp',audit]:
        files[str(path)]=digest(path)
    for path,sha in files.items():require(digest(path)==sha,'Frozen input changed: '+path)
    old=(baseline/'compact/graph_body.cpp').read_text();new=transform(old)
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    (out/'graph_body.cpp').write_text(new)
    for name in ['graph_body.hpp','graph_accel.cpp','graph_accel.hpp','test_graph_expand.cpp']:
        (out/name).write_bytes((baseline/'compact'/name).read_bytes())
    (out/'test_tile_cache.cpp').write_bytes((ROOT/'hardware/vitis/test_tile_cache.cpp').read_bytes())
    (out/'algorithm.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),
        fromfile='baseline/graph_body.cpp',tofile='tile_cache/graph_body.cpp')))
    for name,source in [('full',baseline/'compact/full.txt'),('rtl',fixtures/'compact/rtl.txt')]:
        (out/(name+'.txt')).write_bytes(source.read_bytes())
    (out/'validation.txt').write_text((out/'full.txt').read_text().rstrip()+'\n'+(out/'rtl.txt').read_text())
    plan={'status':'prepared_not_executed','files':files,
          'generated':{str(path):digest(path) for path in out.iterdir()},
          'change':'One last-successful tile coordinate/result cache local to each decode; templates and additions share it. Invalid lookup invalidates the cache. No alias/sort/ABI/pragma change.',
          'hypothesis':'Repeated consecutive edge tile coordinates can avoid binary tile lookup; synthesis control overhead and row workload may offset savings.',
          'limitations':['Static graph within each request required, as for baseline.',
                         'Cache resets per node and cannot retain graph/config identity across requests.',
                         'CPU counts do not establish RTL or board performance.']}
    (out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    print(json.dumps({'output':str(out),'status':plan['status']}))


if __name__=='__main__':main()
