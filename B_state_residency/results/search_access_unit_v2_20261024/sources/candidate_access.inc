#line 1155 "frozen_router.cpp"
    bool graphIsAccessible(int childRnode, int parentRnode, const Connection& c) {
        RouteNodeType t = searchType(childRnode);
        if (!isAnyLocal(t)) {
            switch (t) {
                case RouteNodeType::NON_LOCAL: {
                    RouteNodeType pt = searchType(parentRnode);
                    if (isAnyLocal(pt)) {
                        // LOCAL -> NON_LOCAL : only legal into a Laguna mux (leading-to-laguna parent)
                        bool childLaguna = nodeLaguna(childRnode);
                        if (childLaguna) {
                            int sinkRnode = c.sinkRnode;
                            if (!c.isCrossSLR() || getSLRIndex(childRnode) == getSLRIndex(sinkRnode)) {
                                return false;
                            }
                        }
                        // else CLE output via routethru: not reachable here (lutRoutethru off) -> fall through true
                    } else if (pt == RouteNodeType::SUPER_LONG_LINE &&
                               TLD(parentRnode).prev != -1 && ns[TLD(parentRnode).prev].tileAddr == ns[childRnode].tileAddr) {
                        // UBUMP -> RXD: do not go back the way we came
                        return false;
                    }
                    break;
                }
                case RouteNodeType::NON_LOCAL_LEADING_TO_NORTHBOUND_LAGUNA:
                case RouteNodeType::NON_LOCAL_LEADING_TO_SOUTHBOUND_LAGUNA:
                    break;
                default:
                    break;  // (Versal-only types unreachable on US+)
            }
            return true;
        }

        int sinkRnode = c.sinkRnode;
        int childX = useHotExpand ? hot[childRnode].endX : getEndTileXCoordinate(childRnode);

        // (b) needs to cross an SLR and this is a local node servicing a Laguna
        if (c.isCrossSLR() && isLocalLeadingToLaguna(t) &&
            getSLRIndex(childRnode) != getSLRIndex(sinkRnode)) {
            if ((leadsToNorthboundLaguna(t) && !c.crossSLRnorth) ||
                (leadsToSouthboundLaguna(t) && !c.crossSLRsouth)) {
                return false;
            }
            return true;
        }

        // (c) on the same side as the sink
        bool childSameTile = useHotExpand
            ? (hot[childRnode].tileAddr == hot[sinkRnode].tileAddr)
            : (ns[childRnode].tileAddr == ns[sinkRnode].tileAddr);
        switch (searchType(sinkRnode)) {
            case RouteNodeType::LOCAL_EAST:        // fall-through
            case RouteNodeType::EXCLUSIVE_SINK_EAST:
                if (isWestLocal(t) || t == RouteNodeType::LOCAL_RESERVED) return false;
                break;
            case RouteNodeType::LOCAL_WEST:        // fall-through
            case RouteNodeType::EXCLUSIVE_SINK_WEST:
                if (isEastLocal(t) || t == RouteNodeType::LOCAL_RESERVED) return false;
                break;
            case RouteNodeType::EXCLUSIVE_SINK_BOTH:
                // US+: CTRL sink; only LOCAL_BOTH in the sink tile
                if (!childSameTile) return false;
                if (t != RouteNodeType::LOCAL_BOTH) return false;
                break;
            case RouteNodeType::EXCLUSIVE_SINK_NON_LOCAL:
                if (isAnyLocal(t)) return false;
                break;
            default:
                break;
        }

        // (d) in the sink tile
        if (childSameTile) return true;

        // (e) when in same X as the sink tile, but Y +/- 1
        return childX == getBeginTileXCoordinate(sinkRnode) &&
               std::abs(getEndTileYCoordinate(childRnode) - getBeginTileYCoordinate(sinkRnode)) <= 1;
    }

    bool isAccessible(int child, const Connection& c) const {
        return !cfg.useBoundingBox || searchInBB(child, c);
    }
    bool isAccessibleSink(int child, const Connection& c) const {
        if (TLD(child).target) return true;
        if (searchCountUser(child, c.netIdx) == 0 || !nodePinbounce(child)) return false;
        return true;  // PINBOUNCE exclusive sink of another connection on the same net
    }


