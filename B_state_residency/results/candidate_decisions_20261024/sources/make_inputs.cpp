#include <cstdint>
#include <vector>
#include <stdexcept>
static std::vector<uint8_t> created_delta;
static uint32_t emit_mask=0,raw_position=0;
static void note_create(int node){if(!created_delta.empty())created_delta.at(node)=1;}
static void note_position(int pos){raw_position=pos;}
static void note_emit(int){if(raw_position>=32)throw std::runtime_error("mask capacity");emit_mask|=uint32_t(1)<<raw_position;}
#define main original_router_main
#include "oracle_trace.cpp"
#undef main
#include <fstream>
#include <set>
#include <random>
#include <iomanip>
static void check(bool c){if(!c)throw std::runtime_error("expansion oracle mismatch");}

#include <tuple>
struct CandidateOracle : Router {
std::vector<std::tuple<int,bool,bool>> selected;
    void golden(State& st, int rnode) {
        Connection& c = connections[st.connIdx];
        int seq = st.sequence;
        int nw = c.netIdx;
        bool rnodeIsLaguna = nodeLaguna(rnode);

        const std::vector<int>& kids = getChildren(rnode);
        int nk = (int) kids.size();
        for (int ki = 0; ki < nk; ki++) {
            if (doPrefetch && ki + 1 < nk) {
                int nx = kids[ki + 1];
                __builtin_prefetch(&tl_dyn[nx], 1, 3);   // serial/shadow: the label line; sparse crew: tl_dyn
                                                         // aliases the GLOBAL dyn -> warms the hist read
                if (tl_sparse) tl_sparse->prefetch(nx);  // paged probe-only, never inserts (hash mode: no-op)
                if (useHotExpand) {
                    __builtin_prefetch(&hot[nx], 0, 3);   // one line: type/coords/cost/occ/sharing
                } else {
                    __builtin_prefetch(&ns[nx], 0, 3);
                    __builtin_prefetch(&occCnt[nx], 0, 3);
                    __builtin_prefetch(&type[nx], 0, 3);
                    __builtin_prefetch(&ownerNet[nx], 0, 3);
                    __builtin_prefetch(&ownerCnt[nx], 0, 3);
                }
            }
            int childRNode = kids[ki];
            if (TLD(childRNode).visited == seq) continue;
            if (pruneDeadEnd && deadEnd[childRNode]) { prunedPushes++; continue; }
            bool lookahead = false;
            if (TLD(childRNode).target) {
                if (isAnyExclusiveSink(searchType(childRNode))) {
                    st.earlyTermination = true;
                } else {
                    st.earlyTermination = !searchWillOverUse(childRNode, nw);
                }
                if (st.earlyTermination) {
                    st.queue->clear();
                }
            } else {
                if (!isAccessible(childRNode, c)) continue;
                RouteNodeType childType = searchType(childRNode);
                switch (childType) {
                    case RouteNodeType::LOCAL_EAST_LEADING_TO_NORTHBOUND_LAGUNA:
                    case RouteNodeType::LOCAL_EAST_LEADING_TO_SOUTHBOUND_LAGUNA:
                    case RouteNodeType::LOCAL_WEST_LEADING_TO_NORTHBOUND_LAGUNA:
                    case RouteNodeType::LOCAL_WEST_LEADING_TO_SOUTHBOUND_LAGUNA:
                        lookahead = !searchWillOverUse(childRNode, nw);
                        // fall-through
                    case RouteNodeType::LOCAL_BOTH:
                    case RouteNodeType::LOCAL_EAST:
                    case RouteNodeType::LOCAL_WEST:
                    case RouteNodeType::LOCAL_RESERVED:
                        if (!graphIsAccessible(childRNode, rnode, c)) continue;
                        break;
                    case RouteNodeType::NON_LOCAL_LEADING_TO_NORTHBOUND_LAGUNA:
                    case RouteNodeType::NON_LOCAL_LEADING_TO_SOUTHBOUND_LAGUNA:
                        if (c.isCrossSLR() && getSLRIndex(c.sinkRnode) != getSLRIndex(childRNode) &&
                            ((c.crossSLRnorth && childType == RouteNodeType::NON_LOCAL_LEADING_TO_NORTHBOUND_LAGUNA) ||
                             (c.crossSLRsouth && childType == RouteNodeType::NON_LOCAL_LEADING_TO_SOUTHBOUND_LAGUNA))) {
                            lookahead = !searchWillOverUse(childRNode, nw);
                        }
                        // fall-through
                    case RouteNodeType::NON_LOCAL:
                        if (!graphIsAccessible(childRNode, rnode, c)) continue;
                        if (!cfg.useUTurnNodes /* && delay>10000 (delay==0) */) { /* never triggers */ }
                        lookahead = lookahead || (rnodeIsLaguna || nodeLaguna(childRNode));
                        break;
                    case RouteNodeType::EXCLUSIVE_SINK_BOTH:
                    case RouteNodeType::EXCLUSIVE_SINK_EAST:
                    case RouteNodeType::EXCLUSIVE_SINK_WEST:
                    case RouteNodeType::EXCLUSIVE_SINK_NON_LOCAL:
                        if (!isAccessibleSink(childRNode, c)) continue;
                        break;
                    case RouteNodeType::SUPER_LONG_LINE:
                        break;
                    default:
                        break;
                }
            }
            selected.emplace_back(childRNode,lookahead,st.earlyTermination);
            if (st.earlyTermination) break;
        }
    }


};

