#define main original_router_main
#include "router.cpp"
#undef main
#include <iostream>
#include <random>
#include <unordered_map>

static void require(bool ok,const char* message) {if(!ok)throw std::runtime_error(message);}
static Router::LabelLease lease(Router::SparseLabels& labels,int id) {
    size_t index=labels.acquire(id);
    return Router::LabelLease(&labels,index,labels.frames[index].values.data()+(id&(labels.PSIZE-1)));
}

static Router::ReadLabelLease readLease(Router::SparseLabels& labels,int id) {
    size_t index=labels.acquire(id,false);
    return Router::ReadLabelLease(&labels,index,labels.frames[index].values.data()+(id&(labels.PSIZE-1)));
}
static void checkReadWriteDirty() {
    setenv("B_RESIDENT_PAGES","2",1);
    Router::SparseLabels labels;labels.initPaged(1024,6);
    {auto a=readLease(labels,0);require(a->visited==0,"Fresh read is not zero");}
    {auto b=readLease(labels,64);}
    {auto c=readLease(labels,128);}
    require(labels.writebacks==0,"Read-only page incorrectly dirtied");
    {auto a=lease(labels,0);a->visited=991;}
    {auto a=readLease(labels,0);require(a->visited==991,"Read lost pending write");}
    {auto b=readLease(labels,192);}
    {auto c=readLease(labels,256);}
    require(labels.writebacks==1,"Dirty page did not write back exactly once");
    {auto a=readLease(labels,0);require(a->visited==991,"Read refill lost value");}
    {auto b=readLease(labels,320);}
    {auto c=readLease(labels,384);}
    require(labels.writebacks==1,"Clean refilled page wrote back again");
}

static void checkZeroBypass() {
    setenv("B_RESIDENT_PAGES","2",1);
    Router::SparseLabels labels; labels.initPaged(1024,6);
    Router::tl_sparse=&labels;
    {
        auto zero=Router::TLRead(0);
        require(labels.firstPages==0 && labels.zeroReads==1,"Zero read allocated storage");
        {auto w=Router::TLD(0);w->visited=123;}
        require(zero->visited==0,"Independent default reference changed after write");
        require(Router::TLRead(0)->visited==123,"Resident write bypassed");
        {auto w=Router::TLD(64);w->visited=456;}
        {auto w=Router::TLD(128);w->visited=789;}
        require(Router::TLRead(0)->visited==123,"Saved page bypassed");
        labels.reset();
        require(zero->visited==0 && Router::TLRead(0)->visited==0,"Reset exposed stale state");
    }
    labels.cur=UINT32_MAX; labels.reset();
    require(Router::TLRead(0)->visited==0,"Wrap exposed stale state");
    bool rejected=false;try {auto bad=Router::TLRead(-1);}catch(const std::runtime_error&){rejected=true;}
    require(rejected,"Invalid zero node accepted");
    std::mt19937 rng(714);
    std::unordered_map<int,int> oracle;
    for(int i=0;i<10000;++i) {
        int n=int(rng()%1024);
        if(rng()%3==0){auto w=Router::TLD(n);w->visited=i+1;oracle[n]=i+1;}
        else require(Router::TLRead(n)->visited==oracle[n],"Mixed zero/read/write oracle mismatch");
        if(i%1000==999){labels.reset();oracle.clear();}
    }
    Router::tl_sparse=nullptr;
}

