#!/usr/bin/env python3
"""Bind and run already compiled differential drivers for word-key search."""
import json
from pathlib import Path
import shutil
import subprocess
from prepare_search_heap_router import ROOT,digest

OUT=ROOT/'data/derived/word_controller_checks_20261024_v1'
TEMP=Path('/tmp/a_word_controller_20261024')
NAMES=['test_search_controller','test_search_controller_bounds','test_search_snapshot_provider','test_search_snapshot_cxx14']

def expected_driver(name):
    s=(ROOT/'tests'/(name+'.cpp')).read_text()
    if name=='test_search_snapshot_cxx14':
        return s.replace('#include "search_snapshot_provider.hpp"','#include "search_snapshot_provider.hpp"\n#include "search_controller_words.hpp"').replace('using Core=Provider::Core;','using Core=fpga_search::WordSearchController<StaticLimits>;').replace('Core::Key keys[8]{};','uint64_t keys[8*Core::Index::Storage::Words]{};')
    s=s.replace('search_controller_adapter.hpp','search_word_controller_adapter.hpp').replace('controller_adapter::','word_controller_adapter::')
    s=s.replace('using Core=Provider::Core;','using Core=fpga_search::WordSearchController<SnapshotLimits>;').replace('using Core=fpga_search::SearchController<BoundsLimits>;','using Core=fpga_search::WordSearchController<BoundsLimits>;')
    for name in ['site_search.hpp','site_ledger.hpp','search_word_controller_adapter.hpp']:s=s.replace('../src/native/'+name,str(ROOT/'src/native'/name))
    return s

def verify_derivation():
    s=(ROOT/'hardware/vitis/search_controller.hpp').read_text();begin=s.index('template<class Limits> struct SearchController {');end=s.index('} // namespace fpga_search',begin)
    body=s[begin:end].replace('struct SearchController {','struct WordSearchController {').replace('using Index=LabelIndex<','using Index=WordLabelIndex<').replace('        Key* keys;','        uint64_t* keys;')
    body=body.replace('            const Key current=w.keys[index];','            Key current{};\n            if (!Index::Storage::load(w.keys,index,current)) {out.status=SearchStatus::invalid_input;return out;}')
    body=body.replace('                    w.path[i]={w.keys[r.parent].node,r.edge};cursor=r.parent;','                    Key parent_key{};\n                    if (!Index::Storage::load(w.keys,r.parent,parent_key)) {out.status=SearchStatus::invalid_input;return out;}\n                    w.path[i]={parent_key.node,r.edge};cursor=r.parent;')
    expected='#pragma once\n#include "search_controller.hpp"\n#include "search_key_words.hpp"\n\nnamespace fpga_search {\n// Same complete search algorithm, with explicit word-addressed label keys.\n'+body+'} // namespace fpga_search\n'
    if expected!=(ROOT/'hardware/vitis/search_controller_words.hpp').read_text():raise ValueError('Unaccounted controller algorithm change')
    s=(ROOT/'src/native/search_controller_adapter.hpp').read_text().replace('search_controller.hpp','search_controller_words.hpp').replace('controller_adapter','word_controller_adapter').replace('fpga_search::SearchController','fpga_search::WordSearchController')
    s=s.replace('    std::unique_ptr<typename Core::Key[]> keys{new typename Core::Key[L::labels]};','    std::unique_ptr<uint64_t[]> keys{new uint64_t[Core::Index::Storage::Words*L::labels]};')
    if s!=(ROOT/'src/native/search_word_controller_adapter.hpp').read_text():raise ValueError('Unaccounted CPU adapter change')

def save(path,obj):
    with path.open('x') as f:json.dump(obj,f,indent=2);f.write('\n')

def main():
    verify_derivation();OUT.mkdir(exist_ok=False);source=OUT/'source';source.mkdir()
    files={}
    for name in NAMES:
        expected=expected_driver(name);p=TEMP/(name+'.cpp')
        if p.read_text()!=expected:raise ValueError('Different compiled test source '+name)
        shutil.copyfile(p,source/p.name);shutil.copyfile(TEMP/name,OUT/name);(OUT/name).chmod(0o755)
        for path in [ROOT/'tests'/(name+'.cpp'),source/p.name,OUT/name]:files[str(path)]=digest(path)
    for folder in ['hardware/vitis','src/native']:
        for p in (ROOT/folder).glob('*.hpp'):files[str(p)]=digest(p)
    files[str(Path(__file__).resolve())]=digest(__file__)
    plan={'files':files,'cases':NAMES,'compiler_flags':'-O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined; C++17 for native drivers, C++14 for static provider',
          'scope':'Same complete single-search algorithm and tests, with packed word key storage replacing native Key structs.',
          'limitations':['No full 1062-net word-key result yet.','No HLS top, synthesis, RTL, memory-controller timing or board evidence.']}
    save(OUT/'plan.json',plan)
    for name in NAMES:
        command=[str(OUT/name)]
        with (OUT/(name+'.log')).open('x') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
        save(OUT/(name+'.receipt.json'),{'exit_code':r.returncode,'command':command,'log_sha256':digest(OUT/(name+'.log')),'plan_sha256':digest(OUT/'plan.json')})
        if r.returncode:raise RuntimeError('Word controller failed '+name)
        print((OUT/(name+'.log')).read_text(),flush=True)

if __name__=='__main__':main()
