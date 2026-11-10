"""Replace first-touch filtering only; retain cache ownership, lazy fetch and publish."""

def filter_span(source):
    start = source.index('        // Filter (getOrCreate only sets created[];')
    end = source.index('        if (occLocking) {', start)
    return start, end


def generate(source, header):
    start, end = filter_span(source)
    original = source[start:end]
    new = '''        std::vector<int>* out = new std::vector<int>();
        search_children::Machine walk(lazy ? rawChildrenStore[id].size() : ns[id].childCount, pruneDeadEnd);
        while (walk.request != search_children::PUBLISH) {
            bool ok = false; int child = (int)walk.child;
            switch (walk.request) {
            case search_children::NEXT: {
                int next = lazy ? rawChildrenStore[id][walk.position] : childIds[ns[id].childStart + walk.position];
                ok = walk.next(next, pruneDeadEnd && deadChild(next)); break;
            }
            case search_children::EXCLUDE: ok = walk.excluded(isExcluded(id, child)); break;
            case search_children::CREATE: getOrCreate(child); ok = walk.created(); break;
            case search_children::CLASSIFY: {
                bool inaccessible = type[child] == RouteNodeType::INACCESSIBLE;
                ok = walk.classified(inaccessible, !inaccessible && pruneDeadEnd && deadEnd[child]); break;
            }
            case search_children::EMIT: out->push_back(child); ok = walk.emitted(); break;
            case search_children::CHECK_DEAD: ok = walk.can_mark_dead(canBeDeadEnd(id)); break;
            case search_children::MARK_DEAD: deadEnd[id] = 1; ok = walk.marked_dead(); break;
            default: break;
            }
            if (!ok) throw std::runtime_error("invalid first-touch filtering response");
        }
        // The unchanged ownership/publish block below commits this complete list.
'''
    assert new.count('\n') <= original.count('\n')
    new += '\n' * (original.count('\n') - new.count('\n'))
    source = source[:start] + new + source[end:]
    assert header.count('#include <fstream>') == 1
    header = header.replace('#include <fstream>', '#include <fstream>\n#include "children_machine.hpp"')
    return source, header
