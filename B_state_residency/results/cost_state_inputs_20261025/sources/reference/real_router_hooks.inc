    void bTraceFinish(const btrace::Attempt& a, int idx, long long pops, bool aborted) {
        if (!btrace::metadata.is_open()) return;
        const auto& c = connections[idx];
        auto& out = btrace::metadata;
        out << "{\"record\":\"attempt\",\"attempt\":" << a.id << ",\"iteration\":" << routeIteration
            << ",\"connection_index\":" << idx << ",\"connection_id\":" << c.connId
            << ",\"net_index\":" << c.netIdx << ",\"fanout\":" << nets[c.netIdx].connectionsSize
            << ",\"pops\":" << pops << ",\"label_accesses\":" << a.count
            << ",\"routed\":" << (c.routed?"true":"false") << ",\"aborted\":" << (aborted?"true":"false")
            << ",\"accesses_selected\":" << (a.enabled?"true":"false")
            << ",\"truncated\":" << (a.enabled && a.events.size()<a.count?"true":"false")
            << ",\"access_byte_offset\":" << btrace::byteOffset
            << ",\"access_count\":" << a.events.size() << ",\"previous_path\":[";
        for (size_t i=0;i<a.previousPath.size();++i) { if(i) out<<','; out<<a.previousPath[i]; }
        out << "],\"path\":[";
        for (size_t i=0;i<c.rnodes.size();++i) { if(i) out<<','; out<<c.rnodes[i]; }
        out << "]}\n";
        if (!a.events.empty()) {
            size_t bytes = a.events.size()*sizeof(btrace::Access);
            btrace::accesses.write(reinterpret_cast<const char*>(a.events.data()), bytes);
            btrace::byteOffset += bytes;
        }
        if (!out || !btrace::accesses) throw std::runtime_error("trace write failed");
    }
