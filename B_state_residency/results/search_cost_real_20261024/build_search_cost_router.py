"""Extract pure floating-point stages; preserve geometry, TLD order and source line count."""
def generate(source,header):
    def replace(old,new,count=1):
        nonlocal source
        assert source.count(old)==count,(old,source.count(old))
        assert new.count('\n')<=old.count('\n')
        new+='\n'*(old.count('\n')-new.count('\n'))
        source=source.replace(old,new)
    # Both normal and hot paths retain their own coordinates and present-price lookup.
    old='''        float biasCost = baseCost / nw.connectionsSize * distToCenter / nw.doubleHpwl;
        float nodeCost = baseCost * dyn[id].hist * presentCongestionCost / sharingFactor;   // hist is PERSISTENT: read the global array (batch shadow tl_dyn has no hist)
        return nodeCost + std::min(biasCost, nodeCost / 2);'''
    replace(old,'''        return search_cost::node_cost(baseCost, dyn[id].hist, presentCongestionCost,
                                      sharingFactor, nw.connectionsSize, distToCenter, nw.doubleHpwl);
''',2)
    replace('        float sharingFactor = 1 + st.shareWeight * countSourceUses;',
            '        float sharingFactor = search_cost::sharing_factor(st.shareWeight, countSourceUses);')
    old='''        newPartial += getNodeCostSearch(childRnode, c, countSourceUses, sharingFactor);
        newPartial += st.rnodeWLWeight * (useHotExpand ? hot[childRnode].length : ns[childRnode].length) / sharingFactor;'''
    replace(old,'''        float nodeCost = getNodeCostSearch(childRnode, c, countSourceUses, sharingFactor);
        newPartial = search_cost::partial_cost(newPartial, nodeCost, st.rnodeWLWeight, (useHotExpand ? hot[childRnode].length : ns[childRnode].length), sharingFactor);''')
    a=source.index('        float hBase = st.estWlWeight * (float) distanceToSink;')
    b=source.index('        push(st, childRnode, newPartial, newTotal, lookahead);',a)
    old=source[a:b]
    replace(old,'''        float hBase = search_cost::heuristic(st.estWlWeight, distanceToSink, lmkReady,
            st.lmkT, lmkReady ? &lmk[(size_t)childRnode * 8] : nullptr, lmkInvScale);
        float newTotal = search_cost::total_cost(newPartial, hBase, sharingFactor);
''')
    assert header.count('#include <fstream>')==1
    header=header.replace('#include <fstream>','#include <fstream>\n#include "search_cost.hpp"')
    return source,header
