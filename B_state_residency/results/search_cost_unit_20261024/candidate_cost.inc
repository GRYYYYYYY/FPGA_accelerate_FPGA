    float getNodeCostSearch(int id, const Connection& c, int countSameSourceUsers, float sharingFactor) const {
        if (occLocking || !useHotExpand) return getNodeCost(id, c, countSameSourceUsers, sharingFactor);
        const HotExpand& h = hot[id];
        int occ = h.occCnt;
        float presentCongestionCost = countSameSourceUsers
            ? presentCongestionCosts[occ > 0 ? occ - 1 : 0]
            : presentCongestionCosts[occ];
        float baseCost = h.baseCost;
        const NetWrapper& nw = nets[c.netIdx];
        int ey = searchEndY(id);
        float distToCenter = std::abs(h.endX - nw.xCenter) + std::abs(ey - nw.yCenter);
        return search_cost::node_cost(baseCost, dyn[id].hist, presentCongestionCost,
                                      sharingFactor, nw.connectionsSize, distToCenter, nw.doubleHpwl);

    }

    float getNodeCost(int id, const Connection& c, int countSameSourceUsers, float sharingFactor) const {
        bool hasSame = (countSameSourceUsers != 0);
        float presentCongestionCost;
        if (hasSame) {
            int occWithout = getOccupancy(id) - 1;
            presentCongestionCost = getPresentCongestionCost(occWithout);
        } else {
            presentCongestionCost = getPresentCongestionCostOf(id);
        }
        float baseCost = ns[id].baseCost;
        const NetWrapper& nw = nets[c.netIdx];
        float distToCenter = std::abs(getEndTileXCoordinate(id) - nw.xCenter) +
                             std::abs(getEndTileYCoordinate(id) - nw.yCenter);
        return search_cost::node_cost(baseCost, dyn[id].hist, presentCongestionCost,
                                      sharingFactor, nw.connectionsSize, distToCenter, nw.doubleHpwl);

    }


    void evaluateCostAndPush(State& st, int rnode, int childRnode, bool lookahead) {
        Connection& c = connections[st.connIdx];
        int countSourceUses = searchCountUser(childRnode, c.netIdx);
        float sharingFactor = search_cost::sharing_factor(st.shareWeight, countSourceUses);
        TLD(childRnode).prev = rnode;

        float newPartial = TLD(rnode).upstream;
        float nodeCost = getNodeCostSearch(childRnode, c, countSourceUses, sharingFactor);
        newPartial = search_cost::partial_cost(newPartial, nodeCost, st.rnodeWLWeight, (useHotExpand ? hot[childRnode].length : ns[childRnode].length), sharingFactor);

        int childX = useHotExpand ? hot[childRnode].endX : getEndTileXCoordinate(childRnode);
        int childY = searchEndY(childRnode);
        int sinkRnode = c.sinkRnode;
        int sinkX = getBeginTileXCoordinate(sinkRnode);
        int sinkY = getBeginTileYCoordinate(sinkRnode);
        int deltaX = std::abs(childX - sinkX);
        int deltaY = std::abs(childY - sinkY);
        if (c.isCrossSLR()) {
            int deltaSLR = std::abs(getSLRIndex(sinkRnode) - getSLRIndex(childRnode));
            if (deltaSLR != 0) {
                if (deltaSLR == 1) {
                    int overshootByY = deltaY - superLongLineLength;
                    if (overshootByY < 0) deltaY = superLongLineLength - overshootByY;
                }
                int nextLag = nextLagunaColumn[childX];
                int prevLag = prevLagunaColumn[childX];
                if (nextLag == prevLag) {
                    // on top of the column
                } else {
                    const int IMAX = std::numeric_limits<int>::max();
                    const int IMIN = std::numeric_limits<int>::min();
                    int dToNext, dToPrev, dAndFromNext, dAndFromPrev;
                    if (nextLag == IMAX || nextLag >= c.xMaxBB) { dToNext = IMAX; dAndFromNext = IMAX; }
                    else { dToNext = std::abs(nextLag - childX); dAndFromNext = dToNext + std::abs(sinkX - nextLag); }
                    if (prevLag == IMIN || prevLag <= c.xMinBB) { dToPrev = IMAX; dAndFromPrev = IMAX; }
                    else { dToPrev = std::abs(prevLag - childX); dAndFromPrev = dToPrev + std::abs(sinkX - prevLag); }
                    int det = cfg.maxDetourToSnapBackToPrevLagunaColumn;
                    if (dToNext == dToPrev) deltaX = std::min(dAndFromNext, dAndFromPrev);
                    else if (dToNext < dToPrev && dAndFromNext <= dAndFromPrev + det) deltaX = dAndFromNext;
                    else if (dToPrev < dToNext && dAndFromPrev <= dAndFromNext + det) deltaX = dAndFromPrev;
                    else deltaX = (dToNext < dToPrev) ? dAndFromNext : dAndFromPrev;
                }
            }
        }
        int distanceToSink = deltaX + deltaY;
        float hBase = search_cost::heuristic(st.estWlWeight, distanceToSink, lmkReady,
            st.lmkT, lmkReady ? &lmk[(size_t)childRnode * 8] : nullptr, lmkInvScale);
        float newTotal = search_cost::total_cost(newPartial, hBase, sharingFactor);






        push(st, childRnode, newPartial, newTotal, lookahead);
    }

