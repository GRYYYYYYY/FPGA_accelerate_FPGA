#include "../hardware/vitis/search_label_index.hpp"
#include "../src/native/site_state.hpp"
#include <algorithm>
#include <cassert>
#include <cstring>
#include <iostream>
#include <map>
#include <random>
#include <tuple>
#include <vector>
using Key=fpga_search::LabelKey<4,4,4>;
using Status=fpga_search::IndexStatus;
using NativeKey=std::tuple<uint32_t,std::set<uint32_t>,std::map<uint32_t,std::pair<uint64_t,uint64_t>>,std::map<uint32_t,uint32_t>>;
NativeKey canonical(const Key& k) {
    site_native::Demands d{true,false,{},{},{}};
    for (unsigned i=0;i<k.state.signals.count;++i) d.signals.push_back(k.state.signals.data[i]);
    for (unsigned i=0;i<k.state.bits.count;++i) {auto b=k.state.bits.data[i];d.bits.emplace_back(b.field,b.mask,b.value);}
    for (unsigned i=0;i<k.state.values.count;++i) {auto v=k.state.values.data[i];d.values.emplace_back(v.field,v.value);}
    auto n=site_native::normalize(d);return {k.node,n.signals,n.bits,n.values};
}
Key make_key(uint32_t node,uint32_t salt) {
    Key k{};k.node=node;
    k.state.signals.count=2;k.state.signals.data[0]=salt%5;k.state.signals.data[1]=100+salt%7;
    k.state.bits.count=1;k.state.bits.data[0]={salt%3,UINT64_MAX,uint64_t(salt)*0x100000001ULL};
    k.state.values.count=1;k.state.values.data[0]={salt%11,salt%13};return k;
}
template<class T> std::vector<unsigned char> bytes(const std::vector<T>& values) {
    auto p=reinterpret_cast<const unsigned char*>(values.data());return {p,p+sizeof(T)*values.size()};
}
template<unsigned Slots,unsigned Labels> void exercise() {
    using Index=fpga_search::LabelIndex<Slots,Labels,4,4,4>;
    std::vector<uint64_t> storage(Slots+2,0x123456789abcdefULL);auto slots=storage.data()+1;
    std::vector<Key> keys(Labels);uint32_t epoch=0;unsigned count=123;
    Index::initialize(slots,epoch,count);assert(epoch==1 && count==0);
    std::map<NativeKey,unsigned> oracle;std::vector<Key> saved;std::mt19937_64 rng(Slots*100+Labels);
    unsigned inserted=0,found=0,full=0,invalid=0;
    for (unsigned op=0;op<20000;++op) {
        if (op && op%1000==0) {assert(Index::reset(slots,epoch,count)==Status::reset_complete);oracle.clear();saved.clear();}
        Key k=make_key(uint32_t(rng()%32),uint32_t(rng()%32));
        if (op%3==0 && !saved.empty()) k=saved[rng()%saved.size()];
        const bool malformed=op%137==0;
        if (malformed) k.state.signals.count=UINT32_MAX;
        auto old_storage=storage;auto old_keys=bytes(keys);const unsigned old_count=count;
        unsigned id=UINT32_MAX,probes=UINT32_MAX;
        auto lookup=Index::find(slots,keys.data(),epoch,count,k,id,probes);
        if (malformed) assert(lookup==Status::invalid && id==UINT32_MAX);
        else {
            auto at=oracle.find(canonical(k));
            if (at==oracle.end()) assert(lookup==Status::not_found && id==UINT32_MAX);
            else assert(lookup==Status::found && id==at->second);
        }
        assert(storage==old_storage && bytes(keys)==old_keys && count==old_count);
        id=UINT32_MAX;auto status=Index::get_or_insert(slots,keys.data(),epoch,count,k,id,probes);
        if (malformed) {assert(status==Status::invalid && probes==0);++invalid;}
        else {
            auto native=canonical(k);auto at=oracle.find(native);
            if (at!=oracle.end()) {assert(status==Status::found && id==at->second);++found;}
            else if (oracle.size()==std::min(Slots,Labels)) {assert(status==Status::capacity_exhausted);++full;}
            else {
                assert(status==Status::inserted && id==oracle.size());oracle.emplace(native,id);saved.push_back(k);++inserted;
                assert(canonical(keys[id])==native);
            }
            assert(probes>0 && probes<=Slots);
        }
        assert(count==oracle.size());
        if (status!=Status::inserted) {assert(storage==old_storage && bytes(keys)==old_keys && count==old_count);}
        if (status==Status::invalid || status==Status::capacity_exhausted) assert(id==UINT32_MAX);
        assert(storage.front()==0x123456789abcdefULL && storage.back()==0x123456789abcdefULL);
    }
    assert(inserted && found && full && invalid);
    std::cout<<"LABEL_INDEX_RANDOM_PASS slots="<<Slots<<" labels="<<Labels<<" operations=20000 inserted="<<inserted<<" found="<<found<<" full="<<full<<" invalid="<<invalid<<'\n';
}
void boundaries() {
    using Index=fpga_search::LabelIndex<16,12,4,4,4>;
    std::vector<uint64_t> slots(16);std::vector<Key> keys(12);uint32_t epoch;unsigned count,id,probes;
    Index::initialize(slots.data(),epoch,count);
    std::vector<Key> colliding;
    for (uint32_t node=0;colliding.size()<8;++node) {
        auto k=make_key(node,0);if ((fpga_search::label_key_hash(k)&15)==15) colliding.push_back(k);
    }
    for (unsigned i=0;i<colliding.size();++i) {
        assert(Index::get_or_insert(slots.data(),keys.data(),epoch,count,colliding[i],id,probes)==Status::inserted);
        assert(id==i && probes==i+1);
    }
    // Same node with different config is a different label; zero-mask presence
    // also differs from no field. Distinct nodes with shared config stay distinct.
    auto k=colliding[0];k.state.bits.data[0].value=1;
    assert(Index::get_or_insert(slots.data(),keys.data(),epoch,count,k,id,probes)==Status::inserted && id==8);
    Key zero{};zero.node=UINT32_MAX;
    assert(Index::get_or_insert(slots.data(),keys.data(),epoch,count,zero,id,probes)==Status::inserted && id==9);
    zero.state.bits.count=1;zero.state.bits.data[0]={UINT32_MAX,0,0};
    assert(Index::get_or_insert(slots.data(),keys.data(),epoch,count,zero,id,probes)==Status::inserted && id==10);
    zero.state.values.count=1;zero.state.values.data[0]={UINT32_MAX,UINT32_MAX};
    assert(Index::get_or_insert(slots.data(),keys.data(),epoch,count,zero,id,probes)==Status::inserted && id==11);
    // A duplicate remains findable when label capacity is exhausted.
    assert(Index::get_or_insert(slots.data(),keys.data(),epoch,count,zero,id,probes)==Status::found && id==11);
    auto old_slots=slots;auto old_keys=bytes(keys);unsigned old_count=count;
    for (unsigned kind=0;kind<5;++kind) {
        auto bad=zero;
        if (kind==0) bad.state.bits.data[0].value=1;
        if (kind==1) {bad.state.signals.count=2;bad.state.signals.data[0]=1;bad.state.signals.data[1]=1;}
        if (kind==2) bad.state.values.count=5;
        uint32_t e=kind==3?0:epoch;unsigned c=kind==4?13:count;id=UINT32_MAX;
        assert(Index::get_or_insert(slots.data(),keys.data(),e,c,bad,id,probes)==Status::invalid);
        assert(slots==old_slots && bytes(keys)==old_keys && id==UINT32_MAX && count==old_count);
    }
    // Normal reset invalidates entries without clearing slots; epoch rollover clears.
    assert(Index::reset(slots.data(),epoch,count)==Status::reset_complete && epoch==2 && count==0 && slots==old_slots);
    assert(Index::get_or_insert(slots.data(),keys.data(),epoch,count,zero,id,probes)==Status::inserted && id==0);
    epoch=UINT32_MAX;
    assert(Index::reset(slots.data(),epoch,count)==Status::reset_complete && epoch==1 && count==0);
    assert(std::all_of(slots.begin(),slots.end(),[](uint64_t v){return v==0;}));
    // A live tag that references an unallocated label is rejected before reading keys.
    auto bucket=unsigned(fpga_search::label_key_hash(zero))&15;slots[bucket]=(uint64_t(epoch)<<32)|1;
    old_slots=slots;old_keys=bytes(keys);id=UINT32_MAX;
    assert(Index::get_or_insert(slots.data(),keys.data(),epoch,count,zero,id,probes)==Status::invalid);
    assert(slots==old_slots && bytes(keys)==old_keys && count==0 && id==UINT32_MAX);
    std::cout<<"LABEL_INDEX_BOUNDARY_PASS\n";
}
int main() {exercise<8,4>();exercise<4,8>();exercise<128,64>();boundaries();std::cout<<"LABEL_INDEX_ALL_PASS\n";}
