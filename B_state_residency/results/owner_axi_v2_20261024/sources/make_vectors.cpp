#include "owner_store.hpp"
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
using namespace owner_state;
static void check(bool b){if(!b)throw std::runtime_error("vector generation");}
static constexpr uint64_t BASE=0x1fffff000ull;
static uint64_t address(unsigned region,unsigned index){return BASE+(region==0?0:region==1?4096:12288)+16ull*index;}
static void place(std::vector<unsigned char>& image,unsigned offset,Record r){for(auto word:r){for(unsigned j=0;j<4;++j)image[offset++]=word>>(8*j);}}
static void dump(const char* name,const std::vector<unsigned char>& image){std::ofstream f(name,std::ios::binary);f.write((const char*)image.data(),image.size());check(bool(f));}
int main(){
 Store s(128,256);s.primary[2]=Record{{1,0x0001ffff,0,0}};
 s.primary[3]=Record{{1,0x00020001,1,0}};s.pool[0]=Record{{2,65535,0,0}};s.allocator=Record{{1,0,1,0}};
 std::vector<unsigned char> image(16384);for(unsigned i=0;i<image.size();++i)image[i]=(i*53+19)&255;
 auto snapshot=[&](){for(unsigned i=0;i<s.primary.size();++i)place(image,i*16,s.primary[i]);for(unsigned i=0;i<s.pool.size();++i)place(image,4096+i*16,s.pool[i]);place(image,12288,s.allocator);};
 snapshot();dump("initial.bin",image);
 std::ofstream commands("commands.txt"),writes("expected_writes.txt");unsigned sequence=0;uint64_t write_total=0;
 auto emit=[&](unsigned op,unsigned node,unsigned net){
  auto p=s.prepare(op,node,net);
  check(p.status!=CORRUPT);
  commands<<std::dec<<sequence<<' '<<op<<' '<<std::hex<<node<<' '<<net<<' '<<std::dec<<p.status<<' '<<p.count<<' '<<p.occupancy<<' '<<p.will_overuse<<' '<<p.writes.size()<<'\n';
  for(const auto& w:p.writes){writes<<std::dec<<sequence<<' '<<std::hex<<address(w.region,w.index)<<' ';for(int j=3;j>=0;--j)writes<<std::setw(8)<<std::setfill('0')<<w.after[j];writes<<'\n';++write_total;}
  if(p.status==OK)check(s.commit(p)==OK);++sequence;
 };
 emit(GET,2,0);emit(INC,2,0);emit(INC,3,1);emit(DEC,3,0);emit(GET,3,1);
 emit(GET,128,0);emit(GET,0,0x80000000u);emit(7,0,0);emit(DEC,0,7);
 for(unsigned n=0;n<128;++n)for(unsigned net=0;net<4;++net)emit(INC,n,net);
 emit(DEC,0,2);emit(INC,127,101);emit(DEC,0,0);emit(GET,0,3);
 std::mt19937 rng(215871);
 for(unsigned i=0;i<12000;++i)emit(rng()%3,rng()%128,rng()%8);
 for(unsigned n=0;n<128;++n)for(unsigned net=0;net<8;++net)emit(GET,n,net);
 snapshot();dump("expected.bin",image);
 std::cout<<"OWNER_VECTORS_PASS commands="<<sequence<<" record_writes="<<write_total<<" image_bytes="<<image.size()<<'\n';
}
