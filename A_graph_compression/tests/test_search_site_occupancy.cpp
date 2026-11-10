#include "search_site_occupancy.hpp"
#include "site_ledger.hpp"
#include <algorithm>
#include <array>
#include <cassert>
#include <iostream>
#include <random>

extern "C" void search_site_occupancy_top(const uint64_t*,uint64_t*,uint64_t*,uint64_t*,const uint64_t*,uint32_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*);
using Status=fpga_search::SiteOccupancyStatus;
using Key=site_native::ResourceKey;
constexpr uint64_t Guard=UINT64_C(0xa5a5a5a55a5a5a5a);
uint64_t encode(Key k){return (uint64_t(k.first)<<32)|k.second;}
Key decode(uint64_t k){return {unsigned(k>>32),uint32_t(k)};}

template<unsigned O,unsigned H,unsigned R=O> struct Case {
    using Core=fpga_search::SiteOccupancy<O,H,R>;
    std::array<uint64_t,6> m{};
    std::vector<uint64_t> owners=std::vector<uint64_t>(8*O+1,Guard);
    std::vector<uint64_t> history=std::vector<uint64_t>(4*H+1,Guard);
    std::vector<uint64_t> request=std::vector<uint64_t>(3*R+1,Guard);
    std::vector<uint32_t> flags=std::vector<uint32_t>(O+1,0xdeadbeef);
    std::vector<uint64_t> groups=std::vector<uint64_t>(2*O+1,Guard);
    std::vector<uint64_t> out=std::vector<uint64_t>(4*O+1,Guard);
    std::vector<uint64_t> hout=std::vector<uint64_t>(2*H+1,Guard);
    site_native::DemandLedger oracle;
    std::map<uint32_t,site_native::Normalized> by_net;
    site_native::SiteHistory past;
    unsigned conflicts=0,snapshot_count=0;
    uint64_t version=1;
    bool production=false;
    Case(bool p=false):production(p){assert(call(0)==Status::ok);}
    Status call(unsigned op,uint32_t net=0,unsigned count=0) {
        if(production) {
            assert(O==65536 && H==65536 && R==65536);
            const uint64_t config[8]={op,net,count,0,0,0,0,0};uint64_t result[6]{};
            search_site_occupancy_top(config,m.data(),owners.data(),history.data(),request.data(),flags.data(),groups.data(),out.data(),hout.data(),result);
            conflicts=unsigned(result[4]);snapshot_count=unsigned(result[5]);
            if(result[0]==0){assert(result[1]==m[2] && result[2]==m[4] && result[3]==m[5]);}
            else for(unsigned i=1;i<6;++i)assert(result[i]==0);
            return Status(result[0]);
        }
        if(op==0)return Core::reset(m.data());
        if(op==1)return Core::replace(net,request.data(),count,m.data(),owners.data());
        if(op==2)return Core::analyze(m.data(),owners.data(),flags.data(),groups.data(),conflicts);
        if(op==3)return Core::advance(m.data(),owners.data(),history.data(),flags.data(),groups.data(),conflicts);
        return Core::snapshot(net,m.data(),owners.data(),history.data(),out.data(),hout.data(),snapshot_count);
    }
    void verify() {
        std::vector<std::array<uint64_t,4>> rows;
        for(const auto& net:by_net)for(const auto& e:site_native::entries(net.second))
            rows.push_back({encode(e.first),net.first,e.second.first,e.second.second});
        std::sort(rows.begin(),rows.end());assert(m[2]==rows.size() && m[4]==past.size() && m[5]==version);
        for(unsigned i=0;i<rows.size();++i)for(unsigned w=0;w<4;++w)assert(owners[4*O*m[1]+4*i+w]==rows[i][w]);
        unsigned i=0;for(auto h:past){assert(history[2*H*m[3]+2*i]==encode(h.first));assert(history[2*H*m[3]+2*i+1]==h.second);++i;}
        assert(call(2)==Status::ok);const auto bad=oracle.conflicts();assert(conflicts==bad.size());
        i=0;for(const auto& b:bad){assert(groups[2*i]==encode(b.first));assert(groups[2*i+1]==b.second.size());++i;}
        for(i=0;i<rows.size();++i){const auto it=bad.find(decode(rows[i][0]));assert(flags[i]==unsigned(it!=bad.end() && it->second.count(uint32_t(rows[i][1]))));}
        // Query two real edge-case IDs plus an ordinary owner and an absent one.
        for(uint32_t net:{0u,3u,UINT32_MAX,0x12345678u}) {
            std::fill(out.begin(),out.end(),Guard);std::fill(hout.begin(),hout.end(),Guard);
            assert(call(4,net)==Status::ok);unsigned n=0;
            for(auto row:rows)if(row[1]!=net){for(unsigned w=0;w<4;++w)assert(out[4*n+w]==row[w]);++n;}
            assert(snapshot_count==n);
            for(i=4*n;i<out.size();++i)assert(out[i]==Guard);
            i=0;for(auto h:past){assert(hout[2*i]==encode(h.first) && hout[2*i+1]==h.second);++i;}
            for(i*=2;i<hout.size();++i)assert(hout[i]==Guard);
        }
        assert(owners.back()==Guard && history.back()==Guard && request.back()==Guard && groups.back()==Guard && flags.back()==0xdeadbeef);
    }
    Status replace(uint32_t net,const site_native::Normalized& d) {
        const auto entries=site_native::entries(d);assert(entries.size()<=R);unsigned i=0;
        for(const auto& e:entries){request[3*i]=encode(e.first);request[3*i+1]=e.second.first;request[3*i+2]=e.second.second;++i;}
        const auto old_m=m;const auto old_o=owners,old_h=history;
        size_t n=entries.size();for(const auto& x:by_net)if(x.first!=net)n+=site_native::entries(x.second).size();
        const auto expected=n>O?Status::capacity:Status::ok;
        const auto s=call(1,net,unsigned(entries.size()));assert(s==expected);
        if(s==Status::ok){oracle.replace(net,d);by_net[net]=d;++version;}
        else assert(old_m==m && old_o==owners && old_h==history);
        return s;
    }
    void advance() {
        auto next=past;for(const auto& c:oracle.conflicts())next[c.first]+=c.second.size()-1;
        const auto old_m=m;const auto old_o=owners,old_h=history;
        const auto s=call(3);assert(s==(next.size()>H?Status::capacity:Status::ok));
        if(s==Status::ok){past=next;++version;}else assert(old_m==m && old_o==owners && old_h==history);
    }
    void rejected(unsigned op,Status expected,uint32_t net=0,unsigned count=0) {
        const auto old_m=m;const auto old_o=owners,old_h=history,old_out=out,old_hout=hout;
        assert(call(op,net,count)==expected);
        assert(old_m==m && old_o==owners && old_h==history && old_out==out && old_hout==hout);
    }
};

