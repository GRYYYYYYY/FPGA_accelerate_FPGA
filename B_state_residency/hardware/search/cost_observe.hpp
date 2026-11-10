#pragma once
#include "search_cost.hpp"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <stdexcept>
// Serial CPU observer only. Calls the unchanged helper, samples complete arithmetic packets.
namespace cost_observe {
inline std::uint32_t bits(float f){std::uint32_t u;std::memcpy(&u,&f,4);return u;}
struct Recorder {
 std::FILE* file=nullptr;std::uint64_t calls=0,selected=0;unsigned masks=0;
 std::uint32_t x[23]{},y[5]{};bool enabled=false;int iteration=0,connection=0,parent=0,child=0;unsigned first[128]{};
 ~Recorder(){if(file){std::fprintf(file,"END %llu %llu\n",(unsigned long long)calls,(unsigned long long)selected);std::fclose(file);}}
};
inline Recorder r;
inline void begin(int iteration,int connection,int parent,int child){
 if(!r.file){const char* p=std::getenv("B_COST_VECTORS");if(!p)throw std::runtime_error("B_COST_VECTORS missing");r.file=std::fopen(p,"w");if(!r.file)throw std::runtime_error("cost trace open");}
 if(r.enabled)throw std::runtime_error("nested cost arithmetic");
 r.enabled=true;r.masks=0;r.iteration=iteration;r.connection=connection;r.parent=parent;r.child=child;
}
inline float sharing_factor(float w,int c){float y=search_cost::sharing_factor(w,c);if(r.enabled){r.x[0]=bits(w);r.x[1]=c;r.y[0]=bits(y);r.masks|=1;}return y;}
inline float node_cost(float base,float hist,float present,float sharing,int connections,float dist,int hpwl){
 float y=search_cost::node_cost(base,hist,present,sharing,connections,dist,hpwl);
 if(r.enabled){if(bits(sharing)!=r.y[0])throw std::runtime_error("sharing packet mismatch");r.x[2]=bits(base);r.x[3]=bits(hist);r.x[4]=bits(present);r.x[5]=connections;r.x[6]=bits(dist);r.x[7]=hpwl;r.y[1]=bits(y);r.masks|=2;}return y;
}
inline float partial_cost(float parent,float node,float weight,int length,float sharing){
 float y=search_cost::partial_cost(parent,node,weight,length,sharing);
 if(r.enabled){if(bits(node)!=r.y[1]||bits(sharing)!=r.y[0])throw std::runtime_error("partial packet mismatch");r.x[8]=bits(parent);r.x[9]=bits(weight);r.x[10]=length;r.y[2]=bits(y);r.masks|=4;}return y;
}
inline float heuristic(float weight,int distance,bool landmarks,const std::uint16_t target[8],const std::uint16_t child[8],float scale){
 float y=search_cost::heuristic(weight,distance,landmarks,target,child,scale);
 if(r.enabled){r.x[11]=bits(weight);r.x[12]=distance;r.x[13]=landmarks;r.x[14]=bits(scale);for(int i=0;i<8;i++)r.x[15+i]=landmarks?(std::uint32_t(target[i])|(std::uint32_t(child[i])<<16)):0;r.y[3]=bits(y);r.masks|=8;}return y;
}
inline float total_cost(float partial,float h,float sharing){
 float y=search_cost::total_cost(partial,h,sharing);
 if(r.enabled){
  if(r.masks!=15||bits(partial)!=r.y[2]||bits(h)!=r.y[3]||bits(sharing)!=r.y[0])throw std::runtime_error("incomplete cost packet");
  ++r.calls;r.y[4]=bits(y);bool keep=r.calls%8192==0;
  if(r.iteration>=0&&r.iteration<128&&r.first[r.iteration]<32){++r.first[r.iteration];keep=true;}
  if(keep){std::fprintf(r.file,"V %llu %d %d %d %d",(unsigned long long)r.calls,r.iteration,r.connection,r.parent,r.child);
   for(auto v:r.x)std::fprintf(r.file," %08x",v);for(auto v:r.y)std::fprintf(r.file," %08x",v);std::fprintf(r.file,"\n");++r.selected;}
  r.enabled=false;
 }return y;
}
}
