#pragma once
#include "search_label_index.hpp"

namespace fpga_search {
// Explicit uint64 memory layout; no native struct padding is transferred.
// Word 0: node[31:0], signal_count[39:32], bit_count[47:40],
// value_count[55:48], reserved[63:56]=0.
// Then: paired signal IDs, paired bit-field IDs, bit masks, bit values,
// categorical (value<<32)|field words. Fixed stride per label.
// Stores zero unused slots. Loads ignore unused slots, but validate all active
// fields and preserve zero-mask fields. Caller supplies Labels*Words storage.
template<unsigned Labels,unsigned S,unsigned B,unsigned V> struct LabelKeyWords {
    static_assert(S>0 && S<=255 && B>0 && B<=255 && V>0 && V<=255,"word key state count overflow");
    static constexpr unsigned SignalWords=(S+1)/2,FieldWords=(B+1)/2;
    static constexpr unsigned SignalOffset=1,FieldOffset=SignalOffset+SignalWords;
    static constexpr unsigned MaskOffset=FieldOffset+FieldWords,BitValueOffset=MaskOffset+B,ValueOffset=BitValueOffset+B;
    static constexpr unsigned Words=ValueOffset+V;
    static_assert(Labels>0 && Labels<=UINT32_MAX/Words,"word key address overflow");
    using Key=LabelKey<S,B,V>;
    static bool valid(const Key& key) {
        return valid_state_array<SignalOps>(key.state.signals) && valid_state_array<BitsOps>(key.state.bits) && valid_state_array<ValueOps>(key.state.values);
    }
    static bool store(uint64_t* memory,unsigned index,const Key& key) {
        if(index>=Labels || !valid(key))return false;
        const unsigned base=index*Words;
        for(unsigned i=0;i<Words;++i)memory[base+i]=0;
        memory[base]=uint64_t(key.node)|(uint64_t(key.state.signals.count)<<32)|(uint64_t(key.state.bits.count)<<40)|(uint64_t(key.state.values.count)<<48);
        for(unsigned i=0;i<S;++i){if(i>=key.state.signals.count)break;memory[base+SignalOffset+i/2]|=uint64_t(key.state.signals.data[i])<<(32*(i%2));}
        for(unsigned i=0;i<B;++i){if(i>=key.state.bits.count)break;const auto b=key.state.bits.data[i];memory[base+FieldOffset+i/2]|=uint64_t(b.field)<<(32*(i%2));memory[base+MaskOffset+i]=b.mask;memory[base+BitValueOffset+i]=b.value;}
        for(unsigned i=0;i<V;++i){if(i>=key.state.values.count)break;const auto v=key.state.values.data[i];memory[base+ValueOffset+i]=(uint64_t(v.value)<<32)|v.field;}
        return true;
    }
    static bool load(const uint64_t* memory,unsigned index,Key& output) {
        if(index>=Labels)return false;
        const unsigned base=index*Words;const uint64_t header=memory[base];
        Key key{};key.node=uint32_t(header);key.state.signals.count=unsigned((header>>32)&255);key.state.bits.count=unsigned((header>>40)&255);key.state.values.count=unsigned((header>>48)&255);
        if((header>>56) || key.state.signals.count>S || key.state.bits.count>B || key.state.values.count>V)return false;
        for(unsigned i=0;i<S;++i){if(i>=key.state.signals.count)break;key.state.signals.data[i]=uint32_t(memory[base+SignalOffset+i/2]>>(32*(i%2)));}
        for(unsigned i=0;i<B;++i){if(i>=key.state.bits.count)break;key.state.bits.data[i]={uint32_t(memory[base+FieldOffset+i/2]>>(32*(i%2))),memory[base+MaskOffset+i],memory[base+BitValueOffset+i]};}
        for(unsigned i=0;i<V;++i){if(i>=key.state.values.count)break;const uint64_t word=memory[base+ValueOffset+i];key.state.values.data[i]={uint32_t(word),uint32_t(word>>32)};}
        if(!valid(key))return false;
        output=key;return true;
    }
};

// The original hash, probe order, insertion IDs, epoch reset and full equality
// are retained. Only key storage is replaced by the word layout above.
template<unsigned Slots,unsigned Labels,unsigned S,unsigned B,unsigned V>
struct WordLabelIndex {
    using Base=LabelIndex<Slots,Labels,S,B,V>;
    using Key=typename Base::Key;
    using Storage=LabelKeyWords<Labels,S,B,V>;
    static void initialize(uint64_t* slots,uint32_t& epoch,unsigned& count){Base::initialize(slots,epoch,count);}
    static IndexStatus reset(uint64_t* slots,uint32_t& epoch,unsigned& count){return Base::reset(slots,epoch,count);}
    static IndexStatus access(uint64_t* slots,uint64_t* keys,uint32_t epoch,unsigned& count,const Key& requested,unsigned& index,unsigned& probes,bool insert_allowed) {
        probes=0;
        if(!epoch || count>Labels || !Storage::valid(requested))return IndexStatus::invalid;
        const unsigned first=unsigned(label_key_hash(requested))&(Slots-1);
        for(unsigned probe=0;probe<Slots;++probe) {
            const unsigned slot=(first+probe)&(Slots-1);++probes;const uint64_t tag=slots[slot];
            if(uint32_t(tag>>32)!=epoch) {
                if(!insert_allowed)return IndexStatus::not_found;
                if(count==Labels)return IndexStatus::capacity_exhausted;
                const unsigned id=count;
                if(!Storage::store(keys,id,requested))return IndexStatus::invalid;
                slots[slot]=(uint64_t(epoch)<<32)|uint64_t(id+1);count=id+1;index=id;return IndexStatus::inserted;
            }
            const uint32_t plus_one=uint32_t(tag);
            if(!plus_one || plus_one>count)return IndexStatus::invalid;
            Key stored{};const unsigned id=plus_one-1;
            if(!Storage::load(keys,id,stored))return IndexStatus::invalid;
            if(equal_label_key(stored,requested)){index=id;return IndexStatus::found;}
        }
        return insert_allowed?IndexStatus::capacity_exhausted:IndexStatus::not_found;
    }
    static IndexStatus get_or_insert(uint64_t* slots,uint64_t* keys,uint32_t epoch,unsigned& count,const Key& requested,unsigned& index,unsigned& probes){return access(slots,keys,epoch,count,requested,index,probes,true);}
    static IndexStatus find(uint64_t* slots,uint64_t* keys,uint32_t epoch,unsigned& count,const Key& requested,unsigned& index,unsigned& probes){return access(slots,keys,epoch,count,requested,index,probes,false);}
};
} // namespace fpga_search