void random_differential() {
    Case<24,64> t;std::mt19937_64 rng(0x413597);unsigned accepted=0,rejected=0,rounds=0;
    for(unsigned step=0;step<12000;++step) {
        if(rng()%7==0){t.advance();++rounds;}
        else {
            site_native::Normalized d;const unsigned n=unsigned(rng()%10);
            for(unsigned i=0;i<n;++i) {
                const uint32_t id=rng()%9==0?UINT32_MAX:uint32_t(rng()%12);
                const unsigned kind=unsigned(rng()%3);
                if(kind==0)d.signals.insert(id);
                else if(kind==1){const uint64_t mask=rng();d.bits[id]={mask,rng()&mask};}
                else d.values[id]=uint32_t(rng()%4);
            }
            const uint32_t net=rng()%9==0?UINT32_MAX:uint32_t(rng()%8);
            if(t.replace(net,d)==Status::ok)++accepted;else ++rejected;
        }
        t.verify();
    }
    assert(accepted && rejected && rounds);
    std::cout<<"SITE_OCCUPANCY_RANDOM_PASS operations=12000 accepted="<<accepted<<" capacity_rejected="<<rejected<<" history_rounds="<<rounds<<"\n";
}

void edge_cases() {
    Case<8,2> t;site_native::Normalized a,b,c;
    a.bits[UINT32_MAX]={1,0};b.bits[UINT32_MAX]={1,1};c.bits[UINT32_MAX]={2,2};
    t.replace(0,a);t.replace(UINT32_MAX,b);t.replace(3,c);t.advance();t.verify();
    assert(t.past.at({1,UINT32_MAX})==1); // Third owner has no incompatible pair.
    a.signals.insert(0);b.signals.insert(0);t.replace(0,a);t.replace(UINT32_MAX,b);t.advance();t.verify();
    a.values[1]=0;b.values[1]=1;t.replace(0,a);t.replace(UINT32_MAX,b);
    t.rejected(3,Status::capacity);t.verify(); // New history key exceeds capacity.
    a.values.clear();b.values.clear();t.replace(0,a);t.replace(UINT32_MAX,b);
    // Late overflow: the earlier signal history addition must not be committed.
    const unsigned base=unsigned(t.m[3])*4;
    assert(t.history[base+2]==encode({1,UINT32_MAX}));t.history[base+3]=UINT64_MAX;
    t.rejected(3,Status::overflow);t.history[base+3]=t.past.at({1,UINT32_MAX});
    const uint64_t v=t.m[5];t.m[5]=UINT64_MAX;
    t.rejected(1,Status::overflow);t.rejected(3,Status::overflow);t.m[5]=v;
    t.request[0]=0;t.request[1]=1;t.request[2]=0;t.rejected(1,Status::invalid,0,1);
    t.request[0]=UINT64_C(1)<<32;t.request[1]=0;t.request[2]=1;t.rejected(1,Status::invalid,0,1);
    t.request[0]=UINT64_C(2)<<32;t.request[1]=0;t.request[2]=UINT64_C(1)<<32;t.rejected(1,Status::invalid,0,1);
    t.request[0]=UINT64_C(3)<<32;t.request[2]=0;t.rejected(1,Status::invalid,0,1);
    t.request[0]=0;t.request[3]=0;t.request[4]=0;t.request[5]=0;t.rejected(1,Status::invalid,0,2);
    t.request[0]=1;t.rejected(1,Status::invalid,0,2);
    t.rejected(1,Status::capacity,0,9);
    t.replace(UINT32_MAX,{});t.replace(UINT32_MAX,{});t.advance();t.verify();
    // Zero masks retain ownership/history keys but never create bit conflicts.
    Case<8,8> z;a={};b={};a.bits[0]={0,0};b.bits[0]={UINT64_MAX,UINT64_MAX};
    a.values[0]=UINT32_MAX;b.values[0]=UINT32_MAX;z.replace(0,a);z.replace(1,b);z.advance();z.verify();assert(z.past.empty());
    z.m[0]=0;z.rejected(2,Status::invalid);z.rejected(4,Status::invalid);z.rejected(1,Status::invalid);
    assert(z.call(0)==Status::ok);
    std::cout<<"SITE_OCCUPANCY_BOUNDARIES_PASS\n";
}

