#include "owner_store.hpp"
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
using namespace owner_state;
static void ck(bool x){if(!x)throw std::runtime_error("multiowner independent model mismatch");}
static void load(const char* p,Record* dst,size_t bytes){std::ifstream f(p,std::ios::binary);f.read((char*)dst,bytes);ck(size_t(f.gcount())==bytes);}
int main(int argc,char**argv){
 ck(argc==11);unsigned n=std::stoul(argv[6]),c=std::stoul(argv[7]);uint64_t pb=std::stoull(argv[8]),qb=std::stoull(argv[9]);
 Store s(n,c);load(argv[1],s.primary.data(),uint64_t(n)*16);load(argv[2],s.pool.data(),uint64_t(c)*16);load(argv[3],&s.allocator,16);
 std::ifstream commands(argv[5]);std::ofstream writes(argv[10]);unsigned op,node,net,status,count,occ,ops=0,mut=0,refused=0;uint64_t nw=0;
 while(commands>>op>>node>>net>>status>>count>>occ){auto p=s.prepare(op,node,net);ck(p.status==status&&p.count==count&&p.occupancy==occ);
  for(auto&w:p.writes){uint64_t address=(w.region==0?0:w.region==1?pb:pb+qb)+uint64_t(w.index)*16;writes<<std::hex<<address<<' ';for(int j=3;j>=0;--j)writes<<std::setw(8)<<std::setfill('0')<<w.after[j];writes<<'\n';++nw;}
  if(p.status==OK){ck(s.commit(p)==OK);if(!p.writes.empty())++mut;}else{ck(p.writes.empty());if(p.status==CAPACITY)++refused;}++ops;
 }
 std::ifstream live(argv[4],std::ios::binary);uint64_t checked=0;auto record=[&](const Record&r){Record got;live.read((char*)&got,16);ck(live.gcount()==16&&got==r);checked+=16;};auto pad=[&](uint64_t bytes){for(uint64_t i=0;i<bytes;++i){char x;live.get(x);ck(live&&x==0);}checked+=bytes;};
 for(auto&r:s.primary)record(r);pad(pb-uint64_t(n)*16);for(auto&r:s.pool)record(r);pad(qb-uint64_t(c)*16);record(s.allocator);pad(48);ck(live.peek()==std::char_traits<char>::eof());
 std::cout<<"{\"operations\":"<<ops<<",\"mutations\":"<<mut<<",\"capacity_refusals\":"<<refused<<",\"record_writes\":"<<nw<<",\"bytes_checked\":"<<checked<<"}\n";
}
