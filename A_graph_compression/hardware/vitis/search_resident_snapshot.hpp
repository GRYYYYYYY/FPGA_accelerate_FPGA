#pragma once
#include "search_node_occupancy.hpp"
#include "search_site_occupancy.hpp"
#include "search_key_words.hpp"

namespace fpga_search {
enum class ResidentSnapshotStatus : unsigned {ok=0,invalid=1,capacity=2};

// Static image header16: magic,total,nodes,attributes,nprotected,nsemantics,
// nfixed,nreserved,8 zeros. Sections: protected-node bitset, reserved node/net
// u64 pairs (node<<32)|net, packed pseudo flags, packed blocked flags, protected
// PIP keys, semantic keys, 65-word requirements, 4-word fixed records.
// Mutable inputs must be trusted states produced by the occupancy components.
// All buffers are disjoint/exclusively owned. Failed calls preserve packet.
template<unsigned Nodes=1048576,unsigned Slots=2097152,unsigned Owners=65536,
         unsigned History=65536,unsigned PacketWords=4194304>
struct ResidentSnapshot {
    static_assert(Nodes<=1048576 && Owners<=65536 && History<=65536 && PacketWords<=4194304,"ABI capacity exceeded");
    using Node=NodeOccupancy<Nodes,Slots>;
    using Site=SiteOccupancy<Owners,History,Owners>;
    using Words=LabelKeyWords<1,32,16,8>;
    using Status=ResidentSnapshotStatus;
    static constexpr uint64_t StaticMagic=UINT64_C(0x41534e4150535431);
    static constexpr uint64_t PacketMagic=UINT64_C(0x4153454152434831);
    static constexpr unsigned StaticWords=4194304,Attributes=65536,Protected=1048576,Semantics=256,Fixed=65536;
    static bool query(uint64_t nodes,const uint64_t* c,const uint64_t* initial) {
        if(c[3]>=nodes || !c[4] || c[4]>Nodes || !c[5] || c[5]>200000)return false;
        typename Words::Key k{};return Words::load(initial,0,k) && !k.node;
    }
    static bool flags(const uint64_t* data,unsigned count) {
        for(unsigned i=0;i<count;++i)if(((data[i/8]>>(8*(i%8)))&255)>1)return false;
        return !(count%8) || !(data[count/8]>>(8*(count%8)));
    }
    static void copy(const uint64_t* input,unsigned from,unsigned count,uint64_t* output,unsigned to) {
        for(unsigned i=0;i<count;++i)output[to+i]=input[from+i];
    }
    // control16: op(0 build/1 patch query),net,present,target,nroots,budget,
    // static_words,packet_capacity(build)/packet_length(patch),8 zeros.
    // result8: status,packet_words,node_occupied,node_history,site_owners,
    // site_history,node_version,site_version. Patch returns only first2 fields.
    static void run(const uint64_t* c,const uint64_t* stat,const uint64_t* initial,
                    const uint64_t* nm,const uint32_t* counts,const uint64_t* nh,
                    const uint64_t* nk,const uint32_t* nf,const uint64_t* sm,
                    const uint64_t* so,const uint64_t* sh,uint64_t* packet,uint64_t* result) {
        for(unsigned i=0;i<8;++i)result[i]=0;
        result[0]=uint64_t(Status::invalid);
        for(unsigned i=8;i<16;++i)if(c[i])return;
        if(c[0]>1)return;
        if(c[7]>PacketWords){result[0]=uint64_t(Status::capacity);return;}
        if(c[0]==1) {
            // Packet body is trusted output of a prior successful build. The
            // patch operation never changes frozen metadata or ledger state.
            if(c[1] || c[2] || c[6] || c[7]<32+Words::Words)return;
            if(packet[0]!=PacketMagic || packet[1]!=c[7] || !packet[2] || packet[2]>Nodes)return;
            for(unsigned i=14;i<32;++i)if(packet[i])return;
            if(!query(packet[2],c,initial))return;
            typename Words::Key k{};Words::load(initial,0,k);
            Words::store(packet+32,0,k);packet[6]=c[3];packet[7]=c[4];packet[8]=c[5];
            result[0]=0;result[1]=c[7];return;
        }
        if(c[6]>StaticWords){result[0]=uint64_t(Status::capacity);return;}
        if(c[6]<16 || c[1]>UINT32_MAX || !c[2])return;
        if(stat[0]!=StaticMagic || stat[1]!=c[6])return;
        for(unsigned i=8;i<16;++i)if(stat[i])return;
        if(stat[2]>Nodes || stat[3]>Attributes || stat[4]>Protected || stat[5]>Semantics || stat[6]>Fixed || stat[7]>Nodes) {
            result[0]=uint64_t(Status::capacity);return;
        }
        if(!stat[2] || !stat[3] || !query(stat[2],c,initial))return;
        if(!Node::valid_meta(nm) || nm[1]!=stat[2] || !Site::valid(sm))return;
        const unsigned nodes=unsigned(stat[2]),attrs=unsigned(stat[3]),np=unsigned(stat[4]);
        const unsigned ns=unsigned(stat[5]),nfixed=unsigned(stat[6]),nr=unsigned(stat[7]);
        const unsigned nw=(nodes+63)/64,aw=(attrs+7)/8;
        const unsigned protect=16,reserved=protect+nw,pseudo=reserved+nr,blocked=pseudo+aw;
        const unsigned pips=blocked+aw,sem=pips+np,req=sem+ns,fixed=req+ns*Words::Words;
        if(uint64_t(fixed)+4*nfixed!=c[6])return;
        if(nodes%64 && stat[protect+nw-1]>>(nodes%64))return;
        for(unsigned i=0;i<nr;++i) {
            const unsigned n=unsigned(stat[reserved+i]>>32);
            if(n>=nodes || (i && n<=unsigned(stat[reserved+i-1]>>32)) || ((stat[protect+n/64]>>(n%64))&1))return;
        }
        if(!flags(stat+pseudo,attrs) || !flags(stat+blocked,attrs))return;
        for(unsigned i=0;i<np;++i)if(i && stat[pips+i]<=stat[pips+i-1])return;
        for(unsigned i=0;i<ns;++i) {
            if(i && stat[sem+i]<=stat[sem+i-1])return;
            typename Words::Key k{};if(!Words::load(stat+req+i*Words::Words,0,k) || k.node)return;
        }
        for(unsigned i=0;i<nfixed;++i) {
            const unsigned at=fixed+4*i;const uint64_t k=stat[at];
            if(!Site::entry(k,stat[at+2],stat[at+3]) || stat[at+1]>UINT32_MAX ||
               ((k>>32)!=0 && stat[at+1]) || (i && k<=stat[at-4]))return;
        }
        unsigned owner_count=0;const unsigned sb=unsigned(sm[1])*Owners*4;
        for(unsigned i=0;i<unsigned(sm[2]);++i)if(so[sb+4*i+1]!=c[1])++owner_count;
        const unsigned forbidden_at=32+Words::Words,costs_at=forbidden_at+nw;
        const unsigned pseudo_at=costs_at+2*nodes,blocked_at=pseudo_at+aw,pips_at=blocked_at+aw;
        const unsigned sem_at=pips_at+np,req_at=sem_at+ns,owners_at=req_at+ns*Words::Words;
        const unsigned history_at=owners_at+4*owner_count,fixed_at=history_at+2*unsigned(sm[4]);
        const uint64_t total=uint64_t(fixed_at)+4*nfixed;
        if(total>PacketWords || total>c[7]){result[0]=uint64_t(Status::capacity);return;}
        // Complete preflight done; exclusive trusted inputs cannot change now.
        for(unsigned i=0;i<32;++i)packet[i]=0;
        const uint64_t h[14]={PacketMagic,total,nodes,attrs,c[1],c[2],c[3],c[4],c[5],ns,np,owner_count,sm[4],nfixed};
        for(unsigned i=0;i<14;++i)packet[i]=h[i];
        typename Words::Key initial_key{};Words::load(initial,0,initial_key);Words::store(packet+32,0,initial_key);
        copy(stat,protect,nw,packet,forbidden_at);
        for(unsigned i=0;i<nr;++i)if(uint32_t(stat[reserved+i])!=c[1]) {
            const unsigned n=unsigned(stat[reserved+i]>>32);packet[forbidden_at+n/64]|=uint64_t(1)<<(n%64);
        }
        Node::snapshot(uint32_t(c[1]),nm,counts,nh,nk,nf,packet+costs_at);
        bool occupied=false,past=false;
        for(unsigned i=0;i<nodes;++i){occupied=occupied || packet[costs_at+2*i]!=0;past=past || packet[costs_at+2*i+1]!=0;}
        copy(stat,pseudo,aw,packet,pseudo_at);copy(stat,blocked,aw,packet,blocked_at);
        copy(stat,pips,np,packet,pips_at);copy(stat,sem,ns,packet,sem_at);
        for(unsigned i=0;i<ns;++i) {
            typename Words::Key k{};Words::load(stat+req+i*Words::Words,0,k);Words::store(packet+req_at+i*Words::Words,0,k);
        }
        unsigned exported=0;Site::snapshot(uint32_t(c[1]),sm,so,sh,packet+owners_at,packet+history_at,exported);
        copy(stat,fixed,4*nfixed,packet,fixed_at);
        result[0]=0;result[1]=total;result[2]=occupied;result[3]=past;
        result[4]=owner_count;result[5]=sm[4];result[6]=nm[3];result[7]=sm[5];
    }
};
using ProductionResidentSnapshot=ResidentSnapshot<>;
} // namespace fpga_search
