#include "resident_snapshot_adapter.hpp"
#include "search_kernel_packet.hpp"
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>

using W=fpga_search::LabelKeyWords<1,32,16,8>;
using State=fpga_search::SiteState<32,16,8>;
constexpr uint64_t Guard=UINT64_C(0xabcde123456789ff);
struct Sites {
    std::vector<uint8_t> pseudo_attributes,blocked_attributes;
    std::vector<uint64_t> semantics_keys,protected_pips,fixed;
    std::vector<State> requirements;
};

template<unsigned N,unsigned Slots,unsigned O,unsigned H,unsigned PW> struct Fixture {
    using B=fpga_search::ResidentSnapshot<N,Slots,O,H,PW>;
    using Node=typename B::Node;using Site=typename B::Site;
    using V=fpga_search::SearchKernel<0>::Provider::View;
    std::array<uint64_t,4> nm{};std::array<uint64_t,6> sm{};
    std::vector<uint32_t> counts=std::vector<uint32_t>(N),flags=std::vector<uint32_t>(Slots);
    std::vector<uint64_t> nh=std::vector<uint64_t>(N),nk=std::vector<uint64_t>(Slots);
    std::vector<uint64_t> so=std::vector<uint64_t>(8*O),sh=std::vector<uint64_t>(4*H);
    std::vector<uint32_t> sf=std::vector<uint32_t>(O);std::vector<uint64_t> groups=std::vector<uint64_t>(2*O);
    std::vector<uint64_t> packet=std::vector<uint64_t>(PW+1,Guard),stat;
    std::array<uint64_t,65> initial{};
    std::array<uint64_t,16> c{};std::array<uint64_t,9> result{};
    Sites sites;std::set<uint32_t> protected_nodes;std::map<uint32_t,uint32_t> reserved;
    std::map<uint32_t,std::set<uint32_t>> node_nets;std::map<uint32_t,uint64_t> node_history;
    std::map<uint32_t,site_native::Normalized> site_nets;site_native::DemandLedger oracle;
    site_native::SiteHistory site_history;
    bool production=false;
    explicit Fixture(bool p=false):production(p) {
        assert(Node::reset(N,nm.data(),counts.data(),nh.data(),flags.data())==fpga_search::OccupancyStatus::ok);
        assert(Site::reset(sm.data())==fpga_search::SiteOccupancyStatus::ok);
        sites.pseudo_attributes={0,1,0,0,1,0,0,0,1};sites.blocked_attributes={0,0,1,0,0,0,0,0,1};
        sites.protected_pips={3,UINT64_MAX};sites.semantics_keys={5,9};sites.requirements.resize(2);
        sites.requirements[0].signals.count=1;sites.requirements[0].signals.data[0]=UINT32_MAX;
        sites.requirements[1].bits.count=1;sites.requirements[1].bits.data[0]={3,UINT64_C(1)<<63,UINT64_C(1)<<63};
        sites.fixed={0,UINT32_MAX,0,0,(UINT64_C(1)<<32)|12,0,1,0,UINT64_C(2)<<32,0,0,2};
        protected_nodes={10};reserved={{1,7},{5,UINT32_MAX},{6,0}};
    }
    void image() {
        stat=resident_snapshot_host::static_image(N,sites,protected_nodes,reserved);
        c={{0,UINT32_MAX,8,N-1,1,200000,stat.size(),PW,0,0,0,0,0,0,0,0}};
        if(production)stat.resize(4194304+1,Guard);
    }
    void node_replace(uint32_t net,const std::set<uint32_t>& next) {
        const std::vector<uint32_t> old(node_nets[net].begin(),node_nets[net].end()),fresh(next.begin(),next.end());
        assert(Node::update(net,old.data(),unsigned(old.size()),fresh.data(),unsigned(fresh.size()),nm.data(),counts.data(),nk.data(),flags.data())==fpga_search::OccupancyStatus::ok);
        node_nets[net]=next;
    }
    void site_replace(uint32_t net,const site_native::Normalized& next) {
        std::vector<uint64_t> req;
        for(const auto& e:site_native::entries(next)){req.push_back((uint64_t(e.first.first)<<32)|e.first.second);req.push_back(e.second.first);req.push_back(e.second.second);}
        assert(Site::replace(net,req.data(),unsigned(req.size()/3),sm.data(),so.data())==fpga_search::SiteOccupancyStatus::ok);
        oracle.replace(net,next);site_nets[net]=next;
    }
    void advance() {
        std::map<uint32_t,unsigned> owners;
        for(const auto& n:node_nets)for(auto node:n.second)++owners[node];
        for(auto n:owners)if(n.second>1)node_history[n.first]+=n.second-1;
        for(const auto& s:oracle.conflicts())site_history[s.first]+=s.second.size()-1;
        uint64_t n=0;unsigned s=0;
        assert(Node::advance(nm.data(),counts.data(),nh.data(),n)==fpga_search::OccupancyStatus::ok);
        assert(Site::advance(sm.data(),so.data(),sh.data(),sf.data(),groups.data(),s)==fpga_search::SiteOccupancyStatus::ok);
    }
    std::vector<uint64_t> golden(uint32_t net,uint64_t present,uint32_t target,unsigned nroots,uint64_t budget)const {
        std::vector<uint64_t> forbidden((N+63)/64),costs(2*N),owner_words,history_words;
        for(auto n:protected_nodes)forbidden[n/64]|=uint64_t(1)<<(n%64);
        for(auto r:reserved)if(r.second!=net)forbidden[r.first/64]|=uint64_t(1)<<(r.first%64);
        for(const auto& n:node_nets)if(n.first!=net)for(auto node:n.second)++costs[2*node];
        for(auto h:node_history)costs[2*h.first+1]=h.second;
        std::vector<std::array<uint64_t,4>> rows;
        for(const auto& n:site_nets)if(n.first!=net)for(const auto& e:site_native::entries(n.second))
            rows.push_back({{(uint64_t(e.first.first)<<32)|e.first.second,n.first,e.second.first,e.second.second}});
        std::sort(rows.begin(),rows.end());for(auto row:rows)owner_words.insert(owner_words.end(),row.begin(),row.end());
        for(auto h:site_history){history_words.push_back((uint64_t(h.first.first)<<32)|h.first.second);history_words.push_back(h.second);}
        V v{N,unsigned(sites.pseudo_attributes.size()),forbidden.data(),costs.data(),sites.pseudo_attributes.data(),sites.blocked_attributes.data(),
            sites.protected_pips.data(),sites.semantics_keys.data(),sites.requirements.data(),unsigned(sites.protected_pips.size()),unsigned(sites.semantics_keys.size()),
            {owner_words.data(),history_words.data(),sites.fixed.data(),unsigned(rows.size()),unsigned(site_history.size()),unsigned(sites.fixed.size()/4)},net,present};
        W::Key k{};assert(W::load(initial.data(),0,k));
        return search_kernel_host::packet<fpga_search::SearchRegionLimits>(v,target,nroots,budget,k.state);
    }
    void call(unsigned status=0) {
        const auto old_packet=packet,old_nm=std::vector<uint64_t>(nm.begin(),nm.end()),old_sm=std::vector<uint64_t>(sm.begin(),sm.end());
        const auto old_counts=counts,old_flags=flags;const auto old_nh=nh,old_nk=nk,old_so=so,old_sh=sh;
        const auto old_c=c;const auto old_initial=initial;result.fill(Guard);
        if(production)search_resident_snapshot_top(c.data(),stat.data(),initial.data(),nm.data(),counts.data(),nh.data(),nk.data(),flags.data(),sm.data(),so.data(),sh.data(),packet.data(),result.data());
        else B::run(c.data(),stat.data(),initial.data(),nm.data(),counts.data(),nh.data(),nk.data(),flags.data(),sm.data(),so.data(),sh.data(),packet.data(),result.data());
        assert(result[0]==status && result.back()==Guard && c==old_c && initial==old_initial);
        assert(std::vector<uint64_t>(nm.begin(),nm.end())==old_nm && std::vector<uint64_t>(sm.begin(),sm.end())==old_sm);
        assert(counts==old_counts && flags==old_flags && nh==old_nh && nk==old_nk && so==old_so && sh==old_sh);
        if(status){assert(packet==old_packet);for(unsigned i=1;i<8;++i)assert(result[i]==0);return;}
        const uint32_t net=uint32_t(c[0]?old_packet[4]:c[1]);const uint64_t present=c[0]?old_packet[5]:c[2];
        const auto expected=golden(net,present,uint32_t(c[3]),unsigned(c[4]),c[5]);
        assert(result[1]==expected.size());for(unsigned i=0;i<expected.size();++i)assert(packet[i]==expected[i]);
        for(size_t i=expected.size();i<packet.size();++i)assert(packet[i]==old_packet[i]);
        if(!c[0]) {
            bool occupied=false,past=false;for(const auto& n:node_nets)if(n.first!=net && !n.second.empty())occupied=true;
            for(auto h:node_history)past=past || h.second!=0;
            assert(result[2]==uint64_t(occupied) && result[3]==uint64_t(past) && result[4]==expected[11] && result[5]==expected[12]);
            assert(result[6]==nm[3] && result[7]==sm[5]);
        } else for(unsigned i=2;i<8;++i)assert(result[i]==0);
    }
};

