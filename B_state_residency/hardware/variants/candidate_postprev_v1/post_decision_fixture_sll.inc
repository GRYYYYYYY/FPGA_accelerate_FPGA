#include "access_machine.hpp"
#include <array>
#include <cstring>
#include <tuple>
static size_t total_decisions=0,total_early=0,total_allowed=0,total_pruned=0;
static void decisions(CandidateOracle&r,std::ofstream&vec,int parent,const std::vector<int>&kids,size_t request){
 using namespace search_access;
 std::map<int,int> saved_prev;for(int child:kids)saved_prev.emplace(child,Router::tl_sparse->at(child).prev);
 std::vector<std::array<uint32_t,7>> manual_prefix;
 unsigned ci=(request*97)%r.connections.size();auto&c=r.connections[ci];unsigned seq=request<550?17+request:100;
 r.useHotExpand=request%2;r.cfg.useBoundingBox=request%3!=0;
 // Scripted target contexts exercise EARLY; these are labelled as synthetic query state.
 if(request%13==0&&!kids.empty())Router::tl_sparse->at(kids.front()).target=1;
 unsigned flags=(r.pruneDeadEnd?PRUNE:0)|(r.cfg.useBoundingBox?BB:0)|(c.crossSLRnorth?NORTH:0)|(c.crossSLRsouth?SOUTH:0)|(r.useHotExpand?HOT:0);
 vec<<"D "<<ci<<' '<<c.sinkRnode<<' '<<c.netIdx<<' '<<seq<<' '<<flags<<' '<<c.xMinBB<<' '<<c.xMaxBB<<' '<<c.yMinBB<<' '<<c.yMaxBB<<'\n';
 if(request%13==0&&!kids.empty())vec<<"L "<<kids.front()<<" 4 1\n";
 std::vector<std::tuple<int,bool,bool>>allowed;
 size_t pruned=0;bool early=false;
 for(size_t ordinal=0;ordinal<kids.size();++ordinal){
  int child=kids[ordinal];
  if(post_sll_parents.count(parent)&&r.type[child]==RouteNodeType::SUPER_LONG_LINE){
   Router::tl_sparse->at(child).visited=seq-1;Router::tl_sparse->at(child).target=1;
   vec<<"L "<<child<<" 3 "<<seq-1<<'\n'<<"L "<<child<<" 4 1\n";
  }
  search_access::Config cfg{seq,flags|(r.deadEnd[child]?DEAD:0)|(r.nodeLaguna(parent)?P_LAG:0)|(r.nodeLaguna(child)?C_LAG:0)|(r.nodePinbounce(child)?PINBOUNCE:0),uint32_t(r.searchType(child)),uint32_t(r.searchType(parent)),uint32_t(r.searchType(c.sinkRnode)),
   r.useHotExpand?r.hot[child].endX:r.getEndTileXCoordinate(child),r.useHotExpand?r.hot[child].tileAddr:r.ns[child].tileAddr,r.useHotExpand?r.hot[c.sinkRnode].tileAddr:r.ns[c.sinkRnode].tileAddr,r.getBeginTileXCoordinate(c.sinkRnode),r.getBeginTileYCoordinate(c.sinkRnode),c.xMinBB,c.xMaxBB,c.yMinBB,c.yMaxBB};
  auto state=start();unsigned services=0;
  while(state.phase!=END){
   uint32_t value=0;switch(search_access::request(state)){
    case VISITED:value=Router::tl_sparse->at(child).visited;break;
    case TARGET:case SINK_TARGET:value=Router::tl_sparse->at(child).target;break;
    case BBOX_END_Y:value=r.searchEndY(child);break;
    case WILL_OVERUSE:value=r.searchWillOverUse(child,c.netIdx);break;
    case COUNT_USER:value=r.searchCountUser(child,c.netIdx);break;
    case CHILD_SLR:value=r.getSLRIndex(child);break;
    case SINK_SLR:value=r.getSLRIndex(c.sinkRnode);break;
    case PARENT_PREV:value=Router::tl_sparse->at(parent).prev;break;
    case PREV_TILE:value=r.ns.at(state.aux).tileAddr;break;
    case GRAPH_END_Y:value=r.getEndTileYCoordinate(child);break;
    default:check(false);
   }
   check(accept(cfg,state,value));++services;
  }
  std::array<uint32_t,14>words;static_assert(sizeof(cfg)==sizeof(words));std::memcpy(words.data(),&cfg,sizeof(cfg));
  vec<<"A "<<ordinal<<' '<<child<<' '<<state.bits<<' '<<state.action<<' '<<services;
  for(auto w:words)vec<<' '<<w;vec<<'\n';++total_decisions;
  pruned+=bool(state.bits&PRUNED);
  if(state.action){allowed.emplace_back(child,state.action==2,bool(state.bits&EARLY));++total_allowed;
   auto p=r.preparePrefix(parent,child,c.netIdx);manual_prefix.push_back(p);
   *prefix_out<<request<<' '<<ordinal;for(auto w:p)*prefix_out<<' '<<w;*prefix_out<<' '<<bool(state.bits&EARLY)<<'\n';
  }
  if(state.bits&EARLY){early=true;++total_early;break;}
 }
 std::vector<Router::DaryPQ::E>storage;Router::DaryPQ queue(storage,4);Router::State state{};state.queue=&queue;state.connIdx=ci;state.sequence=seq;
 for(auto p:saved_prev)Router::tl_sparse->at(p.first).prev=p.second;
 auto before=r.prunedPushes;r.selected.clear();r.prefixes.clear();r.golden(state,parent);
 check(manual_prefix==r.prefixes);
 check(allowed==r.selected);check(state.earlyTermination==early);check(r.prunedPushes-before==pruned);total_pruned+=pruned;
 vec<<"Z "<<allowed.size()<<' '<<early<<' '<<pruned<<'\n';
}
