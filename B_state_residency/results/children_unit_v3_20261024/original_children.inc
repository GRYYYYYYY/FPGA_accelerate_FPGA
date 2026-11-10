    const std::vector<int>& getChildren(int id) {
        {   // acquire: batch workers touch the SAME nodes concurrently (no territory disjointness).
            // Sentinel-claim protocol (non-occLocking): first thread CASes a 0x1 sentinel and builds;
            // others spin for the publish instead of building duplicates (16x redundant first-touch
            // builds measured 6.5x iter-1 work in batch mode).
            std::vector<int>* c = __atomic_load_n(&childrenCache[id], __ATOMIC_ACQUIRE);
            if ((uintptr_t) c > 1) return *c;
            if (!occLocking) {
                std::vector<int>* expected = nullptr;
                if (c == (std::vector<int>*) 1 ||
                    !__atomic_compare_exchange_n(&childrenCache[id], &expected, (std::vector<int>*) 1,
                                                 false, __ATOMIC_ACQ_REL, __ATOMIC_ACQUIRE)) {
                    for (;;) {
                        std::vector<int>* p = __atomic_load_n(&childrenCache[id], __ATOMIC_ACQUIRE);
                        if ((uintptr_t) p > 1) return *p;
                        __builtin_ia32_pause();
                    }
                }
            }
        }
        // Lazy (JNI): pull raw allowed-tile adjacency, interning children. Interning may grow the
        // node arrays, so finish ALL interning before index-assigning rawChildrenStore (realloc-safe).
        if (lazy && !rawFetched[id]) {
            // Per-thread fetch buffers: leaf workers fetch concurrently (compact device is read-only).
            static thread_local std::vector<int> tl_fetchPacked, tl_fetchRaw;
            if (tl_wid < 0) {   // timing is main-thread-only (workers skip the clock, not the fetch)
                auto _t0 = std::chrono::steady_clock::now();
                fetchChildrenPacked(keyOf(id), tl_fetchPacked);
                jniDeviceSecs += std::chrono::duration<double>(std::chrono::steady_clock::now() - _t0).count();
                jniDeviceCalls++;
            } else {
                fetchChildrenPacked(keyOf(id), tl_fetchPacked);
            }
            int cnt = tl_fetchPacked.empty() ? 0 : tl_fetchPacked[0];
            tl_fetchRaw.clear();
            internChildrenBatch(tl_fetchPacked, cnt, tl_fetchRaw);   // one lock per fetch, not per child
            rawChildrenStore[id] = tl_fetchRaw;
            rawFetched[id] = 1;
        }
        // Filter (getOrCreate only sets created[]; isExcluded reads attrs — no array growth here).
        std::vector<int>* out = new std::vector<int>();
        // anyAlive: does id have >=1 STRUCTURALLY usable child (not preserved / inaccessible / dead-end)?
        // Computed from static attrs only, so it does not depend on this parent's transient state.
        bool anyAlive = false;
        if (lazy) {
            for (int child : rawChildrenStore[id]) {
                if (pruneDeadEnd && !deadChild(child)) anyAlive = true;
                if (isExcluded(id, child)) continue;
                getOrCreate(child);
                if (type[child] == RouteNodeType::INACCESSIBLE) continue;
                if (pruneDeadEnd && deadEnd[child]) continue;   // GRoute prune: drop known dead-ends
                out->push_back(child);
            }
        } else {
            const NodeStatic& n = ns[id];
            for (int k = 0; k < n.childCount; k++) {
                int child = childIds[n.childStart + k];
                if (pruneDeadEnd && !deadChild(child)) anyAlive = true;
                if (isExcluded(id, child)) continue;
                getOrCreate(child);
                if (type[child] == RouteNodeType::INACCESSIBLE) continue;
                if (pruneDeadEnd && deadEnd[child]) continue;   // GRoute prune: drop known dead-ends
                out->push_back(child);
            }
        }
        // Memoize: if id has no structurally-alive child and cannot itself be a destination, it is a
        // dead-end -> mark it so every future expansion (this/other connections, later iterations) skips
        // it without re-deriving. Monotonic + structural => safe to keep set for the whole route.
        if (pruneDeadEnd && !anyAlive && canBeDeadEnd(id)) deadEnd[id] = 1;
        if (occLocking) {                     // parallel: publish under the node lock (double-checked); the
            lockNode(id);                     // filter above is lock-free and, at first-touch, state-independent
            if (childrenCache[id]) { unlockNode(id); delete out; return *childrenCache[id]; }
            childrenCache[id] = out; unlockNode(id);
        } else {
            // We hold the 0x1 sentinel claim: publish the built list (release) for any spinners.
            __atomic_store_n(&childrenCache[id], out, __ATOMIC_RELEASE);
        }
        return *out;
    }

