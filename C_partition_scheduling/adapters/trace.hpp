#pragma once
// Diagnostic instrumentation only; IDs are converted to upstream canonical keys on output.
#include <fstream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <cstdlib>
namespace ctrace {
inline std::ofstream output;
inline std::mutex mutex;
inline std::atomic<long long> attempts{0}, recorded{0}, aborted{0};
// Lightweight serial accounting works with footprint collection disabled.
inline std::atomic<long long> searchNs{0}, discardedNs{0}, popCount{0};
inline long long routeNs = 0;
inline std::string metricsPath;
inline long long limit = 2000, cap = 200000;
struct Attempt;
inline thread_local Attempt* active = nullptr;
inline void emit(const std::string& s) {
    std::lock_guard<std::mutex> lock(mutex);
    output << s << '\n';
    if (!output) throw std::runtime_error("trace write failed");
}
template<class Range> void numbers(std::ostream& o, const Range& r) {
    o << '['; bool first = true;
    for (auto x : r) { if (!first) o << ','; first = false; o << x; }
    o << ']';
}
struct Attempt {
    Attempt* parent;
    long long id;
    bool enabled, truncated = false;
    std::set<int> labels, writes, occupancy;
    std::set<std::pair<int,int>> edges;
    std::chrono::steady_clock::time_point start;
    Attempt() : parent(active), id(++attempts), enabled(output.is_open() && id <= limit) {
        active = this;
        start = std::chrono::steady_clock::now();
    }
    ~Attempt() { active = parent; }
    void add(std::set<int>& s, int id) {
        if (!enabled) return;
        if ((long long)s.size() < cap || s.count(id)) s.insert(id);
        else truncated = true;
    }
    void edge(int a, int b) {
        if (!enabled) return;
        if ((long long)edges.size() < cap || edges.count({a,b})) edges.insert({a,b});
        else truncated = true;
    }
};
inline void label(int id) { if (active) active->add(active->labels, id); }
inline void write(int id) { if (active) active->add(active->writes, id); }
inline void occ(int id) { if (active) active->add(active->occupancy, id); }
inline void edge(int a, int b) { if (active) active->edge(a,b); }
}
