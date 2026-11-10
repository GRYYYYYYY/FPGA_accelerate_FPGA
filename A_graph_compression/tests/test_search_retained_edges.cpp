#include "search_retained_edges.hpp"
#include <array>
#include <cassert>
#include <map>
#include <vector>
#include <random>
#include <algorithm>
#include <iostream>
extern "C" void search_retained_edges_top(const uint64_t*,uint64_t*,uint32_t*,const uint32_t*,uint32_t*,uint64_t*);
using S=fpga_search::RetainedEdgeStatus;
void random_test(){
    using C=fpga_search::RetainedEdges<64,128,16>;
    std::array<uint64_t,6> m{};std::vector<uint32_t> rows(128*18+1,0xdeadbeef),out(128*8+1,0xabcdef01);
    std::map<uint32_t,std::vector<uint32_t>> ref;std::mt19937 rng(4751);uint64_t version=1;
    assert(C::reset(64,m.data())==S::ok);unsigned accepted=0,rejected=0;
    for(unsigned t=0;t<4000;++t){
        uint32_t net=t%9?rng()%21:UINT32_MAX;unsigned n=rng()%20;bool append=rng()%2;
        std::vector<uint32_t> path(8*n);
        for(unsigned i=0;i<n;++i){for(unsigned j=0;j<8;++j)path[8*i+j]=rng();path[8*i]%=64;path[8*i+1]%=64;path[8*i+7]%=2;}
        auto candidate=ref;auto &v=candidate[net];if(!append)v.clear();v.insert(v.end(),path.begin(),path.end());if(v.empty())candidate.erase(net);
        unsigned total=0;for(auto &e:candidate)total+=e.second.size()/8;
        S wanted=(total>128 || candidate.size()>16)?S::capacity:S::ok;
        if(n && t%11==0){path[0]=64;wanted=S::invalid;}
        if(n && t%13==0){path.back()=2;wanted=S::invalid;}
        auto before=rows;auto old=m;const auto input=path;
        assert(C::update(net,path.data(),n,append,m.data(),rows.data())==wanted && path==input);
        if(wanted==S::ok){ref=candidate;++version;++accepted;}else{assert(rows==before && m==old);++rejected;}
        std::vector<uint32_t> expected;
        for(auto &e:ref)for(unsigned i=0;i<e.second.size()/8;++i){expected.push_back(e.first);expected.insert(expected.end(),e.second.begin()+8*i,e.second.begin()+8*i+8);}
        assert(m[2]*9==expected.size() && m[4]==ref.size() && m[5]==version && rows.back()==0xdeadbeef);
        assert(std::equal(expected.begin(),expected.end(),rows.begin()+m[3]*128*9));
        auto oldout=out;old=m;before=rows;unsigned count=999;
        assert(C::get(net,m.data(),rows.data(),out.data(),count)==S::ok);
        const auto it=ref.find(net);const std::vector<uint32_t> empty;const auto &want=it==ref.end()?empty:it->second;
        assert(count*8==want.size() && std::equal(want.begin(),want.end(),out.begin()));
        assert(std::equal(out.begin()+count*8,out.end(),oldout.begin()+count*8) && old==m && before==rows);
    }
    assert(accepted>100 && rejected>100);
    auto before=rows;m[5]=UINT64_MAX;auto old=m;uint32_t p[8]{};
    assert(C::update(0,p,1,true,m.data(),rows.data())==S::overflow && m==old && rows==before);
    auto oldout=out;m[0]=0;unsigned count=9;
    assert(C::get(0,m.data(),rows.data(),out.data(),count)==S::invalid && !count && out==oldout);
    std::cout<<"EDGE_RANDOM_PASS operations=4000 accepted="<<accepted<<" rejected="<<rejected<<"\n";
}
void production(){
    constexpr unsigned E=2097152;constexpr uint32_t G=0xdeadbeef;
    std::vector<uint32_t> rows(18*E+1,G),path(8*E+1,G),out(8*E+1,G);
    std::array<uint64_t,9> c{};std::array<uint64_t,7> m{};std::array<uint64_t,6> r{};c.back()=m.back()=r.back()=UINT64_MAX;
    auto call=[&](unsigned status){search_retained_edges_top(c.data(),m.data(),rows.data(),path.data(),out.data(),r.data());assert(r[0]==status && c.back()==UINT64_MAX && m.back()==UINT64_MAX && r.back()==UINT64_MAX && rows.back()==G && path.back()==G && out.back()==G);if(status)for(unsigned i=1;i<5;++i)assert(!r[i]);};
    c[2]=1048576;call(0);
    for(unsigned i=0;i<E;++i){path[8*i]=1048575;path[8*i+1]=0;path[8*i+2]=UINT32_MAX;path[8*i+3]=i%2;path[8*i+4]=17;path[8*i+5]=19;path[8*i+6]=0xfedcba98;path[8*i+7]=i%2;}
    c[0]=1;c[1]=UINT32_MAX;c[2]=0;c[3]=E;call(0);assert(m[2]==E && m[4]==1);
    c[0]=2;c[3]=0;call(0);assert(r[4]==E && std::equal(path.begin(),path.end()-1,out.begin()));
    auto old=m;c[0]=3;c[3]=1;call(2);assert(m==old); // Full store append rejected.
    c[0]=1;c[1]=0;call(2);assert(m==old); // Distinct net cannot exceed total.
    c[1]=UINT32_MAX;c[3]=0;call(0);assert(m[2]==0 && m[4]==0);
    c[0]=3;c[3]=2;call(0);call(0);assert(m[2]==4);
    c[0]=2;c[3]=0;call(0);assert(r[4]==4);for(unsigned i=0;i<4;++i)for(unsigned j=0;j<8;++j)assert(out[8*i+j]==path[8*(i%2)+j]);
    c[0]=1;c[3]=1;path[7]=2;old=m;call(1);assert(m==old);path[7]=0;
    c[4]=1;call(1);assert(m==old);c[4]=0;
    std::cout<<"EDGE_PRODUCTION_PASS edges=2097152 duplicate_order=1 full_fields=1\n";
}
int main(){random_test();production();}
