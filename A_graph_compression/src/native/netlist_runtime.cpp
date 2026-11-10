// First/resident timing companion to the archived canonical integration CLI.
// Same complete traces in both batches; preparation excludes fixture generation.
#include "netlist_routes.hpp"
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
template<class T> static void numbers(const T& values) {
    std::cout<<'[';bool first=true;
    for (auto v:values) {if (!first) {std::cout<<',';} first=false;std::cout<<v;}
    std::cout<<']';
}
static void path_json(const std::vector<std::pair<uint32_t,Edge>>& path) {
    std::cout<<'[';bool first=true;
    for (const auto& p:path) {
        if (!first) {std::cout<<',';} first=false;
        const auto& e=p.second;
        std::cout<<'['<<p.first<<','<<e.dst<<','<<e.tile<<','<<e.pip<<','<<e.up<<','<<e.down<<','<<e.attr<<','<<e.dir<<']';
    }
    std::cout<<']';
}
int main(int argc,char** argv) {try {
    require(argc==8,"usage: netlist_bench image fixture cache iterations budget present direct|expanded");
    const auto start=Clock::now();RoutingGraph graph(argv[1],std::stoull(argv[3]));
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
    std::string execution=argv[7];require(execution=="direct"||execution=="expanded","invalid execution mode");
    if (execution=="expanded") graph.graph.materialize_all();
    const auto preparation=ms(start);
    std::vector<double> export_times;
    std::cout<<"{\"batches\":[";
    for (unsigned batch=0;batch<2;++batch) {
    if (batch) std::cout<<',';
    const auto logical_start=graph.graph.logical_bytes;
    const auto hits_start=graph.graph.hits, misses_start=graph.graph.misses;
    auto route_start=Clock::now();
    const auto iterations=std::stoull(argv[4]);require(iterations<=UINT32_MAX,"iteration count overflow");
    auto result=netlist_native::route_batch(graph,queries,protected_nodes,
        [&](uint32_t,uint32_t,const Edge& e) {return protected_pips.count({e.tile,e.pip})||blocked_attributes.count(e.attr);},
        unsigned(iterations),std::stoull(argv[5]),std::stoull(argv[6]),
        [](unsigned round,size_t done) {std::cerr<<"NATIVE_ROUTING_PROGRESS "<<round<<' '<<done<<'\n';});
    const auto route_ms=ms(route_start);uint64_t peak_kib=0;
    std::ifstream proc("/proc/self/status");std::string line;
    while (std::getline(proc,line)) if (line.rfind("VmHWM:",0)==0) {std::istringstream stream(line.substr(6));stream>>peak_kib;}
    const auto export_start=Clock::now();
    std::cout<<std::setprecision(17)<<"{\"scope\":\"canonical_node_negotiation_only\",\"status\":\""<<result.status
        <<"\",\"preparation_ms\":"<<preparation<<",\"route_ms\":"<<route_ms<<",\"peak_kib\":"<<peak_kib
        <<",\"logical_bytes\":"<<(graph.graph.logical_bytes-logical_start)<<",\"cache_hits\":"<<(graph.graph.hits-hits_start)
        <<",\"cache_misses\":"<<(graph.graph.misses-misses_start)<<",\"routes\":[";bool first=true;
    for (const auto& item:result.routes) {
        if (!first) {std::cout<<',';} first=false;const auto& r=item.second;
        std::cout<<"{\"net_id\":"<<item.first<<",\"source\":"<<r.source<<",\"sinks\":";numbers(r.sinks);
        std::cout<<",\"complete\":"<<(r.complete?"true":"false")<<",\"nodes\":";numbers(r.nodes);
        std::cout<<",\"edges\":";path_json(r.edges);std::cout<<'}';
    }
    std::cout<<"],\"iterations\":[";first=true;
    for (const auto& round:result.iterations) {
        if (!first) {std::cout<<',';} first=false;
        std::cout<<"{\"present_factor\":"<<round.present<<",\"conflicts\":[";bool cf=true;
        for (const auto& c:round.conflicts) {if (!cf) {std::cout<<',';} cf=false;std::cout<<'['<<c.first<<',';numbers(c.second);std::cout<<']';}
        std::cout<<"],\"incomplete_nets\":";numbers(round.incomplete);std::cout<<",\"unknown_sources\":";numbers(round.unknown);
        std::cout<<",\"outcomes\":[";bool of=true;
        for (const auto& connections:round.outcomes) {
            if (!of) {std::cout<<',';} of=false;std::cout<<'[';bool con_first=true;
            for (const auto& c:connections) {
                if (!con_first) {std::cout<<',';} con_first=false;
                std::cout<<"{\"status\":\""<<c.status<<"\",\"cost\":";
                if (c.status=="found") std::cout<<c.cost;else std::cout<<"null";
                std::cout<<",\"expanded\":"<<c.expanded<<",\"examined\":"<<c.examined<<",\"fetched\":"<<c.fetched
                    <<",\"blocked_edges\":"<<c.blocked<<",\"unknown_sources\":";numbers(c.unknown);
                std::cout<<",\"path\":";path_json(c.path);std::cout<<'}';
            }
            std::cout<<']';
        }
        std::cout<<"]}";
    }
    std::cout<<"],\"history\":[";first=true;
    for (const auto& h:result.history) {if (!first) {std::cout<<',';} first=false;std::cout<<'['<<h.first<<','<<h.second<<']';}
    std::cout<<"]}\n";require(bool(std::cout),"write native result");
    export_times.push_back(ms(export_start));
    }
    std::cout<<"],\"export_ms\":["<<export_times[0]<<','<<export_times[1]<<"]}\n";
    return 0;
} catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}}
