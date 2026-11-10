#define main original_router_main
#include "trace.cpp"
#undef main
#include <fstream>
#include <cstring>
#include <stdexcept>
static uint32_t raw(float f){uint32_t u;std::memcpy(&u,&f,4);return u;}
static void word(std::ofstream&f,uint32_t u){for(int j=0;j<4;++j)f.put(char(u>>(8*j)));}
static void pad(std::ofstream&f,uint64_t end){while(uint64_t(f.tellp())<end)f.put(0);}
int main(int argc,char**argv){
 if(argc!=3)throw std::runtime_error("args");Router r;r.load(argv[1]);if(r.lazy)throw std::runtime_error("eager required");
 r.updatePresentCongestionCosts(r.cfg.initialPresentCongestionFactor);
 const uint64_t history=((r.ns.size()*4ull+63)&~63ull),prices=history+4096,nets=prices+1024+4096,total=nets+((r.nets.size()*16ull+63)&~63ull);
 std::string out=argv[2];std::ofstream f(out+"/initial.bin",std::ios::binary);
 for(auto&n:r.dyn)word(f,raw(n.hist));pad(f,prices);
 for(int i=0;i<256;++i)word(f,raw(r.presentCongestionCosts[i]));pad(f,nets);
 for(auto&n:r.nets){word(f,raw(n.xCenter));word(f,raw(n.yCenter));word(f,uint32_t(n.connectionsSize));word(f,uint32_t(n.doubleHpwl));}pad(f,total);f.close();if(!f)throw std::runtime_error("write");
 std::ofstream meta(out+"/layout.json");meta<<"{\"nodes\":"<<r.ns.size()<<",\"net_count\":"<<r.nets.size()<<",\"prices_offset\":"<<prices<<",\"nets_offset\":"<<nets<<",\"total_bytes\":"<<total<<",\"initial_factor_bits\":"<<raw(r.cfg.initialPresentCongestionFactor)<<"}\n";
 std::printf("COST_STATE_EXPORT_PASS nodes=%zu nets=%zu\n",r.ns.size(),r.nets.size());
}
