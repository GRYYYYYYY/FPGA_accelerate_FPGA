#include "../src/native/netlist_routes.hpp"
struct Fixture {
    std::vector<std::vector<Edge>> rows=std::vector<std::vector<Edge>>(12);
    bool unknown=false;
    size_t node_count() const {return rows.size();}
    bool neighbors(uint32_t n,std::vector<Edge>& out) {
        if (unknown && n==2) return false;
        out=rows[n];return true;
    }
};
template<class T> void numbers(const T& values) {
    std::cout<<'[';bool first=true;
    for (auto v:values) {if (!first) {std::cout<<',';} first=false;std::cout<<v;}
    std::cout<<']';
}
int main(int argc,char** argv) {try {
    require(argc==5,"expected iterations budget unknown cap");
    Fixture graph;graph.unknown=std::stoul(argv[3]);
    unsigned pip=0;
    for (auto pair:std::vector<std::pair<unsigned,unsigned>>{{0,2},{2,6},{1,2},{2,7},{1,3},{3,4},{4,5},{5,8},{8,9},{9,7}})
        graph.rows[pair.first].push_back(Edge{pair.second,0,pip++,0,0,0,0});
    std::vector<netlist_native::NetQuery> queries={{0,0,{6}},{1,1,{7}}};
    auto result=netlist_native::route_batch(graph,queries,{},
        [](uint32_t,uint32_t,const Edge&){return false;},
        std::stoul(argv[1]),std::stoull(argv[2]),std::stoull(argv[4]));
    std::cout<<"{\"status\":\""<<result.status<<"\",\"routes\":[";
    bool first=true;
    for (const auto& item:result.routes) {
        if (!first) {std::cout<<',';} first=false;
        const auto& r=item.second;
        std::cout<<"{\"net\":"<<item.first<<",\"complete\":"<<(r.complete?"true":"false")<<",\"nodes\":";
        numbers(r.nodes);std::cout<<",\"pips\":[";bool edge_first=true;
        for (const auto& p:r.edges) {if (!edge_first) std::cout<<',';edge_first=false;std::cout<<p.second.pip;}
        std::cout<<"]}";
    }
    std::cout<<"],\"iterations\":[";first=true;
    for (const auto& round:result.iterations) {
        if (!first) {std::cout<<',';} first=false;
        std::cout<<"{\"present\":"<<round.present<<",\"conflicts\":[";bool cfirst=true;
        for (const auto& c:round.conflicts) {if (!cfirst) std::cout<<',';cfirst=false;std::cout<<'['<<c.first<<',';numbers(c.second);std::cout<<']';}
        std::cout<<"],\"incomplete\":";numbers(round.incomplete);
        std::cout<<",\"unknown\":";numbers(round.unknown);
        std::cout<<",\"connections\":[";bool rfirst=true;
        for (const auto& connections:round.outcomes) for (const auto& c:connections) {
            if (!rfirst) {std::cout<<',';} rfirst=false;
            std::cout<<"{\"status\":\""<<c.status<<"\",\"cost\":";
            if (c.status=="found") std::cout<<c.cost;else std::cout<<"null";
            std::cout<<",\"expanded\":"<<c.expanded<<",\"examined\":"<<c.examined<<",\"fetched\":"<<c.fetched
                     <<",\"blocked_edges\":"<<c.blocked<<",\"unknown_sources\":";numbers(c.unknown);std::cout<<'}';
        }
        std::cout<<"]}";
    }
    std::cout<<"],\"history\":[";first=true;
    for (const auto& h:result.history) {if (!first) {std::cout<<',';} first=false;std::cout<<'['<<h.first<<','<<h.second<<']';}
    std::cout<<"]}\n";return 0;
} catch (const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}}
