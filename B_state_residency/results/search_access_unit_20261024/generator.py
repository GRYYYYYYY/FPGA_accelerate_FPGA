"""Per-child decision state machine with original dynamic read sequence and source lines."""
def generate(source,header):
 def line(fragment):
  assert source.count(fragment)==1,fragment
  return source[:source.index(fragment)].count('\n')+1
 visited=line('            if (TLD(childRNode).visited == seq) continue;')
 target=line('            if (TLD(childRNode).target) {')
 sink_target=line('        if (TLD(child).target) return true;')
 prev=line('                               TLD(parentRnode).prev != -1 && ns[TLD(parentRnode).prev].tileAddr == ns[childRnode].tileAddr) {')
 a=source.index('            if (TLD(childRNode).visited == seq) continue;')
 b=source.index('            evaluateCostAndPush(st, rnode, childRNode, lookahead);',a)
 old=source[a:b]
 new=f'''            using namespace search_access;
            Config ac{{uint32_t(seq),uint32_t((pruneDeadEnd?PRUNE:0)|(deadEnd[childRNode]?DEAD:0)|(cfg.useBoundingBox?BB:0)|(c.crossSLRnorth?NORTH:0)|(c.crossSLRsouth?SOUTH:0)|(rnodeIsLaguna?P_LAG:0)|(nodeLaguna(childRNode)?C_LAG:0)|(nodePinbounce(childRNode)?PINBOUNCE:0)|(useHotExpand?HOT:0)),uint32_t(searchType(childRNode)),uint32_t(searchType(rnode)),uint32_t(searchType(c.sinkRnode)),
                useHotExpand?hot[childRNode].endX:getEndTileXCoordinate(childRNode),useHotExpand?hot[childRNode].tileAddr:ns[childRNode].tileAddr,useHotExpand?hot[c.sinkRnode].tileAddr:ns[c.sinkRnode].tileAddr,getBeginTileXCoordinate(c.sinkRnode),getBeginTileYCoordinate(c.sinkRnode),c.xMinBB,c.xMaxBB,c.yMinBB,c.yMaxBB}};
            search_access::State as=search_access::start();
            while(as.phase!=search_access::END){{
                uint32_t value=0;
                switch(search_access::request(as)){{
                case VISITED:value=uint32_t(bTLD(childRNode,{visited}).visited);break;
                case TARGET:value=uint32_t(bTLD(childRNode,{target}).target);break;
                case BBOX_END_Y:value=uint32_t(searchEndY(childRNode));break;
                case WILL_OVERUSE:value=uint32_t(searchWillOverUse(childRNode,nw));break;
                case SINK_TARGET:value=uint32_t(bTLD(childRNode,{sink_target}).target);break;
                case COUNT_USER:value=uint32_t(searchCountUser(childRNode,nw));break;
                case CHILD_SLR:value=uint32_t(getSLRIndex(childRNode));break;
                case SINK_SLR:value=uint32_t(getSLRIndex(c.sinkRnode));break;
                case PARENT_PREV:value=uint32_t(bTLD(rnode,{prev}).prev);break;
                case PREV_TILE:value=uint32_t(ns[as.aux].tileAddr);break;
                case GRAPH_END_Y:value=uint32_t(getEndTileYCoordinate(childRNode));break;
                default:throw std::runtime_error("invalid access request");
                }}
                if(!search_access::accept(ac,as,value))throw std::runtime_error("invalid access state");
            }}
            if(as.bits&PRUNED)prunedPushes++;
            if(as.action==0)continue;
            bool lookahead=as.action==2;
            if(as.bits&IS_TARGET){{st.earlyTermination=(as.bits&EARLY)!=0;if(st.earlyTermination)st.queue->clear();}}
'''
 # Avoid colliding with Router::Config and Router::State.
 new=new.replace('            Config ac{','            search_access::Config ac{')
 assert new.count('\n')<=old.count('\n')
 new+='\n'*(old.count('\n')-new.count('\n'));source=source[:a]+new+source[b:]
 assert header.count('#include <fstream>')==1
 header=header.replace('#include <fstream>','#include <fstream>\n#include "access_machine.hpp"')
 return source,header
