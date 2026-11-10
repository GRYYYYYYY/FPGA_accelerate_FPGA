#pragma once
// CPU bridge for the bounded word-addressed record store; not HLS allocation.
#include "search_label_adapter.hpp"
#include "search_label_records.hpp"
#include <memory>
#include <stdexcept>
#include <utility>
namespace record_adapter {
using Core=fpga_search::LabelRecords<LABEL_INDEX_LABELS>;
using Status=fpga_search::RecordStatus;
struct Counters {uint64_t searches=0,appends=0,improvements=0,validated_paths=0,failures=0;unsigned peak=0;};
inline thread_local Counters counters;
inline uint64_t* storage() {
    static thread_local std::unique_ptr<uint64_t[]> words{new uint64_t[10*LABEL_INDEX_LABELS]};return words.get();
}
template<class Label> class Labels {
    using Key=decltype(std::declval<Label>().key);
    using Edge=decltype(std::declval<Label>().edge);
    uint64_t* words;unsigned count=0;Status last=Status::ok;
    label_adapter::Context& keys;
    static fpga_search::LabelEdge packed(const Edge& e) {return {e.dst,e.tile,e.pip,e.up,e.down,e.attr,e.dir};}
    static Edge unpacked(const fpga_search::LabelEdge& e) {return {e.dst,e.tile,e.pip,e.up,e.down,e.attr,e.dir};}
    fpga_search::LabelRecord get(size_t index) const {
        fpga_search::LabelRecord r{};
        if (index>=count || Core::read(words,count,unsigned(index),r)!=Status::ok) throw std::runtime_error("invalid label record read");
        return r;
    }
public:
    Labels():words(storage()),keys(label_adapter::context()) {++counters.searches;}
    size_t size() const {return count;}
    const char* failure_status() const {return last==Status::capacity_exhausted?"capacity_exhausted":"invalid_search_state";}
    bool push_back(const Label& value) {
        if (count>=LABEL_INDEX_LABELS) {last=Status::capacity_exhausted;++counters.failures;return false;}
        if (keys.count!=count+1 || keys.keys[count].node!=value.key.node || value.parent>UINT32_MAX || (value.root && value.cost)) {
            last=Status::invalid;++counters.failures;return false;
        }
        unsigned id=0;
        last=value.root?Core::append_root(words,count,id):Core::append_child(words,count,value.cost,unsigned(value.parent),packed(value.edge),id);
        if (last!=Status::ok) {++counters.failures;return false;}
        ++counters.appends;counters.peak=std::max(counters.peak,count);return true;
    }
    bool improve(size_t index,uint64_t cost,size_t parent,const Edge& edge) {
        if (index>=count || parent>=count) last=Status::invalid;
        else last=Core::improve(words,count,unsigned(index),cost,unsigned(parent),packed(edge));
        if (last!=Status::ok) {++counters.failures;return false;}
        ++counters.improvements;return true;
    }
    uint64_t cost(size_t index) const {
        uint64_t out=0;if (index>=count || Core::cost(words,count,unsigned(index),out)!=Status::ok) throw std::runtime_error("invalid label cost read");return out;
    }
    uint32_t node(size_t index) const {
        if (index>=count) throw std::runtime_error("invalid label key read");
        return keys.keys[index].node;
    }
    Key key(size_t index) const {
        if (index>=count) throw std::runtime_error("invalid label key read");
        const auto& k=keys.keys[index];Key out{};out.node=k.node;
        for (unsigned i=0;i<k.state.signals.count;++i) out.demands.signals.insert(k.state.signals.data[i]);
        for (unsigned i=0;i<k.state.bits.count;++i) {auto b=k.state.bits.data[i];out.demands.bits.emplace(b.field,std::make_pair(b.mask,b.value));}
        for (unsigned i=0;i<k.state.values.count;++i) {auto v=k.state.values.data[i];out.demands.values.emplace(v.field,v.value);}
        return out;
    }
    bool root(size_t index) const {return get(index).root;}
    size_t parent(size_t index) const {return get(index).parent;}
    Edge edge(size_t index) const {return unpacked(get(index).edge);}
    bool validate_path(size_t index) {
        unsigned length=0;
        last=index>=count?Status::invalid:Core::validate_path(words,count,unsigned(index),length);
        if (last!=Status::ok) {++counters.failures;return false;}
        ++counters.validated_paths;return true;
    }
};
} // namespace record_adapter
