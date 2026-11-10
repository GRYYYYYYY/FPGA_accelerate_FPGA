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