#line 1412 "frozen_router.cpp"
    void exploreAndExpand(State& st, int rnode) {
        Connection& c = connections[st.connIdx];
        int seq = st.sequence;
        int nw = c.netIdx;
        bool rnodeIsLaguna = nodeLaguna(rnode);

        const std::vector<int>& kids = getChildren(rnode);
        int nk = (int) kids.size();
        for (int ki = 0; ki < nk; ki++) {
            if (doPrefetch && ki + 1 < nk) {
                int nx = kids[ki + 1];
                __builtin_prefetch(&tl_dyn[nx], 1, 3);   // serial/shadow: the label line; sparse crew: tl_dyn
                                                         // aliases the GLOBAL dyn -> warms the hist read
                if (tl_sparse) tl_sparse->prefetch(nx);  // paged probe-only, never inserts (hash mode: no-op)
                if (useHotExpand) {
                    __builtin_prefetch(&hot[nx], 0, 3);   // one line: type/coords/cost/occ/sharing
                } else {
                    __builtin_prefetch(&ns[nx], 0, 3);
                    __builtin_prefetch(&occCnt[nx], 0, 3);
                    __builtin_prefetch(&type[nx], 0, 3);
                    __builtin_prefetch(&ownerNet[nx], 0, 3);
                    __builtin_prefetch(&ownerCnt[nx], 0, 3);
                }
            }
            int childRNode = kids[ki];
            using namespace search_access;
            search_access::Config ac{uint32_t(seq),uint32_t((pruneDeadEnd?PRUNE:0)|(deadEnd[childRNode]?DEAD:0)|(cfg.useBoundingBox?BB:0)|(c.crossSLRnorth?NORTH:0)|(c.crossSLRsouth?SOUTH:0)|(rnodeIsLaguna?P_LAG:0)|(nodeLaguna(childRNode)?C_LAG:0)|(nodePinbounce(childRNode)?PINBOUNCE:0)|(useHotExpand?HOT:0)),uint32_t(searchType(childRNode)),uint32_t(searchType(rnode)),uint32_t(searchType(c.sinkRnode)),
                useHotExpand?hot[childRNode].endX:getEndTileXCoordinate(childRNode),useHotExpand?hot[childRNode].tileAddr:ns[childRNode].tileAddr,useHotExpand?hot[c.sinkRnode].tileAddr:ns[c.sinkRnode].tileAddr,getBeginTileXCoordinate(c.sinkRnode),getBeginTileYCoordinate(c.sinkRnode),c.xMinBB,c.xMaxBB,c.yMinBB,c.yMaxBB};
            search_access::State as=record_start(ac);
            while(as.phase!=search_access::END){
                uint32_t value=0;
                switch(search_access::request(as)){
                case VISITED:value=uint32_t(bTLD(childRNode,1437).visited);break;
                case TARGET:value=uint32_t(bTLD(childRNode,1440).target);break;
                case BBOX_END_Y:value=uint32_t(searchEndY(childRNode));break;
                case WILL_OVERUSE:value=uint32_t(searchWillOverUse(childRNode,nw));break;
                case SINK_TARGET:value=uint32_t(bTLD(childRNode,1237).target);break;
                case COUNT_USER:value=uint32_t(searchCountUser(childRNode,nw));break;
                case CHILD_SLR:value=uint32_t(getSLRIndex(childRNode));break;
                case SINK_SLR:value=uint32_t(getSLRIndex(c.sinkRnode));break;
                case PARENT_PREV:value=uint32_t(bTLD(rnode,1172).prev);break;
                case PREV_TILE:value=uint32_t(ns[as.aux].tileAddr);break;
                case GRAPH_END_Y:value=uint32_t(getEndTileYCoordinate(childRNode));break;
                default:throw std::runtime_error("invalid access request");
                }
                if(!record_accept(ac,as,value))throw std::runtime_error("invalid access state");
            }
            if(as.bits&PRUNED)prunedPushes++;
            if(as.action==0)continue;
            bool lookahead=as.action==2;
            if(as.bits&IS_TARGET){st.earlyTermination=(as.bits&EARLY)!=0;if(st.earlyTermination)st.queue->clear();}



























            evaluateCostAndPush(st, rnode, childRNode, lookahead);
            if (st.earlyTermination) break;
        }
    }