void random_and_rejections() {
    Fixture<64,128,64,64,4096> t;t.image();std::mt19937_64 rng(0x41534e41);
    for(unsigned i=0;i<1000;++i) {
        const uint32_t net=rng()%9==0?UINT32_MAX:uint32_t(rng()%8);
        std::set<uint32_t> nodes;for(unsigned j=0;j<4;++j)nodes.insert(uint32_t(rng()%64));t.node_replace(net,nodes);
        site_native::Normalized d;d.signals.insert(uint32_t(rng()%8));
        const uint64_t mask=rng();d.bits[uint32_t(rng()%8)]={mask,rng()&mask};d.values[uint32_t(rng()%8)]=uint32_t(rng()%3);
        t.site_replace(net,d);if(i%7==0)t.advance();
        t.c[1]=net;t.c[2]=1+rng()%32;t.call();
        const auto build=t.c;t.c={{1,0,0,uint64_t(rng()%64),1,100,0,t.result[1],0,0,0,0,0,0,0,0}};
        W::Key k{};k.state.signals.count=1;k.state.signals.data[0]=UINT32_MAX;assert(W::store(t.initial.data(),0,k));
        t.call();t.c=build;t.initial.fill(0);
    }
    const auto goodc=t.c;const auto goods=t.stat;const auto goodi=t.initial;unsigned rejected=0;
    auto reject=[&](unsigned status){t.call(status);++rejected;t.c=goodc;t.stat=goods;t.initial=goodi;};
    t.c[0]=2;reject(1);t.c[1]=UINT64_C(1)<<32;reject(1);t.c[2]=0;reject(1);t.c[3]=64;reject(1);
    t.c[4]=0;reject(1);t.c[5]=0;reject(1);t.c[5]=200001;reject(1);t.c[6]=15;reject(1);
    t.c[6]=4194305;reject(2);t.c[7]=4097;reject(2);t.c[7]=1;reject(2);t.c[15]=1;reject(1);
    for(unsigned at:{0u,1u,8u,15u}){t.stat[at]^=1;reject(1);}
    for(unsigned at:{2u,3u,4u,5u,6u,7u}){t.stat[at]=UINT64_MAX;reject(2);}
    t.stat[2]=0;reject(1);t.stat[3]=0;reject(1);
    t.stat[17]=UINT64_C(64)<<32;reject(1);t.stat[18]=t.stat[17];reject(1);
    t.stat[16]|=2;reject(1); // Reserved node1 intersects protected bitset.
    t.stat[20]=2;reject(1);t.stat[21]|=UINT64_C(1)<<63;reject(1);
    t.stat[25]=t.stat[24];reject(1); // Protected PIP ordering.
    t.stat[27]=t.stat[26];reject(1); // Semantic key ordering.
    t.stat[28]|=1;reject(1); // Requirement key must use node0.
    t.stat[28+130+4+1]=1;reject(1); // Fixed bits record may not have an owner.
    t.initial[0]=1;reject(1);t.initial[0]=UINT64_C(33)<<32;reject(1);
    t.stat[28+64]=UINT64_MAX;t.initial[64]=UINT64_MAX;t.call();t.stat=goods;t.initial=goodi;
    const uint64_t magic=t.nm[0];t.nm[0]=0;t.call(1);++rejected;t.nm[0]=magic;
    t.call();const uint64_t length=t.result[1];
    t.c={{1,0,0,64,1,100,0,length,0,0,0,0,0,0,0,0}};t.call(1);++rejected;
    t.c[3]=0;t.c[2]=1;t.call(1);++rejected;t.c[2]=0;t.c[7]=1;t.call(1);++rejected;
    std::cout<<"RESIDENT_SNAPSHOT_RANDOM_PASS builds=1000 patches=1000 rejections="<<rejected<<"\n";
}

