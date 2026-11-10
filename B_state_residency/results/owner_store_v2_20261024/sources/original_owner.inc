    inline int countUserSlot(int id, int nw) const {
        int o = ownerNet[id];
        if (o == nw) return ownerCnt[id];
        auto* ov = userOverflow[id];
        if (!ov) return 0;
        auto it = ov->find(nw);
        return it == ov->end() ? 0 : it->second;
    }
    inline void promoteOverflowOwner(int id) {
        auto* ov = userOverflow[id];
        if (!ov || ov->empty()) return;
        auto it = ov->begin();
        ownerNet[id] = it->first;
        ownerCnt[id] = (uint16_t) it->second;
        ov->erase(it);
        if (ov->empty()) { delete ov; userOverflow[id] = nullptr; }
    }

    inline void syncHotOcc(int id) {
        HotExpand& h = hot[id];
        h.ownerNet = ownerNet[id];
        h.ownerCnt = ownerCnt[id];
        h.occCnt = (uint8_t) std::min(255, (int) occCnt[id]);
    }

    inline void incUserSlot(int id, int nw) {
        int& on = ownerNet[id];
        if (on < 0) {
            on = nw; ownerCnt[id] = 1;
            occCnt[id]++; if (trackDirty) markDirty(id);
        } else if (on == nw) {
            ownerCnt[id]++;
        } else {
            auto*& ov = userOverflow[id];
            if (!ov) ov = new std::unordered_map<int,int>();
            int& c = (*ov)[nw];
            if (c == 0) { occCnt[id]++; if (trackDirty) markDirty(id); }
            c++;
        }
        syncHotOcc(id);
    }
    inline void decUserSlot(int id, int nw) {
        if (ownerNet[id] == nw) {
            if (--ownerCnt[id] == 0) {
                ownerNet[id] = -1;
                occCnt[id]--; if (trackDirty) markDirty(id);
                promoteOverflowOwner(id);
            }
        } else {
            auto* ov = userOverflow[id];
            auto it = ov->find(nw);
            if (it->second == 1) {
                ov->erase(it);
                occCnt[id]--; if (trackDirty) markDirty(id);
                if (ov->empty()) { delete ov; userOverflow[id] = nullptr; }
            } else it->second--;
        }
        syncHotOcc(id);
    }
