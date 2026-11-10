#define main original_router_main
#include "router.cpp"
#undef main
#include <random>
#include <unordered_map>
#include <iostream>

static void require(bool ok, const char* message) {if(!ok) throw std::runtime_error(message);}
static bool same(const Router::NodeDyn& a, const Router::NodeDyn& b) {
    return a.lb==b.lb && a.upstream==b.upstream && a.hist==b.hist && a.prev==b.prev && a.visited==b.visited && a.target==b.target;
}
int main() {
    std::mt19937 rng(3901);
    for(int bits:{6,9,12}) {
        int pageSize=1<<bits, nodes=6000*pageSize;
        Router::SparseLabels labels, other;
        labels.initPaged(nodes,bits); other.initPaged(nodes,bits);
        for(int query=0;query<8;++query) {
            labels.reset();
            std::unordered_map<int,Router::NodeDyn> oracle;
            for(int access=0;access<100000;++access) {
                int id=access<5000 ? access*pageSize+(query%pageSize) : int(rng()%nodes);
                labels.prefetch(id);
                auto& value=labels.at(id);
                require(same(value,oracle[id]),"Identity lookup exposed stale labels");
                value.lb=float(access);value.prev=id-1;value.visited=query+1;value.target=access&1;
                oracle[id]=value;
            }
            for(const auto& row:oracle) require(same(labels.at(row.first),row.second),"Growth lost live label");
        }
        require(same(other.at(1),Router::NodeDyn{}),"Contexts alias");
        labels.pool.resize(4096*pageSize);labels.pool.shrink_to_fit();labels.bAfterPoolShrink();labels.reset();
        require(labels.bDenseIds.size()==labels.bCompactValues.size(),"Dense IDs/payload shrink mismatch");
        for(int page=0;page<5500;++page) require(same(labels.at(page*pageSize),Router::NodeDyn{}),"Reclaim exposed stale value");

        Router::SparseLabels adversary;adversary.initPaged(nodes,bits);
        adversary.at(0).lb=42;adversary.reset();
        adversary.at(pageSize).lb=77; // physical page slot 0 now belongs to another logical page
        size_t slot=(size_t)adversary.pageSlot[1]*pageSize+1;
        adversary.pool[slot]=0; // old index inside live range, but dense identity is wrong
        adversary.prefetch(pageSize+1);
        require(same(adversary.at(pageSize+1),Router::NodeDyn{}),"In-range stale index accepted");
        require(adversary.at(pageSize).lb==77,"Stale index overwrote another label");
        adversary.pool[slot+1]=UINT32_MAX;
        adversary.prefetch(pageSize+2); // bounds test must short-circuit before dense ID access
        require(same(adversary.at(pageSize+2),Router::NodeDyn{}),"Out-of-range stale index accepted");
        adversary.cur=UINT32_MAX;adversary.reset();
        require(same(adversary.at(pageSize),Router::NodeDyn{}),"Page epoch wrap resurrected label");
        require(labels.bGrows>0 && labels.bCompactGrows>0,"Growth paths not covered");
    }
    std::cout << "{\"status\":\"passed\",\"page_bits\":[6,9,12],\"adversarial_identity\":true}\n";
}
