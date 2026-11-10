#include "../src/native/site_search.hpp"
struct Fixture {
    std::vector<std::vector<Edge>> rows=std::vector<std::vector<Edge>>(4);
    bool unknown=false;
    size_t node_count() const {return rows.size();}
    bool neighbors(uint32_t n,std::vector<Edge>& out) {if (unknown&&n==0) return false;out=rows[n];return true;}
};
template<class T> void numbers(const T& values) {
    std::cout<<'[';bool first=true;
    for (auto v:values) {if (!first) {std::cout<<',';} first=false;std::cout<<v;}
    std::cout<<']';
}
int main(int argc,char** argv) {try {
    if (argc!=2) throw std::invalid_argument("scenario required");
    unsigned scenario=std::stoul(argv[1]);Fixture graph;
    std::map<unsigned,site_native::Demands> requirements;std::set<unsigned> pseudo,roots={0};
    site_native::Demands initial;initial.verified=true;site_native::SiteState state;
    auto add=[&](unsigned a,unsigned b,unsigned pip,bool p) {
        graph.rows[a].push_back(Edge{b,0,pip,0,0,0,0});if (p) pseudo.insert(pip);
    };
    auto demand=[]() {site_native::Demands d;d.verified=true;return d;};
    if (scenario<=1) {
        add(0,1,0,true);add(0,2,1,true);add(2,1,2,false);add(1,3,3,true);
        for (unsigned pip:{0,1,3}) {auto d=demand();d.bits.emplace_back(0,1,pip==0?1:0);requirements[pip]=d;}
    } else if (scenario==2 || scenario==3) {add(0,3,0,true);graph.unknown=scenario==3;}
    else if (scenario==5 || scenario==6) {
        roots={0,1};initial.values.emplace_back(0,2);add(0,3,0,true);add(1,3,1,true);
        for (unsigned pip:{0,1}) {auto d=demand();d.values.emplace_back(0,pip+1);requirements[pip]=d;}
    } else {
        add(0,3,0,true);auto d=demand();d.signals={1};requirements[0]=d;
        if (scenario==4) state=site_native::SiteState({{1,99}});
        if (scenario==7 || scenario==8) {add(0,2,1,false);add(2,3,2,false);}
        if (scenario==7) state.replace(1,d);
        if (scenario==9) requirements[0].verified=false;
        if (scenario==11) requirements[0].additional_unresolved=true;
    }
    auto result=site_native::search(graph,roots,3,initial,scenario==1?1:100,{},
        [&](unsigned,const Edge& e) {
            site_native::EdgeSemantics s;s.pseudo=pseudo.count(e.pip);
            auto it=requirements.find(e.pip);if (it!=requirements.end()) s.demands=it->second;return s;
        },[&](unsigned,const Edge& e) {return scenario==6&&e.pip==1;},
        [&](const site_native::Normalized& d) {return !state.conflicts(0,site_native::payload(d));},
        [&](unsigned,const Edge& e,const site_native::Normalized&,const site_native::Normalized&) {
            return scenario==10?-1:(scenario==8&&e.pip==0?10:1);
        });
    std::cout<<"{\"status\":\""<<result.status<<"\",\"expanded\":"<<result.expanded<<",\"blocked\":";
    if (result.status=="budget_exhausted") std::cout<<"null";else std::cout<<result.blocked;
    std::cout<<",\"cost\":";if (result.status=="found") std::cout<<result.cost;else std::cout<<"null";
    std::cout<<",\"path\":[";bool first=true;
    for (auto p:result.path) {if (!first) {std::cout<<',';} first=false;std::cout<<p.second.pip;}
    std::cout<<"],\"unknown_sources\":";numbers(result.unknown_sources);std::cout<<",\"unknown_pips\":[";first=true;
    for (auto p:result.unknown_pips) {if (!first) {std::cout<<',';} first=false;std::cout<<p.second;}
    std::cout<<"],\"demands\":";
    if (result.status!="found") std::cout<<"null";
    else {
        std::cout<<'[';numbers(result.demands.signals);std::cout<<",[";first=true;
        for (auto b:result.demands.bits) {if (!first) {std::cout<<',';} first=false;std::cout<<'['<<b.first<<','<<b.second.first<<','<<b.second.second<<']';}
        std::cout<<"],[";first=true;
        for (auto v:result.demands.values) {if (!first) {std::cout<<',';} first=false;std::cout<<'['<<v.first<<','<<v.second<<']';}
        std::cout<<"]]";
    }
    std::cout<<"}\n";return 0;
} catch (const std::invalid_argument&) {std::cout<<"{\"error\":true}\n";return 0;}}
