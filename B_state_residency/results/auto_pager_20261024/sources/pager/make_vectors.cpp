#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <cassert>
// Golden functions are extracted byte-for-byte from the original CPU router.
struct Oracle {
    struct Attr {bool preserved,isPinfeed,pinfeedLeadsToLaguna,isLaguna,arcLockedInit;};
    struct Attrs {int child;Attr attr; const Attr& operator[](int id)const{assert(id==child);return attr;}} ns;
    struct Label {int prev,visited;};
    int parent_id,child_id;Label parent_label,child_label;
    bool created,hasLaguna;mutable std::vector<int> reads;
    int getNode(int id)const{assert(id==child_id);return created?id:-1;}
    const Label& read(int id)const{assert(id==parent_id||id==child_id);reads.push_back(id);return id==parent_id?parent_label:child_label;}
#define TLD(id) read(id)
#include "original_functions.inc"
#undef TLD
};
static unsigned page_for(unsigned i){return i==95?0x1fffff:0x1234+i*12347;}
int main(int argc,char**argv){
    assert(argc==2);FILE*f=std::fopen(argv[1],"w");assert(f);unsigned count=0,total_reads=0;
    auto emit=[&](unsigned mode,unsigned parent,unsigned child,unsigned flags,unsigned created,unsigned lag,
                  int previous,unsigned cs,unsigned ps){
        Oracle o{{int(child),{bool(flags&64),bool(flags&4),bool(flags&8),bool(flags&2),bool(flags&32)}},
            int(parent),int(child),{-1,int(ps)},{previous,int(cs)},bool(created),bool(lag),{}};
        bool excluded=o.isExcluded(parent,child);assert(o.reads.size()<=4);
        unsigned cols[19]={mode,parent,child,flags,created,lag,unsigned(previous),cs,ps,unsigned(excluded),unsigned(o.reads.size())};
        for(unsigned i=0;i<o.reads.size();++i){
            cols[11+i*2]=i==0?1:(previous==-1?4:(i==1?2:(i==2?3:4)));
            cols[12+i*2]=o.reads[i];
            assert(unsigned(o.reads[i])==(cols[11+i*2]==3?parent:child));
        }
        for(unsigned i=0;i<19;++i)std::fprintf(f,"%08x%c",cols[i],i==18?'\n':' ');
        ++count;total_reads+=o.reads.size();
    };
    const unsigned seq[]={0,1,0x80000000u};
    for(unsigned flags=0;flags<256;++flags)for(unsigned created=0;created<2;++created)for(unsigned lag=0;lag<2;++lag)
    for(unsigned prev=0;prev<3;++prev)for(unsigned cs:seq)for(unsigned ps:seq){
        unsigned topology=count%3,pi=(count*17)%96,ci=(count*29+3)%96;
        if(topology==2){pi=(count*17)%95;ci=95;}
        if(ci==pi)ci=(ci+1)%96;
        unsigned parent=page_for(pi)*8,child=topology==0?parent+1:page_for(ci)*8+7;
        emit(1,parent,child,flags,created,lag,prev==0?-1:int(prev==1?parent:child),cs,ps);
    }
    const unsigned flags[]={0,32,64,96,2,4,8,12};
    for(unsigned fl:flags)for(unsigned cr=0;cr<2;++cr)for(unsigned lag=0;lag<2;++lag)emit(0,28,29,fl,cr,lag,0,0,0);
    std::fclose(f);assert(count==27680);
    std::printf("EDGE_VECTORS_PASS edges=%u reads=%u\n",count,total_reads);
}
