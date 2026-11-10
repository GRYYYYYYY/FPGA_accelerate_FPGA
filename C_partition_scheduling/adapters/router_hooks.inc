    // Included inside Router. No policy change unless C_CPU_BUDGET is explicitly enabled.
    void cTraceFinish(ctrace::Attempt& a, int idx, long long budget, long long pops,
                      bool found, bool aborted, bool corridor) {
        auto end = std::chrono::steady_clock::now();
        const auto ns = std::chrono::duration_cast<std::chrono::nanoseconds>(end-a.start).count();
        ctrace::searchNs += ns;
        ctrace::popCount += pops;
        if (aborted) ctrace::discardedNs += ns;
        if (aborted) ++ctrace::aborted;
        if (!a.enabled) return;
        ++ctrace::recorded;
        const auto& c = connections[idx];
        std::ostringstream o;
        o << "{\"record\":\"attempt\",\"attempt_id\":" << a.id
          << ",\"parent_attempt_id\":" << (a.parent ? a.parent->id : 0)
          << ",\"connection_id\":" << c.connId << ",\"connection_index\":" << idx
          << ",\"net_index\":" << c.netIdx << ",\"iteration\":" << routeIteration
          << ",\"worker\":" << tl_wid << ",\"budget_pops\":" << budget
          << ",\"pops\":" << pops << ",\"elapsed_ns\":"
          << std::chrono::duration_cast<std::chrono::nanoseconds>(end-a.start).count()
          << ",\"status\":\"" << (aborted ? "budget_exhausted" : c.routed ? "routed" : "no_path")
          << "\",\"found_target\":" << (found ? "true" : "false")
          << ",\"corridor\":" << (corridor ? "true" : "false")
          << ",\"truncated\":" << (a.truncated ? "true" : "false")
          << ",\"bbox\":[" << c.xMinBB << ',' << c.yMinBB << ',' << c.xMaxBB << ',' << c.yMaxBB << ']';
        auto keys = [&](const char* name, const auto& ids) {
            o << ",\"" << name << "\":["; bool first = true;
            for (int id : ids) { if (!first) o << ','; first = false; o << '"' << keyOf(id) << '"'; }
            o << ']';
        };
        keys("label_access_resources", a.labels);
        keys("label_write_resources", a.writes);
        keys("occupancy_write_resources", a.occupancy);
        keys("path_resources", c.rnodes);
        std::set<int> pages;
        for (int id : a.labels) pages.insert(id / 512);
        o << ",\"dense_label_pages_512\":"; ctrace::numbers(o, pages);
        o << ",\"examined_edges\":["; bool first = true;
        for (auto e : a.edges) {
            if (!first) o << ','; first = false;
            o << "[\"" << keyOf(e.first) << "\",\"" << keyOf(e.second) << "\"]";
        }
        o << "]}"; ctrace::emit(o.str());
    }

    void cTracePartitions() {
        if (!ctrace::output.is_open()) return;
        if (cfg.enlargeBoundingBox) throw std::runtime_error("C audit requires fixed input bboxes");
        ptBuildTree(); ptasks.clear(); ptCollect(0);
        for (size_t i = 0; i < ptasks.size(); ++i) {
            const auto& t = ptasks[i];
            std::ostringstream o;
            o << "{\"record\":\"partition\",\"task_id\":" << i
              << ",\"bbox\":[" << t.ux0 << ',' << t.uy0 << ',' << t.ux1 << ',' << t.uy1
              << "],\"connection_indices\":";
            ctrace::numbers(o, ptree[t.node].conns);
            o << ",\"successors\":"; ctrace::numbers(o, t.out);
            o << '}'; ctrace::emit(o.str());
        }
    }

    void cTraceVerify() {
        if (!ctrace::output.is_open() && ctrace::metricsPath.empty()) return;
        long unrouted = 0, bad = 0, overused = 0;
        std::unordered_map<int, std::set<int>> owners;
        for (const auto& c : connections) {
            if (!c.routed || c.rnodes.empty()) { ++unrouted; continue; }
            bool ok = c.rnodes.back() == c.sourceRnode &&
                (c.rnodes.front() == c.sinkRnode ||
                 std::find(c.altSinks.begin(),c.altSinks.end(),c.rnodes.front()) != c.altSinks.end());
            std::set<int> seen;
            for (size_t j = 0; j < c.rnodes.size(); ++j) {
                int id = c.rnodes[j];
                if (!seen.insert(id).second) ok = false;
                owners[id].insert(c.netIdx);
                if (j + 1 < c.rnodes.size()) {
                    int parent = c.rnodes[j+1];
                    auto begin = childIds.begin() + ns[parent].childStart;
                    if (std::find(begin, begin + ns[parent].childCount, id) == begin + ns[parent].childCount) ok = false;
                }
            }
            if (!ok) ++bad;
        }
        for (const auto& x : owners) if (x.second.size() > CAPACITY) ++overused;
        std::ostringstream o;
        o << "{\"record\":\"verification\",\"connections\":" << connections.size()
          << ",\"unrouted\":" << unrouted << ",\"bad_paths\":" << bad
          << ",\"final_overused_nodes\":" << overused
          << ",\"attempts_total\":" << ctrace::attempts.load()
          << ",\"attempts_recorded\":" << ctrace::recorded.load()
          << ",\"budget_aborts_total\":" << ctrace::aborted.load() << '}';
        if (ctrace::output.is_open()) {
            ctrace::emit(o.str());
            ctrace::output.flush();
            if (!ctrace::output) throw std::runtime_error("trace flush failed");
        }
        if (!ctrace::metricsPath.empty()) {
            std::ofstream metrics(ctrace::metricsPath);
            metrics << "{\"route_ns\":" << ctrace::routeNs
                    << ",\"search_ns\":" << ctrace::searchNs.load()
                    << ",\"discarded_search_ns\":" << ctrace::discardedNs.load()
                    << ",\"pops\":" << ctrace::popCount.load()
                    << ",\"verification\":" << o.str() << "}\n";
            metrics.flush();
            if (!metrics) throw std::runtime_error("metrics write failed");
        }
    }
