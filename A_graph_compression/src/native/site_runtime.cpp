// First/resident timing for the physically validated partial site workload.
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
    require(argc==9,"usage: site_runtime image routing sites cache iterations budget cap direct|expanded");
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
    std::string execution=argv[8];require(execution=="direct"||execution=="expanded","invalid execution mode");
    auto materialization_start=Clock::now();
    if (execution=="expanded") graph.graph.materialize_all();
    auto materialization_ms=ms(materialization_start);
    auto preparation=ms(start);
    std::cout<<std::setprecision(17)<<"{\"execution\":\""<<execution<<"\",\"materialization_ms\":"<<materialization_ms<<",\"batches\":[";
    std::vector<double> export_times;
    auto iterations=std::stoull(argv[5]);require(iterations<=UINT32_MAX,"iteration overflow");
    for (unsigned batch=0;batch<2;++batch) {
    if (batch) std::cout<<',';
    auto logical_start=graph.graph.logical_bytes,hits_start=graph.graph.hits,misses_start=graph.graph.misses;
    auto route_start=Clock::now();
    auto r=site_native::route_batch(graph,queries,protected_nodes,fixed,
        [&](uint32_t,const Edge& e) {return sites.semantics(e);},
        [&](uint32_t,uint32_t,const Edge& e) {return protected_pips.count({e.tile,e.pip})||blocked_attributes.count(e.attr);},
        unsigned(iterations),std::stoull(argv[6]),std::stoull(argv[7]),
        [](unsigned round,size_t done) {std::cerr<<"NATIVE_SITE_PROGRESS "<<round<<' '<<done<<'\n';});
    auto route_ms=ms(route_start);uint64_t peak_kib=0;
    std::ifstream proc("/proc/self/status");std::string line;
    while (std::getline(proc,line)) if (line.rfind("VmHWM:",0)==0) {std::istringstream stream(line.substr(6));stream>>peak_kib;}
    auto export_start=Clock::now();
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
        <<",\"scope\":\"tested_site_instances_only\",\"cache_hits\":"<<(graph.graph.hits-hits_start)
        <<",\"cache_misses\":"<<(graph.graph.misses-misses_start)<<",\"logical_bytes\":"<<(graph.graph.logical_bytes-logical_start)
        <<",\"peak_kib\":"<<peak_kib<<"}\n";
    std::cout.flush();require(bool(std::cout),"write site result");
    export_times.push_back(ms(export_start));
    }
    std::cout<<"],\"export_ms\":["<<export_times[0]<<','<<export_times[1]<<"]}\n";
    require(bool(std::cout),"write runtime result");return 0;
} catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}}
