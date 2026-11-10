#line 731 "frozen_router.cpp"
    int searchEndY(int id) const {
        if (!useHotExpand) return getEndTileYCoordinate(id);
        const HotExpand& h = hot[id];
        if (h.type == (uint8_t) RouteNodeType::SUPER_LONG_LINE) {
            int p = TLD(id).prev;
            if (p != -1 && ns[p].endY == h.endY) return h.beginY;
        }
        return h.endY;
    }
    bool searchInBB(int id, const Connection& c) const {
        if (!useHotExpand) return isInConnectionBoundingBox(id, c);
        const HotExpand& h = hot[id];
        int ey = searchEndY(id);
        return h.endX > c.xMinBB && h.endX < c.xMaxBB && ey > c.yMinBB && ey < c.yMaxBB;
    }

#line 1025 "frozen_router.cpp"
    int getEndTileYCoordinate(int id) const {
        if (type[id] == RouteNodeType::SUPER_LONG_LINE) {
            int p = TLD(id).prev;
            if (p != -1 && ns[p].endY == ns[id].endY) return ns[id].beginY;
        }
        return ns[id].endY;
    }
    int getEndTileXCoordinate(int id) const { return ns[id].endX; }
    int getBeginTileXCoordinate(int id) const { return ns[id].beginX; }
    int getBeginTileYCoordinate(int id) const { return ns[id].beginY; }
    int getSLRIndex(int id) const { return slrTable[getEndTileYCoordinate(id)]; }

    bool isInConnectionBoundingBox(int id, const Connection& c) const {
        int ex = ns[id].endX, ey = getEndTileYCoordinate(id);
        return ex > c.xMinBB && ex < c.xMaxBB && ey > c.yMinBB && ey < c.yMaxBB;
    }