static void checkIndexOrder() {
    std::mt19937 rng(2917);
    for(int capacity:{2,3,17,256}) {
        std::string count=std::to_string(capacity);setenv("B_RESIDENT_PAGES",count.c_str(),1);
        Router::SparseLabels labels;labels.initPaged(65536,6);
        std::list<int> order;std::vector<int> pages(capacity,-1),pins(capacity,0),held;
        for(int i=0;i<capacity;++i)order.push_back(i);
        for(int step=0;step<5000;++step) {
            if(!held.empty() && rng()%3==0) {
                size_t h=rng()%held.size();int slot=held[h];labels.release(slot);--pins[slot];held.erase(held.begin()+h);
            } else {
                int page=int(rng()%512),expected=-1;
                for(int i=0;i<capacity;++i)if(pages[i]==page)expected=i;
                if(expected<0)for(int i:order)if(!pins[i]){expected=i;break;}
                bool threw=false;size_t slot=0;try{slot=labels.acquire(page*64);}catch(const std::runtime_error&){threw=true;}
                require(threw==(expected<0),"Pinned victim oracle mismatch");
                if(!threw){require(slot==size_t(expected),"Exact LRU victim changed");pages[slot]=page;++pins[slot];held.push_back(int(slot));order.remove(int(slot));order.push_back(int(slot));}
            }
            int previous=-1,current=labels.lruHead;
            for(int expected:order){require(current==expected,"LRU order mismatch");require(labels.frames[current].previous==previous,"Reverse link mismatch");previous=current;current=labels.frames[current].next;}
            require(current==-1 && previous==labels.lruTail,"LRU tail/cycle mismatch");
            if(step%499==498){for(int i:held)labels.release(i);held.clear();std::fill(pins.begin(),pins.end(),0);labels.reset();std::fill(pages.begin(),pages.end(),-1);}
        }
        for(int i:held)labels.release(i);
    }
}

static void checkPushLease() {
    setenv("B_RESIDENT_PAGES","2",1);
    Router router; Router::SparseLabels labels; labels.initPaged(65536,6);
    Router::tl_sparse=&labels;
    std::vector<Router::DaryPQ::E> storage;Router::DaryPQ queue(storage,8);
    Router::State state{};state.queue=&queue;
    std::mt19937 rng(8291);
    auto pinned=lease(labels,65535);pinned->visited=991;
    router.dumpMode=true;
    for(int i=0;i<1000;++i){
        int node=int(rng()%65000);state.sequence=i+1;
        {auto w=lease(labels,node);w->prev=node-1;}
        queue.clear();float partial=float(i)*0.5f,total=partial+3.0f;
        router.push(state,node,partial,total,false);
        {auto read=readLease(labels,node);require(read->lb==total && read->upstream==partial && read->visited==state.sequence && read->prev==node-1,"Push fields changed");}
        require(queue.sz==1 && queue.h[0].id==node && queue.h[0].lb==total,"Push queue changed");
        size_t pins=0;for(const auto& f:labels.frames)pins+=f.pins;
        require(pins==1 && pinned->visited==991,"Push retained lease or evicted outer pin");
    }
    require(router.dumpExplored.size()==1000,"Push dump behavior changed");
    Router::tl_sparse=nullptr;
}

int main() {
    checkPushLease();
    checkIndexOrder();
    checkZeroBypass();
    checkReadWriteDirty();
    setenv("B_RESIDENT_PAGES","2",1);
    std::mt19937 rng(4831);
    for(int bits:{6,9,12}) {
        Router::SparseLabels labels;labels.initPaged(256*(1<<bits),bits);
        for(int query=0;query<3;++query) {
            labels.reset();std::unordered_map<int,int> oracle;
            for(int i=0;i<3000;++i) {
                int node=int(rng()%(256*(1<<bits)));
                auto handle=lease(labels,node);
                require(handle->visited==oracle[node],"Eviction lost actual NodeDyn fields");
                handle->visited=i+1;handle->prev=node-1;oracle[node]=i+1;
            }
            for(const auto& row:oracle) {
                auto handle=lease(labels,row.first);
                require(handle->visited==row.second && handle->prev==row.first-1,"Backing/refill mismatch");
            }
        }
        require(labels.writebacks && labels.refills,"Test must exercise IO");
        labels.reset();
        {
            auto first=lease(labels,0);first->visited=123;
            auto second=lease(labels,1<<bits);second->visited=456;
            bool blocked=false;
            try {auto third=lease(labels,2<<bits);} catch(const std::runtime_error&) {blocked=true;}
            require(blocked,"Live frame leases were evicted");
            require(first->visited==123 && second->visited==456,"Pinned references changed");
            blocked=false;
            try {labels.reset();} catch(const std::runtime_error&) {blocked=true;}
            require(blocked,"Reset accepted live reference");
        }
        labels.reset();require(lease(labels,0)->visited==0,"Reset exposed old label");
        {auto handle=lease(labels,0);handle->target=1;}
        labels.cur=UINT32_MAX;labels.reset();
        require(lease(labels,0)->target==0,"Page epoch wrap exposed label");
    }
    std::cout << "{\"status\":\"passed\",\"slots\":2,\"page_bits\":[6,9,12]}\n";
}
