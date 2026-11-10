// Read-only metadata export using the frozen original loader; no routing run.
#define main original_router_main
#include "../build/real_trace/original.cpp"
#undef main
#include <fstream>
int main(int argc, char** argv) {
    if (argc != 3) return 2;
    Router r; r.load(argv[1]);
    std::ofstream f(argv[2]);
    for (size_t i=0; i<r.connections.size(); ++i) {
        const auto& c=r.connections[i];
        f << "{\"connection\":" << i << ",\"id\":" << c.connId
          << ",\"net\":" << c.netIdx << ",\"sink\":" << c.sinkRnode
          << ",\"has_alt\":" << (c.hasAltSinks()?"true":"false") << ",\"path\":[";
        for(size_t j=0;j<c.rnodes.size();++j) {if(j)f<<',';f<<c.rnodes[j];}
        f << "]}\n";
    }
    for(size_t i=0;i<r.occCnt.size();++i) if(r.occCnt[i])
        f << "{\"resource\":" << i << ",\"occupancy\":" << r.occCnt[i] << "}\n";
    if(!f) return 1;
}
