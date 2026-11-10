#include "../hardware/vitis/search_site_state.hpp"
#include "../src/native/site_inputs.hpp"
#include <cassert>
#include <cstring>
#include <iostream>
#include <random>
using fpga_search::StateStatus;
using site_native::Demands;
using site_native::Normalized;

template<unsigned S,unsigned B,unsigned V>
Normalized unpack(const fpga_search::SiteState<S,B,V>& s) {
    assert(fpga_search::valid_state_array<fpga_search::SignalOps>(s.signals));
    assert(fpga_search::valid_state_array<fpga_search::BitsOps>(s.bits));
    assert(fpga_search::valid_state_array<fpga_search::ValueOps>(s.values));
    Normalized out;
    for (unsigned i=0;i<s.signals.count;++i) out.signals.insert(s.signals.data[i]);
    for (unsigned i=0;i<s.bits.count;++i) {auto b=s.bits.data[i];out.bits.emplace(b.field,std::make_pair(b.mask,b.value));}
    for (unsigned i=0;i<s.values.count;++i) {auto v=s.values.data[i];out.values.emplace(v.field,v.value);}
    return out;
}
static bool same(const Normalized& a,const Normalized& b) {
    return a.signals==b.signals && a.bits==b.bits && a.values==b.values;
}
template<unsigned S,unsigned B,unsigned V>
StateStatus normalize(const Demands& d,fpga_search::SiteState<S,B,V>& out) {
    std::vector<fpga_search::ConfigBits> bits;
    std::vector<fpga_search::ConfigValue> values;
    for (auto b:d.bits) bits.push_back({std::get<0>(b),std::get<1>(b),std::get<2>(b)});
    for (auto v:d.values) values.push_back({v.first,v.second});
    return fpga_search::normalize_site_state<2048>(d.verified,d.additional_unresolved,d.signals.data(),unsigned(d.signals.size()),
        bits.data(),unsigned(bits.size()),values.data(),unsigned(values.size()),out);
}
template<class T> std::vector<unsigned char> bytes(const T& s) {
    const auto p=reinterpret_cast<const unsigned char*>(&s);return {p,p+sizeof(s)};
}
template<unsigned C> void random_cases(unsigned seed) {
    std::mt19937_64 rng(seed);unsigned successful=0,failed=0,merged=0;
    using State=fpga_search::SiteState<C,C,C>;
    for (unsigned trial=0;trial<10000;++trial) {
        Demands d{true,false,{},{},{}};
        unsigned n=unsigned(rng()%25),domain=trial%3?C:2*C;
        for (unsigned i=0;i<n;++i) {
            uint32_t field=uint32_t(rng()%domain);if (trial%37==0) field=UINT32_MAX;
            d.signals.push_back(field);
            uint64_t mask=rng(),value=(uint64_t(field)*0x123456789abcdefULL)&mask;
            if (trial%11==0) value=rng();
            d.bits.emplace_back(field,mask,value);
            d.values.emplace_back(field,trial%13==0?uint32_t(rng()%3):field);
        }
        if (trial%17==0) d.verified=false;
        if (trial%19==0) d.additional_unresolved=true;
        State result{};result.signals.data[0]=12345;auto before=bytes(result);
        auto status=normalize(d,result);Normalized expected;bool accepted=true;
        try {expected=site_native::normalize(d);}catch (const std::invalid_argument&) {accepted=false;}
        bool fits=expected.signals.size()<=C && expected.bits.size()<=C && expected.values.size()<=C;
        assert((status==StateStatus::ok)==(accepted&&fits));
        if (status!=StateStatus::ok) {assert(bytes(result)==before);++failed;continue;}
        assert(same(unpack(result),expected));++successful;
        // Test alias-safe merge, successful union, and late cross-component conflict.
        Demands extra{true,false,{uint32_t(rng()%(2*C))},{{uint32_t(rng()%(2*C)),1,trial%2}},{{uint32_t(rng()%(2*C)),trial%2}}};
        State other{};assert(normalize(extra,other)==StateStatus::ok);
        bool compatible=true;Normalized union_state;
        try {union_state=site_native::merge(expected,site_native::normalize(extra));}
        catch (const std::invalid_argument&) {compatible=false;}
        fits=union_state.signals.size()<=C && union_state.bits.size()<=C && union_state.values.size()<=C;
        auto original=result;before=bytes(result);
        status=fpga_search::merge_site_state(result,other,result);
        assert((status==StateStatus::ok)==(compatible&&fits));
        if (status==StateStatus::ok) {assert(same(unpack(result),union_state));++merged;}
        else assert(bytes(result)==before);
        auto before_other=bytes(other);
        auto reverse=fpga_search::merge_site_state(original,other,other);
        assert(reverse==status);
        if (status==StateStatus::ok) assert(same(unpack(other),union_state));
        else assert(bytes(other)==before_other);
    }
    assert(successful && failed && merged);
    std::cout<<"SITE_STATE_RANDOM_PASS capacity="<<C<<" cases=10000 success="<<successful<<" rejected="<<failed<<" merged="<<merged<<'\n';
}

