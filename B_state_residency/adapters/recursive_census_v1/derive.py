"""Observer-only source transformation; original route/search bodies retained."""
def derive(s):
 changes=[]
 def replace(a,b):
  nonlocal s
  assert s.count(a)==1,a;s=s.replace(a,b,1);changes.append((a,b))
 replace('namespace rw =','#include "recursive_census.hpp"\nnamespace rw =')
 replace('    void routeIndirectConnection(int connIdx, long long budget = -1) {\n        Connection& c = connections[connIdx];','''    void routeIndirectConnection(int connIdx, long long budget = -1) {
        Connection& c = connections[connIdx];
        recensus::Attempt rc_attempt(routeIteration,connIdx,c.connId,c.netIdx,c.sourceRnode,c.sinkRnode,nets[c.netIdx].connectionsSize,(c.crossSLRnorth?8:0)|(c.crossSLRsouth?16:0),presentCongestionFactor,lmkReady,&c.routed,&c.rnodes);''')
 replace('        tl_pushes++;','        recensus::pushed(lookahead,child);\n        tl_pushes++;')
 # Match expansion region only, preserving the exact ordered getChildren call.
 a=s.index('    void exploreAndExpand(State& st, int rnode) {');b=s.index('    // ----------------------------------------------------------------- rip up / save',a)
 old=s[a:b];new=old.replace('        int nk = (int) kids.size();','        int nk = (int) kids.size();\n        recensus::Frame rc_frame(rnode,nk,ns[rnode].childCount);',1).replace('        for (int ki = 0; ki < nk; ki++) {','        for (int ki = 0; ki < nk; ki++) {\n            rc_frame.position=ki;',1)
 replace(old,new)
 replace('        prepareRouteConnection(st);','''        prepareRouteConnection(st);
        rc_attempt.sequence=st.sequence;rc_attempt.share=recensus::bits(st.shareWeight);rc_attempt.wire=recensus::bits(st.rnodeWLWeight);rc_attempt.estimate=recensus::bits(st.estWlWeight);rc_attempt.initial_queue=queue.sz;rc_attempt.targets=st.targets.size();''')
 replace('        lastPops = pops; lastFoundLb = foundLb;', '        rc_attempt.pops=pops;rc_attempt.found=found;rc_attempt.aborted=aborted;\n        lastPops = pops; lastFoundLb = foundLb;')
 replace('    Router router;\n    router.load(argv[1]);','    recensus::init();\n    Router router;\n    router.load(argv[1]);')
 replace('    auto t3 = clk::now();','    recensus::finish();\n    auto t3 = clk::now();')
 return s,changes
