#pragma once
#include "children_machine.hpp"
#ifndef CHILDREN_GENERATION_BITS
#define CHILDREN_GENERATION_BITS 32
#endif
namespace children_port {
enum Op : std::uint32_t {START=0, RESPONSE=1, SNAPSHOT=2};
enum Status : std::uint32_t {OK=0,BUSY=1,NO_REQUEST=2,STALE=3,WRONG_PHASE=4,EXHAUSTED=5,BAD=6,WRONG_POSITION=7,SERVICE_ERROR=8,STOPPED=9};
struct Command {std::uint32_t op,parent,count,prune,query,price,generation,position,phase,node,value,aux,service_status;};
struct Reply {std::uint32_t status,generation,request,position,node,parent,query,price,emitted,active,fault;};
template<unsigned Bits> struct Controller {
    static_assert(Bits>=1&&Bits<=32,"generation width");
    static constexpr std::uint32_t limit=~std::uint32_t(0)>>(32-Bits);
    std::uint32_t generation=0,parent=0,query=0,price=0,emitted=0;
    bool active=false,fault=false;
    search_children::Machine machine{0,false};
    Controller(){machine.request=search_children::DONE;}
    std::uint32_t node()const{
        if(!active)return 0;
        return machine.request==search_children::NEXT||machine.request==search_children::CHECK_DEAD||machine.request==search_children::MARK_DEAD||machine.request==search_children::PUBLISH?parent:machine.child;
    }
    Reply step(const Command& c){
        std::uint32_t status=OK;
        if(c.op==START){
            if(fault)status=STOPPED;
            else if(active)status=BUSY;
            else if(c.parent>=0x1000000u||c.prune>1||c.query>3||c.price>15)status=BAD;
            else if(generation==limit)status=EXHAUSTED;
            else {++generation;parent=c.parent;query=c.query;price=c.price;emitted=0;active=true;machine=search_children::Machine(c.count,c.prune!=0);}
        }else if(c.op==RESPONSE){
            if(fault)status=STOPPED;
            else if(!active)status=NO_REQUEST;
            else if(c.generation!=generation||c.parent!=parent||c.query!=query||c.price!=price||c.node!=node())status=STALE;
            else if(c.phase!=std::uint32_t(machine.request))status=WRONG_PHASE;
            else if(c.position!=machine.position)status=WRONG_POSITION;
            else if(c.service_status!=0){fault=true;status=SERVICE_ERROR;}
            else {
                bool accepted=false;
                switch(machine.request){
                case search_children::NEXT:if(c.aux<=1)accepted=machine.next(c.value,c.aux!=0);break;
                case search_children::EXCLUDE:if(c.value<=1&&c.aux==0)accepted=machine.excluded(c.value!=0);break;
                case search_children::CREATE:if(c.value==0&&c.aux==0)accepted=machine.created();break;
                case search_children::CLASSIFY:if(c.value<=1&&c.aux<=1)accepted=machine.classified(c.value!=0,c.aux!=0);break;
                case search_children::EMIT:if(c.value==0&&c.aux==0){accepted=machine.emitted();if(accepted)++emitted;}break;
                case search_children::CHECK_DEAD:if(c.value<=1&&c.aux==0)accepted=machine.can_mark_dead(c.value!=0);break;
                case search_children::MARK_DEAD:if(c.value==0&&c.aux==0)accepted=machine.marked_dead();break;
                case search_children::PUBLISH:if(c.value==0&&c.aux==0){accepted=machine.published();if(accepted)active=false;}break;
                default:break;
                }
                if(!accepted)status=BAD;
            }
        }else if(c.op!=SNAPSHOT)status=BAD;
        return {status,generation,std::uint32_t(machine.request),machine.position,node(),parent,query,price,emitted,std::uint32_t(active),std::uint32_t(fault)};
    }
};
}
void children_step(std::uint32_t op,std::uint32_t parent,std::uint32_t count,std::uint32_t prune,std::uint32_t query,std::uint32_t price,std::uint32_t generation,std::uint32_t position,std::uint32_t phase,std::uint32_t node,std::uint32_t value,std::uint32_t aux,std::uint32_t service_status,std::uint32_t& status,std::uint32_t& result_generation,std::uint32_t& request,std::uint32_t& result_position,std::uint32_t& result_node,std::uint32_t& result_parent,std::uint32_t& result_query,std::uint32_t& result_price,std::uint32_t& emitted,std::uint32_t& active,std::uint32_t& fault);
