#define main original_router_main
#include "router.cpp"
#undef main
#include <iostream>
#include <random>
#include <unordered_map>

static void require(bool value,const char* message) { if(!value)throw std::runtime_error(message); }
static bool same(const Router::NodeDyn& a,const Router::NodeDyn& b) {
    return a.lb==b.lb && a.upstream==b.upstream && a.hist==b.hist && a.prev==b.prev && a.visited==b.visited && a.target==b.target;
}
int main() {
    std::mt19937 rng(291);
    for(int bits:{6,9,12}) {
        const int size=1<<bits,N=6000*size;
        Router::SparseLabels labels,independent;
        labels.initPaged(N,bits);independent.initPaged(N,bits);
        for(int query=0;query<8;++query) {
            labels.reset();std::unordered_map<int,Router::NodeDyn> expected;
            for(int access=0;access<100000;++access) {
                int id=access<5000 ? (access*size+(query%size)) : int(rng()%N);
                auto& actual=labels.at(id);
                require(same(actual,expected[id]),"compact label alias or stale value");
                actual.lb=float(access);actual.upstream=float(query);actual.prev=id-1;
                actual.visited=query+1;actual.target=uint8_t(access&1);expected[id]=actual;
            }
            for(const auto& row:expected)require(same(labels.at(row.first),row.second),"compact growth lost live labels");
        }
        require(same(independent.at(1),Router::NodeDyn{}),"contexts alias");
        require(labels.bCompactValues.size()>65536,"compact reclaim threshold not exercised");
        labels.pool.resize(4096*size);labels.pool.shrink_to_fit();labels.bAfterPoolShrink();
        require(labels.bCompactValues.size()==65536,"compact payload was not reclaimed");labels.reset();
        for(int page=0;page<5500;++page)require(same(labels.at(page*size),Router::NodeDyn{}),"reclaim/regrowth exposed label");
        Router::SparseLabels wrap;wrap.initPaged(N,bits);wrap.at(1).target=1;
        wrap.cur=UINT32_MAX;wrap.reset();require(same(wrap.at(1),Router::NodeDyn{}),"epoch wrap exposed stale mapping");
        require(labels.bCompactValues.size()<labels.pool.size(),"sparse labels did not use compact capacity");
        require(labels.bCompactGrows>0 && labels.bGrows>0,"both growth paths must execute");
    }
    std::cout<<"{\"status\":\"passed\",\"page_bits\":[6,9,12]}\n";
}
