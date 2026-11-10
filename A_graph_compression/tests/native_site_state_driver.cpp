#include "../src/native/site_state.hpp"
#include <iostream>
static void snapshot(const site_native::SiteState& state) {
    std::cout<<'[';bool first=true;
    for (const auto& owner:state.by_net()) {
        if (!first) {std::cout<<',';} first=false;
        std::cout<<'['<<owner.first<<",[";bool f=true;
        for (auto r:owner.second.signals) {if (!f) {std::cout<<',';} f=false;std::cout<<r;}
        std::cout<<"],[";f=true;
        for (const auto& b:owner.second.bits) {if (!f) {std::cout<<',';} f=false;std::cout<<'['<<b.first<<','<<b.second.first<<','<<b.second.second<<']';}
        std::cout<<"],[";f=true;
        for (const auto& v:owner.second.values) {if (!f) {std::cout<<',';} f=false;std::cout<<'['<<v.first<<','<<v.second<<']';}
        std::cout<<"]]";
    }
    std::cout<<']';
}
int main() {try {
    site_native::Demands fixed{true,false,{},{{0,15,5}},{{0,1}}};
    site_native::SiteState state({{7,99}},fixed);
    unsigned count;std::cin>>count;std::cout<<'[';
    for (unsigned action=0;action<count;++action) {
        std::string operation;uint32_t net,n;std::cin>>operation>>net;
        site_native::Demands d;
        if (operation=="R") {
            unsigned verified,additional;std::cin>>verified>>additional;d.verified=verified;d.additional_unresolved=additional;
            std::cin>>n;for (unsigned i=0;i<n;++i) {uint32_t r;std::cin>>r;d.signals.push_back(r);}
            std::cin>>n;for (unsigned i=0;i<n;++i) {uint32_t r;uint64_t m,v;std::cin>>r>>m>>v;d.bits.emplace_back(r,m,v);}
            std::cin>>n;for (unsigned i=0;i<n;++i) {uint32_t r,v;std::cin>>r>>v;d.values.emplace_back(r,v);}
        } else if (operation!="D") throw std::invalid_argument("unknown operation");
        if (!std::cin) throw std::invalid_argument("invalid input");
        bool accepted=true;
        try {if (operation=="D") state.release(net);else state.replace(net,d);}
        catch (const std::invalid_argument&) {accepted=false;}
        if (action) std::cout<<',';
        std::cout<<"{\"accepted\":"<<(accepted?"true":"false")<<",\"state\":";snapshot(state);std::cout<<'}';
    }
    std::cout<<"]\n";return 0;
} catch (const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}}
