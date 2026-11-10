"""Isolated real-router ablation: page clearing versus per-node epochs."""
import argparse
import json
from pathlib import Path
import subprocess
from prepare_real import ROOT, UPSTREAM, sha
from build_real_router import source


def generate(node_epoch):
    text = source()
    def replace(old, new):
        nonlocal text
        if text.count(old) != 1: raise ValueError(f"Nonunique source anchor: {old}")
        text = text.replace(old, new)
    replace("        int poolUsed = 0;", """        int poolUsed = 0;
        std::vector<uint32_t> bNodeEpoch;
        size_t bPeakNodes = 0;
        uint64_t bGrows = 0, bResets = 0, bPages = 0, bClearedNodes = 0;
        void bAfterPoolShrink() {
#if B_NODE_EPOCH
            bNodeEpoch.resize(pool.size()); bNodeEpoch.shrink_to_fit();
#endif
        }
        void bStats(std::ostream& out) const {
            out << "{\\\"paged\\\":" << (paged?"true":"false")
                << ",\\\"page_bits\\\":" << PBITS << ",\\\"pool_nodes\\\":" << pool.size()
                << ",\\\"pool_capacity_bytes\\\":" << pool.capacity()*sizeof(NodeDyn)
                << ",\\\"node_epoch_bytes\\\":" << bNodeEpoch.capacity()*sizeof(uint32_t)
                << ",\\\"page_table_bytes\\\":" << pageEp.capacity()*sizeof(uint32_t)+pageSlot.capacity()*sizeof(int32_t)
                << ",\\\"peak_pool_nodes\\\":" << bPeakNodes << ",\\\"growth_events\\\":" << bGrows
                << ",\\\"resets\\\":" << bResets << ",\\\"page_claims\\\":" << bPages
                << ",\\\"cleared_nodes\\\":" << bClearedNodes << '}';
        }""")
    replace("            paged = true; poolUsed = 0; cur = 1;", """            paged = true; poolUsed = 0; cur = 1;
            bPeakNodes = pool.size();
#if B_NODE_EPOCH
            bNodeEpoch.assign(pool.size(), 0);
#endif""")
    replace("            cur++; used = 0; poolUsed = 0;", """            cur++; used = 0; poolUsed = 0;
#ifdef B_LABEL_DIAGNOSTIC
            ++bResets;
#endif""")
    replace("                std::fill(pageEp.begin(), pageEp.end(), 0);", """                std::fill(pageEp.begin(), pageEp.end(), 0);
                std::fill(bNodeEpoch.begin(), bNodeEpoch.end(), 0);""")
    replace("                    if ((size_t) (poolUsed + 1) * PSIZE > pool.size()) pool.resize(pool.size() * 2);", """                    if ((size_t) (poolUsed + 1) * PSIZE > pool.size()) {
                        pool.resize(std::max((size_t)(poolUsed+1)*PSIZE, pool.size()*2));
#if B_NODE_EPOCH
                        bNodeEpoch.resize(pool.size(), 0);
#endif
                        ++bGrows; bPeakNodes = std::max(bPeakNodes, pool.size());
                    }""")
    replace("                    std::memset(pool.data() + (size_t) pageSlot[p] * PSIZE, 0, sizeof(NodeDyn) * (size_t) PSIZE);", """#ifdef B_LABEL_DIAGNOSTIC
                    ++bPages;
#endif
#if !B_NODE_EPOCH
                    std::memset(pool.data() + (size_t) pageSlot[p] * PSIZE, 0, sizeof(NodeDyn) * (size_t) PSIZE);
#ifdef B_LABEL_DIAGNOSTIC
                    bClearedNodes += PSIZE;
#endif
#endif""")
    replace("                return pool[((size_t) pageSlot[p] << PBITS) | ((size_t) id & (size_t) (PSIZE - 1))];", """                size_t slot = ((size_t) pageSlot[p] << PBITS) | ((size_t) id & (size_t)(PSIZE-1));
#if B_NODE_EPOCH
                if (bNodeEpoch[slot] != cur) {
                    pool[slot] = NodeDyn{};
                    bNodeEpoch[slot] = cur;
#ifdef B_LABEL_DIAGNOSTIC
                    ++bClearedNodes;
#endif
                }
#endif
                return pool[slot];""")
    replace("                    L.pool.shrink_to_fit();", "                    L.pool.shrink_to_fit();\n                    L.bAfterPoolShrink();")
    replace("    static thread_local SparseLabels* tl_sparse;", """    SparseLabels bSerialLabels;
    bool bSerialPaged = false;
    void bConfigureLabels() {
        if (batchMin > 0 && !lazy) {
            // RRT1 already contains the complete CSR. The upstream batch gate is
            // normally armed by the JNI/GPU loader; validate and arm it here.
            for (const auto& node : ns)
                if (node.childStart < 0 || node.childCount < 0 ||
                    (size_t)node.childStart + (size_t)node.childCount > childIds.size())
                    throw std::runtime_error("Invalid frozen RRT adjacency");
            flatGraphBuilt = true;
        }
        bSerialPaged = rwEnvI("B_SERIAL_PAGED", 0) != 0;
        if (bSerialPaged) {
            if (parPart || parIter1 || overlapT || lazy) throw std::runtime_error("Serial paging requires frozen serial route");
            int bits = rwEnvI("RW_BATCH_PBITS", 9);
            if (bits < 2 || bits > 12) throw std::runtime_error("Invalid page bits");
            bSerialLabels.initPaged(numNodes(), bits);
            tl_sparse = &bSerialLabels;
        }
    }
    void bReportLabels() const {
        const char* file = std::getenv("B_LABEL_REPORT"); if (!file) return;
        std::ofstream out(file);
        out << "{\\\"node_epoch\\\":" << (B_NODE_EPOCH?"true":"false")
#ifdef B_LABEL_DIAGNOSTIC
            << ",\\\"diagnostic\\\":true"
#else
            << ",\\\"diagnostic\\\":false"
#endif
            << ",\\\"global_dyn_bytes\\\":" << dyn.capacity()*sizeof(NodeDyn)
            << ",\\\"node_size\\\":" << sizeof(NodeDyn) << ",\\\"contexts\\\":[";
        bool comma = false;
        if (bSerialPaged) { bSerialLabels.bStats(out); comma = true; }
        for (const auto& labels : batchLabels) { if(comma) out << ','; labels.bStats(out); comma = true; }
        out << "]}\\n";
        if (!out) throw std::runtime_error("Label report write failed");
    }
    static thread_local SparseLabels* tl_sparse;""")
    replace("    void routeIndirectConnection(int connIdx, long long budget = -1) {", """    void routeIndirectConnection(int connIdx, long long budget = -1) {
        if (bSerialPaged) {
            bSerialLabels.reset();
            TLD(connections[connIdx].sourceRnode).prev = -1;
        }""")
    replace("    router.routeIndirectConnectionsIteratively();\n    auto t2 = clk::now();", "    router.bConfigureLabels();\n    router.routeIndirectConnectionsIteratively();\n    auto t2 = clk::now();")
    replace("    auto t3 = clk::now();", "    auto t3 = clk::now();\n    router.bReportLabels();")
    return f"#define B_NODE_EPOCH {int(node_epoch)}\n#include <fstream>\n" + text


