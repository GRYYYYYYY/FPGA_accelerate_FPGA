"""Replace isExcluded only; preserve conditional label order and trace source locations."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def generate(source,header):
 start=source.index('    bool isExcluded(int parent, int child) {')
 end=source.index('    // ----------------------------------------------------------------- getChildren',start)
 original=source[start:end]
 def line(fragment):
  assert source.count(fragment)==1,fragment
  return source[:source.index(fragment)].count('\n')+1
 previous=line('int p = TLD(endR).prev;')
 visited=line('if (TLD(endR).visited == TLD(parent).visited)')
 arc=line('if (childRnode != -1 && ns[childRnode].arcLockedInit && TLD(childRnode).prev != parent)')
 new=f'''    bool isExcluded(int parent, int child) {{
        const auto& a=ns[child];
        const uint8_t flags=(a.preserved?64:0)|(a.isPinfeed?4:0)|(a.pinfeedLeadsToLaguna?8:0)|(a.isLaguna?2:0)|(a.arcLockedInit?32:0);
        search_filter::Machine machine(parent,flags,getNode(child)!=-1,hasLaguna);
        while(machine.request!=search_filter::DONE) {{
            uint32_t value=0;
            switch(machine.request) {{
            case search_filter::CHILD_PREV:value=(uint32_t)bTLD(child,{previous}).prev;break;
            case search_filter::CHILD_VISITED:value=(uint32_t)bTLD(child,{visited}).visited;break;
            case search_filter::PARENT_VISITED:value=(uint32_t)bTLD(parent,{visited}).visited;break;
            case search_filter::ARC_PREV:value=(uint32_t)bTLD(child,{arc}).prev;break;
            default:throw std::runtime_error("invalid exclusion request");
            }}
            machine.accept(value);
        }}
        return machine.excluded;
    }}

'''
 assert new.count('\n')<=original.count('\n')
 new+='\n'*(original.count('\n')-new.count('\n'))
 source=source[:start]+new+source[end:]
 assert header.count('#include <fstream>')==1
 header=header.replace('#include <fstream>','#include <fstream>\n#include "exclusion_machine.hpp"')
 return source,header
