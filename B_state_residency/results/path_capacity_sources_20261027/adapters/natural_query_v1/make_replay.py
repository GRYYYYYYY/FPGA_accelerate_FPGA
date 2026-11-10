"""Driver restores the captured prepared query then invokes original search body."""
def make(code):
 start=code.index('        int rnode = -1;',code.index('    void routeIndirectConnection('))
 end=code.index('        lastPops = pops; lastFoundLb = foundLb;',start)
 search=code[start:end]
 return r'''#define main original_router_main
#include "router.cpp"
#undef main
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
 nqs::begin(r,st);
 long long budget=-1;bool measurePops=false;
''' + search.replace('nqs::poll(*this,','nqs::poll(r,').replace('nqs::end(*this,','nqs::end(r,').replace('TLD(rnode)','r.dyn[rnode]').replace('connections[connIdx]','r.connections[st.connIdx]').replace('routeIteration,','r.routeIteration,').replace('tl_wid);','Router::tl_wid);').replace('exploreAndExpand(st, rnode);','r.exploreAndExpand(st, rnode);').replace('getEndTileXCoordinate(','r.getEndTileXCoordinate(').replace('getEndTileYCoordinate(','r.getEndTileYCoordinate(').replace('getBeginTileXCoordinate(','r.getBeginTileXCoordinate(').replace('getBeginTileYCoordinate(','r.getBeginTileYCoordinate(')+r'''
 return found&&!aborted?0:3;
}
'''
