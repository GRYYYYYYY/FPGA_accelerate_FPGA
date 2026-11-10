#pragma once
// Native CPU executable for AGRAPH01. No synthesis claims; little-endian hosts.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <deque>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <list>
#include <map>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>
#include <sstream>
using Clock=std::chrono::steady_clock;
static inline double ms(Clock::time_point t){return std::chrono::duration<double,std::milli>(Clock::now()-t).count();}
static inline void require(bool ok,const char* s){if(!ok)throw std::runtime_error(s);}
struct Section{uint64_t off,bytes;uint32_t count,width;};
struct Edge{uint32_t dst,tile,pip,up,down,attr,dir;
 bool operator<(const Edge& b)const{return std::tie(dst,tile,pip,up,down,attr,dir)<std::tie(b.dst,b.tile,b.pip,b.up,b.down,b.attr,b.dir);}};
static_assert(sizeof(Edge)==28,"edge layout");
struct Rule{int32_t dx,dy;uint32_t pip,up,down,attr,dir;};
struct Node{uint32_t name,attr,anchor;int32_t row;};
struct Tile{uint32_t name,attr;int32_t x,y,slr;uint32_t type;};
struct Grid{int32_t x,y;uint32_t tile;};
struct Alias{uint32_t tile,wire,node;};
struct Instance{int32_t tid;uint32_t rs,rc,as,ac,ps,pc;};
struct Query{uint32_t src,dst,budget,timed;};
struct Patch{uint32_t index,attr;};
enum SectionId{STR_OFF,STR_DATA,ATTR_OFF,ATTR_KV,TILE,NODE,ROOT,ALIAS,GRID,AUDIT,CSR_OFF,CSR_EDGE,TPL_OFF,RULE,INSTANCE,REMOVE,ADD,PATCH,SECTION_COUNT};
class Graph{
 std::vector<uint8_t> data;
 std::map<std::string,Section> sections;
 std::array<Section,SECTION_COUNT> views{};
 struct Entry{std::vector<Edge> edges;std::list<uint32_t>::iterator position;};
 std::unordered_map<uint32_t,Entry> cache;
 std::list<uint32_t> lru;
 size_t cache_payload=0;
 bool materialized=false;
 std::vector<uint64_t> expanded_offsets;
 std::vector<Edge> expanded_edges;
 template<class T>T load(SectionId s,size_t i,bool charge=true){
  const auto& d=views[s];require(sizeof(T)==d.width && i<d.count,"record index/size");
  T v;std::memcpy(&v,data.data()+d.off+i*d.width,sizeof(v));if(charge)logical_bytes+=sizeof(T);return v;
 }
 uint32_t lookup_tile(int32_t x,int32_t y){
  size_t lo=0,hi=views[GRID].count;
  while(lo<hi){size_t mid=lo+(hi-lo)/2;auto g=load<Grid>(GRID,mid);
   if(std::tie(g.x,g.y)<std::tie(x,y))lo=mid+1;else hi=mid;}
  require(lo<views[GRID].count,"missing grid coordinate");auto g=load<Grid>(GRID,lo);
  require(g.x==x&&g.y==y,"missing grid coordinate");return g.tile;
 }
 uint32_t lookup_alias(uint32_t tile,uint32_t wire){
  size_t lo=0,hi=views[ALIAS].count;
  while(lo<hi){size_t mid=lo+(hi-lo)/2;auto a=load<Alias>(ALIAS,mid);
   if(std::tie(a.tile,a.wire)<std::tie(tile,wire))lo=mid+1;else hi=mid;}
  require(lo<views[ALIAS].count,"missing wire alias");auto a=load<Alias>(ALIAS,lo);
  require(a.tile==tile&&a.wire==wire,"missing wire alias");return a.node;
 }
 Edge expand(uint32_t src,const Tile& anchor,Rule r){
  auto tile=lookup_tile(anchor.x+r.dx,anchor.y+r.dy);require(r.dir<=1,"bad rule direction");
  uint32_t sw=r.dir?r.down:r.up,dw=r.dir?r.up:r.down;
  require(lookup_alias(tile,sw)==src,"canonical source mismatch");
  return {lookup_alias(tile,dw),tile,r.pip,r.up,r.down,r.attr,r.dir};
 }
public:
 uint32_t mode=0;size_t capacity=0;uint64_t logical_bytes=0,hits=0,misses=0,peak_cache_edge_bytes=0;
 explicit Graph(const std::string& path,size_t cap):capacity(cap){
  uint32_t endian=1;require(*reinterpret_cast<uint8_t*>(&endian)==1,"little-endian host required");
  std::ifstream f(path,std::ios::binary);require(bool(f),"open packed file");f.seekg(0,std::ios::end);
  auto length=f.tellg();require(length>=24,"short header");data.resize(size_t(length));f.seekg(0);f.read(reinterpret_cast<char*>(data.data()),length);require(bool(f),"read file");
  require(std::memcmp(data.data(),"AGRAPH01",8)==0,"bad magic");
  uint32_t h[4];std::memcpy(h,data.data()+8,16);require(h[0]==1&&h[1]<=1&&h[2]==0x01020304,"bad format");mode=h[1];
  require(h[3]<=64&&24ull+40ull*h[3]<=data.size(),"bad directory");
  std::vector<std::pair<uint64_t,uint64_t>> spans;uint64_t max_end=24+40ull*h[3];
  for(uint32_t i=0;i<h[3];i++){
   auto p=data.data()+24+i*40;size_t n=0;while(n<16&&p[n])n++;require(n<16,"unterminated section name");
   std::string name(reinterpret_cast<const char*>(p),n);Section d;
   std::memcpy(&d.off,p+16,8);std::memcpy(&d.bytes,p+24,8);std::memcpy(&d.count,p+32,4);std::memcpy(&d.width,p+36,4);
   require(d.width&&d.bytes==uint64_t(d.count)*d.width&&d.off%64==0&&d.off>=24+40ull*h[3]&&d.off<=data.size()&&d.bytes<=data.size()-d.off,"bad section");
   require(sections.emplace(name,d).second,"duplicate section");if(d.bytes)spans.emplace_back(d.off,d.off+d.bytes);max_end=std::max(max_end,d.off+d.bytes);
  }
  const char* names[]={"STR_OFF","STR_DATA","ATTR_OFF","ATTR_KV","TILE","NODE","ROOT","ALIAS","GRID","AUDIT","CSR_OFF","CSR_EDGE","TPL_OFF","RULE","INSTANCE","REMOVE","ADD","PATCH"};
  for(size_t i=0;i<SECTION_COUNT;i++){auto it=sections.find(names[i]);if(it!=sections.end())views[i]=it->second;}
  std::sort(spans.begin(),spans.end());for(size_t i=1;i<spans.size();i++)require(spans[i-1].second<=spans[i].first,"section overlap");
  require(data.size()==((max_end+63)/64)*64,"trailing/truncated file");
  for(auto name:{"STR_OFF","STR_DATA","ATTR_OFF","ATTR_KV","TILE","NODE","ROOT","ALIAS","GRID","AUDIT"})require(sections.count(name),"missing common section");
  require(views[NODE].width==16&&views[TILE].width==24&&views[ROOT].width==12,"bad common width");
  if(mode){for(auto name:{"TPL_OFF","RULE","INSTANCE","REMOVE","ADD","PATCH"})require(sections.count(name),"missing compact section");}
  else{require(sections.count("CSR_OFF")&&sections.count("CSR_EDGE"),"missing CSR section");}
 }
 size_t node_count()const{return views[NODE].count;}
 size_t source_count()const{return views[ROOT].count;}
 size_t file_bytes()const{return data.size();}
 void clear_cache(){cache.clear();lru.clear();cache_payload=0;hits=misses=logical_bytes=peak_cache_edge_bytes=0;}
 bool neighbors(uint32_t node,std::vector<Edge>& out){
  auto n=load<Node>(NODE,node);if(n.row<0)return false;
  if(materialized){auto begin=expanded_offsets[node],end=expanded_offsets[node+1];logical_bytes+=16+(end-begin)*sizeof(Edge);out.assign(expanded_edges.begin()+begin,expanded_edges.begin()+end);misses++;return true;}
  if(capacity){auto it=cache.find(node);if(it!=cache.end()){
    hits++;lru.splice(lru.begin(),lru,it->second.position);out=it->second.edges;return true;}}
  misses++;out.clear();
  if(!mode){auto start=load<uint64_t>(CSR_OFF,n.row);auto end=load<uint64_t>(CSR_OFF,n.row+1);
   require(start<=end&&end<=views[CSR_EDGE].count,"bad CSR range");out.reserve(end-start);
   for(auto i=start;i<end;i++)out.push_back(load<Edge>(CSR_EDGE,i));
  }else{
   auto inst=load<Instance>(INSTANCE,n.row);auto tile=load<Tile>(TILE,n.anchor);
   std::vector<uint32_t> remove;for(uint32_t i=0;i<inst.rc;i++)remove.push_back(load<uint32_t>(REMOVE,size_t(inst.rs)+i));
   std::map<uint32_t,uint32_t> patch;for(uint32_t i=0;i<inst.pc;i++){auto p=load<Patch>(PATCH,size_t(inst.ps)+i);require(patch.emplace(p.index,p.attr).second,"duplicate patch");}
   require(std::is_sorted(remove.begin(),remove.end())&&std::adjacent_find(remove.begin(),remove.end())==remove.end(),"remove order/duplicates");
   if(inst.tid>=0){auto start=load<uint64_t>(TPL_OFF,inst.tid);auto end=load<uint64_t>(TPL_OFF,inst.tid+1);
    require(start<=end&&end<=views[RULE].count,"bad template range");
    for(auto x:remove)require(x<end-start&&!patch.count(x),"bad removal index");
    for(auto p:patch)require(p.first<end-start,"bad patch index");
    for(uint64_t i=start;i<end;i++)if(!std::binary_search(remove.begin(),remove.end(),uint32_t(i-start))){auto r=load<Rule>(RULE,i);auto p=patch.find(i-start);if(p!=patch.end())r.attr=p->second;out.push_back(expand(node,tile,r));}
   }else require(inst.tid==-1&&remove.empty()&&patch.empty(),"bad fallback instance");
   for(uint32_t i=0;i<inst.ac;i++)out.push_back(expand(node,tile,load<Rule>(ADD,size_t(inst.as)+i)));
   std::sort(out.begin(),out.end());
  }
  for(auto& e:out)require(e.dst<node_count()&&e.dir<=1&&e.tile<views[TILE].count&&e.pip<views[STR_OFF].count-1&&e.up<views[STR_OFF].count-1&&e.down<views[STR_OFF].count-1&&e.attr<views[ATTR_OFF].count-1,"bad edge reference");
  if(capacity){if(cache.size()==capacity){auto key=lru.back();cache_payload-=cache.at(key).edges.size()*sizeof(Edge);cache.erase(key);lru.pop_back();}
   lru.push_front(node);cache.emplace(node,Entry{out,lru.begin()});cache_payload+=out.size()*sizeof(Edge);peak_cache_edge_bytes=std::max<uint64_t>(peak_cache_edge_bytes,cache_payload);}
  return true;
 }
 void dump(const std::string& path){
  std::ofstream f(path,std::ios::binary);require(bool(f),"open native dump");std::vector<Edge> edges;
  for(uint32_t n=0;n<node_count();n++)if(neighbors(n,edges))for(auto& e:edges){f.write(reinterpret_cast<const char*>(&n),4);f.write(reinterpret_cast<const char*>(&e),28);}
  require(bool(f),"write native dump");clear_cache();
 }
 void materialize_all(){
  require(!materialized,"already materialized");expanded_offsets.push_back(0);std::vector<Edge> edges;
  for(uint32_t n=0;n<node_count();n++){if(neighbors(n,edges))expanded_edges.insert(expanded_edges.end(),edges.begin(),edges.end());expanded_offsets.push_back(expanded_edges.size());}
  clear_cache();materialized=true;
 }
 size_t expanded_allocation_bytes()const{return expanded_edges.capacity()*sizeof(Edge)+expanded_offsets.capacity()*sizeof(uint64_t);}
};
