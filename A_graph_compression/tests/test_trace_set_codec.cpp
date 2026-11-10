#include "search_trace_set_codec.hpp"
#include <algorithm>
#include <cassert>
#include <fstream>
#include <random>
#include <vector>
using C=fpga_search::TraceSetCodec<>;
int main(int argc,char** argv){
    assert(argc==2);std::ofstream file(argv[1],std::ios::binary);
    auto put=[&](uint64_t v){for(unsigned b=0;b<8;++b)file.put(char(v>>(8*b)));};
    std::mt19937_64 random(73);unsigned cases=0;
    auto test=[&](const std::vector<uint64_t>& keys){
        std::vector<uint64_t> out(keys.size()+2,UINT64_C(0xdeadbeef));unsigned encoding=9;uint64_t bytes=0;
        assert(C::encode(keys.data(),unsigned(keys.size()),unsigned(keys.size()),out.data(),encoding,bytes));
        assert(out[(bytes+7)/8]==UINT64_C(0xdeadbeef));
        put(keys.size());put(encoding);put(bytes);for(auto key:keys)put(key);for(unsigned i=0;i<(bytes+7)/8;++i)put(out[i]);++cases;
        if(bytes){auto before=out;assert(!C::encode(keys.data(),unsigned(keys.size()),unsigned((bytes+7)/8)-1,out.data(),encoding,bytes) && out==before);}
    };
    test({});test({0});test({0,1,2,3,127,128,UINT64_MAX-1,UINT64_MAX});test({0,UINT64_MAX});
    std::vector<uint64_t> spread(128);for(unsigned i=0;i<128;++i)spread[i]=uint64_t(i)<<56;test(spread);
    for(unsigned c=0;c<500;++c){std::vector<uint64_t> keys;uint64_t key=random()%1000;for(unsigned i=0;i<c*3;++i){key+=1+random()%((c%3)?4:1000000000);keys.push_back(key);}test(keys);}
    std::vector<uint64_t> maximum(1100754);for(unsigned i=0;i<maximum.size();++i)maximum[i]=i;test(maximum);
    uint64_t bad[2]={8,8},guard[2]={41,42};unsigned encoding=0;uint64_t bytes=0;assert(!C::encode(bad,2,2,guard,encoding,bytes) && guard[0]==41 && guard[1]==42);
    bad[1]=7;assert(!C::encode(bad,2,2,guard,encoding,bytes) && guard[0]==41 && guard[1]==42);
    assert(!C::encode(nullptr,1100755,2,guard,encoding,bytes) && guard[0]==41 && guard[1]==42);
    file.close();assert(file);assert(cases==506);
}
