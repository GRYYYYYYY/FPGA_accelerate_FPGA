#include "search_key_words.hpp"
#include <algorithm>
#include <array>
#include <cassert>
#include <iostream>
#include <random>
#include <vector>
using namespace fpga_search;
template<unsigned Slots,unsigned Labels> void randomized() {
    using Native=LabelIndex<Slots,Labels,4,4,4>;using Packed=WordLabelIndex<Slots,Labels,4,4,4>;using Store=typename Packed::Storage;using Key=typename Packed::Key;
    std::array<uint64_t,Slots> a{},b{};std::array<Key,Labels> native{};
    std::vector<uint64_t> words(Labels*Store::Words+2,UINT64_MAX);uint64_t* data=words.data()+1;
    uint32_t ae=0,be=0;unsigned ac=0,bc=0;Native::initialize(a.data(),ae,ac);Packed::initialize(b.data(),be,bc);
    std::mt19937_64 rng(20261024+Slots+Labels);unsigned inserts=0,found=0,rejects=0;
    for(unsigned step=0;step<20000;++step) {
        if(step%71==0){if(step%142==0)ae=be=UINT32_MAX;assert(Native::reset(a.data(),ae,ac)==Packed::reset(b.data(),be,bc));}
        Key key{};
        if(ac && rng()%2)key=native[rng()%ac];
        else {
            key.node=uint32_t(rng());
            for(unsigned i=0;i<4;++i) {
                if(rng()%2)key.state.signals.data[key.state.signals.count++]=i;
                if(rng()%2){const uint64_t mask=rng();key.state.bits.data[key.state.bits.count++]={i,mask,rng()&mask};}
                if(rng()%2)key.state.values.data[key.state.values.count++]={i,uint32_t(rng())};
            }
        }
        if(step%101==0)key.state.signals.count=5;
        unsigned ai=UINT32_MAX,bi=UINT32_MAX,ap=0,bp=0;auto before_words=words;auto before_slots=b;const unsigned before_count=bc;
        auto x=Native::find(a.data(),native.data(),ae,ac,key,ai,ap);auto y=Packed::find(b.data(),data,be,bc,key,bi,bp);
        assert(x==y && ai==bi && ap==bp && words==before_words && b==before_slots && bc==before_count);
        ai=bi=UINT32_MAX;
        x=Native::get_or_insert(a.data(),native.data(),ae,ac,key,ai,ap);y=Packed::get_or_insert(b.data(),data,be,bc,key,bi,bp);
        assert(x==y && ai==bi && ap==bp && ae==be && ac==bc && a==b);
        if(y==IndexStatus::inserted)++inserts;
        else if(y==IndexStatus::found){++found;assert(words==before_words);}
        else {++rejects;assert(words==before_words && b==before_slots && bc==before_count);}
        for(unsigned i=0;i<bc;++i){Key decoded{};assert(Store::load(data,i,decoded) && equal_label_key(decoded,native[i]) && label_key_hash(decoded)==label_key_hash(native[i]));}
        assert(words.front()==UINT64_MAX && words.back()==UINT64_MAX);
    }
    std::cout<<"WORD_INDEX_RANDOM_PASS slots="<<Slots<<" labels="<<Labels<<" operations=20000 inserts="<<inserts<<" found="<<found<<" rejects="<<rejects<<'\n';
}
int main() {
    using Store=LabelKeyWords<2,3,3,2>;static_assert(Store::Words==13,"ABI stride");
    Store::Key key{};key.node=0x12345678;key.state.signals.count=2;key.state.signals.data[0]=1;key.state.signals.data[1]=UINT32_MAX;
    key.state.bits.count=2;key.state.bits.data[0]={2,uint64_t(1)<<32,uint64_t(1)<<32};key.state.bits.data[1]={5,0,0};
    key.state.values.count=1;key.state.values.data[0]={9,7};
    const std::array<uint64_t,13> golden{{0x0001020212345678ULL,0xffffffff00000001ULL,0,0x0000000500000002ULL,0,0x100000000ULL,0,0,0x100000000ULL,0,0,0x0000000700000009ULL,0}};
    std::array<uint64_t,26> data{};assert(Store::store(data.data(),0,key));assert(std::equal(golden.begin(),golden.end(),data.begin()));
    Store::Key out{};assert(Store::load(data.data(),0,out) && equal_label_key(out,key));
    // Unused slots are outside semantic identity, even if left by an old epoch.
    for(unsigned at:{2u,4u,7u,10u,12u})data[at]=UINT64_MAX;
    assert(Store::load(data.data(),0,out) && equal_label_key(out,key));
    assert(Store::store(data.data(),0,key) && std::equal(golden.begin(),golden.end(),data.begin()));
    auto before=data;auto invalid=key;invalid.state.signals.count=4;
    assert(!Store::store(data.data(),0,invalid) && data==before);
    assert(!Store::store(nullptr,2,key) && !Store::load(nullptr,2,out));
    for(auto mutation:std::vector<std::pair<unsigned,uint64_t>>{{0,golden[0]|(uint64_t(1)<<63)},{0,golden[0]|(uint64_t(128)<<32)},{1,0x0000000100000001ULL},{8,3}}) {
        data=before;data[mutation.first]=mutation.second;out=key;
        assert(!Store::load(data.data(),0,out) && equal_label_key(out,key));
    }
    // Full-field equality distinguishes same-node state and physical identities.
    randomized<8,4>();randomized<4,8>();randomized<128,64>();
    using Production=LabelKeyWords<524288,32,16,8>;
    static_assert(Production::Words==65,"production ABI stride");
    std::cout<<"WORD_KEY_LITERAL_ABI_PASS words=13\nWORD_KEY_PRODUCTION_STRIDE words="<<Production::Words<<" bytes="<<8*Production::Words<<" pool_bytes="<<uint64_t(524288)*8*Production::Words<<"\nWORD_KEY_ALL_PASS\n";
}
