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
            if (TLD(childRNode).visited == seq) continue;
            if (pruneDeadEnd && deadEnd[childRNode]) { prunedPushes++; continue; }
            bool lookahead = false;
            if (TLD(childRNode).target) {
                if (isAnyExclusiveSink(searchType(childRNode))) {
                    st.earlyTermination = true;
                } else {
                    st.earlyTermination = !searchWillOverUse(childRNode, nw);
                }
                if (st.earlyTermination) {
                    st.queue->clear();
                }
            } else {
                if (!isAccessible(childRNode, c)) continue;
                RouteNodeType childType = searchType(childRNode);
                switch (childType) {
                    case RouteNodeType::LOCAL_EAST_LEADING_TO_NORTHBOUND_LAGUNA:
                    case RouteNodeType::LOCAL_EAST_LEADING_TO_SOUTHBOUND_LAGUNA:
                    case RouteNodeType::LOCAL_WEST_LEADING_TO_NORTHBOUND_LAGUNA:
                    case RouteNodeType::LOCAL_WEST_LEADING_TO_SOUTHBOUND_LAGUNA:
                        lookahead = !searchWillOverUse(childRNode, nw);
                        // fall-through
                    case RouteNodeType::LOCAL_BOTH:
                    case RouteNodeType::LOCAL_EAST:
                    case RouteNodeType::LOCAL_WEST:
                    case RouteNodeType::LOCAL_RESERVED:
                        if (!graphIsAccessible(childRNode, rnode, c)) continue;
                        break;
                    case RouteNodeType::NON_LOCAL_LEADING_TO_NORTHBOUND_LAGUNA:
                    case RouteNodeType::NON_LOCAL_LEADING_TO_SOUTHBOUND_LAGUNA:
                        if (c.isCrossSLR() && getSLRIndex(c.sinkRnode) != getSLRIndex(childRNode) &&
                            ((c.crossSLRnorth && childType == RouteNodeType::NON_LOCAL_LEADING_TO_NORTHBOUND_LAGUNA) ||
                             (c.crossSLRsouth && childType == RouteNodeType::NON_LOCAL_LEADING_TO_SOUTHBOUND_LAGUNA))) {
                            lookahead = !searchWillOverUse(childRNode, nw);
                        }
                        // fall-through
                    case RouteNodeType::NON_LOCAL:
                        if (!graphIsAccessible(childRNode, rnode, c)) continue;
                        if (!cfg.useUTurnNodes /* && delay>10000 (delay==0) */) { /* never triggers */ }
                        lookahead = lookahead || (rnodeIsLaguna || nodeLaguna(childRNode));
                        break;
                    case RouteNodeType::EXCLUSIVE_SINK_BOTH:
                    case RouteNodeType::EXCLUSIVE_SINK_EAST:
                    case RouteNodeType::EXCLUSIVE_SINK_WEST:
                    case RouteNodeType::EXCLUSIVE_SINK_NON_LOCAL:
                        if (!isAccessibleSink(childRNode, c)) continue;
                        break;
                    case RouteNodeType::SUPER_LONG_LINE:
                        break;
                    default:
                        break;
                }
            }
            evaluateCostAndPush(st, rnode, childRNode, lookahead);
            if (st.earlyTermination) break;
        }
    }

