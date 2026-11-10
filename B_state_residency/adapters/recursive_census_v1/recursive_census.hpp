#pragma once
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <vector>
namespace recensus {
inline std::FILE* output=nullptr;
inline uint64_t serial=0,all_expands=0,all_pushes=0,all_lookahead=0,orphan_pushes=0;
inline uint32_t bits(float value){uint32_t u;std::memcpy(&u,&value,4);return u;}
struct Attempt;struct Frame;
inline thread_local Attempt* current=nullptr;
inline thread_local Frame* frame=nullptr;
struct Attempt {
 Attempt* previous;uint64_t id,expands=0,pushes=0,lookahead=0,siblings=0,pops=0;
 int iter,index,conn,net,source,sink,fanout,cross,sequence=0,initial_queue=0,targets=0;
 int depth=0,max_depth=0,max_raw=0,max_filtered=0;
 int first_parent=-1,first_child=-1,first_pos=-1,first_remaining=-1,first_degree=-1;
 uint32_t share=0,wire=0,estimate=0,present=0;int landmark;
 bool found=false,aborted=false;const bool* routed;const std::vector<int>*path;
 Attempt(int it,int idx,int cid,int ni,int src,int dst,int fan,int x,float pf,bool lm,const bool*route,const std::vector<int>*p):previous(current),id(++serial),iter(it),index(idx),conn(cid),net(ni),source(src),sink(dst),fanout(fan),cross(x),present(bits(pf)),landmark(lm),routed(route),path(p){current=this;}
 ~Attempt(){
  if(depth!=0)std::abort();
  if(output)std::fprintf(output,"%llu %d %d %d %d %d %d %d %d %d %u %u %u %u %d %d %d %llu %llu %llu %llu %d %d %d %d %d %d %d %d %llu %d %d %d %zu\n",
    (unsigned long long)id,iter,index,conn,net,source,sink,fanout,cross,sequence,share,wire,estimate,present,landmark,initial_queue,targets,
    (unsigned long long)expands,(unsigned long long)pushes,(unsigned long long)lookahead,(unsigned long long)siblings,max_depth,max_raw,max_filtered,first_parent,first_child,first_pos,first_remaining,first_degree,(unsigned long long)pops,int(found),int(aborted),int(*routed),path->size());
  all_expands+=expands;all_pushes+=pushes;all_lookahead+=lookahead;current=previous;
 }
};
struct Frame {
 Frame*previous;Attempt*owner;int node,degree,position=-1;
 Frame(int n,int count,int raw):previous(frame),owner(current),node(n),degree(count){
  frame=this;if(owner){++owner->expands;++owner->depth;owner->max_depth=std::max(owner->max_depth,owner->depth);owner->max_raw=std::max(owner->max_raw,raw);owner->max_filtered=std::max(owner->max_filtered,count);}
 }
 ~Frame(){if(owner)--owner->depth;frame=previous;}
};
inline void pushed(bool ahead,int child){
 if(!current){++orphan_pushes;return;}++current->pushes;
 if(!ahead)return;
 ++current->lookahead;
 if(!frame)std::abort();
 int remaining=frame->degree-frame->position-1;
 if(remaining>0){++current->siblings;if(current->first_parent<0){current->first_parent=frame->node;current->first_child=child;current->first_pos=frame->position;current->first_remaining=remaining;current->first_degree=frame->degree;}}
}
inline void init(){
 const char*p=std::getenv("B_RECURSION_CENSUS");if(!p)throw std::runtime_error("missing census output");
 output=std::fopen(p,"w");if(!output)throw std::runtime_error("census open");
 std::fputs("attempt iteration connection_index connection_id net source sink fanout cross sequence share_bits wl_bits heuristic_bits present_factor_bits landmark initial_queue targets expansions pushes lookahead lookahead_with_siblings max_depth max_raw_degree max_filtered_degree first_parent first_child first_position first_remaining first_degree pops found aborted routed path_length\n",output);
}
inline void finish(){
 if(!output||std::fflush(output)||std::ferror(output))throw std::runtime_error("census write");std::fclose(output);output=nullptr;
 std::fprintf(stderr,"RECURSION_CENSUS_FINISHED attempts=%llu expansions=%llu pushes=%llu lookahead=%llu orphan_pushes=%llu\n",(unsigned long long)serial,(unsigned long long)all_expands,(unsigned long long)all_pushes,(unsigned long long)all_lookahead,(unsigned long long)orphan_pushes);
}
}
