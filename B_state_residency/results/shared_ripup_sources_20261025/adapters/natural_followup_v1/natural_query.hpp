#pragma once
#include <cstdlib>
#include <cstring>
#include <stdexcept>
namespace nqs {
inline FILE* events=nullptr;
inline bool active=false;
inline unsigned bits(float x){unsigned u;std::memcpy(&u,&x,4);return u;}
inline FILE* open(const char* name){const char* p=std::getenv("B_NATURAL_QUERY");if(!p)throw std::runtime_error("missing snapshot path");auto s=std::string(p)+"/"+name;FILE*f=std::fopen(s.c_str(),"wb");if(!f)throw std::runtime_error(s);return f;}
inline void word(FILE*f,unsigned x){if(std::fwrite(&x,4,1,f)!=1)throw std::runtime_error("snapshot write");}
template<class R> void labels(R&r,const char* name){FILE*f=open(name);for(size_t i=0;i<r.dyn.size();++i){auto&d=r.dyn[i];word(f,bits(d.lb));word(f,bits(d.upstream));word(f,bits(d.hist));word(f,d.prev);word(f,d.visited);word(f,d.target);word(f,r.ownerNet[i]);word(f,r.ownerCnt[i]);word(f,r.occCnt[i]);word(f,r.created[i]);word(f,(unsigned)r.type[i]);}if(std::fclose(f))throw std::runtime_error("close");}
template<class R,class S> void begin(R&r,S&st){
 const char* selected=std::getenv("B_QUERY_SEQUENCE");int wanted=selected?std::atoi(selected):1;
 if(st.sequence!=wanted||!std::getenv("B_NATURAL_QUERY"))return;
 if(R::tl_dyn!=r.dyn.data()||R::tl_sparse||r.lazy||r.occLocking)throw std::runtime_error("unsupported nonserial snapshot");
 labels(r,"initial_nodes.u32");FILE*f=open("initial_overflow.u32");for(size_t i=0;i<r.userOverflow.size();i++)if(r.userOverflow[i]){std::vector<std::pair<int,int>> entries(r.userOverflow[i]->begin(),r.userOverflow[i]->end());std::sort(entries.begin(),entries.end());for(auto kv:entries){word(f,i);word(f,kv.first);word(f,kv.second);}}std::fclose(f);
 f=open("initial_caches.u32");for(size_t i=0;i<r.childrenCache.size();i++)if(r.childrenCache[i]){word(f,i);word(f,r.childrenCache[i]->size());for(int n:*r.childrenCache[i])word(f,n);}std::fclose(f);
 f=open("prices.u32");for(float x:r.presentCongestionCosts)word(f,bits(x));std::fclose(f);
 auto&c=r.connections[st.connIdx];auto&n=r.nets[c.netIdx];f=open("state.txt");
 std::fprintf(f,"conn_index %d\nconn_id %d\nnet %d\nsource %d\nsink %d\niteration %d\nsequence %d\nshare %u\nwire %u\nestimate %u\npresent_factor %u\nhistorical_factor %u\nbbox %d %d %d %d\nnet_geometry %u %u %d %d %d\ncross %d %d\nlandmark %d\nflags %d %d %d %d\nheap %d %d\nnodes %zu\n",st.connIdx,c.connId,c.netIdx,c.sourceRnode,c.sinkRnode,r.routeIteration,st.sequence,bits(st.shareWeight),bits(st.rnodeWLWeight),bits(st.estWlWeight),bits(r.presentCongestionFactor),bits(r.historicalCongestionFactor),c.xMinBB,c.xMaxBB,c.yMinBB,c.yMaxBB,bits(n.xCenter),bits(n.yCenter),n.doubleHpwl,n.connectionsSize,n.sourceRnode,c.crossSLRnorth,c.crossSLRsouth,r.lmkReady,r.useHotExpand,r.doPrefetch,r.pruneDeadEnd,r.cfg.useBoundingBox,st.queue->D,st.queue->sz,r.dyn.size());
 std::fprintf(f,"targets");for(int x:st.targets)std::fprintf(f," %d",x);std::fprintf(f,"\nlmkT");for(auto x:st.lmkT)std::fprintf(f," %u",x);std::fprintf(f,"\n");std::fclose(f);
 f=open("initial_heap.u32");for(int i=0;i<st.queue->sz;i++){word(f,bits(st.queue->h[i].lb));word(f,st.queue->h[i].id);}std::fclose(f);
 events=open("events.txt");active=true;
}
template<class R,class S> void expand(R&r,S&st,int parent,const std::vector<int>&kids){if(!active)return;std::fprintf(events,"E %d %zu %d\n",parent,kids.size(),st.queue->sz);for(int c:kids)std::fprintf(events,"K %d %d\n",parent,c);}
template<class R,class S> void candidate(R&r,S&st,int parent,int child,int position){if(!active)return;auto&d=r.dyn[child];std::fprintf(events,"C %d %d %d %u %u %d %d %u %u %u\n",parent,child,position,bits(d.lb),bits(d.upstream),d.prev,d.visited,(unsigned)d.target,(unsigned)r.type[child],(unsigned)r.created[child]);}
template<class R,class S> void pushed(R&r,S&st,int child,bool lookahead){if(!active)return;auto&d=r.dyn[child];std::fprintf(events,"W %d %d %u %u %d %u %d %d\n",child,d.prev,bits(d.lb),bits(d.upstream),d.visited,(unsigned)d.target,(int)lookahead,st.queue->sz);}
template<class R,class S> void poll(R&r,S&st,int node){if(active)std::fprintf(events,"P %d %u %d\n",node,bits(r.dyn[node].lb),st.queue->sz);}
template<class R,class S> void end(R&r,S&st,long long pops,bool found,bool aborted){if(!active)return;std::fprintf(events,"END %lld %d %d %d\n",pops,found,aborted,st.queue->sz);std::fclose(events);events=nullptr;active=false;labels(r,"search_final_nodes.u32");FILE*f=open("search_final_heap.u32");for(int i=0;i<st.queue->sz;i++){word(f,bits(st.queue->h[i].lb));word(f,st.queue->h[i].id);}std::fclose(f);}
}
