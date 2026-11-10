"""Observe all scalar-stage packets without changing TLD source-line identity."""
def generate(source,header):
    signature='    void evaluateCostAndPush(State& st, int rnode, int childRnode, bool lookahead) {'
    assert source.count(signature)==1 and source.count('search_cost::')==6
    source=source.replace('search_cost::','cost_observe::')
    source=source.replace(signature,signature+' cost_observe::begin(routeIteration, st.connIdx, rnode, childRnode);')
    assert header.count('#include <fstream>')==1
    header=header.replace('#include <fstream>','#include <fstream>\n#include "cost_observe.hpp"')
    return source,header
