#include "owner_store.hpp"
#include <fstream>
#include <iostream>
#include <cassert>
#include <string>
using namespace owner_state;
void load(const std::string&p,void*dst,size_t n){std::ifstream f(p,std::ios::binary);assert(f);f.read((char*)dst,n);assert((size_t)f.gcount()==n);}
int main(int argc,char**argv){assert(argc==4);std::string root=argv[1];unsigned nodes=std::stoul(argv[2]),capacity=std::stoul(argv[3]);Store s(nodes,capacity);load(root+"/owners.bin",s.primary.data(),nodes*16ull);if(capacity)load(root+"/owner_pool.bin",s.pool.data(),capacity*16ull);load(root+"/owner_allocator.bin",s.allocator.data(),16);unsigned occupied=0,extra=0,chosen=nodes;
for(unsigned i=0;i<nodes;i++) {auto a=s.primary[i];auto p=s.prepare(GET,i,a[0]?a[0]-1:0);assert(p.status==OK&&p.occupancy==(a[1]>>16)&&p.count==(a[1]&65535));occupied+=a[0]!=0;if(a[2]&&chosen==nodes)chosen=i;for(unsigned ptr=a[2];ptr;ptr=s.pool[ptr-1][2]){auto r=s.pool[ptr-1];auto q=s.prepare(GET,i,r[0]-1);assert(q.status==OK&&q.count==r[1]);extra++;}}
unsigned transitions=0;if(chosen<nodes){auto original=s.primary[chosen];unsigned net=original[0]-1,occ=original[1]>>16,refs=original[1]&65535;
// Drive the actual loaded owner model through primary removal and pool promotion.
for(unsigned j=0;j<refs;j++){auto p=s.prepare(DEC,chosen,net);assert(p.status==OK&&s.commit(p)==OK);transitions++;}assert(s.primary[chosen][0]!=original[0]);auto absent=s.prepare(GET,chosen,net);assert(absent.status==OK&&absent.count==0&&absent.occupancy==occ-1);
// Re-add now missing net using the just freed pool record, not fresh allocation.
auto unused=s.allocator[0];auto p=s.prepare(INC,chosen,net);assert(p.status==OK&&s.commit(p)==OK&&s.allocator[0]==unused);transitions++;auto q=s.prepare(GET,chosen,net);assert(q.status==OK&&q.count==1&&q.occupancy==occ);
for(unsigned j=1;j<refs;j++){auto p=s.prepare(INC,chosen,net);assert(p.status==OK&&s.commit(p)==OK);transitions++;}q=s.prepare(GET,chosen,net);assert(q.status==OK&&q.count==refs&&q.occupancy==occ);
}
std::cout<<"{\"status\":\"passed\",\"nodes\":"<<nodes<<",\"occupied_nodes\":"<<occupied<<",\"overflow_gets\":"<<extra<<",\"promotion_node\":"<<chosen<<",\"transitions\":"<<transitions<<"}\n";
}
