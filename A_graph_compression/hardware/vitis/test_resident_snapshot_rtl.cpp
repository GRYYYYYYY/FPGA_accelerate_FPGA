// Derived from the frozen native packet/ledger oracle test. Only production
// Fixture is instantiated; every top pointer has full declared depth plus guard.
// Oracle remains the original native serializer/ledger, not literal DUT output.
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
    std::array<uint64_t,5> nm{};std::array<uint64_t,7> sm{};
    std::vector<uint32_t> counts=std::vector<uint32_t>(N+1,0),flags=std::vector<uint32_t>(Slots+1,0);
    std::vector<uint64_t> nh=std::vector<uint64_t>(N+1,0),nk=std::vector<uint64_t>(Slots+1,0);
    std::vector<uint64_t> so=std::vector<uint64_t>(8*O+1,0),sh=std::vector<uint64_t>(4*H+1,0);
    std::vector<uint32_t> sf=std::vector<uint32_t>(O);std::vector<uint64_t> groups=std::vector<uint64_t>(2*O);
    std::vector<uint64_t> packet=std::vector<uint64_t>(PW+1,Guard),stat;
    std::array<uint64_t,66> initial{};
    std::array<uint64_t,17> c{};std::array<uint64_t,9> result{};
    Sites sites;std::set<uint32_t> protected_nodes;std::map<uint32_t,uint32_t> reserved;
    std::map<uint32_t,std::set<uint32_t>> node_nets;std::map<uint32_t,uint64_t> node_history;
    std::map<uint32_t,site_native::Normalized> site_nets;site_native::DemandLedger oracle;
    site_native::SiteHistory site_history;
    unsigned transaction=0;
    bool production=false;
    explicit Fixture(bool p=false):production(p) {
        nm.back()=Guard;sm.back()=Guard;counts.back()=0xdeadbeef;flags.back()=0xdeadbeef;
        nh.back()=nk.back()=so.back()=sh.back()=Guard;
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
        assert(production && N==1048576 && Slots==2097152 && O==65536 && H==65536 && PW==4194304);
        assert(stat.size()==4194305);
        c.back()=initial.back()=Guard;
        const auto old_packet=packet,old_nm=std::vector<uint64_t>(nm.begin(),nm.end()),old_sm=std::vector<uint64_t>(sm.begin(),sm.end());
        const auto old_counts=counts,old_flags=flags;const auto old_nh=nh,old_nk=nk,old_so=so,old_sh=sh;
        const auto old_c=c;const auto old_initial=initial;const auto old_stat=stat;result.fill(Guard);
        if(production)search_resident_snapshot_top(c.data(),stat.data(),initial.data(),nm.data(),counts.data(),nh.data(),nk.data(),flags.data(),sm.data(),so.data(),sh.data(),packet.data(),result.data());
        else B::run(c.data(),stat.data(),initial.data(),nm.data(),counts.data(),nh.data(),nk.data(),flags.data(),sm.data(),so.data(),sh.data(),packet.data(),result.data());
        assert(result[0]==status && result.back()==Guard && c==old_c && initial==old_initial && stat==old_stat);
        assert(std::vector<uint64_t>(nm.begin(),nm.end())==old_nm && std::vector<uint64_t>(sm.begin(),sm.end())==old_sm);
        assert(counts==old_counts && flags==old_flags && nh==old_nh && nk==old_nk && so==old_so && sh==old_sh);
        std::cout<<"SNAPSHOT_RTL_TX "<<transaction++<<' '<<c[0];
        for(unsigned i=0;i<8;++i)std::cout<<' '<<result[i];
        std::cout<<'\n';
        assert(nm.back()==Guard && sm.back()==Guard && nh.back()==Guard && nk.back()==Guard && so.back()==Guard && sh.back()==Guard);
        assert(counts.back()==0xdeadbeef && flags.back()==0xdeadbeef && stat.back()==Guard);
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
    t.c={{0,UINT32_MAX,8,1048575,1,200000,2408976,4194304,0,0,0,0,0,0,0,0}};
    const auto good=t.c;const auto original_initial=t.initial;
    auto reject=[&](unsigned expected){t.call(expected);t.c=good;t.initial=original_initial;};
    t.c[0]=2;reject(1);t.c[1]=UINT64_C(1)<<32;reject(1);t.c[2]=0;reject(1);
    t.c[3]=1048576;reject(1);t.c[4]=0;reject(1);t.c[4]=1048577;reject(1);
    t.c[5]=0;reject(1);t.c[5]=200001;reject(1);t.c[6]=15;reject(1);
    t.c[6]=4194305;reject(2);t.c[7]=4194305;reject(2);t.c[15]=1;reject(1);
    t.initial[0]|=1;reject(1);
    auto saved=t.stat;
    for(unsigned at:{0u,1u,8u,15u}){t.stat[at]^=1;t.call(1);t.stat=saved;}
    t.nm[0]^=1;t.call(1);t.nm[0]^=1;
    t.sm[0]^=1;t.call(1);t.sm[0]^=1;
    t.call();
    const uint64_t length=t.result[1];
    t.c={{1,0,0,1048576,1,200000,0,length,0,0,0,0,0,0,0,0}};t.call(1);
    t.c[3]=0;t.c[2]=1;t.call(1);t.c[2]=0;t.c[7]=1;t.call(1);
    t.c[7]=length;t.c[4]=1048576;t.call();
    // Actual node ownership/history, self exclusion and reserved-net changes.
    t.node_replace(0,{0,1048575});t.node_replace(UINT32_MAX,{1048575});t.advance();
    t.c=good;t.call();
    t.c[1]=0;t.call();t.c[1]=1;t.call();
    assert(t.transaction==30);
    std::cout<<"RESIDENT_SNAPSHOT_PRODUCTION_PASS nodes=1048576 owners=65536 history=65536 reserved=1048576 protected_pips=1048576 semantics=256 fixed=65536 packet_words=3850849\n";
}
int main(){production_capacity();std::cout<<"SNAPSHOT_RTL_GOLDEN_PASS transactions=30 full_depths=1\n";}
