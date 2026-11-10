"""Replace only the isolated CPU heap with the exact helper used by HLS compute."""
def generate(source,header):
 start=source.index('    struct DaryPQ {');end=source.index('    std::vector<DaryPQ::E> pqStorage;',start)
 old=source[start:end]
 new='''    struct DaryPQ {
        using E=frontier::Entry;
        std::vector<E>& h; int sz=0; int D;
        DaryPQ(std::vector<E>& storage,int arity):h(storage),D(arity) {
            if(D!=8)throw std::runtime_error("bounded frontier requires arity8");
            if(h.size()<frontier::capacity)h.resize(frontier::capacity);
        }
        inline bool empty()const{return sz==0;}
        inline void clear(){if(btrace::current)btrace::current->frontierCleared+=(uint64_t)sz;sz=0;}
        inline void offer(float lb,int id){
            uint32_t bits;std::memcpy(&bits,&lb,4);E entry={bits,(uint32_t)id};uint32_t size=(uint32_t)sz;
            if(!frontier::offer(h.data(),size,entry))throw std::runtime_error("bounded frontier full");
            sz=(int)size;
            if(btrace::current){++btrace::current->frontierPushes;btrace::current->frontierPeak=std::max(btrace::current->frontierPeak,(uint64_t)sz);}
        }
        inline int poll(){
            E entry;uint32_t size=(uint32_t)sz;
            if(!frontier::poll(h.data(),size,entry))throw std::runtime_error("bounded frontier empty");
            sz=(int)size;if(btrace::current)++btrace::current->frontierPolls;
            return (int)entry.id;
        }
    };
'''
 assert new.count('\n')<=old.count('\n')
 new+='\n'*(old.count('\n')-new.count('\n'))
 result=source[:start]+new+source[end:];assert result.count('\n')==source.count('\n')
 assert header.count('#include <fstream>')==1
 header=header.replace('#include <fstream>','#include <fstream>\n#include "frontier_bounded.hpp"')
 return result,header
