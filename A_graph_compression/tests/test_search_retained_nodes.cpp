#include "search_retained_nodes.hpp"
#include <algorithm>
#include <array>
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <vector>
extern "C" void search_retained_nodes_top(const uint64_t*,uint64_t*,uint64_t*,const uint32_t*,uint32_t*,uint64_t*);
constexpr uint64_t G=UINT64_C(0x123456789abcdef0);
using Status=fpga_search::RetainedStatus;
void small(){
    using Core=fpga_search::RetainedNodes<64,128,16>;
    std::array<uint64_t,6> m{};std::vector<uint64_t> rows(257,G);std::vector<uint32_t> output(65,UINT32_MAX);
    std::map<uint32_t,std::set<uint32_t>> oracle;std::mt19937 rng(0x41524554);uint64_t version=1;
    assert(Core::reset(64,m.data())==Status::ok);unsigned accepted=0,rejected=0;
    for(unsigned trial=0;trial<6000;++trial){
        uint32_t net=trial%11?uint32_t(rng()%20):UINT32_MAX;std::set<uint32_t> next;
        for(unsigned i=0,n=rng()%21;i<n;++i)next.insert(rng()%64);
        std::vector<uint32_t> input(next.begin(),next.end());auto candidate=oracle;
        if(next.empty())candidate.erase(net);else candidate[net]=next;
        unsigned total=0;for(auto e:candidate)total+=e.second.size();
        Status wanted=(total>128 || candidate.size()>16)?Status::capacity:Status::ok;
        if(trial%7==0 && input.size()>1){input[1]=input[0];wanted=Status::invalid;}
        if(trial%13==0 && !input.empty()){input.back()=64;wanted=Status::invalid;}
        const auto old_m=m;
        const auto before=rows;const auto old_input=input;
        auto status=Core::replace(net,input.data(),unsigned(input.size()),m.data(),rows.data());assert(status==wanted && input==old_input && rows.back()==G);
        if(status==Status::ok){oracle=candidate;++version;++accepted;}else{assert(m==old_m && rows==before);++rejected;}
        std::vector<uint64_t> expected;for(auto e:oracle)for(auto n:e.second)expected.push_back((uint64_t(e.first)<<32)|n);
        assert(m[2]==expected.size() && m[4]==oracle.size() && m[5]==version);
        assert(std::equal(expected.begin(),expected.end(),rows.begin()+unsigned(m[3])*128));
        auto before_output=output;auto old_meta=m;auto old_storage=rows;unsigned count=999;
        assert(Core::get(net,m.data(),rows.data(),output.data(),count)==Status::ok);
        auto found=oracle.find(net);std::vector<uint32_t> want;
        if(found!=oracle.end())want.assign(found->second.begin(),found->second.end());
        assert(count==want.size() && std::equal(want.begin(),want.end(),output.begin()));
        assert(std::equal(output.begin()+count,output.end(),before_output.begin()+count) && m==old_meta && rows==old_storage);
    }
    assert(accepted>100 && rejected>100);
    auto before=rows;auto meta=m;uint32_t n=0;m[5]=UINT64_MAX;
    const auto saturated=m;assert(Core::replace(0,&n,1,m.data(),rows.data())==Status::overflow && m==saturated && rows==before);m=meta;
    assert(Core::reset(65,m.data())==Status::capacity && m==meta && rows==before);
    assert(Core::reset(0,m.data())==Status::invalid && m==meta && rows==before);
    auto oldout=output;m[0]=0;unsigned count=3;
    assert(Core::get(0,m.data(),rows.data(),output.data(),count)==Status::invalid && !count && output==oldout && rows==before);
    std::cout<<"RETAINED_RANDOM_PASS operations=6000 accepted="<<accepted<<" rejected="<<rejected<<"\n";
}
void production(){
    constexpr unsigned N=1048576,P=2097152;constexpr uint32_t G32=0xdeadbeef;
    std::vector<uint64_t> config(9,G),meta(7,G),rows(2*P+1,G),result(6,G);
    std::vector<uint32_t> nodes(N+1,G32),out(N+1,G32);
    auto call=[&](unsigned expected){
        const auto c=config;
        const auto input=nodes,oldout=out;const auto oldmeta=meta,oldrows=rows;
        search_retained_nodes_top(config.data(),meta.data(),rows.data(),nodes.data(),out.data(),result.data());
        assert(result[0]==expected && config==c && nodes==input && meta.back()==G && rows.back()==G && out.back()==G32 && result.back()==G);
        if(expected){assert(meta==oldmeta && rows==oldrows && out==oldout);for(unsigned i=1;i<5;++i)assert(result[i]==0);}
        else{assert(result[1]==meta[2] && result[2]==meta[4] && result[3]==meta[5]);
            if(config[0]!=2)assert(out==oldout && result[4]==0);
            else assert(meta==oldmeta && rows==oldrows && std::equal(out.begin()+result[4],out.end(),oldout.begin()+result[4]));}
    };
    std::fill(config.begin(),config.begin()+8,0);config[2]=N;call(0);
    for(unsigned i=0;i<N;++i)nodes[i]=i;
    config[0]=1;config[2]=0;config[3]=N;call(0);config[1]=UINT32_MAX;call(0);assert(meta[2]==P && meta[4]==2);
    config[0]=2;config[3]=0;call(0);assert(result[4]==N);for(unsigned i=0;i<N;++i)assert(out[i]==i);
    config[1]=3;call(0);assert(result[4]==0);
    config[0]=1;config[1]=1;config[3]=1;call(2);
    config[1]=0;config[3]=0;call(0);assert(meta[2]==N && meta[4]==1);
    config[1]=1;config[3]=N;call(0);assert(meta[2]==P);
    config[3]=N+1;call(2);config[3]=1;nodes[0]=N;call(1);nodes[0]=0;
    config[0]=0;config[1]=0;config[2]=N;config[3]=0;call(0);
    // Explicitly seeded valid65536-net boundary, not65536 natural replacements.
    meta[2]=meta[4]=65536;
    for(unsigned i=0;i<65535;++i)rows[i]=uint64_t(i)<<32;
    rows[65535]=uint64_t(UINT32_MAX)<<32;
    config[0]=1;config[1]=65535;config[2]=0;config[3]=1;call(2);
    config[1]=UINT32_MAX;nodes[0]=N-1;call(0);
    config[0]=2;config[3]=0;call(0);assert(result[4]==1 && out[0]==N-1);
    meta[5]=UINT64_MAX;config[0]=1;config[3]=0;call(3);
    config[0]=2;call(0);assert(result[4]==1);
    config[4]=1;call(1);config[4]=0;config[0]=3;call(1);
    std::cout<<"RETAINED_PRODUCTION_PASS nodes=1048576 pairs=2097152 seeded_nets=65536 full_buffers=1\n";
}
int main(){small();production();std::cout<<"RETAINED_ALL_PASS\n";}
