"""Keep page lookup direct, map touched offsets to a compact reusable label pool."""
import argparse
import json
from pathlib import Path
import subprocess
from prepare_real import ROOT, UPSTREAM, sha
from build_paged_router import generate as generate_epoch


def generate():
    text=generate_epoch(True)
    start=text.index("    struct SparseLabels {")
    end=text.index("    SparseLabels bSerialLabels;",start)
    section=text[start:end]
    def replace(old,new):
        nonlocal section
        if section.count(old)!=1:raise ValueError(f"Compact anchor mismatch: {old}")
        section=section.replace(old,new)
    replace("        std::vector<NodeDyn>  pool;", """        std::vector<uint32_t> pool; // physical page offset -> compact label index
        std::vector<NodeDyn> bCompactValues;
        size_t bCompactUsed = 0, bPeakCompactNodes = 0;
        uint64_t bCompactGrows = 0;""")
    replace("            bPeakNodes = pool.size();", """            bPeakNodes = pool.size();
            bCompactValues.resize(4096); bCompactUsed = 0;
            bPeakCompactNodes = bCompactValues.size();""")
    replace("            cur++; used = 0; poolUsed = 0;", "            cur++; used = 0; poolUsed = 0; bCompactUsed = 0;")
    replace("            bNodeEpoch.resize(pool.size()); bNodeEpoch.shrink_to_fit();", """            bNodeEpoch.resize(pool.size()); bNodeEpoch.shrink_to_fit();
            // Caller has joined all workers and immediately resets this context.
            if (bCompactValues.size() > 65536) {
                bCompactValues.resize(65536); bCompactValues.shrink_to_fit();
            }""")
    replace('pool.capacity()*sizeof(NodeDyn)', 'pool.capacity()*sizeof(uint32_t)')
    anchor='                << ",\\\"page_bits\\\":" << PBITS'
    replace(anchor, '''                << ",\\\"layout\\\":\\\"compact\\\",\\\"pool_slot_bytes\\\":4"
                << ",\\\"compact_payload_bytes\\\":" << bCompactValues.capacity()*sizeof(NodeDyn)
                << ",\\\"compact_live_nodes\\\":" << bCompactUsed
                << ",\\\"peak_compact_nodes\\\":" << bPeakCompactNodes
                << ",\\\"compact_growth_events\\\":" << bCompactGrows
''' + anchor)
    old="""            if (pageEp[p] == cur)
                __builtin_prefetch(pool.data() + (((size_t) pageSlot[p] << PBITS) | ((size_t) id & (size_t) (PSIZE - 1))), 1, 3);"""
    replace(old,"""            if (pageEp[p] != cur) return;
            size_t slot = ((size_t)pageSlot[p] << PBITS) | ((size_t)id & (size_t)(PSIZE-1));
            __builtin_prefetch(pool.data()+slot, 0, 3);
            if (bNodeEpoch[slot] == cur)
                __builtin_prefetch(bCompactValues.data()+pool[slot], 1, 3);""")
    replace("                    pool[slot] = NodeDyn{};", """                    if (bCompactUsed == bCompactValues.size()) {
                        bCompactValues.resize(std::max(size_t(4096), bCompactValues.size()*2));
                        bPeakCompactNodes = std::max(bPeakCompactNodes, bCompactValues.size());
                        ++bCompactGrows;
                    }
                    uint32_t index = (uint32_t)bCompactUsed++;
                    pool[slot] = index;
                    bCompactValues[index] = NodeDyn{};""")
    replace("                return pool[slot];", "                return bCompactValues[pool[slot]];")
    text=text[:start]+section+text[end:]
    return "#define B_COMPACT_LABELS 1\n"+text


def build(directory):
    directory.mkdir(parents=True,exist_ok=False)
    source=directory/"router.cpp";source.write_text(generate())
    binary=directory/"router"
    command=["g++","-std=c++17","-O3","-g","-fno-fast-math","-fno-omit-frame-pointer","-no-pie","-pthread",
             "-I",str(UPSTREAM/"cpp_router/include"),str(source),"-o",str(binary)]
    with (directory/"build.log").open("w") as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
    inputs=[Path(__file__),ROOT/"adapters/build_paged_router.py",ROOT/"adapters/build_real_router.py",UPSTREAM/"cpp_router/src/main.cpp",*sorted((UPSTREAM/"cpp_router/include").glob("*.hpp"))]
    record={"layout":"compact","variants":{"compact":{"source":str(source),"binary":str(binary),"command":command,
              "source_sha256":sha(source),"binary_sha256":sha(binary)}},"inputs":{str(p):sha(p) for p in inputs}}
    (directory/"build.json").write_text(json.dumps(record,indent=2)+"\n")
    print("Built compact router",flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--output",type=Path,default=ROOT/"build/compact_real_v1")
    args=parser.parse_args();build(args.output.resolve())
