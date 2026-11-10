"""Checked vector-to-record-store transform on the isolated indexed search."""
from label_index_transform import replace_once

def transform_search(text):
    text=replace_once(text,'#include "search_label_adapter.hpp"','#include "search_label_adapter.hpp"\n#include "search_record_adapter.hpp"')
    text=replace_once(text,'std::vector<Label> labels;','record_adapter::Labels<Label> labels;')
    for old in ['labels.push_back({key,0,0,{},true});','labels.push_back({std::move(key),following,index,edge,false});']:
        text=replace_once(text,old,'if (!'+old[:-1]+') {result.status=labels.failure_status();return result;}')
    text=replace_once(text,'if (cost!=labels[index].cost) continue;','if (cost!=labels.cost(index)) continue;')
    text=replace_once(text,'const auto current=labels[index].key;','const auto current=labels.key(index);')
    text=replace_once(text,'// Copy before label-vector growth; later insertions must not invalidate it.',
                     '// Decode a private native view from the immutable bounded key storage.')
    text=replace_once(text,'        if (current.node==target) {','        if (current.node==target) {\n            if (!labels.validate_path(index)) {result.status=labels.failure_status();return result;}')
    text=replace_once(text,'for (size_t cursor=index;!labels[cursor].root;cursor=labels[cursor].parent)\n                result.path.emplace_back(labels[labels[cursor].parent].key.node,labels[cursor].edge);',
        'for (size_t cursor=index;!labels.root(cursor);cursor=labels.parent(cursor))\n                result.path.emplace_back(labels.node(labels.parent(cursor)),labels.edge(cursor));')
    text=replace_once(text,'if (following>=labels[next].cost) continue;','if (following>=labels.cost(next)) continue;')
    text=replace_once(text,'labels[next].cost=following;labels[next].parent=index;labels[next].edge=edge;',
        'if (!labels.improve(next,following,index,edge)) {result.status=labels.failure_status();return result;}')
    if 'labels[' in text:raise ValueError('Unconverted label-vector access')
    return text

def transform_runtime(text):
    text=replace_once(text,'    label_adapter::counters={};','    label_adapter::counters={};\n    record_adapter::counters={};')
    text=replace_once(text,'    const auto lc=label_adapter::counters;',
        '    const auto rc=record_adapter::counters;\n'
        '    std::cerr<<"RECORD_COUNTERS "<<batch<<\' \'<<rc.searches<<\' \'<<rc.appends<<\' \'<<rc.improvements<<\' \'<<rc.validated_paths<<\' \'<<rc.failures<<\' \'<<rc.peak<<\'\\n\';\n'
        '    require(rc.failures==0,"bounded label record failure");\n'
        '    const auto lc=label_adapter::counters;')
    return text
