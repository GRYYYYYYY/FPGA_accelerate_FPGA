#pragma once
// CPU integration bridge; ownership/allocation are not HLS implementation.
// Indexing itself calls the same bounded, full-state hardware component.
#include "search_label_index.hpp"
#include <algorithm>
#include <memory>
#ifndef LABEL_INDEX_SLOTS
#define LABEL_INDEX_SLOTS 1048576
#endif
#ifndef LABEL_INDEX_LABELS
#define LABEL_INDEX_LABELS 524288
#endif
namespace label_adapter {
using Core=fpga_search::LabelIndex<LABEL_INDEX_SLOTS,LABEL_INDEX_LABELS,32,16,8>;
using Status=fpga_search::IndexStatus;
struct Counters {
    uint64_t searches=0,lookups=0,inserts=0,failures=0;
    unsigned peak_labels=0,max_probes=0,peak_signals=0,peak_bits=0,peak_values=0;
};
inline thread_local Counters counters;
struct Context {
    std::unique_ptr<uint64_t[]> slots{new uint64_t[LABEL_INDEX_SLOTS]};
    std::unique_ptr<Core::Key[]> keys{new Core::Key[LABEL_INDEX_LABELS]};
    uint32_t epoch=0;unsigned count=0;
    Context() {Core::initialize(slots.get(),epoch,count);}
};
inline Context& context() {static thread_local Context c;return c;}
class Index {
    Context& c;
    Status last;
    template<class Key> bool convert(const Key& native,Core::Key& out) {
        if (native.demands.signals.size()>32 || native.demands.bits.size()>16 || native.demands.values.size()>8) {
            last=Status::capacity_exhausted;++counters.failures;return false;
        }
        out={};out.node=native.node;
        for (auto s:native.demands.signals) out.state.signals.data[out.state.signals.count++]=s;
        for (auto b:native.demands.bits) out.state.bits.data[out.state.bits.count++]={b.first,b.second.first,b.second.second};
        for (auto v:native.demands.values) out.state.values.data[out.state.values.count++]={v.first,v.second};
        counters.peak_signals=std::max(counters.peak_signals,out.state.signals.count);
        counters.peak_bits=std::max(counters.peak_bits,out.state.bits.count);
        counters.peak_values=std::max(counters.peak_values,out.state.values.count);
        return true;
    }
    void record(unsigned probes) {
        counters.max_probes=std::max(counters.max_probes,probes);
        counters.peak_labels=std::max(counters.peak_labels,c.count);
        if (!ok()) ++counters.failures;
    }
public:
    struct Iterator {
        bool present;size_t second;
        const Iterator* operator->() const {return this;}
        bool operator==(const Iterator& b) const {return present==b.present && (!present || second==b.second);}
        bool operator!=(const Iterator& b) const {return !(*this==b);}
    };
    Index():c(context()),last(Core::reset(c.slots.get(),c.epoch,c.count)) {++counters.searches;}
    bool ok() const {return last!=Status::invalid && last!=Status::capacity_exhausted;}
    const char* failure_status() const {return last==Status::capacity_exhausted?"capacity_exhausted":"invalid_search_state";}
    Iterator end() const {return {false,0};}
    template<class Key> Iterator find(const Key& native) {
        ++counters.lookups;Core::Key key;
        if (!convert(native,key)) return end();
        unsigned index=0,probes=0;last=Core::find(c.slots.get(),c.keys.get(),c.epoch,c.count,key,index,probes);record(probes);
        return last==Status::found?Iterator{true,index}:end();
    }
    template<class Key> bool emplace(const Key& native,size_t expected_index) {
        ++counters.inserts;Core::Key key;
        if (!convert(native,key)) return false;
        unsigned index=0,probes=0;
        last=Core::get_or_insert(c.slots.get(),c.keys.get(),c.epoch,c.count,key,index,probes);
        if (ok() && index!=expected_index) last=Status::invalid;
        record(probes);return ok();
    }
};
} // namespace label_adapter
