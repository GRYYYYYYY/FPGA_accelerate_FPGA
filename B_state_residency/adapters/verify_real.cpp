// Independent final path checks against the frozen exported graph, outside timings.
#define main original_router_main
#include "original.cpp"
#undef main
#include <fstream>
#include <iostream>
#include <set>
int main(int argc,char** argv) {
    if(argc!=3) return 2;
    Router r; r.load(argv[1]);
    std::ifstream f(argv[2],std::ios::binary);
    auto u32=[&](){ unsigned char b[4]; f.read(reinterpret_cast<char*>(b),4);
        if(!f) throw std::runtime_error("truncated result");
        return (uint32_t(b[0])<<24)|(uint32_t(b[1])<<16)|(uint32_t(b[2])<<8)|b[3]; };
    if(u32()!=0x52575231) throw std::runtime_error("bad result magic");
    uint32_t count=u32();
    if(count!=r.connections.size()) throw std::runtime_error("connection count mismatch");
    std::unordered_map<int,int> byId;
    for(size_t i=0;i<r.connections.size();++i)
        if(!byId.emplace(r.connections[i].connId,int(i)).second) throw std::runtime_error("duplicate input connection ID");
    std::vector<int> owners(r.numNodes(),-1);
    uint64_t badEdges=0,badEndpoints=0,cycles=0,overused=0,unrouted=0,segments=0;
    for(uint32_t k=0;k<count;++k) {
        int id=int(u32()); auto it=byId.find(id);
        if(it==byId.end()) throw std::runtime_error("unknown/duplicate result connection");
        auto& c=r.connections[it->second]; byId.erase(it);
        int routed=f.get(); uint32_t length=u32();
        if(length>uint32_t(r.numNodes())) throw std::runtime_error("invalid path length");
        std::vector<int> path; path.reserve(length); std::set<int> seen;
        for(uint32_t j=0;j<length;++j) {
            int tile=int(u32()),wire=int(u32());
            int node=r.keyToId.find((int64_t(tile)<<20)|wire);
            if(node<0) throw std::runtime_error("unknown canonical node");
            path.push_back(node); if(!seen.insert(node).second) ++cycles;
            // Count resource owners by net, including source/sink terminals for cross-net shorts.
            if(owners[node]<0) owners[node]=c.netIdx;
            else if(owners[node]!=c.netIdx) ++overused;
        }
        if(routed!=1 || path.empty()) { ++unrouted; continue; }
        if(path.back()!=c.sourceRnode || !r.isValidSink(c,path.front())) ++badEndpoints;
        for(size_t j=1;j<path.size();++j) {
            int parent=path[j],child=path[j-1];
            auto begin=r.childIds.begin()+r.ns[parent].childStart;
            if(std::find(begin,begin+r.ns[parent].childCount,child)==begin+r.ns[parent].childCount) ++badEdges;
            ++segments;
        }
    }
    if(f.get()!=EOF) throw std::runtime_error("trailing result bytes");
    std::cout<<"{\"connections\":"<<count<<",\"segments\":"<<segments<<",\"bad_edges\":"<<badEdges
        <<",\"bad_endpoints\":"<<badEndpoints<<",\"cycles\":"<<cycles<<",\"cross_net_resource_conflicts\":"<<overused
        <<",\"unrouted\":"<<unrouted<<"}\n";
    return (badEdges||badEndpoints||cycles||overused||unrouted)?1:0;
}
