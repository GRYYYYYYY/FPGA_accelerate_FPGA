"""Exhaustive flag/label-equivalence cases against extracted original functions."""
from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha

def main():
 out=ROOT/'results/exclusion_unit_20261024';out.mkdir()
 original=ROOT/'results/frontier_real_20261024/original_trace.cpp';s=original.read_text()
 first=s.index('    bool isPartOfExistingRoute(int parent, int child) const {');last=s.index('    // ----------------------------------------------------------------- getChildren',first)
 methods=s[first:last];(out/'original_functions.inc').write_text(methods)
 helper=ROOT/'hardware/search/exclusion_machine.hpp';(out/helper.name).write_bytes(helper.read_bytes())
 code='''#include "exclusion_machine.hpp"
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
 std::printf("EXCLUSION_UNIT_PASS checks=%u\\n",checks);
}
'''
 (out/'test.cpp').write_text(code)
 commands=[]
 for stage,argv in [('build',['g++','-std=c++14','-O2',str(out/'test.cpp'),'-o',str(out/'verify')]),('verify',[str(out/'verify')])]:
  with (out/(stage+'.log')).open('w') as log:r=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT)
  commands.append({'stage':stage,'argv':argv,'exit_code':r.returncode});assert r.returncode==0
 assert 'EXCLUSION_UNIT_PASS checks=27648' in (out/'verify.log').read_text()
 m={'status':'passed','checks':27648,'original_source_sha256':sha(original),'helper_sha256':sha(helper),'runner_sha256':sha(Path(__file__)),'commands':commands,'artifacts':{p.name:sha(p) for p in out.iterdir() if p.is_file()},'scope':'Exhaustive flags, created, Laguna, prev relationship and small sequence-equivalence classes; native decision and label-read order preserved. No RTL claim.'}
 (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('EXCLUSION_UNIT_PASS checks=27648')
if __name__=='__main__':main()
