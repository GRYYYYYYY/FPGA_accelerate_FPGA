#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <list>
#include <malloc.h>
#include <stdexcept>
#include <unordered_map>
#include <vector>
int rwEnvI(const char* key,int fallback){auto* value=std::getenv(key);return value?std::atoi(value):fallback;}
struct Router {
    struct NodeDyn {       // pure per-connection scratch (+ cross-iteration hist); rewritten every push
        float lb;          // lowerBoundTotalPathCost
        float upstream;    // upstreamPathCost
        float hist;        // historicalCongestionCost (1.0 default)
        int   prev;        // prev node id (-1 default)
        int   visited;     // per-connection sequence guard (0 default)
        uint8_t target;    // isTargetFlag
    };
    struct SparseLabels {
        struct Frame {
            int page = -1;
            size_t pins = 0;
            bool dirty = false;
            std::vector<NodeDyn> values;
            std::list<size_t>::iterator position;
        };
        bool paged = false;
        size_t mask = 0; // compatibility gate; init(hash) explicitly fails closed
        int PBITS = 6, PSIZE = 64;
        uint32_t cur = 1;
        std::vector<uint32_t> pageEp;
        std::vector<int32_t> pageSlot;
        std::vector<Frame> frames;
        std::list<size_t> lru;
        std::unordered_map<int, std::vector<NodeDyn>> backing;
        std::vector<NodeDyn> pool; // empty: legacy batch shrink gate is inert
        uint64_t writebacks = 0, refills = 0, firstPages = 0, resets = 0;
        size_t peakBackingPages = 0;
        void init(size_t) { throw std::runtime_error("Resident labels require paged mode"); }
        void initPaged(size_t nodes, int bits) {
            if (bits < 2 || bits > 12) throw std::runtime_error("Bad resident page size");
            if (paged) throw std::runtime_error("Reinitialization of resident labels is unsupported");
            PBITS = bits; PSIZE = 1 << bits;
            int capacity = rwEnvI("B_RESIDENT_PAGES", 64);
            if (capacity < 2 || capacity > 4096) throw std::runtime_error("Bad frame capacity");
            pageEp.assign((nodes >> bits) + 2, 0);
            pageSlot.assign(pageEp.size(), -1);
            frames.resize(size_t(capacity));
            for (size_t i = 0; i < frames.size(); ++i) {
                frames[i].values.resize(size_t(PSIZE));
                lru.push_back(i);
                frames[i].position = std::prev(lru.end());
            }
            paged = true;
        }
        void reset() {
            for (const auto& frame : frames)
                if (frame.pins) throw std::runtime_error("Query reset with live label reference");
            ++cur; ++resets;
            if (!cur) { std::fill(pageEp.begin(), pageEp.end(), 0); cur = 1; }
            backing.clear();
            for (auto& frame : frames) { frame.page = -1; frame.dirty = false; }
        }
        uint64_t zeroReads = 0;
        bool readIsZero(int id) {
            if (id < 0 || (size_t(id) >> PBITS) >= pageEp.size()) throw std::runtime_error("Bad label node");
            int page = id >> PBITS;
            if (pageEp[size_t(page)] == cur || backing.find(page) != backing.end()) return false;
            ++zeroReads;
            return true;
        }
        size_t acquire(int id, bool write = true) {
            if (id < 0 || (size_t(id) >> PBITS) >= pageEp.size()) throw std::runtime_error("Bad label node");
            int page = id >> PBITS;
            size_t index;
            if (pageEp[size_t(page)] == cur) {
                index = size_t(pageSlot[size_t(page)]);
            } else {
                auto victim = std::find_if(lru.begin(), lru.end(), [&](size_t i) { return frames[i].pins == 0; });
                if (victim == lru.end()) throw std::runtime_error("All frames pinned; no safe eviction");
                index = *victim;
                auto& frame = frames[index];
                if (frame.page >= 0) {
                    if (frame.dirty) {
                        // Complete this copy before unbinding/reusing the frame.
                        backing[frame.page] = frame.values;
                        ++writebacks;
                        peakBackingPages = std::max(peakBackingPages, backing.size());
                    }
                    pageEp[size_t(frame.page)] = 0;
                }
                auto saved = backing.find(page);
                if (saved == backing.end()) {
                    std::fill(frame.values.begin(), frame.values.end(), NodeDyn{});
                    ++firstPages;
                } else {
                    // Copy into fixed-size storage: references never see reallocation.
                    std::copy(saved->second.begin(), saved->second.end(), frame.values.begin());
                    ++refills;
                }
                frame.page = page;
                frame.dirty = false; // new binding starts clean
                pageEp[size_t(page)] = cur;
                pageSlot[size_t(page)] = int32_t(index);
            }
            auto& frame = frames[index];
            lru.splice(lru.end(), lru, frame.position);
            ++frame.pins;
            // Conservative: reference API cannot distinguish reads from writes.
            frame.dirty = frame.dirty || write;
            return index;
        }
        void release(size_t index) {
            if (!frames[index].pins) std::terminate();
            --frames[index].pins;
        }
        void prefetch(int id) const {
            if (id < 0) return;
            size_t page = size_t(id) >> PBITS;
            if (page < pageEp.size() && pageEp[page] == cur)
                __builtin_prefetch(frames[size_t(pageSlot[page])].values.data() + (id & (PSIZE-1)), 1, 3);
        }
        void bAfterPoolShrink() {}
        void bStats(std::ostream& out) const {
            size_t resident = 0, saved = 0;
            for (const auto& f : frames) resident += f.values.capacity()*sizeof(NodeDyn);
            for (const auto& row : backing) saved += row.second.capacity()*sizeof(NodeDyn);
            out << "{\"layout\":\"resident_sync\",\"page_bits\":" << PBITS
                << ",\"physical_pages\":" << frames.size() << ",\"resident_payload_bytes\":" << resident
                << ",\"backing_payload_bytes\":" << saved << ",\"peak_backing_pages\":" << peakBackingPages
                << ",\"page_table_bytes\":" << pageEp.capacity()*4+pageSlot.capacity()*4
                << ",\"writebacks\":" << writebacks << ",\"refills\":" << refills
                << ",\"zero_reads\":" << zeroReads
                << ",\"first_pages\":" << firstPages << ",\"resets\":" << resets << '}';
        }
    };
};
int main(int argc,char** argv){
    Router::SparseLabels labels;labels.initPaged(std::stoull(argv[1]),6);
    size_t payload=0,usablePayload=0,listRequested=0,listUsable=0;
    for(const auto& f:labels.frames){payload+=f.values.capacity()*sizeof(Router::NodeDyn);usablePayload+=malloc_usable_size((void*)f.values.data());}
    for(auto i=labels.lru.begin();i!=labels.lru.end();++i){listRequested+=sizeof(std::_List_node<size_t>);listUsable+=malloc_usable_size(i._M_node);}
    size_t table=labels.pageEp.capacity()*sizeof(uint32_t)+labels.pageSlot.capacity()*sizeof(int32_t);
    size_t frameBytes=labels.frames.capacity()*sizeof(Router::SparseLabels::Frame);
    std::cout<<"{\"object_bytes\":"<<sizeof(labels)<<",\"frame_size\":"<<sizeof(Router::SparseLabels::Frame)<<",\"frame_capacity_bytes\":"<<frameBytes<<",\"resident_payload_bytes\":"<<payload<<",\"page_table_bytes\":"<<table<<",\"list_node_requested_bytes\":"<<listRequested<<",\"list_node_usable_bytes\":"<<listUsable<<",\"known_requested_total_bytes\":"<<sizeof(labels)+frameBytes+payload+table+listRequested<<",\"known_usable_total_bytes\":"<<sizeof(labels)+malloc_usable_size(labels.frames.data())+usablePayload+malloc_usable_size(labels.pageEp.data())+malloc_usable_size(labels.pageSlot.data())+listUsable<<"}\n";
}
