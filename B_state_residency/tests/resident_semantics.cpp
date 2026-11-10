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
int main() {
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