def build(directory, diagnostic=False):
    directory.mkdir(parents=True, exist_ok=False)
    manifest = {"diagnostic": diagnostic, "variants": {}, "inputs": {str(p): sha(p) for p in
        [Path(__file__), ROOT/"adapters/build_real_router.py", UPSTREAM/"cpp_router/src/main.cpp", *sorted((UPSTREAM/"cpp_router/include").glob("*.hpp"))]}}
    for variant, node_epoch in (("paged", False), ("node_epoch", True)):
        target = directory/variant; target.mkdir()
        source_path = target/"router.cpp"; source_path.write_text(generate(node_epoch))
        binary = target/"router"
        cmd = ["g++", "-std=c++17", "-O3", "-g", "-fno-fast-math", "-fno-omit-frame-pointer", "-no-pie", "-pthread",
               "-I", str(UPSTREAM/"cpp_router/include"), str(source_path), "-o", str(binary)]
        if diagnostic: cmd.insert(1, "-DB_LABEL_DIAGNOSTIC")
        with (target/"build.log").open("w") as log: subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
        manifest["variants"][variant] = {"source": str(source_path), "binary": str(binary), "command": cmd,
                                         "source_sha256": sha(source_path), "binary_sha256": sha(binary)}
        print(f"built {variant}", flush=True)
    (directory/"build.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT/"build/paged_real")
    parser.add_argument("--diagnostic", action="store_true")
    args = parser.parse_args(); build(args.output.resolve(), args.diagnostic)
