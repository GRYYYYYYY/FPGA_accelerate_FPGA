#include "exclusion_machine.hpp"
#include <cstdio>
#include <stdexcept>
#include <vector>
struct Oracle {
 struct Attr{bool preserved,isPinfeed,pinfeedLeadsToLaguna,isLaguna,arcLockedInit;} ns[2];
 struct Label{int prev,visited;} labels[2];
 bool created[2],hasLaguna;mutable std::vector<int> reads;
 int getNode(int id)const{return created[id]?id:-1;}
 const Label& read(int id)const{reads.push_back(id);return labels[id];}
#define TLD(id) read(id)
#include "original_functions.inc"
#undef TLD
};
int main(){unsigned checks=0;
 for(unsigned flags=0;flags<256;++flags)for(unsigned created=0;created<2;++created)for(unsigned lag=0;lag<2;++lag)
 for(int previous=-1;previous<=1;++previous)for(unsigned child_seq=0;child_seq<3;++child_seq)for(unsigned parent_seq=0;parent_seq<3;++parent_seq){
  Oracle o{};o.ns[1]={bool(flags&64),bool(flags&4),bool(flags&8),bool(flags&2),bool(flags&32)};
  o.created[1]=created;o.hasLaguna=lag;o.labels[1]={previous,int(child_seq)};o.labels[0]={-1,int(parent_seq)};
  bool expected=o.isExcluded(0,1);search_filter::Machine machine(0,flags,created,lag);std::vector<int> reads;
  unsigned steps=0;while(machine.request!=search_filter::DONE){if(++steps>4)throw std::runtime_error("unbounded requests");
   int id=machine.request==search_filter::PARENT_VISITED?0:1;reads.push_back(id);
   bool prev=machine.request==search_filter::CHILD_PREV||machine.request==search_filter::ARC_PREV;
   if(!machine.accept(uint32_t(prev?o.labels[id].prev:o.labels[id].visited)))throw std::runtime_error("response rejected");
  }
  if(machine.excluded!=expected||reads!=o.reads||machine.accept(0))throw std::runtime_error("semantic/read-order mismatch");++checks;
 }
 std::printf("EXCLUSION_UNIT_PASS checks=%u\n",checks);
}
