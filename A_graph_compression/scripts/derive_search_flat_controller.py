#!/usr/bin/env python3
"""Account for every change from the frozen word-key controller to flat I/O."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def replace_once(text,old,new):
    if text.count(old)!=1:raise ValueError('Unexpected derivation anchor '+old)
    return text.replace(old,new)

def core():
    s=(ROOT/'hardware/vitis/search_controller_words.hpp').read_text()
    s=s.replace('WordSearchController','FlatSearchController')
    s=replace_once(s,'// Same complete search algorithm, with explicit word-addressed label keys.',
        '// Same complete search algorithm; all external workspace payloads are words.\n'
        '// PIP word=(tile<<32)|pip. Path edge=8 uint32 words:\n'
        '// source,dst,tile,pip,up,down,attr,dir. Only count-delimited output is valid.\n'
        '// edges is a local scratch array, not an external interface.')
    s=replace_once(s,'PipIdentity* unknown_pips;','uint64_t* unknown_pips;')
    s=replace_once(s,'PathEdge* path;','uint32_t* path;')
    s=replace_once(s,'        unsigned lo=0,hi=out.unknown_pip_count;',
        '        const uint64_t encoded=(uint64_t(pip.tile)<<32)|pip.pip;\n        unsigned lo=0,hi=out.unknown_pip_count;')
    s=replace_once(s,'pip_less(w.unknown_pips[mid],pip)','w.unknown_pips[mid]<encoded')
    s=replace_once(s,'!pip_less(pip,w.unknown_pips[lo])','encoded==w.unknown_pips[lo]')
    s=replace_once(s,'w.unknown_pips[lo]=pip;','w.unknown_pips[lo]=encoded;')
    s=replace_once(s,'                    w.path[i]={parent_key.node,r.edge};cursor=r.parent;',
        '                    const uint64_t at=uint64_t(i)*8;\n'
        '                    w.path[at]=parent_key.node;w.path[at+1]=r.edge.dst;\n'
        '                    w.path[at+2]=r.edge.tile;w.path[at+3]=r.edge.pip;\n'
        '                    w.path[at+4]=r.edge.up;w.path[at+5]=r.edge.down;\n'
        '                    w.path[at+6]=r.edge.attr;w.path[at+7]=r.edge.dir;cursor=r.parent;')
    s=replace_once(s,'                    const PathEdge temp=w.path[i];w.path[i]=w.path[length-1-i];w.path[length-1-i]=temp;',
        '                    for (unsigned word=0;word<8;++word) {\n'
        '                        const uint64_t a=uint64_t(i)*8+word,b=uint64_t(length-1-i)*8+word;\n'
        '                        const uint32_t temp=w.path[a];w.path[a]=w.path[b];w.path[b]=temp;\n'
        '                    }')
    return s

def adapter():
    s=(ROOT/'src/native/search_word_controller_adapter.hpp').read_text()
    s=s.replace('search_controller_words.hpp','search_controller_flat.hpp').replace('word_controller_adapter','flat_controller_adapter').replace('WordSearchController','FlatSearchController')
    s=replace_once(s,'std::unique_ptr<fpga_search::PipIdentity[]> pips{new fpga_search::PipIdentity[L::unknown_pips]};',
        'std::unique_ptr<uint64_t[]> pips{new uint64_t[L::unknown_pips]};')
    s=replace_once(s,'std::unique_ptr<fpga_search::PathEdge[]> path{new fpga_search::PathEdge[L::path]};',
        'std::unique_ptr<uint32_t[]> path{new uint32_t[uint64_t(8)*L::path]};')
    s=replace_once(s,'for (unsigned i=0;i<r.path_length;++i) out.path.emplace_back(w.path[i].source,native_edge(w.path[i].edge));',
        'for (unsigned i=0;i<r.path_length;++i) {const uint32_t* p=w.path+uint64_t(i)*8;out.path.emplace_back(p[0],Edge{p[1],p[2],p[3],p[4],p[5],p[6],p[7]});}')
    s=replace_once(s,'out.unknown_pips.emplace(w.unknown_pips[i].tile,w.unknown_pips[i].pip);',
        'out.unknown_pips.emplace(uint32_t(w.unknown_pips[i]>>32),uint32_t(w.unknown_pips[i]));')
    return s

if __name__=='__main__':
    for path,body in [('hardware/vitis/search_controller_flat.hpp',core()),('src/native/search_flat_controller_adapter.hpp',adapter())]:
        with (ROOT/path).open('x') as f:f.write(body)
