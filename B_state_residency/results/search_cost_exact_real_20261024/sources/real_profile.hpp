#pragma once
#include <array>
#include <chrono>
#include <csignal>
#include <fstream>
#include <iomanip>
#include <map>
#include <sys/time.h>
#include <ucontext.h>
#include <pthread.h>

// Single-thread CPU profiling. Signal sampling needs no perf_event permissions.
namespace bprof {
using Clock = std::chrono::steady_clock;
inline uint64_t ns(Clock::time_point start) {
    return uint64_t(std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now()-start).count());
}
enum Phase { INIT_LABELS, INIT_STATE, RIP, COMMIT, BACKTRACE, TARGET_SET, TARGET_CLEAR, UPDATE_COST, PHASES };
inline const char* names[] = {"label_initial_allocation", "mutable_state_initialization", "rip_up", "commit",
    "path_backtrace", "target_set", "target_clear", "update_cost"};
inline uint64_t nanos[PHASES] = {}, calls[PHASES] = {};
struct Scope {
    Phase phase; Clock::time_point start;
    explicit Scope(Phase p) : phase(p), start(Clock::now()) {}
    ~Scope() { nanos[phase] += ns(start); ++calls[phase]; }
};
constexpr int MAX_SAMPLES = 1000000;
struct Sample { uintptr_t pc[8]; unsigned depth; };
inline Sample* samples = nullptr;
inline volatile sig_atomic_t sampleCount = 0, dropped = 0;
inline uintptr_t stackLo = 0, stackHi = 0;
inline int interval = 0;
inline void signalHandler(int, siginfo_t*, void* context) {
#if defined(__x86_64__)
    int i = sampleCount;
    if (i >= MAX_SAMPLES) { ++dropped; return; }
    auto* uc = static_cast<ucontext_t*>(context);
    samples[i].pc[0] = uintptr_t(uc->uc_mcontext.gregs[REG_RIP]);
    unsigned depth = 1;
    uintptr_t fp = uintptr_t(uc->uc_mcontext.gregs[REG_RBP]);
    while (depth < 8 && fp >= stackLo && fp + 2*sizeof(uintptr_t) <= stackHi && !(fp & 7)) {
        auto* frame = reinterpret_cast<const uintptr_t*>(fp);
        samples[i].pc[depth++] = frame[1];
        uintptr_t next = frame[0];
        if (next <= fp) break;
        fp = next;
    }
    samples[i].depth = depth;
    sampleCount = i + 1;
#endif
}
inline void startSampling() {
    const char* env = std::getenv("B_SAMPLE_US"); interval = env ? std::atoi(env) : 0;
    if (interval <= 0) return;
    samples = new Sample[MAX_SAMPLES];
    pthread_attr_t attr;
    if (pthread_getattr_np(pthread_self(), &attr)) throw std::runtime_error("cannot get stack bounds");
    void* base; size_t size;
    pthread_attr_getstack(&attr, &base, &size); pthread_attr_destroy(&attr);
    stackLo = uintptr_t(base); stackHi = stackLo + size;
    struct sigaction action{};
    action.sa_sigaction = signalHandler; action.sa_flags = SA_SIGINFO;
    sigemptyset(&action.sa_mask);
    if (sigaction(SIGPROF, &action, nullptr)) throw std::runtime_error("sigaction failed");
    itimerval timer{};
    timer.it_interval.tv_sec = interval / 1000000; timer.it_interval.tv_usec = interval % 1000000;
    timer.it_value = timer.it_interval;
    if (setitimer(ITIMER_PROF, &timer, nullptr)) throw std::runtime_error("setitimer failed");
}
inline void stopSampling() {
    if (!interval) return;
    itimerval timer{}; setitimer(ITIMER_PROF, &timer, nullptr);
}
inline void report(double loadMs, double routeMs, double writeMs) {
    const char* prefix = std::getenv("B_PROFILE_PREFIX");
    if (!prefix) return;
    std::ofstream out(std::string(prefix)+".json");
    out << std::setprecision(12) << "{\"load_ms\":" << loadMs << ",\"route_ms\":" << routeMs
        << ",\"write_ms\":" << writeMs << ",\"samples\":" << sampleCount
        << ",\"sample_interval_requested_us\":" << interval << ",\"samples_dropped\":" << dropped
        << ",\"phases\":{";
    for (int p=0; p<PHASES; ++p) {
        if (p) out << ',';
        out << '"' << names[p] << "\":{\"ms\":" << nanos[p]/1e6 << ",\"calls\":" << calls[p] << '}';
    }
    out << "}}\n";
    if (!out) throw std::runtime_error("profile write failed");
    if (interval) {
        std::ofstream pcs(std::string(prefix)+".pcs");
        for (int i=0; i<sampleCount; ++i) {
            for (unsigned j=0; j<samples[i].depth; ++j) pcs << (j?" ":"") << std::hex << samples[i].pc[j];
            pcs << '\n';
        }
        if (!pcs) throw std::runtime_error("sample write failed");
    }
}
}
