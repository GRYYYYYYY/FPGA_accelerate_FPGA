#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>
#define fpga_search original_search
#include "../search_label_records.hpp"
#undef fpga_search
#include "search_label_records.hpp"
template<class R> std::array<uint64_t,10> pack(const R&r){return {{r.cost,r.parent,r.root,r.edge.dst,r.edge.tile,r.edge.pip,r.edge.up,r.edge.down,r.edge.attr,r.edge.dir}};}
int main(){
 constexpr unsigned C=64;std::mt19937_64 random(0x316382);unsigned reads=0,paths=0,valid=0,invalid=0;
 for(unsigned trial=0;trial<20000;++trial){
  std::vector<uint64_t> words(C*10+2,0);std::array<unsigned,C> order;std::iota(order.begin(),order.end(),0);std::shuffle(order.begin(),order.end(),random);
  for(unsigned depth=0;depth<C;++depth){unsigned at=10*order[depth];words[at]=depth;words[at+1]=depth?order[depth-1]:0;words[at+2]=!depth;for(unsigned j=3;j<10;++j)words[at+j]=uint32_t(random());}
  unsigned changed=random()%C,field=random()%10;
  if(trial%3==0)words[10*changed+field]=random();
  if(trial%13==0)words[10*changed+2]=2;
  if(trial%17==0)words[10*changed]=UINT64_MAX;
  if(trial%19==0)words[10*changed+1]=changed;
  if(trial%23==0)words[10*changed+1]=C;
  unsigned count=trial%29==0?C+1:trial%31==0?0:trial%37==0?UINT32_MAX:C;
  auto before=words;
  for(unsigned index:std::array<unsigned,5>{{0,C-1,changed,C,UINT32_MAX}}){
   original_search::LabelRecord a{12345,9,true,{1,2,3,4,5,6,7}};fpga_search::LabelRecord b{12345,9,true,{1,2,3,4,5,6,7}};
   auto x=original_search::LabelRecords<C>::read(words.data(),count,index,a);auto y=fpga_search::LabelRecords<C>::read(words.data(),count,index,b);
   assert(unsigned(x)==unsigned(y)&&pack(a)==pack(b));++reads;if(unsigned(x))++invalid;else ++valid;
   unsigned ea=0xa5a5,eb=ea;auto px=original_search::LabelRecords<C>::validate_path(words.data(),count,index,ea);auto py=fpga_search::LabelRecords<C>::validate_path(words.data(),count,index,eb);
   assert(unsigned(px)==unsigned(py)&&ea==eb);++paths;
  }
  assert(words==before);
 }
 assert(valid&&invalid);std::cout<<"CONTROL_STAGING_CPU_PASS reads="<<reads<<" paths="<<paths<<" valid="<<valid<<" invalid="<<invalid<<" arbitrary_parent_order=1 input_unchanged=1\n";
}
