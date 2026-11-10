#include "exclusion_port.hpp"
#include <cstdio>
#include <cstdlib>
#include <vector>
using namespace exclusion_port;
static unsigned long long checks=0;static unsigned contexts=0;
static void require(bool yes){if(!yes){std::fprintf(stderr,"EXCLUSION_FAIL check=%llu contexts=%u\n",checks,contexts);std::exit(1);}}
static Reply call(Command c){Reply r{};exclusion_step(c.op,c.parent,c.child,c.flags,c.created,c.has_laguna,c.generation,c.phase,c.value,r.status,r.generation,r.request,r.node,r.excluded);++checks;return r;}
static bool same(Reply a,Reply b){return a.generation==b.generation&&a.request==b.request&&a.node==b.node&&a.excluded==b.excluded;}
static void rejected(Command c,Status status,Reply before){Reply r=call(c);require(r.status==status&&same(r,before));}
struct Oracle {
 struct Attr{bool preserved,isPinfeed,pinfeedLeadsToLaguna,isLaguna,arcLockedInit;} ns[2];
 struct Label{int prev,visited;} labels[2];bool created[2],hasLaguna;mutable std::vector<int> reads;
 int getNode(int id)const{return created[id]?id:-1;}
 const Label& read(int id)const{reads.push_back(id);return labels[id];}
#define TLD(id) read(id)
#include "original_functions.inc"
#undef TLD
};
int main(){
 Command snapshot={SNAPSHOT,0,0,0,0,0,0,0,0};Reply current=call(snapshot);require(current.status==OK&&current.generation==0&&current.request==0&&current.excluded==0);
 rejected({RESPONSE,0,0,0,0,0,0,1,0},NO_REQUEST,current);
#if EXCLUSION_GENERATION_BITS == 3
 // Real reduced-width RTL exhaustion; production32 is not exercised for 2^32 starts.
 for(unsigned i=1;i<=7;++i){current=call({START,0,1,0,0,0,0,0,0});++contexts;require(current.status==OK&&current.generation==i&&current.request==0);}
 rejected({START,0,1,0,0,0,0,0,0},EXHAUSTED,current);
 rejected({RESPONSE,0,0,0,0,0,1,1,0},NO_REQUEST,current);
 require(same(call(snapshot),current));
#else
 for(unsigned flags=0;flags<256;++flags)for(unsigned created=0;created<2;++created)for(unsigned lag=0;lag<2;++lag)
 for(int previous=-1;previous<=1;++previous)for(unsigned child_seq=0;child_seq<3;++child_seq)for(unsigned parent_seq=0;parent_seq<3;++parent_seq){
  Oracle o{};o.ns[1]={bool(flags&64),bool(flags&4),bool(flags&8),bool(flags&2),bool(flags&32)};o.created[1]=created;o.hasLaguna=lag;o.labels[1]={previous,int(child_seq)};o.labels[0]={-1,int(parent_seq)};
  const bool expected=o.isExcluded(0,1);const unsigned prior=current.generation;
  current=call({START,0,1,flags,created,lag,0,0,0});++contexts;require(current.status==OK&&current.generation==prior+1);
  for(unsigned i=0;i<o.reads.size();++i){
   const unsigned phase=i==0?1:(previous==-1?4:(i==1?2:(i==2?3:4)));
   require(current.request==phase&&current.node==unsigned(o.reads[i])&&current.excluded==0);
   rejected({START,0,1,0,0,0,0,0,0},BUSY,current);
   rejected({RESPONSE,0,0,0,0,0,prior,phase,123},STALE,current);
   rejected({RESPONSE,0,0,0,0,0,current.generation,phase==4?1:phase+1,123},WRONG_PHASE,current);
   rejected({99,0,0,0,0,0,0,0,0},BAD,current);
   require(same(call(snapshot),current));
   const unsigned value=phase==1||phase==4?unsigned(previous):(phase==2?child_seq:parent_seq);
   current=call({RESPONSE,0,0,0,0,0,current.generation,phase,value});require(current.status==OK);
   // A duplicated reply must not advance the next phase or a completed edge.
   rejected({RESPONSE,0,0,0,0,0,current.generation,phase,value},current.request?WRONG_PHASE:NO_REQUEST,current);
  }
  require(current.request==0&&current.node==0&&current.excluded==unsigned(expected));
  rejected({START,0,1,256,0,0,0,0,0},BAD,current);
  rejected({START,0,1,0,2,0,0,0,0},BAD,current);
  rejected({START,0x80000000u,1,0,0,0,0,0,0},BAD,current);
 }
 require(contexts==27648);
#endif
 std::printf("EXCLUSION_PORT_PASS generation_bits=%d contexts=%u checks=%llu\n",EXCLUSION_GENERATION_BITS,contexts,checks);return 0;
}
