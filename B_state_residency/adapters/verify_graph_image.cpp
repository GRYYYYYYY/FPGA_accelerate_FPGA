// Verify canonical arrays against the unmodified CPU Router loader, without routing.
#define main b_original_main
#include "trace.cpp"
#undef main
#include <fstream>
#include <stdexcept>
static void check(bool condition) {if(!condition)throw std::runtime_error("graph image mismatch");}
static uint32_t u32(std::ifstream& f){unsigned char b[4];f.read((char*)b,4);check(bool(f));return uint32_t(b[0])|(uint32_t(b[1])<<8)|(uint32_t(b[2])<<16)|(uint32_t(b[3])<<24);}
static int16_t i16(std::ifstream& f){unsigned char b[2];f.read((char*)b,2);check(bool(f));return int16_t(uint16_t(b[0])|(uint16_t(b[1])<<8));}
static uint8_t u8(std::ifstream& f){char b;f.get(b);check(bool(f));return uint8_t(b);}
static void eof(std::ifstream& f){check(f.peek()==std::char_traits<char>::eof());}
int main(int argc,char** argv){
 check(argc==5);Router router;router.load(argv[1]);const size_t nodes=std::stoull(argv[3]),edges=std::stoull(argv[4]);
 check(router.ns.size()==nodes && router.childIds.size()==edges && !router.lazy);
 const std::string path=argv[2];std::ifstream off(path+"/offsets.u32le",std::ios::binary),adj(path+"/edges.u32le",std::ios::binary),attrs(path+"/nodes.rrt32",std::ios::binary);
 uint64_t edge=0;check(u32(off)==0);
 for(size_t i=0;i<nodes;++i){
  const auto& a=router.ns[i];const auto& c=router.nc[i];
  check(int32_t(u32(attrs))==a.tileAddr);check(int32_t(u32(attrs))==c.wireIndex);
  check(u8(attrs)==uint8_t(c.type));const uint8_t flags=u8(attrs);
  const unsigned expected=(c.createdAtInit?1:0)|(a.isLaguna?2:0)|(a.isPinfeed?4:0)|(a.pinfeedLeadsToLaguna?8:0)|(a.arcLockedInit?32:0)|(a.preserved?64:0)|(a.isPinbounce?128:0);
  check((flags&239)==expected);
  check(i16(attrs)==a.beginX);check(i16(attrs)==a.beginY);check(i16(attrs)==a.endX);check(i16(attrs)==a.endY);check(i16(attrs)==a.length);
  uint32_t bits;std::memcpy(&bits,&a.baseCost,4);check(u32(attrs)==bits);
  check(int32_t(u32(attrs))==c.hashCode);check(int32_t(u32(attrs))==c.prevInit);
  check(a.childStart>=0 && uint64_t(a.childStart)==edge && a.childCount>=0);
  for(int k=0;k<a.childCount;++k){const uint32_t child=u32(adj);check(child<nodes && int(child)==router.childIds[size_t(a.childStart)+k]);++edge;}
  check(u32(off)==edge);
 }
 check(edge==edges);eof(off);eof(adj);eof(attrs);
 std::printf("GRAPH_IMAGE_PASS nodes=%zu edges=%zu\n",nodes,edges);return 0;
}
