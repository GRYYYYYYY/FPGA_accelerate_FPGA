#pragma once
#include <vector>
#include <cstdint>
#include <cstring>
namespace golden {
    struct DaryPQ {
        struct E { float lb; int id; };
        std::vector<E>& h;              // reused backing storage (shared across connections)
        int sz = 0;
        int D;                          // arity (>= 2)
        DaryPQ(std::vector<E>& storage, int arity) : h(storage), D(arity) { sz = 0; }
        inline bool empty() const { return sz == 0; }
        inline void clear() { sz = 0; }
        inline void offer(float lb, int id) {            // sift-up
            int k = sz;
            if ((int) h.size() <= k) h.resize((size_t) k + 1);
            while (k > 0) { int parent = (k - 1) / D;
                if (h[parent].lb <= lb) break; h[k] = h[parent]; k = parent; }
            h[k].lb = lb; h[k].id = id; sz++;
        }
        inline int poll() {                              // pop-min + sift-down
            int result = h[0].id;
            int s = --sz;
            if (s != 0) { float xlb = h[s].lb; int xid = h[s].id; int k = 0;
                for (;;) {
                    int first = k * D + 1; if (first >= sz) break;
                    int best = first; float blb = h[first].lb;
                    int end = first + D; if (end > sz) end = sz;
                    for (int cc = first + 1; cc < end; cc++) if (h[cc].lb < blb) { blb = h[cc].lb; best = cc; }
                    if (xlb <= blb) break; h[k] = h[best]; k = best; }
                h[k].lb = xlb; h[k].id = xid; }
            return result;
        }
    };

inline float as_float(std::uint32_t b){float x;std::memcpy(&x,&b,4);return x;}
inline std::uint32_t as_bits(float x){std::uint32_t b;std::memcpy(&b,&x,4);return b;}
}
