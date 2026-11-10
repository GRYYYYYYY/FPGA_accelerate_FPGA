#include "../src/native/site_inputs.hpp"
static void demands(const site_native::Demands& d) {
    std::cout<<"[";bool f=true;
    for(auto s:d.signals) {if(!f) std::cout<<',';f=false;std::cout<<s;}
    std::cout<<"],[";f=true;
    for(auto [r,m,v]:d.bits) {if(!f) std::cout<<',';f=false;std::cout<<'['<<r<<','<<m<<','<<v<<']';}
    std::cout<<"],[";f=true;
    for(auto [r,v]:d.values) {if(!f) std::cout<<',';f=false;std::cout<<'['<<r<<','<<v<<']';}
    std::cout<<']';
}
int main(int argc,char** argv) {try {
    require(argc==2,"site file required");site_native::SiteInputs in(argv[1]);
    site_native::SiteState state(in.fixed_signals,in.fixed);
    std::cout<<"{\"resources\":"<<in.resources<<",\"values\":"<<in.values<<",\"attributes\":"<<in.attributes<<",\"fixed\":[";
    demands(in.fixed);std::cout<<"],\"requirements\":[";bool first=true;
    for(const auto& [key,d]:in.requirements) {
        if(!first) std::cout<<',';
        first=false;std::cout<<'['<<key.first<<','<<key.second<<",[";demands(d);std::cout<<"]]";
        auto known=in.semantics(Edge{0,key.first,key.second,0,0,*in.pseudo_attributes.begin(),0});
        require(known.pseudo&&known.demands.has_value(),"known instance missing");
        require(!in.semantics(Edge{0,UINT32_MAX,UINT32_MAX,0,0,*in.pseudo_attributes.begin(),0}).demands.has_value(),"unknown instance became authorized");
    }
    std::cout<<"],\"pseudo\":[";first=true;
    for(auto a:in.pseudo_attributes) {if(!first) std::cout<<',';first=false;std::cout<<a;}
    std::cout<<"]}\n";return 0;
} catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}}
