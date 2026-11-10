"""Build isolated original, phase-profiled, and access-traced CPU routers."""
import json
from pathlib import Path
import subprocess
from prepare_real import ROOT, UPSTREAM, sha


def source():
    path = UPSTREAM / "cpp_router/src/main.cpp"
    if sha(path) != "cbd6e0b810a46ca06b0058ee7f2318a1862f66c64178bf27f0d6b574e5bf6826":
        raise ValueError("Source snapshot changed")
    text = path.read_text()
    anchor = "        drop(floodCong); drop(floodCongShare); drop(shareMark);"
    assert text.count(anchor) == 1
    return text.replace(anchor, "#ifdef WITH_CUDA\n"+anchor+"\n#endif")


def generate(mode):
    text = source()
    def replace(old,new):
        nonlocal text
        if text.count(old)!=1: raise ValueError(f"Anchor mismatch: {old}")
        text=text.replace(old,new)
    if mode == "original": return text
    replace("namespace rw =", '#include "real_profile.hpp"\nnamespace rw =')
    for sig,phase in [("void ripUp(Connection& c) {","RIP"),
                      ("void updateUsersAndPresentCongestionCost(Connection& c) {","COMMIT"),
                      ("bool saveRouting(Connection& c, int rnode) {","BACKTRACE"),
                      ("void setAllTargets(Connection& c, State& st) {","TARGET_SET"),
                      ("void updateCost() {","UPDATE_COST")]:
        replace(sig, sig+f"\n        bprof::Scope b_scope(bprof::{phase});")
    replace("        // init mutable state\n", "        auto b_state_start = bprof::Clock::now();\n        // init mutable state\n")
    replace("        dyn.assign(n, NodeDyn{0.0f, 0.0f, 1.0f, -1, 0, 0});",
            "        { bprof::Scope b_scope(bprof::INIT_LABELS); dyn.assign(n, NodeDyn{0.0f, 0.0f, 1.0f, -1, 0, 0}); }")
    anchor = "            initHotFromStatic(i);\n        }\n\n        int numNets = r.i32();"
    replace(anchor, "            initHotFromStatic(i);\n        }\n\n        bprof::nanos[bprof::INIT_STATE] += bprof::ns(b_state_start); ++bprof::calls[bprof::INIT_STATE];\n        int numNets = r.i32();")
    replace("        for (int t : st.targets) TLD(t).target = 0;\n        st.targets.clear();",
            "        { bprof::Scope b_scope(bprof::TARGET_CLEAR);\n        for (int t : st.targets) TLD(t).target = 0;\n        st.targets.clear(); }")
    replace("    router.routeIndirectConnectionsIteratively();\n    auto t2 = clk::now();",
            "    bprof::startSampling();\n    auto b_route_start = clk::now();\n    router.routeIndirectConnectionsIteratively();\n    auto t2 = clk::now();\n    bprof::stopSampling();")
    replace("    auto t3 = clk::now();", "    auto t3 = clk::now();\n    auto b_ms = [](auto a, auto b) { return std::chrono::duration<double,std::milli>(b-a).count(); };\n    bprof::report(b_ms(t0,t1), b_ms(b_route_start,t2), b_ms(t2,t3));")
    if mode == "trace":
        replace('#include "real_profile.hpp"', '#include "real_profile.hpp"\n#include "real_trace.hpp"\n#define TLD(id) bTLD((id), __LINE__)')
        replace("static inline NodeDyn& TLD(int id) { return", "static inline NodeDyn& bTLD(int id, int line) { btrace::label(id,line); return")
        sig="    void routeIndirectConnection(int connIdx, long long budget = -1) {"
        replace(sig,sig+"\n        btrace::Attempt b_attempt; b_attempt.previousPath = connections[connIdx].rnodes;")
        replace("        lastAborted = aborted;   // caller floods", "        bTraceFinish(b_attempt,connIdx,pops,aborted);\n        lastAborted = aborted;   // caller floods")
        replace("    void writeResult(const std::string& path) {", '    #include "real_router_hooks.inc"\n    void writeResult(const std::string& path) {')
        replace("    Router router;\n    router.load(argv[1]);", "    btrace::init();\n    Router router;\n    router.load(argv[1]);")
        replace("    bprof::stopSampling();", "    bprof::stopSampling();\n    btrace::flush();")
    return text


def build():
    directory=ROOT/"build/real_trace"
    directory.mkdir(parents=True,exist_ok=True)
    flags=["-std=c++17","-O3","-g","-fno-fast-math","-fno-omit-frame-pointer","-no-pie","-pthread"]
    records={}
    for mode in ("original","profile","trace"):
        path=directory/f"{mode}.cpp"; path.write_text(generate(mode))
        binary=directory/f"router_{mode}"
        cmd=["g++",*flags,"-I",str(UPSTREAM/"cpp_router/include"),"-I",str(ROOT/"adapters"),str(path),"-o",str(binary)]
        with (directory/f"{mode}.build.log").open("w") as log:
            subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        records[mode]={"command":cmd,"source_sha256":sha(path),"binary_sha256":sha(binary)}
        print(f"built {mode}",flush=True)
    records["inputs"]={str(p):sha(p) for p in [Path(__file__),ROOT/"adapters/real_profile.hpp",ROOT/"adapters/real_trace.hpp",ROOT/"adapters/real_router_hooks.inc",UPSTREAM/"cpp_router/src/main.cpp"]}
    (directory/"build.json").write_text(json.dumps(records,indent=2)+"\n")

if __name__=="__main__": build()
