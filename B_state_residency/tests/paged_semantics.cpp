// Exercise the exact generated router label store, including epoch wrap and reclaim.
#define main original_router_main
#include "router.cpp"
#undef main
#include <iostream>
#include <random>
#include <unordered_map>

static void check(bool value, const char* what) { if(!value) throw std::runtime_error(what); }
static bool equal(const Router::NodeDyn& a, const Router::NodeDyn& b) {
    return a.lb==b.lb && a.upstream==b.upstream && a.hist==b.hist && a.prev==b.prev && a.visited==b.visited && a.target==b.target;
}
int main() {
    Router::SparseLabels labels, independent;
    constexpr int N=160000;
    labels.initPaged(N,4); independent.initPaged(N,4);
    std::mt19937 rng(291);
    for(int query=0;query<20;++query) {
        labels.reset();
        std::unordered_map<int, Router::NodeDyn> expected;
        // Force allocation growth, then reassign physical slots to other logical pages.
        for(int access=0;access<22000;++access) {
            int id = query%2 ? int(rng()%N) : (access*16)%N;
            auto& got=labels.at(id);
            check(equal(got,expected[id]),"stale/wrong per-search label");
            got.lb=float(access);got.upstream=float(query);got.prev=id-1;
            got.visited=query+1;got.target=uint8_t(access&1);expected[id]=got;
        }
        for(const auto& row:expected) check(equal(labels.at(row.first),row.second),"growth lost a live label");
    }
    labels.at(17).target=1; labels.at(17).prev=99;
    check(equal(independent.at(17),Router::NodeDyn{}),"contexts alias");
    Router::SparseLabels wrap; wrap.initPaged(N,4);
    wrap.at(17).target=1; wrap.at(17).prev=99;
    wrap.cur=UINT32_MAX; wrap.reset();
    check(wrap.cur==1 && equal(wrap.at(17),Router::NodeDyn{}),"epoch wrap exposed old label");
    labels.pool.resize(4096*labels.PSIZE); labels.pool.shrink_to_fit(); labels.bAfterPoolShrink(); labels.reset();
    for(int i=0;i<10000;++i) check(equal(labels.at(i*16),Router::NodeDyn{}),"reclaim/regrowth exposed old label");
#if B_NODE_EPOCH
    check(labels.bNodeEpoch.size()==labels.pool.size(),"tag storage did not track pool capacity");
#endif
    check(labels.bGrows>0,"growth not exercised");
    std::cout << "{\"status\":\"passed\",\"node_epoch\":" << B_NODE_EPOCH << "}\n";
}
