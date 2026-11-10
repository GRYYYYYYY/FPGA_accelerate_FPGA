// Export the actual loader state in the owner AXI store's little-endian layout.
#define main original_router_main
#include "trace.cpp"
#undef main
#include <fstream>
#include <stdexcept>
static void require(bool value){if(!value)throw std::runtime_error("owner export invariant");}
static void word(std::ofstream& f,uint32_t value){for(unsigned j=0;j<4;++j)f.put(char(value>>(8*j)));}
int main(int argc,char**argv){
 require(argc==3);Router r;r.load(argv[1]);require(!r.lazy);
 std::string out=argv[2];std::ofstream f(out+"/owners.bin",std::ios::binary),list(out+"/owners.tsv");
 require(bool(f)&&bool(list));size_t occupied=0,refs=0;
 for(size_t i=0;i<r.ns.size();++i){
  require(r.userOverflow[i]==nullptr);require(r.occCnt[i]<=1);
  require((r.ownerNet[i]<0)==(r.occCnt[i]==0));require((r.ownerCnt[i]==0)==(r.occCnt[i]==0));
  if(r.ownerNet[i]>=0){require(size_t(r.ownerNet[i])<r.nets.size());++occupied;refs+=r.ownerCnt[i];list<<i<<'\t'<<r.ownerNet[i]<<'\t'<<r.ownerCnt[i]<<'\t'<<r.occCnt[i]<<'\n';}
  word(f,r.ownerNet[i]+1);word(f,uint32_t(r.ownerCnt[i])|(uint32_t(r.occCnt[i])<<16));word(f,0);word(f,0);
 }
 // Match the existing owner test address map; pool is 64 records, initially empty.
 const uint64_t primary=(r.ns.size()*16ull+63)&~63ull,pool=primary+4096,allocator=pool+1024+4096,total=allocator+64;
 while(uint64_t(f.tellp())<total)f.put(0);f.close();require(bool(f));
 std::ofstream meta(out+"/layout.json");meta<<"{\"nodes\":"<<r.ns.size()<<",\"nets\":"<<r.nets.size()<<",\"connections\":"<<r.connections.size()<<",\"occupied\":"<<occupied<<",\"references\":"<<refs<<",\"primary_bytes\":"<<primary<<",\"pool_offset\":"<<pool<<",\"pool_capacity\":64,\"allocator_offset\":"<<allocator<<",\"total_bytes\":"<<total<<"}\n";
 std::printf("INITIAL_OWNER_EXPORT_PASS occupied=%zu references=%zu nodes=%zu\n",occupied,refs,r.ns.size());
}