void boundaries() {
    using State=fpga_search::SiteState<2,2,2>;
    State a{},b{},out{};auto before=bytes(out);
    Demands d{true,false,{UINT32_MAX,0,UINT32_MAX},{{UINT32_MAX,0,0},{UINT32_MAX,UINT64_MAX,UINT64_MAX}},{{UINT32_MAX,UINT32_MAX}}};
    assert(normalize(d,a)==StateStatus::ok);
    assert(a.signals.count==2 && a.bits.count==1 && a.bits.data[0].value==UINT64_MAX);
    Demands zero{true,false,{},{{0,0,0}}, {}};
    assert(normalize(zero,b)==StateStatus::ok && b.bits.count==1);
    assert(fpga_search::merge_site_state(a,b,out)==StateStatus::ok && out.bits.count==2);
    // Invalid count must be rejected before indexing; malformed sort/mask likewise.
    for (unsigned kind=0;kind<4;++kind) {
        auto bad=a;out={};before=bytes(out);
        if (kind==0) bad.signals.count=UINT32_MAX;
        if (kind==1) bad.signals.data[1]=0;
        if (kind==2) {bad.bits.data[0].mask=0;bad.bits.data[0].value=1;}
        if (kind==3) bad.values.count=3;
        assert(fpga_search::merge_site_state(bad,b,out)==StateStatus::invalid);
        assert(bytes(out)==before);
    }
    out={};before=bytes(out);
    auto status=fpga_search::normalize_site_state<1>(true,false,static_cast<const uint32_t*>(nullptr),2,
        static_cast<const fpga_search::ConfigBits*>(nullptr),0,static_cast<const fpga_search::ConfigValue*>(nullptr),0,out);
    assert(status==StateStatus::capacity_exhausted && bytes(out)==before);
    // Output must not acquire the signal union if a later category conflicts.
    assert(normalize(Demands{true,false,{0},{},{{1,0}}},a)==StateStatus::ok);
    assert(normalize(Demands{true,false,{1},{},{{1,1}}},b)==StateStatus::ok);
    assert(fpga_search::merge_site_state(a,b,out)==StateStatus::conflict && bytes(out)==before);
    std::cout<<"SITE_STATE_BOUNDARY_PASS\n";
}

void real_fixture(const char* path) {
    site_native::SiteInputs input(path);
    using State=fpga_search::SiteState<1024,1024,1024>;
    State fixed{};assert(normalize(input.fixed,fixed)==StateStatus::ok);
    assert(same(unpack(fixed),site_native::normalize(input.fixed)));
    unsigned checked=0;
    for (const auto& item:input.requirements) {
        State state{},merged{};assert(normalize(item.second,state)==StateStatus::ok);
        auto native=site_native::normalize(item.second);assert(same(unpack(state),native));
        bool compatible=true;Normalized expected;
        try {expected=site_native::merge(site_native::normalize(input.fixed),native);}
        catch (const std::invalid_argument&) {compatible=false;}
        auto status=fpga_search::merge_site_state(fixed,state,merged);
        assert((status==StateStatus::ok)==compatible);
        if (compatible) assert(same(unpack(merged),expected));
        ++checked;
    }
    std::cout<<"SITE_STATE_REAL_PASS requirements="<<checked<<" fixed_bits="<<fixed.bits.count<<'\n';
}
int main(int argc,char** argv) {
    random_cases<1>(1);random_cases<2>(2);random_cases<8>(8);random_cases<32>(32);boundaries();
    for (int i=1;i<argc;++i) real_fixture(argv[i]);
    std::cout<<"SITE_STATE_ALL_PASS\n";
}
