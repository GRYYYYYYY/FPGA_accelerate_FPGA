#include "../src/native/site_inputs.hpp"
#include "../src/native/site_ledger.hpp"
#include "../src/native/search_controller_adapter.hpp"
#include "search_snapshot_provider.hpp"
#include <array>
#include <cassert>
#include <iostream>
struct SingleNodeAdjacency {
    unsigned node_count()const{return 1;}
    fpga_search::RowStatus neighbors(unsigned,fpga_search::LabelEdge*,unsigned,unsigned& count)const {count=0;return fpga_search::RowStatus::known;}
};
using Limits=controller_adapter::RegionLimits;
using Provider=fpga_search::SearchSnapshotProvider<Limits,SingleNodeAdjacency,256,65536,1,1,1,65536>;
using Core=Provider::Core;
int main(int argc,char** argv) {
    assert(argc==3);unsigned total=0;
    for(int file=1;file<argc;++file) {
        site_native::SiteInputs sites(argv[file]);assert(sites.attributes<=65536 && !sites.pseudo_attributes.empty());
        site_native::SiteState native_fixed(sites.fixed_signals,sites.fixed);
        auto fixed=site_native::normalize(sites.fixed);std::vector<std::array<uint64_t,4>> rows;
        for(auto p:sites.fixed_signals)rows.push_back({p.first,p.second,0,0});
        for(auto e:site_native::entries(fixed))rows.push_back({(uint64_t(e.first.first)<<32)|e.first.second,0,e.second.first,e.second.second});
        std::sort(rows.begin(),rows.end());std::vector<uint64_t> fixed_words;
        for(auto r:rows)fixed_words.insert(fixed_words.end(),r.begin(),r.end());
        std::vector<uint64_t> keys;std::vector<Core::State> states;
        for(auto p:sites.requirements) {
            keys.push_back((uint64_t(p.first.first)<<32)|p.first.second);Core::State s{};
            assert(controller_adapter::pack<Limits>(site_native::normalize(p.second),s));states.push_back(s);
        }
        std::vector<uint8_t> pseudo(sites.attributes),blocked(sites.attributes);
        for(auto a:sites.pseudo_attributes)pseudo[a]=1;
        SingleNodeAdjacency graph;Provider provider(graph);uint64_t forbidden[1]{},node_costs[2]{};
        Provider::View view{1,sites.attributes,forbidden,node_costs,pseudo.data(),blocked.data(),nullptr,keys.data(),states.data(),0,unsigned(keys.size()),{nullptr,nullptr,fixed_words.data(),0,0,unsigned(rows.size())},0,1};
        for(uint32_t net:{0u,1u,UINT32_MAX}) {
            view.net=net;assert(provider.bind(view)==fpga_search::CostStatus::ok);
            unsigned i=0;
            for(const auto& p:sites.requirements) {
                Edge edge{0,p.first.first,p.first.second,0,0,*sites.pseudo_attributes.begin(),0};
                auto native=sites.semantics(edge);assert(native.demands);
                fpga_search::LabelEdge encoded{edge.dst,edge.tile,edge.pip,edge.up,edge.down,edge.attr,edge.dir};Core::State out{};
                assert(provider.semantics(0,encoded,out)==fpga_search::SemanticsStatus::verified);
                auto expected=site_native::normalize(*native.demands),actual=controller_adapter::unpack(out);
                assert(expected.signals==actual.signals && expected.bits==actual.bits && expected.values==actual.values);
                assert(provider.compatible(out)==!native_fixed.conflicts(net,*native.demands));
                encoded.dir=1;assert(provider.semantics(0,encoded,out)==fpga_search::SemanticsStatus::invalid);
                ++i;
            }
            assert(i==sites.requirements.size());
        }
        fpga_search::LabelEdge unmodeled{0,UINT32_MAX,UINT32_MAX,0,0,*sites.pseudo_attributes.begin(),0};Core::State out{};
        assert(provider.semantics(0,unmodeled,out)==fpga_search::SemanticsStatus::unknown);
        unmodeled.attr=sites.attributes;assert(provider.semantics(0,unmodeled,out)==fpga_search::SemanticsStatus::invalid);
        total+=sites.requirements.size();
        std::cout<<"SNAPSHOT_REAL_SITE_PASS mode="<<(file==1?"csr":"compact")<<" requirements="<<sites.requirements.size()<<" attributes="<<sites.attributes<<" fixed_bits="<<fixed.bits.size()<<" fixed_records="<<rows.size()<<'\n';
    }
    assert(total==28);std::cout<<"SNAPSHOT_REAL_SITES_ALL_PASS\n";
}
