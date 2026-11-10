"""Checked isolated transformations; never edits the frozen native baseline."""
def replace_once(text,old,new):
    if text.count(old)!=1:raise ValueError('Unexpected source anchor: '+old)
    return text.replace(old,new)

def transform_search(text):
    text=replace_once(text,'#include <type_traits>','#include <type_traits>\n#include "search_label_adapter.hpp"')
    text=replace_once(text,'std::map<SearchKey,size_t,SearchKeyLess> ids;','label_adapter::Index ids;')
    # The input is already the frozen bounded-heap integration, whose result
    # exists before root initialization. Failures never masquerade as no_path.
    if text.index('    SearchResult result;')>text.index('    for (auto root:roots)'):raise ValueError('Result must exist before root insertion')
    for old in ['ids.emplace(key,index);','ids.emplace(key,next);']:
        text=replace_once(text,old,'if (!'+old[:-1]+') {result.status=ids.failure_status();return result;}')
    text=replace_once(text,'auto found=ids.find(key);size_t next;',
                     'auto found=ids.find(key);if (!ids.ok()) {result.status=ids.failure_status();return result;}size_t next;')
    return text

def transform_runtime(text):
    text=replace_once(text,'    heap_adapter::counters={};','    heap_adapter::counters={};\n    label_adapter::counters={};')
    text=replace_once(text,'    const auto hc=heap_adapter::counters;',
        '    const auto lc=label_adapter::counters;\n'
        '    std::cerr<<"LABEL_COUNTERS "<<batch<<\' \'<<lc.searches<<\' \'<<lc.lookups<<\' \'<<lc.inserts<<\' \'<<lc.failures<<\' \'<<lc.peak_labels<<\' \'<<lc.max_probes<<\' \'<<lc.peak_signals<<\' \'<<lc.peak_bits<<\' \'<<lc.peak_values<<\'\\n\';\n'
        '    require(lc.failures==0,"bounded label index failure");\n'
        '    const auto hc=heap_adapter::counters;')
    return text
