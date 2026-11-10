#include "../src/native/site_routes.hpp"
struct Fixture {
    using Id=uint32_t;
    std::vector<std::vector<Edge>> rows=std::vector<std::vector<Edge>>(12);
    size_t node_count() const {return rows.size();}
    bool neighbors(Id n,std::vector<Edge>& out) {out=rows[n];return true;}
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
    if (argc!=2) throw std::invalid_argument("scenario required");
    unsigned scenario=std::stoul(argv[1]);
    Fixture graph;std::map<unsigned,site_native::Demands> requirements;
    auto add=[&](unsigned a,unsigned b,unsigned pip) {graph.rows[a].push_back(Edge{b,0,pip,0,0,0,0});};
    unsigned middle=scenario==9?2:3;
    add(0,2,0);add(2,6,1);add(1,middle,2);add(middle,7,3);
    add(1,4,4);add(4,5,5);add(5,8,6);add(8,9,7);add(9,7,8);
    for (unsigned pip:{0,2}) {
        site_native::Demands d;d.verified=true;
        if (scenario==1 || scenario==4) d.bits.emplace_back(1,1,pip==0?0:1);
        else if (scenario==2) d.values.emplace_back(1,pip==0?1:2);
        else if (scenario==3) d.bits.emplace_back(1,pip==0?1:2,pip==0?1:0);
        else d.signals={1};
        if (scenario!=5) requirements[pip]=d;
    }
    site_native::Demands fixed;fixed.verified=true;
    if (scenario==4) fixed.bits.emplace_back(1,1,0);
    site_native::SiteState state({},fixed);
    std::vector<netlist_native::NetQuery> queries={{0,0,{6}},{1,1,{7}}};
    if (scenario==7) queries[0].sinks={2,6};
    auto r=site_native::route_batch(graph,queries,scenario==8?std::set<uint32_t>{4}:std::set<uint32_t>{},state,
        [&](unsigned,const Edge& e) {
            site_native::EdgeSemantics s;s.pseudo=e.pip==0||e.pip==2;
            auto found=requirements.find(e.pip);if (found!=requirements.end()) s.demands=found->second;return s;
        },[&](unsigned,unsigned,const Edge& e) {return scenario==10&&e.pip==2;},
        scenario==11?1:8,scenario==6?1:100,8);
    std::cout<<"{\"status\":\""<<r.status<<"\",\"routes\":[";bool first=true;
    for (const auto& item:r.routes) {
        if (!first) {std::cout<<',';} first=false;const auto& route=item.second;
        std::cout<<"{\"net\":"<<item.first<<",\"complete\":"<<(route.complete?"true":"false")<<",\"nodes\":";numbers(route.nodes);
        std::cout<<",\"pips\":[";bool f=true;
        for (const auto& p:route.edges) {if (!f) {std::cout<<',';} f=false;std::cout<<p.second.pip;}
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
                for (auto p:c.unknown_pips) {if (!pf) {std::cout<<',';} pf=false;std::cout<<p.second;}
                std::cout<<"]}";
            }
            std::cout<<']';
        }
        std::cout<<"]}";
    }
    std::cout<<"]}\n";return 0;
} catch (const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}}