void production() {
    Case<65536,65536> t(true);site_native::Normalized all;
    for(unsigned i=0;i<65536;++i)all.signals.insert(i);
    t.replace(UINT32_MAX,all);t.verify(); // Request and owner limits reached.
    site_native::Normalized one;one.signals.insert(UINT32_MAX);assert(t.replace(0,one)==Status::capacity);
    t.replace(UINT32_MAX,{});
    for(unsigned batch=0;batch<2;++batch) {
        site_native::Normalized d;for(unsigned i=0;i<32768;++i)d.signals.insert(batch*32768+i);
        t.replace(0,d);t.replace(UINT32_MAX,d);t.advance();t.verify();
        t.replace(0,{});t.replace(UINT32_MAX,{});
    }
    assert(t.past.size()==65536);t.verify();
    t.replace(0,one);t.replace(UINT32_MAX,one);t.rejected(3,Status::capacity);
    const uint64_t config[8]={4,0,0,0,0,0,0,1};uint64_t result[6]{};
    const auto old_m=t.m;const auto old_out=t.out;
    search_site_occupancy_top(config,t.m.data(),t.owners.data(),t.history.data(),t.request.data(),t.flags.data(),t.groups.data(),t.out.data(),t.hout.data(),result);
    assert(result[0]==1 && t.m==old_m && t.out==old_out);
    for(unsigned i=1;i<6;++i)assert(result[i]==0);
    std::cout<<"SITE_OCCUPANCY_PRODUCTION_PASS owner_capacity=65536 history_capacity=65536 request_capacity=65536\n";
}
int main(){random_differential();edge_cases();production();std::cout<<"SITE_OCCUPANCY_ALL_PASS\n";}
