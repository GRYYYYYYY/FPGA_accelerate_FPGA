#define main original_router_main
#include "router.cpp"
#undef main
#include "export_inputs.hpp"
#include <fstream>
#include <sstream>
#include <map>
#include <cassert>
float frombits(unsigned v){float f;std::memcpy(&f,&v,4);return f;}
unsigned readword(FILE*f){unsigned v;if(std::fread(&v,4,1,f)!=1)throw std::runtime_error("short snapshot");return v;}
int main(int argc,char**argv){
 if(argc!=3)return 2;
 Router r;r.load(argv[1]);std::string base=argv[2];
 std::map<std::string,std::vector<long long>> meta;std::ifstream sf(base+"/state.txt");std::string line;
 while(std::getline(sf,line)){std::istringstream is(line);std::string k;is>>k;long long v;while(is>>v)meta[k].push_back(v);}
 auto get=[&](const char*k){return meta.at(k).at(0);};
 assert(get("nodes")==r.numNodes() && get("landmark")==0);
 FILE*f=std::fopen((base+"/initial_nodes.u32").c_str(),"rb");assert(f);
 for(int i=0;i<r.numNodes();i++){
  auto&d=r.dyn[i];d.lb=frombits(readword(f));d.upstream=frombits(readword(f));d.hist=frombits(readword(f));d.prev=(int)readword(f);d.visited=(int)readword(f);d.target=readword(f);
  r.ownerNet[i]=(int)readword(f);r.ownerCnt[i]=readword(f);r.occCnt[i]=readword(f);r.created[i]=readword(f);r.type[i]=(RouteNodeType)readword(f);
  if(r.userOverflow[i]){delete r.userOverflow[i];r.userOverflow[i]=nullptr;}if(r.childrenCache[i]){delete r.childrenCache[i];r.childrenCache[i]=nullptr;}r.initHotFromStatic(i);
 }assert(std::fgetc(f)==EOF);std::fclose(f);
 f=std::fopen((base+"/initial_overflow.u32").c_str(),"rb");assert(f);unsigned id;
 while(std::fread(&id,4,1,f)==1){int net=(int)readword(f),count=readword(f);if(!r.userOverflow[id])r.userOverflow[id]=new std::unordered_map<int,int>();(*r.userOverflow[id])[net]=count;}std::fclose(f);
 f=std::fopen((base+"/initial_caches.u32").c_str(),"rb");assert(f);
 while(std::fread(&id,4,1,f)==1){unsigned n=readword(f);auto*v=new std::vector<int>();for(unsigned j=0;j<n;j++)v->push_back(readword(f));r.childrenCache[id]=v;}std::fclose(f);
 f=std::fopen((base+"/prices.u32").c_str(),"rb");assert(f);for(float&v:r.presentCongestionCosts)v=frombits(readword(f));std::fclose(f);
 r.routeIteration=get("iteration");r.presentCongestionFactor=frombits(get("present_factor"));r.historicalCongestionFactor=frombits(get("historical_factor"));r.lmkReady=false;
 r.useHotExpand=meta["flags"][0];r.doPrefetch=meta["flags"][1];r.pruneDeadEnd=meta["flags"][2];r.cfg.useBoundingBox=meta["flags"][3];assert(!r.pruneDeadEnd);
 Router::tl_dyn=r.dyn.data();Router::tl_pq=&r.pqStorage;Router::tl_sparse=nullptr;
 Router::DaryPQ queue(r.pqStorage,meta["heap"][0]);f=std::fopen((base+"/initial_heap.u32").c_str(),"rb");assert(f);
 for(int i=0;i<meta["heap"][1];i++){unsigned key=readword(f);int node=readword(f);queue.h.push_back({frombits(key),node});}queue.sz=meta["heap"][1];assert(std::fgetc(f)==EOF);std::fclose(f);
 Router::State st;st.queue=&queue;st.connIdx=get("conn_index");st.sequence=get("sequence");st.shareWeight=frombits(get("share"));st.rnodeWLWeight=frombits(get("wire"));st.estWlWeight=frombits(get("estimate"));st.earlyTermination=false;
 for(auto v:meta["targets"])st.targets.push_back(v);for(int i=0;i<8;i++)st.lmkT[i]=meta["lmkT"][i];
 auto&c=r.connections[st.connIdx];assert(c.connId==get("conn_id")&&c.sourceRnode==get("source")&&c.sinkRnode==get("sink")&&c.netIdx==get("net"));
 c.xMinBB=meta["bbox"][0];c.xMaxBB=meta["bbox"][1];c.yMinBB=meta["bbox"][2];c.yMaxBB=meta["bbox"][3];c.crossSLRnorth=meta["cross"][0];c.crossSLRsouth=meta["cross"][1];
 auto&n=r.nets[c.netIdx];n.xCenter=frombits(meta["net_geometry"][0]);n.yCenter=frombits(meta["net_geometry"][1]);n.doubleHpwl=meta["net_geometry"][2];n.connectionsSize=meta["net_geometry"][3];n.sourceRnode=meta["net_geometry"][4];
 natcodec::export_inputs(r,st);
 nqs::begin(r,st);
 long long budget=-1;bool measurePops=false;
        int rnode = -1;
        bool found = false, aborted = false;
        long long pops = 0, sumFront = 0, maxFront = 0;
        // §prune ceiling test: the TIGHTEST admissible upper bound is C* itself (foundLb). A B&B that prunes
        // g+h>UB can only cut EXPANSIONS whose f exceeds UB>=C*. With a consistent h, A* never expands f>C*,
        // so maxPoppedF (max f among expanded non-target nodes) <= foundF => B&B-UB cuts ZERO expansions.
        // Measuring maxPoppedF/foundF thus bounds the entire "h-bounded pruning" idea for free (no old path).
        float maxPoppedLb = -1.0f, foundLb = -1.0f;
        // §h-slack: how much of the true priced optimal cost the base-Manhattan h captures. h(n)=lb-upstream,
        // g(n)=upstream. If h << (C*-g) broadly => h is loose => a tighter admissible (priced coarse) h has
        // room to shrink the f<=C* expanded set. If h ~= (C*-g) => no room => monsters only via GPU accel.
        double sumH = 0, sumG = 0;
        float srcH = measurePops ? st.estWlWeight * (float)(
                         std::abs(r.getEndTileXCoordinate(c.sourceRnode) - r.getBeginTileXCoordinate(c.sinkRnode)) +
                         std::abs(r.getEndTileYCoordinate(c.sourceRnode) - r.getBeginTileYCoordinate(c.sinkRnode))) : 0.0f;
        while (!queue.empty()) {
            rnode = queue.poll();
            nqs::poll(r,st,rnode);
            pops++;
            if ((pops & ((1 << 22) - 1)) == 0)   // watchdog: a sane search never gets near 4M pops
                std::fprintf(stderr, "[watchdog] conn=%d iter=%d pops=%lld qsz=%lld node=%d wid=%d\n",
                             r.connections[st.connIdx].connId, r.routeIteration, pops, (long long) queue.sz, rnode, Router::tl_wid);
            float lbp = r.dyn[rnode].lb;
            if (r.dyn[rnode].target) { found = true; foundLb = lbp; break; }
            if (budget > 0 && pops > budget) { aborted = true; break; }   // §budget-abort: bail this search to GPU flood
            if (measurePops) {
                long long f = queue.sz; sumFront += f; if (f > maxFront) maxFront = f;
                if (lbp > maxPoppedLb) maxPoppedLb = lbp;
                sumH += (double)(lbp - r.dyn[rnode].upstream); sumG += (double) r.dyn[rnode].upstream;
            }
            r.exploreAndExpand(st, rnode);
        }
        nqs::end(r,st,pops,found,aborted);

 return found&&!aborted?0:3;
}
