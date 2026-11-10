// Real site negotiation. Launch only with a hash-validated input manifest.
#include "site_routes.hpp"
#include "site_inputs.hpp"
struct RoutingGraph {
    Graph graph;
    RoutingGraph(const std::string& path,size_t cache):graph(path,cache) {}
    size_t node_count() const {return graph.node_count();}
    bool neighbors(uint32_t n,std::vector<Edge>& out) {
        if (!graph.neighbors(n,out)) return false;
        // Python order: dst, full PIP name, direction, src wire, dst wire.
        std::stable_sort(out.begin(),out.end(),[](const Edge& a,const Edge& b) {
            return std::make_tuple(a.dst,a.tile,a.pip,a.dir,a.dir?a.down:a.up,a.dir?a.up:a.down)
                 < std::make_tuple(b.dst,b.tile,b.pip,b.dir,b.dir?b.down:b.up,b.dir?b.up:b.down);
        });
        return true;
    }
};
template<class T> void numbers(const T& values) {
    std::cout<<'[';bool first=true;
    for (auto v:values) {if (!first) {std::cout<<',';} first=false;std::cout<<v;}
    std::cout<<']';
}
static void demands_json(const site_native::Normalized& d) {
    std::cout<<'[';numbers(d.signals);std::cout<<",[";bool first=true;
    for (auto b:d.bits) {if (!first) {std::cout<<',';} first=false;std::cout<<'['<<b.first<<','<<b.second.first<<','<<b.second.second<<']';}
    std::cout<<"],[";first=true;
    for (auto v:d.values) {if (!first) {std::cout<<',';} first=false;std::cout<<'['<<v.first<<','<<v.second<<']';}
    std::cout<<"]]";
}
int main(int argc,char** argv) {try {
    require(argc==8,"usage: site_bench image routing sites cache iterations budget cap");
    auto start=Clock::now();RoutingGraph graph(argv[1],std::stoull(argv[4]));
    std::ifstream input(argv[2]);require(bool(input),"open routing fixture");
    auto integer=[&]() {uint64_t v=0;input>>v;require(bool(input)&&v<=UINT32_MAX,"invalid fixture integer");return uint32_t(v);};
    std::string magic;input>>magic;require(magic=="NATIVE_ROUTING_V1","invalid fixture schema");
    require(integer()==graph.node_count(),"fixture node domain differs");
    std::set<uint32_t> protected_nodes,blocked_attributes;
    auto count=integer();require(count<=graph.node_count(),"too many protected nodes");
    for (uint32_t i=0;i<count;++i) {auto n=integer();require(n<graph.node_count()&&protected_nodes.insert(n).second,"invalid protected node");}
    std::set<std::pair<uint32_t,uint32_t>> protected_pips;
    count=integer();
    for (uint32_t i=0;i<count;++i) {auto tile=integer();auto pip=integer();require(protected_pips.emplace(tile,pip).second,"duplicate protected PIP");}
    count=integer();
    for (uint32_t i=0;i<count;++i) require(blocked_attributes.insert(integer()).second,"duplicate excluded attribute");
    count=integer();std::vector<netlist_native::NetQuery> queries;
    require(count>0&&count<=graph.node_count(),"invalid query count");
    for (uint32_t i=0;i<count;++i) {
        auto net=integer();auto source=integer();auto sinks=integer();
        require(sinks<=graph.node_count(),"invalid sink count");
        netlist_native::NetQuery q{net,source,{}};
        for (uint32_t j=0;j<sinks;++j) q.sinks.push_back(integer());
        queries.push_back(std::move(q));
    }
    std::string trailing;require(!(input>>trailing),"trailing fixture data");

    site_native::SiteInputs sites(argv[3]);
    site_native::SiteState fixed(sites.fixed_signals,sites.fixed);
    auto preparation=ms(start);auto route_start=Clock::now();
    auto iterations=std::stoull(argv[5]);require(iterations<=UINT32_MAX,"iteration overflow");
    auto r=site_native::route_batch(graph,queries,protected_nodes,fixed,
        [&](uint32_t,const Edge& e) {return sites.semantics(e);},
        [&](uint32_t,uint32_t,const Edge& e) {return protected_pips.count({e.tile,e.pip})||blocked_attributes.count(e.attr);},
        unsigned(iterations),std::stoull(argv[6]),std::stoull(argv[7]),
        [](unsigned round,size_t done) {std::cerr<<"NATIVE_SITE_PROGRESS "<<round<<' '<<done<<'\n';});
    auto route_ms=ms(route_start);
    std::cout<<"{\"status\":\""<<r.status<<"\",\"routes\":[";bool first=true;
    for (const auto& item:r.routes) {
        if (!first) {std::cout<<',';} first=false;const auto& route=item.second;
        std::cout<<"{\"net\":"<<item.first<<",\"complete\":"<<(route.complete?"true":"false")<<",\"nodes\":";numbers(route.nodes);
        std::cout<<",\"edges\":[";bool f=true;
        for (const auto& p:route.edges) {if (!f) {std::cout<<',';} f=false;std::cout<<'['<<p.first<<','<<p.second.dst<<','<<p.second.tile<<','<<p.second.pip<<','<<p.second.up<<','<<p.second.down<<','<<p.second.attr<<','<<p.second.dir<<']';}
        std::cout<<"],\"demands\":";demands_json(r.site_demands.at(item.first));std::cout<<'}';
    }
    std::cout<<"],\"iterations\":[";first=true;
    for (const auto& round:r.iterations) {
        if (!first) {std::cout<<',';} first=false;std::cout<<"{\"conflicts\":[";bool f=true;
        for (const auto& c:round.conflicts) {if (!f) {std::cout<<',';} f=false;std::cout<<'['<<c.first<<',';numbers(c.second);std::cout<<']';}
        std::cout<<"],\"site_conflicts\":[";f=true;
        for (const auto& c:round.site_conflicts) {if (!f) {std::cout<<',';} f=false;std::cout<<'['<<c.first.first<<','<<c.first.second<<',';numbers(c.second);std::cout<<']';}
        std::cout<<"],\"incomplete\":";numbers(round.incomplete);std::cout<<",\"connections\":[";bool nf=true;
        for (const auto& connections:round.outcomes) {
            if (!nf) {std::cout<<',';} nf=false;std::cout<<'[';bool cf=true;
            for (const auto& c:connections) {
                if (!cf) {std::cout<<',';} cf=false;
                std::cout<<"{\"status\":\""<<c.status<<"\",\"cost\":";
                if (c.status=="found") std::cout<<c.cost;else std::cout<<"null";
                std::cout<<",\"expanded\":"<<c.expanded<<",\"blocked\":";
                if (c.status=="budget_exhausted") std::cout<<"null";else std::cout<<c.blocked;
                std::cout<<",\"unknown_sources\":";numbers(c.unknown_sources);std::cout<<",\"unknown_pips\":[";bool pf=true;
                for (auto p:c.unknown_pips) {if (!pf) {std::cout<<',';} pf=false;std::cout<<'['<<p.first<<','<<p.second<<']';}
                std::cout<<"]}";
            }
            std::cout<<']';
        }
        std::cout<<"]}";
    }

    std::cout<<"],\"preparation_ms\":"<<std::setprecision(17)<<preparation<<",\"route_ms\":"<<route_ms
        <<",\"scope\":\"tested_site_instances_only\",\"cache_hits\":"<<graph.graph.hits
        <<",\"cache_misses\":"<<graph.graph.misses<<"}\n";
    require(bool(std::cout),"write site result");return 0;
} catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}}
