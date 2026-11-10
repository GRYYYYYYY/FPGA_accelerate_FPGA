#pragma once
#include <cstdint>
namespace search_filter {
// Single edge context. Graph flags/created/has_laguna are stable until DONE.
enum Request : std::uint8_t { DONE=0, CHILD_PREV=1, CHILD_VISITED=2, PARENT_VISITED=3, ARC_PREV=4 };
struct Machine {
    std::int32_t parent,previous= -1;
    std::uint32_t child_sequence=0;
    std::uint8_t flags;
    bool created,has_laguna,excluded=false;
    Request request=DONE;
    Machine(std::int32_t p,std::uint8_t f,bool c,bool lag):parent(p),flags(f),created(c),has_laguna(lag) {
        if(created)request=CHILD_PREV;else ordinary();
    }
    void finish(bool value){excluded=value;request=DONE;}
    void ordinary(){
        if(flags&64u){finish(true);return;}
        if((flags&4u)&&!created&&(!has_laguna||!(flags&8u))){finish(true);return;}
        if(!has_laguna&&(flags&2u)){finish(true);return;}
        if(created&&(flags&32u)){request=ARC_PREV;return;}
        finish(false);
    }
    // Caller returns exactly the requested label value; DONE cannot consume a response.
    bool accept(std::uint32_t value){
        switch(request){
        case CHILD_PREV:
            previous=static_cast<std::int32_t>(value);
            if(previous==-1)ordinary();else request=CHILD_VISITED;
            return true;
        case CHILD_VISITED:child_sequence=value;request=PARENT_VISITED;return true;
        case PARENT_VISITED:
            if(value!=child_sequence && previous==parent && (flags&64u))finish(false);
            else ordinary();
            return true;
        case ARC_PREV:finish(static_cast<std::int32_t>(value)!=parent);return true;
        default:return false;
        }
    }
};
}
