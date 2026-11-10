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
        std::vector<int>* out = new std::vector<int>();
        search_children::Machine walk(lazy ? rawChildrenStore[id].size() : ns[id].childCount, pruneDeadEnd);
        while (walk.request != search_children::PUBLISH) {
            bool ok = false; int child = (int)walk.child;
            switch (walk.request) {
            case search_children::NEXT: {
                int next = lazy ? rawChildrenStore[id][walk.position] : childIds[ns[id].childStart + walk.position];
                ok = walk.next(next, pruneDeadEnd && deadChild(next)); break;
            }
            case search_children::EXCLUDE: ok = walk.excluded(isExcluded(id, child)); break;
            case search_children::CREATE: getOrCreate(child); ok = walk.created(); break;
            case search_children::CLASSIFY: {
                bool inaccessible = type[child] == RouteNodeType::INACCESSIBLE;
                ok = walk.classified(inaccessible, !inaccessible && pruneDeadEnd && deadEnd[child]); break;
            }
            case search_children::EMIT: out->push_back(child); ok = walk.emitted(); break;
            case search_children::CHECK_DEAD: ok = walk.can_mark_dead(canBeDeadEnd(id)); break;
            case search_children::MARK_DEAD: deadEnd[id] = 1; ok = walk.marked_dead(); break;
            default: break;
            }
            if (!ok) throw std::runtime_error("invalid first-touch filtering response");
        }
        // The unchanged ownership/publish block below commits this complete list.







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

