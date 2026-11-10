#pragma once
#include <cstdint>

namespace search_children {
// One exclusive first-touch cache build. Storage/labels/exclusion are services.
// A cache hit bypasses this machine. Publishing an empty list is still a hit.
enum Request : std::uint8_t {
    NEXT=0, EXCLUDE=1, CREATE=2, CLASSIFY=3, EMIT=4,
    CHECK_DEAD=5, MARK_DEAD=6, PUBLISH=7, DONE=8
};
struct Machine {
    std::uint32_t count, position=0, child=0;
    bool prune, any_alive=false;
    Request request;
    Machine(std::uint32_t n, bool p):count(n),prune(p),request(n?NEXT:(p?CHECK_DEAD:PUBLISH)) {}
    void advance() {
        ++position;
        request=position<count?NEXT:(prune&&!any_alive?CHECK_DEAD:PUBLISH);
    }
    bool next(std::uint32_t node, bool structural_dead) {
        if(request!=NEXT || node>=0x1000000u)return false;
        child=node;
        if(prune&&!structural_dead)any_alive=true;
        request=EXCLUDE;return true;
    }
    bool excluded(bool value) {
        if(request!=EXCLUDE)return false;
        if(value)advance();else request=CREATE;
        return true;
    }
    bool created() {
        if(request!=CREATE)return false;
        request=CLASSIFY;return true;
    }
    bool classified(bool inaccessible, bool known_dead) {
        if(request!=CLASSIFY)return false;
        if(inaccessible || (prune&&known_dead))advance();else request=EMIT;
        return true;
    }
    bool emitted() {
        if(request!=EMIT)return false;
        advance();return true;
    }
    bool can_mark_dead(bool value) {
        if(request!=CHECK_DEAD)return false;
        request=value?MARK_DEAD:PUBLISH;return true;
    }
    bool marked_dead() {
        if(request!=MARK_DEAD)return false;
        request=PUBLISH;return true;
    }
    bool published() {
        if(request!=PUBLISH)return false;
        request=DONE;return true;
    }
};
}
