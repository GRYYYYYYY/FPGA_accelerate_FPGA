#pragma once
#include <cstdint>

namespace fpga_search {
enum class SiteOccupancyStatus : unsigned { ok=0, invalid=1, capacity=2, overflow=3 };

// Caller owns disjoint, full-sized buffers and serializes transactions. Internal
// state must come from reset and successful calls, not arbitrary memory. Two
// banks permit preflight before writing ANY persistent word on a rejected call.
// meta: magic, owner bank/count, history bank/count, version.
// Owners: [key,net,mask,value], sorted (key,net); history: [key,cost].
// Request: [key,mask,value], sorted unique key; key=(kind<<32)|physical_id.
template<unsigned Owners, unsigned History, unsigned Requests=Owners>
struct SiteOccupancy {
    static_assert(Owners>0 && History>0 && Requests>0,"nonempty capacities required");
    static constexpr uint64_t Magic=UINT64_C(0x41534954454f5731);
    using Status=SiteOccupancyStatus;
    static bool valid(const uint64_t* m) {
        return m[0]==Magic && m[1]<2 && m[2]<=Owners && m[3]<2 && m[4]<=History && m[5]!=0;
    }
    static Status reset(uint64_t* m) {
        m[0]=Magic;m[1]=0;m[2]=0;m[3]=0;m[4]=0;m[5]=1;return Status::ok;
    }
    static bool entry(uint64_t key,uint64_t mask,uint64_t value) {
        const uint64_t kind=key>>32;
        return (kind==0 && !mask && !value) || (kind==1 && !(value&~mask)) ||
               (kind==2 && !mask && value<=UINT32_MAX);
    }
    static Status replace(uint32_t net,const uint64_t* request,unsigned count,
                          uint64_t* m,uint64_t* owners) {
        if(!valid(m))return Status::invalid;
        if(count>Requests)return Status::capacity;
        if(m[5]==UINT64_MAX)return Status::overflow;
        for(unsigned i=0;i<count;++i) {
            if(!entry(request[3*i],request[3*i+1],request[3*i+2]) ||
               (i && request[3*i]<=request[3*(i-1)]))return Status::invalid;
        }
        const unsigned n=unsigned(m[2]),src=unsigned(m[1])*Owners*4;
        const unsigned dst=(1-unsigned(m[1]))*Owners*4;
        unsigned removed=0;
        for(unsigned i=0;i<n;++i)if(owners[src+4*i+1]==net)++removed;
        if(uint64_t(n)-removed+count>Owners)return Status::capacity;
        unsigned i=0,j=0,k=0;
        // Every iteration consumes one old row or one request (including skips).
        for(uint64_t step=0;step<uint64_t(Owners)+Requests;++step) {
            if(i==n && j==count)break;
            if(i<n && owners[src+4*i+1]==net){++i;continue;}
            const bool take=j<count && (i==n || request[3*j]<owners[src+4*i] ||
                 (request[3*j]==owners[src+4*i] && net<owners[src+4*i+1]));
            if(take) {
                owners[dst+4*k]=request[3*j];owners[dst+4*k+1]=net;
                owners[dst+4*k+2]=request[3*j+1];owners[dst+4*k+3]=request[3*j+2];++j;
            } else {
                for(unsigned w=0;w<4;++w)owners[dst+4*k+w]=owners[src+4*i+w];
                ++i;
            }
            ++k;
        }
        m[1]=1-m[1];m[2]=k;++m[5];return Status::ok;
    }
    // scratch flags correspond to active owner rows. summaries=[key,bad_count]
    // only for conflicting keys. Scratch is disposable even on advance failure.
    static Status analyze(const uint64_t* m,const uint64_t* owners,uint32_t* flags,
                          uint64_t* summaries,unsigned& groups) {
        groups=0;if(!valid(m))return Status::invalid;
        const unsigned n=unsigned(m[2]),base=unsigned(m[1])*Owners*4;
        unsigned start=0;
        for(unsigned group=0;group<Owners && start<n;++group) {
            const uint64_t key=owners[base+4*start],kind=key>>32;
            const uint64_t first=owners[base+4*start+3];
            uint64_t ones=0,zeros=0;bool differs=false;unsigned end=start;
            for(unsigned i=start;i<n;++i) {
                if(owners[base+4*i]!=key)break;
                const uint64_t mask=owners[base+4*i+2],value=owners[base+4*i+3];
                ones|=value;zeros|=mask&~value;differs=differs || value!=first;end=i+1;
            }
            unsigned bad=0;
            for(unsigned i=start;i<end;++i) {
                const uint64_t mask=owners[base+4*i+2],value=owners[base+4*i+3];
                const bool conflict=kind==0 ? end-start>1 : kind==2 ? differs :
                    ((value&zeros)|((mask&~value)&ones))!=0;
                flags[i]=conflict?1:0;bad+=conflict?1:0;
            }
            if(bad){summaries[2*groups]=key;summaries[2*groups+1]=bad;++groups;}
            start=end;
        }
        return Status::ok;
    }
    static Status advance(uint64_t* m,const uint64_t* owners,uint64_t* history,
                          uint32_t* flags,uint64_t* summaries,unsigned& groups) {
        groups=0;if(!valid(m))return Status::invalid;
        if(m[5]==UINT64_MAX)return Status::overflow;
        const Status s=analyze(m,owners,flags,summaries,groups);if(s!=Status::ok)return s;
        const unsigned n=unsigned(m[4]),src=unsigned(m[3])*History*2;
        const unsigned dst=(1-unsigned(m[3]))*History*2;
        unsigned final_count=0;
        // Dry run validates union capacity and ALL additions before any writes.
        for(unsigned pass=0;pass<2;++pass) {
            unsigned i=0,j=0,k=0;
            for(uint64_t step=0;step<uint64_t(History)+Owners;++step) {
                if(i==n && j==groups)break;
                const bool old=i<n && (j==groups || history[src+2*i]<=summaries[2*j]);
                const bool add=j<groups && (i==n || summaries[2*j]<=history[src+2*i]);
                const uint64_t key=old?history[src+2*i]:summaries[2*j];
                const uint64_t value=old?history[src+2*i+1]:0;
                const uint64_t delta=add?summaries[2*j+1]-1:0;
                if(k==History)return Status::capacity;
                if(value>UINT64_MAX-delta)return Status::overflow;
                if(pass){history[dst+2*k]=key;history[dst+2*k+1]=value+delta;}
                if(old)++i;
                if(add)++j;
                ++k;
            }
            final_count=k;
        }
        m[3]=1-m[3];m[4]=final_count;++m[5];return Status::ok;
    }
    static Status snapshot(uint32_t net,const uint64_t* m,const uint64_t* owners,
                           const uint64_t* history,uint64_t* out_owners,uint64_t* out_history,
                           unsigned& count) {
        count=0;if(!valid(m))return Status::invalid;
        const unsigned base=unsigned(m[1])*Owners*4;
        for(unsigned i=0;i<unsigned(m[2]);++i)if(owners[base+4*i+1]!=net) {
            for(unsigned w=0;w<4;++w)out_owners[4*count+w]=owners[base+4*i+w];
            ++count;
        }
        const unsigned hbase=unsigned(m[3])*History*2;
        for(unsigned i=0;i<2*unsigned(m[4]);++i)out_history[i]=history[hbase+i];
        return Status::ok;
    }
};
using ProductionSiteOccupancy=SiteOccupancy<65536,65536,65536>;
} // namespace fpga_search