void production_capacity() {
    Fixture<1048576,2097152,65536,65536,4194304> t(true);
    t.sites.pseudo_attributes.assign(65536,1);t.sites.blocked_attributes.assign(65536,0);
    t.sites.protected_pips.clear();for(unsigned i=0;i<1048576;++i)t.sites.protected_pips.push_back(i);
    t.sites.semantics_keys.clear();t.sites.requirements.clear();
    State full{};
    for(unsigned i=0;i<32;++i)full.signals.data[full.signals.count++]=i;
    for(unsigned i=0;i<16;++i)full.bits.data[full.bits.count++]={i,UINT64_MAX,uint64_t(i)};
    for(unsigned i=0;i<8;++i)full.values.data[full.values.count++]={i,UINT32_MAX-i};
    for(unsigned i=0;i<256;++i){t.sites.semantics_keys.push_back(i);t.sites.requirements.push_back(full);}
    t.sites.fixed.clear();for(unsigned i=0;i<65536;++i)t.sites.fixed.insert(t.sites.fixed.end(),{i,0,0,0});
    t.protected_nodes.clear();t.reserved.clear();for(unsigned i=0;i<1048576;++i)t.reserved[i]=0;
    for(unsigned batch=0;batch<2;++batch) {
        t.site_replace(0,{});t.site_replace(1,{});site_native::Normalized d;
        for(unsigned i=0;i<32768;++i)d.signals.insert(batch*32768+i);
        t.site_replace(0,d);t.site_replace(1,d);t.advance();
    }
    t.image();assert(t.c[6]==2408976);assert(W::store(t.initial.data(),0,{0,full}));t.call();
    assert(t.result[1]==3850849 && t.result[4]==65536 && t.result[5]==65536);
    t.c[7]=3850848;t.call(2);
    t.c={{1,0,0,1048575,1048576,200000,0,3850849,0,0,0,0,0,0,0,0}};t.call();
    std::cout<<"RESIDENT_SNAPSHOT_PRODUCTION_PASS nodes=1048576 owners=65536 history=65536 reserved=1048576 protected_pips=1048576 semantics=256 fixed=65536 packet_words=3850849\n";
}
int main(){random_and_rejections();production_capacity();std::cout<<"RESIDENT_SNAPSHOT_ALL_PASS\n";}
