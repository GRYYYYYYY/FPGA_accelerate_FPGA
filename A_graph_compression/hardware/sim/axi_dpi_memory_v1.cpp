// Four-state backing storage for simulation only. No FPGA DUT code.
#include "svdpi.h"
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <memory>
#include <string>
#include <vector>
struct Write { int page; std::uint64_t index; std::vector<svLogicVecVal> value; };
struct Memory {
    unsigned words,pages;std::uint64_t depth;
    std::vector<svLogicVecVal> data;std::vector<Write> pending;
};
static std::vector<std::unique_ptr<Memory>> memories;
static Memory* lookup(int id) {return id>=0 && std::size_t(id)<memories.size()?memories[id].get():nullptr;}
static bool valid(Memory* m,int page,long long index) {return m && page>=0 && unsigned(page)<m->pages && index>=0 && std::uint64_t(index)<m->depth;}
static std::size_t offset(Memory* m,int page,std::uint64_t index) {return (std::uint64_t(page)*m->depth+index)*m->words;}
extern "C" int a_model_register(const char* name,int bits,long long depth,int pages) {
    if(bits<32 || bits>512 || bits%32 || depth<=0 || pages<=0)return -1;
    const std::uint64_t words=unsigned(bits)/32;
    if(std::uint64_t(depth)>SIZE_MAX/unsigned(pages)/words/sizeof(svLogicVecVal))return -1;
    try {
        std::unique_ptr<Memory> m(new Memory);
        m->words=words;m->pages=pages;m->depth=depth;
        m->data.resize(std::uint64_t(depth)*pages*words,svLogicVecVal{0,0});
        memories.push_back(std::move(m));
        std::fprintf(stderr,"A_DPI_REGISTER id=%zu name=%s bits=%d depth=%lld pages=%d\n",memories.size()-1,name,bits,depth,pages);
        return int(memories.size()-1);
    } catch(...) {return -1;}
}
extern "C" void a_model_read(int id,int page,long long index,svLogicVecVal* result) {
    std::fill(result,result+16,svLogicVecVal{0,0});auto* m=lookup(id);
    if(!valid(m,page,index)){std::fill(result,result+16,svLogicVecVal{UINT32_MAX,UINT32_MAX});return;}
    std::copy_n(m->data.data()+offset(m,page,index),m->words,result);
}
extern "C" void a_model_write(int id,int page,long long index,const svLogicVecVal* value) {
    auto* m=lookup(id);if(valid(m,page,index))std::copy_n(value,m->words,m->data.data()+offset(m,page,index));
}
extern "C" void a_model_enqueue(int id,int page,long long index,const svLogicVecVal* value) {
    auto* m=lookup(id);if(!valid(m,page,index))return;
    m->pending.push_back(Write{page,std::uint64_t(index),std::vector<svLogicVecVal>(value,value+m->words)});
}
extern "C" void a_model_commit(int id) {
    auto* m=lookup(id);if(!m)return;
    for(const auto& w:m->pending)std::copy(w.value.begin(),w.value.end(),m->data.begin()+offset(m,w.page,w.index));
    m->pending.clear();
}
