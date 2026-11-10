#pragma once
#include <cstdint>
namespace fpga_search {
// Read-only end-of-round observation/decision. Never advances a ledger.
// control8=[nodes,nets,iteration,max_iterations,present_cap,site_groups,0,0].
// result8=[status,node_groups,incomplete,action,next_iteration,next_present,
//          advance_histories,current_present]. action0 routed/1 incomplete/2 next.
template<unsigned Nodes=1048576,unsigned Nets=65536> struct RoundControl {
    static_assert(Nodes>0 && Nodes<=1048576 && Nets>0 && Nets<=65536,"invalid capacity");
    static uint64_t present(uint64_t iteration,uint64_t cap){
        const uint64_t p=UINT64_C(1)<<unsigned(iteration<20?iteration:20);return p<cap?p:cap;
    }
    static void run(const uint64_t* c,const uint32_t* counts,const uint32_t* complete,uint64_t* r){
        for(unsigned i=0;i<8;++i)r[i]=0;
        r[0]=1;
        if(c[6] || c[7] || c[2]>UINT32_MAX || c[3]>UINT32_MAX)return;
        if(c[0]>Nodes || c[1]>Nets || c[5]>65536){r[0]=2;return;}
        if(!c[0] || !c[1] || !c[3] || c[2]>=c[3] || !c[4])return;
        uint64_t incomplete=0,groups=0;
        for(unsigned i=0;i<unsigned(c[1]);++i){if(complete[i]>1)return;incomplete+=complete[i]==0;}
        for(unsigned i=0;i<unsigned(c[0]);++i)groups+=counts[i]>1;
        const bool conflicts=groups!=0 || c[5]!=0;
        uint64_t action=conflicts?1:(incomplete?1:0),next=0,penalty=0;
        if(conflicts && c[2]+1<c[3]){action=2;next=c[2]+1;penalty=present(next,c[4]);}
        r[0]=0;r[1]=groups;r[2]=incomplete;r[3]=action;r[4]=next;r[5]=penalty;
        r[6]=conflicts;r[7]=present(c[2],c[4]);
    }
};
}
