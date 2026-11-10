#include "search_route_tree.hpp"
#include <algorithm>
#include <array>
#include <cassert>
#include <iostream>
#include <random>
#include <set>
#include <vector>
extern "C" void search_route_tree_top(const uint64_t*,uint64_t*,uint64_t*,uint64_t*,const uint64_t*,const uint32_t*,const uint32_t*,uint32_t*,uint64_t*);
using Small=fpga_search::RouteTree<257,16>;
using Status=fpga_search::RouteTreeStatus;
// Literal ABI oracle; deliberately does not use DUT state pack/unpack helpers.
std::array<uint64_t,65> state(unsigned ns,unsigned nb,unsigned nv,uint32_t node=0) {
    std::array<uint64_t,65> a{};
    a[0]=node|(uint64_t(ns)<<32)|(uint64_t(nb)<<40)|(uint64_t(nv)<<48);
    for(unsigned i=0;i<ns;++i)a[1+i/2]|=uint64_t(2*i+1)<<(32*(i%2));
    for(unsigned i=0;i<nb;++i){a[17+i/2]|=uint64_t(3*i+2)<<(32*(i%2));a[25+i]=UINT64_MAX;a[41+i]=uint64_t(1)<<(i+32);}
    for(unsigned i=0;i<nv;++i)a[57+i]=(uint64_t(i+9)<<32)|(4*i+3);
    return a;
}
void random_and_rejections() {
    std::array<uint64_t,5> meta{};std::array<uint64_t,6> bits{};
    std::array<uint64_t,65> demands{};std::array<uint64_t,81> result{};
    std::array<uint32_t,128> path{};std::array<uint32_t,258> roots{};
    assert(Small::reset(257,0,meta.data(),bits.data(),demands.data())==Status::ok);
    std::set<uint32_t> reference{0};std::mt19937 rng(0x41545245);
    unsigned ns=0,nb=0,nv=0;uint64_t version=1;bool applied=false;
    for(unsigned trial=0;trial<1000;++trial) {
        const unsigned length=1+rng()%16;auto it=reference.begin();std::advance(it,rng()%reference.size());
        uint32_t previous=*it;
        for(unsigned i=0;i<length;++i){path[8*i]=previous;previous=rng()%257;path[8*i+1]=previous;path[8*i+7]=rng()%2;}
        ns=std::min(32u,ns+unsigned(trial%3==0));nb=std::min(16u,nb+unsigned(trial%5==0));nv=std::min(8u,nv+unsigned(trial%7==0));
        result.fill(0);result[15]=1;result[7]=length;result[1]=length;
        auto expected=state(ns,nb,nv,previous);std::copy(expected.begin(),expected.end(),result.begin()+16);
        const auto input=result;const auto input_path=path;
        assert(Small::accept(previous,result.data(),path.data(),meta.data(),bits.data(),demands.data(),applied)==Status::ok && applied);
        for(unsigned i=0;i<length;++i)reference.insert(path[8*i+1]);
        ++version;expected[0]&=UINT64_C(0xffffffff00000000);
        assert(demands==expected && meta[3]==reference.size() && meta[4]==version);
        assert(input==result && input_path==path);
        for(unsigned n=0;n<257;++n)assert(((bits[n/64]>>(n%64))&1)==reference.count(n));
        roots.fill(UINT32_MAX);unsigned count=0;
        assert(Small::roots(meta.data(),bits.data(),roots.data(),count)==Status::ok);
        assert(count==reference.size() && std::equal(reference.begin(),reference.end(),roots.begin()));
        for(unsigned i=count;i<roots.size();++i)assert(roots[i]==UINT32_MAX);
        bool done=false;uint32_t sinks[]={previous,previous,0};
        assert(Small::complete(meta.data(),bits.data(),sinks,3,done)==Status::ok && done);
        assert(Small::complete(meta.data(),bits.data(),sinks,0,done)==Status::ok && done);
        const auto oldmeta=meta;const auto oldbits=bits;const auto olddemands=demands;
        result.fill(0);result[15]=1;result[0]=1+trial%6;
        assert(Small::accept(previous,result.data(),path.data(),meta.data(),bits.data(),demands.data(),applied)==Status::ok && !applied);
        assert(meta==oldmeta && bits==oldbits && demands==olddemands);
    }
    unsigned rejected=0;
    auto reject=[&](unsigned target,Status wanted){const auto m=meta;
        const auto bs=bits;
        const auto ds=demands;const auto r=result;const auto p=path;
        assert(Small::accept(target,result.data(),path.data(),meta.data(),bits.data(),demands.data(),applied)==wanted && !applied);
        assert(meta==m && bits==bs && demands==ds && result==r && path==p);++rejected;};
    auto valid=[&](){result.fill(0);result[15]=1;result[7]=2;result[1]=2;auto s=state(32,16,8,2);std::copy(s.begin(),s.end(),result.begin()+16);path.fill(0);path[0]=0;path[1]=1;path[8]=1;path[9]=2;};
    valid();result[15]=0;reject(2,Status::invalid);
    valid();result[0]=7;reject(2,Status::invalid);
    valid();result[7]=17;reject(2,Status::capacity);
    valid();result[1]=UINT64_MAX;reject(2,Status::invalid);
    valid();reject(257,Status::invalid);
    valid();path[0]=257;reject(2,Status::invalid);
    valid();path[9]=257;reject(2,Status::invalid);
    valid();path[8]=0;reject(2,Status::invalid);
    valid();path[15]=2;reject(2,Status::invalid);
    valid();path[9]=3;reject(2,Status::invalid);
    valid();result[16]^=1;reject(2,Status::invalid);
    valid();result[16]|=uint64_t(1)<<56;reject(2,Status::invalid);
    valid();result[16]-=uint64_t(1)<<32;reject(2,Status::invalid);
    valid();result[16+41]^=1;reject(2,Status::invalid);
    valid();result[16+57]^=uint64_t(1)<<32;reject(2,Status::invalid);
    valid();result[0]=1;reject(2,Status::invalid);
    valid();result[0]=1;result[7]=0;reject(2,Status::invalid);
    valid();meta[4]=UINT64_MAX;reject(2,Status::overflow);meta[4]=version;
    valid();meta[0]=0;reject(2,Status::invalid);meta[0]=Small::Magic;
    // Empty path cannot add demands or reach a node not already in the tree.
    assert(Small::reset(257,0,meta.data(),bits.data(),demands.data())==Status::ok);
    valid();result[7]=0;reject(2,Status::invalid);
    result[16]=state(32,16,8,0)[0];reject(0,Status::invalid);
    result.fill(0);result[15]=1;
    assert(Small::accept(0,result.data(),path.data(),meta.data(),bits.data(),demands.data(),applied)==Status::ok && applied);
    bool done=true;uint32_t sinks[]={0,1};
    assert(Small::complete(meta.data(),bits.data(),sinks,2,done)==Status::ok && !done);
    sinks[1]=257;assert(Small::complete(meta.data(),bits.data(),sinks,2,done)==Status::invalid && !done);
    assert(Small::complete(meta.data(),bits.data(),sinks,258,done)==Status::capacity);
    std::cout<<"random accepted=1000 nonfound=1000 atomic_rejections="<<rejected<<"\n";
}
void production() {
    constexpr unsigned N=1048576,P=524288;constexpr uint64_t Guard=UINT64_C(0xbad0cafe12345678);
    std::vector<uint64_t> config(9,Guard),meta(6,Guard),bits(16385,Guard),demands(66,Guard),search(82,Guard),out(7,Guard);
    std::vector<uint32_t> path(4194305,0xdeadbeef),sinks(N+1,0xdeadbeef),roots(N+1,0xdeadbeef);
    auto call=[&](){const auto c=config,s=search;const auto p=path,si=sinks;
        search_route_tree_top(config.data(),meta.data(),bits.data(),demands.data(),search.data(),path.data(),sinks.data(),roots.data(),out.data());
        assert(config==c && search==s && path==p && sinks==si);
        assert(meta.back()==Guard && bits.back()==Guard && demands.back()==Guard && out.back()==Guard && roots.back()==0xdeadbeef);
    };
    std::fill(config.begin(),config.begin()+8,0);config[1]=N;call();assert(out[0]==0 && out[1]==1 && out[2]==1);
    for(unsigned batch=0;batch<2;++batch){unsigned start=batch?P:0,length=batch?P-1:P,target=start+length;
        for(unsigned i=0;i<length;++i){std::fill(path.begin()+8*i,path.begin()+8*i+8,0);path[8*i]=start+i;path[8*i+1]=start+i+1;path[8*i+7]=i%2;}
        std::fill(search.begin(),search.begin()+81,0);search[15]=1;search[1]=length;search[7]=length;
        auto s=state(32,16,8,target);std::copy(s.begin(),s.end(),search.begin()+16);
        config[0]=1;config[1]=0;config[3]=target;call();assert(out[0]==0 && out[1]==target+1 && out[2]==batch+2 && out[3]==1);
        auto expected=state(32,16,8);assert(std::equal(expected.begin(),expected.end(),demands.begin()));
    }
    config[0]=2;config[3]=0;call();assert(out[0]==0 && out[4]==N);
    for(unsigned i=0;i<N;++i){assert(roots[i]==i);sinks[i]=i;}
    config[0]=3;config[4]=N;call();assert(out[0]==0 && out[5]==1);
    auto reject=[&](unsigned status){const auto m=meta,b=bits,d=demands;const auto r=roots;call();assert(out[0]==status);for(unsigned i=1;i<6;++i)assert(out[i]==0);assert(meta==m && bits==b && demands==d && roots==r);};
    config[4]=N+1;reject(2);config[4]=N;sinks[N-1]=N;reject(1);sinks[N-1]=N-1;
    config[0]=1;config[4]=0;config[3]=N-1;search[7]=P+1;reject(2);
    config[5]=1;reject(1);config[5]=0;config[0]=4;reject(1);
    config[0]=0;config[1]=N+1;config[3]=0;reject(2);config[1]=N;config[2]=N;reject(1);
    config[1]=64;config[2]=63;auto oldbits=bits;call();assert(out[0]==0 && out[1]==1 && out[2]==1 && bits[0]==(uint64_t(1)<<63));
    assert(std::equal(bits.begin()+1,bits.end(),oldbits.begin()+1));
    config[0]=2;config[1]=0;config[2]=0;auto oldroots=roots;call();assert(out[4]==1 && roots[0]==63);
    assert(std::equal(roots.begin()+1,roots.end(),oldroots.begin()+1));
    std::cout<<"production nodes=1048576 max_path=524288 state=32/16/8 full_buffers_and_guards=PASS\n";
}
int main(){random_and_rejections();production();std::cout<<"route_tree_cpu PASS\n";}
