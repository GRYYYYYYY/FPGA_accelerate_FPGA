// Exercise the actual alternative source, including static sort_edges_merge.
#include "graph_body.cpp"
#include <algorithm>
#include <iostream>
#include <random>
#include <stdexcept>
#include <vector>

static bool oracle_less(const EdgeRecord &a,const EdgeRecord &b) {
    return std::lexicographical_compare(a.w,a.w+7,b.w,b.w+7);
}
int main() {
    try {
        std::mt19937 random(20261023);
        uint32_t cases=0;
        for (uint32_t degree=0; degree<=MAX_DEGREE; ++degree) {
            for (unsigned pattern=0; pattern<5; ++pattern) {
                struct Guarded {
                    uint32_t before[8];
                    EdgeRecord rows[MAX_DEGREE];
                    uint32_t after[8];
                } buffer;
                std::fill(buffer.before,buffer.before+8,0xdecafbad);
                std::fill(buffer.after,buffer.after+8,0xdecafbad);
                for (unsigned i=0;i<MAX_DEGREE;++i)
                    for (unsigned k=0;k<7;++k) buffer.rows[i].w[k]=0xdecafbad;
                std::vector<EdgeRecord> expected(degree);
                for (uint32_t i=0;i<degree;++i) {
                    for (unsigned k=0;k<7;++k) {
                        // Many equal prefixes force comparison of later fields.
                        uint32_t value=pattern==4 ? 0xffffffff :
                            (pattern==3 ? (k==6 ? random()%2 : 17) : random()%8);
                        expected[i].w[k]=value;
                    }
                }
                if (pattern==1 || pattern==2) {
                    std::sort(expected.begin(),expected.end(),oracle_less);
                    if (pattern==2) std::reverse(expected.begin(),expected.end());
                }
                std::copy(expected.begin(),expected.end(),buffer.rows);
                std::stable_sort(expected.begin(),expected.end(),oracle_less);
                sort_edges_merge(buffer.rows,degree);
                for (uint32_t i=0;i<degree;++i)
                    for (unsigned k=0;k<7;++k)
                        if (buffer.rows[i].w[k]!=expected[i].w[k]) throw std::runtime_error("record differs");
                for (uint32_t i=degree;i<MAX_DEGREE;++i)
                    for (unsigned k=0;k<7;++k)
                        if (buffer.rows[i].w[k]!=0xdecafbad) throw std::runtime_error("tail guard differs");
                for (unsigned i=0;i<8;++i)
                    if (buffer.before[i]!=0xdecafbad || buffer.after[i]!=0xdecafbad)
                        throw std::runtime_error("boundary guard differs");
                ++cases;
            }
        }
        std::cout<<"MERGE_SORT_PASS cases="<<cases<<" degrees=0..1024 patterns=5"<<std::endl;
        return 0;
    } catch (const std::exception &error) {
        std::cerr<<"MERGE_SORT_FAIL "<<error.what()<<std::endl;
        return 1;
    }
}