#include "decision_fixture.inc"
int main(int argc,char**argv){
 check(argc==3);const std::string out=argv[2];CandidateOracle r;r.load(argv[1]);check(!r.lazy);const size_t n=r.ns.size();created_delta.assign(n,0);
 Router::SparseLabels labels;labels.initPaged(n,9);Router::tl_sparse=&labels;Router::tl_dyn=r.dyn.data();
 std::vector<uint32_t> masks(n,0);std::ofstream vec(out+"/vectors.txt"),sink(out+"/sink_nodes.txt");
 std::vector<uint32_t> image(((n*16+63)/64)*16,0);size_t sinks=0;
 for(size_t i=0;i<n;++i)if(r.isSinkNode[i]){sink<<i<<'\n';image[i*4]=8;++sinks;}
 {std::ofstream f(out+"/initial_design.bin",std::ios::binary);f.write((char*)image.data(),image.size()*4);}
 std::set<int> parents;for(int i=0;i<128;++i){parents.insert(i);parents.insert(n-1-i);}
 std::set<int> degrees;int flag_seen[256]={};int sink_added=0;bool duplicate_added=false;
 for(size_t i=0;i<n;++i){
  int degree=r.ns[i].childCount;check(degree<=32);
  if(degrees.insert(degree).second)parents.insert(i);
  unsigned flag=(r.nc[i].createdAtInit?1:0)|(r.ns[i].isLaguna?2:0)|(r.ns[i].isPinfeed?4:0)|(r.ns[i].pinfeedLeadsToLaguna?8:0)|(r.ns[i].arcLockedInit?32:0)|(r.ns[i].preserved?64:0)|(r.ns[i].isPinbounce?128:0);
  if(flag_seen[flag]++<2)parents.insert(i);
  if(r.isSinkNode[i]&&sink_added++<32)parents.insert(i);
  if(!duplicate_added&&degree>1){std::set<int>s;for(int j=0;j<degree;++j)s.insert(r.childIds[r.ns[i].childStart+j]);if((int)s.size()<degree){parents.insert(i);duplicate_added=true;}}
 }
 std::mt19937 rng(20261025);for(int i=0;i<256;++i)parents.insert(rng()%n);
 std::vector<int> ordered(parents.begin(),parents.end());std::vector<int> later;
 for(int i=0;i<128;++i){int p=rng()%n;if(!parents.count(p)){parents.insert(p);later.push_back(p);}}
 size_t requests=0,hits=0,children=0,empty=0,label_writes=0,creates=0;
 auto control=[&](int op,int q,int price){vec<<"Q "<<op<<' '<<q<<' '<<price<<'\n';if(op==0)labels.reset();};
 auto label=[&](int node,int field,uint32_t value){vec<<"L "<<node<<' '<<field<<' '<<value<<'\n';if(field==2)labels.at(node).prev=int32_t(value);else labels.at(node).visited=value;++label_writes;};
 auto expand=[&](int parent,bool prune){
  bool hit=(uintptr_t)r.childrenCache[parent]>1;emit_mask=0;r.pruneDeadEnd=prune;
  const auto& result=r.getChildren(parent);if(!hit)masks[parent]=emit_mask;
  std::vector<int> decoded;for(int j=0;j<r.ns[parent].childCount;++j)if(masks[parent]&(uint32_t(1)<<j))decoded.push_back(r.childIds[r.ns[parent].childStart+j]);check(decoded==result);
  ++requests;hits+=hit;empty+=result.empty();children+=result.size();
  vec<<"E "<<requests<<' '<<parent<<' '<<prune<<' '<<r.hasLaguna<<' '<<hit<<' '<<r.ns[parent].childCount<<' '<<masks[parent]<<' '<<result.size()<<'\n';
  for(int j=0;j<r.ns[parent].childCount;++j)if(masks[parent]&(uint32_t(1)<<j))vec<<"C "<<j<<' '<<r.childIds[r.ns[parent].childStart+j]<<'\n';
  decisions(r,vec,parent,result,requests);
 };
 control(0,1,3);
 for(size_t i=0;i<std::min(size_t(64),ordered.size());++i){int p=ordered[i];label(p,3,i+17);if(r.ns[p].childCount){int c=r.childIds[r.ns[p].childStart];label(c,2,i%2?uint32_t(-1):uint32_t(p));label(c,3,i%3?i+18:i+17);}}
 for(size_t i=0;i<ordered.size();++i)expand(ordered[i],i%2);
 control(1,1,3);for(size_t i=0;i<16;++i)expand(ordered[i],!(i%2));
 control(2,1,3);control(0,2,5);
 for(size_t i=0;i<std::min(size_t(32),ordered.size());++i){int p=ordered[i];label(p,3,99);if(r.ns[p].childCount){int c=r.childIds[r.ns[p].childStart];label(c,2,p);label(c,3,100);}}
 for(size_t i=0;i<ordered.size();++i)expand(ordered[i],!(i%2));
 for(int p:later)expand(p,true);
 control(1,2,5);
 for(size_t i=0;i<n;++i){
  image[i*4]=(created_delta[i]?1:0)|(r.deadEnd[i]?2:0)|(r.isSinkNode[i]?8:0);creates+=created_delta[i]!=0;
  if((uintptr_t)r.childrenCache[i]>1){image[i*4]|=4;image[i*4+1]=r.ns[i].childCount;image[i*4+2]=masks[i];}
  check(bool(r.created[i])==bool(r.nc[i].createdAtInit||created_delta[i]));
 }
 {std::ofstream f(out+"/expected_design.bin",std::ios::binary);f.write((char*)image.data(),image.size()*4);}
 std::ofstream dc(out+"/decision_coverage.json");dc<<"{\"decisions\":"<<total_decisions<<",\"allowed\":"<<total_allowed<<",\"early\":"<<total_early<<",\"pruned\":"<<total_pruned<<"}\n";
 std::ofstream meta(out+"/coverage.json");meta<<"{\"nodes\":"<<n<<",\"nets\":"<<r.nets.size()<<",\"connections\":"<<r.connections.size()<<",\"sinks\":"<<sinks<<",\"has_laguna\":"<<r.hasLaguna<<",\"expansions\":"<<requests<<",\"cache_hits\":"<<hits<<",\"children\":"<<children<<",\"empty_results\":"<<empty<<",\"label_writes\":"<<label_writes<<",\"created_delta_nodes\":"<<creates<<"}\n";
 std::printf("EXPANSION_INPUTS_PASS expansions=%zu hits=%zu children=%zu sinks=%zu writes=%zu\n",requests,hits,children,sinks,label_writes);
}
