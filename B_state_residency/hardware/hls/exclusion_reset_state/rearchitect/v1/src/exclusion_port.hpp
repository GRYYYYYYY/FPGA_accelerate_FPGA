#pragma once
#include "exclusion_machine.hpp"
#ifndef EXCLUSION_GENERATION_BITS
#define EXCLUSION_GENERATION_BITS 32
#endif
namespace exclusion_port {
enum Op : std::uint32_t { START=0, RESPONSE=1, SNAPSHOT=2 };
enum Status : std::uint32_t { OK=0, BUSY=1, NO_REQUEST=2, STALE=3, WRONG_PHASE=4, EXHAUSTED=5, BAD=6 };
struct Command {std::uint32_t op,parent,child,flags,created,has_laguna,generation,phase,value;};
struct Reply {std::uint32_t status,generation,request,node,excluded;};
template<unsigned Bits> struct Controller {
    static_assert(Bits>=1 && Bits<=32,"generation width");
    static constexpr std::uint32_t limit=~std::uint32_t(0)>>(32-Bits);
    std::uint32_t generation=0,child=0;
    search_filter::Machine machine{0,0,false,false};
    Reply step(const Command& c){
        std::uint32_t status=OK;
        if(c.op==START){
            if(machine.request!=search_filter::DONE)status=BUSY;
            else if(c.parent>0x7fffffffu || c.child>0x7fffffffu || c.flags>255 || c.created>1 || c.has_laguna>1)status=BAD;
            else if(generation==limit)status=EXHAUSTED;
            else {++generation;child=c.child;machine=search_filter::Machine(static_cast<std::int32_t>(c.parent),static_cast<std::uint8_t>(c.flags),bool(c.created),bool(c.has_laguna));}
        }else if(c.op==RESPONSE){
            if(machine.request==search_filter::DONE)status=NO_REQUEST;
            else if(c.generation!=generation)status=STALE;
            else if(c.phase!=std::uint32_t(machine.request))status=WRONG_PHASE;
            else machine.accept(c.value);
        }else if(c.op!=SNAPSHOT)status=BAD;
        const bool done=machine.request==search_filter::DONE;
        Reply reply={status,generation,std::uint32_t(machine.request),done?0u:(machine.request==search_filter::PARENT_VISITED?std::uint32_t(machine.parent):child),done&&generation!=0?std::uint32_t(machine.excluded):0u};
        return reply;
    }
};
}
void exclusion_step(std::uint32_t op,std::uint32_t parent,std::uint32_t child,std::uint32_t flags,std::uint32_t created,std::uint32_t has_laguna,std::uint32_t generation,std::uint32_t phase,std::uint32_t value,std::uint32_t& status,std::uint32_t& result_generation,std::uint32_t& request,std::uint32_t& node,std::uint32_t& excluded);
