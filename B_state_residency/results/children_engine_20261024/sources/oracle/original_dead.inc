    inline bool canBeDeadEnd(int id) const {
        if (isSinkNode[id]) return false;
        if (isAnyExclusiveSink(type[id])) return false;
        const NodeStatic& a = ns[id];
        return !(a.isPinfeed || a.isPinbounce || a.isLaguna || a.pinfeedLeadsToLaguna);
    }
    // Is `child` STRUCTURALLY incapable of contributing to any usable path (so a parent whose children
    // are ALL such is itself a dead-end)? Static attrs only: preserved (reserved for another net),
    // INACCESSIBLE, already-dead, or an EXCLUSIVE_SINK pin that no connection actually targets (GRoute's
    // "dead-end at an unused site pin"). Pass-throughs and real/pinbounce/laguna access nodes stay alive.
    inline bool deadChild(int child) const {
        if (ns[child].preserved || deadEnd[child]) return true;
        RouteNodeType t = type[child];
        if (t == RouteNodeType::INACCESSIBLE) return true;
        if (isAnyExclusiveSink(t) && !isSinkNode[child]) return true;
        return false;
    }

