"""Pure observation of the first prepared natural query; reversible replacements."""
def derive(s):
 changes=[]
 def rep(a,b):
  nonlocal s
  assert s.count(a)==1,a
  s=s.replace(a,b,1);changes.append((a,b))
 rep('namespace rw =','#include "natural_query.hpp"\nnamespace rw =')
 rep('        tl_pushes++;','        nqs::pushed(*this,st,child,lookahead);\n        tl_pushes++;')
 rep('        int nk = (int) kids.size();','        nqs::expand(*this,st,rnode,kids);\n        int nk = (int) kids.size();')
 rep('            int childRNode = kids[ki];','            int childRNode = kids[ki];\n            nqs::candidate(*this,st,rnode,childRNode,ki);')
 rep('        prepareRouteConnection(st);','        prepareRouteConnection(st);\n        nqs::begin(*this,st);')
 rep('        while (!queue.empty()) {\n            rnode = queue.poll();\n            pops++;','        while (!queue.empty()) {\n            rnode = queue.poll();\n            nqs::poll(*this,st,rnode);\n            pops++;')
 rep('        lastPops = pops; lastFoundLb = foundLb;','        nqs::end(*this,st,pops,found,aborted);\n        lastPops = pops; lastFoundLb = foundLb;')
 return s,changes
