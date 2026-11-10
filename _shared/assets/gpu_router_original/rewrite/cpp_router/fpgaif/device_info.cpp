// F1 verification: open an (uncompressed) FPGAIF .device and print structure counts,
// so we can cross-check against RapidWright's Device before building the router on it.
//
// The .device file RapidWright writes is GZIPPED + standard (non-packed) Cap'n Proto.
// Decompress once:  gunzip -c xcvu13p.device > xcvu13p.device.raw
// then run:         rwroute_fpgaif xcvu13p.device.raw
#include "DeviceResources.capnp.h"

#include <capnp/serialize.h>
#include <kj/array.h>

#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

#include <cstdint>
#include <cstdio>
#include <string>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::fprintf(stderr, "USAGE: rwroute_fpgaif <xcvu13p.device.raw>  (gunzip'd .device)\n");
        return 1;
    }
    const char* path = argv[1];
    int fd = ::open(path, O_RDONLY);
    if (fd < 0) { std::perror("open"); return 1; }
    struct stat st;
    if (::fstat(fd, &st) != 0) { std::perror("fstat"); return 1; }
    size_t sz = (size_t)st.st_size;
    void* p = ::mmap(nullptr, sz, PROT_READ, MAP_PRIVATE, fd, 0);
    if (p == MAP_FAILED) { std::perror("mmap"); return 1; }

    std::printf("INFO: mapped %s (%.1f MB)\n", path, sz / 1e6);
    std::fflush(stdout);

    kj::ArrayPtr<const capnp::word> words(
        reinterpret_cast<const capnp::word*>(p), sz / sizeof(capnp::word));

    capnp::ReaderOptions opts;
    opts.traversalLimitInWords = (uint64_t)1 << 40;  // effectively unlimited
    opts.nestingLimit = 1024;

    capnp::FlatArrayMessageReader message(words, opts);
    auto device = message.getRoot<DeviceResources::Device>();

    auto strList = device.getStrList();
    auto tileList = device.getTileList();
    auto tileTypeList = device.getTileTypeList();
    auto siteTypeList = device.getSiteTypeList();
    auto wires = device.getWires();
    auto nodes = device.getNodes();
    auto wireTypes = device.getWireTypes();

    std::printf("device name      : %s\n", std::string(device.getName().cStr()).c_str());
    std::printf("strList          : %u\n", strList.size());
    std::printf("siteTypeList     : %u\n", siteTypeList.size());
    std::printf("tileTypeList     : %u\n", tileTypeList.size());
    std::printf("tileList         : %u\n", tileList.size());
    std::printf("wires (global)   : %u\n", wires.size());
    std::printf("nodes            : %u\n", nodes.size());
    std::printf("wireTypes        : %u\n", wireTypes.size());

    // Print the IntentCode table (wireTypes is indexed by IntentCode ordinal).
    std::printf("--- wireTypes[0..min(30)] (IntentCode ordinal -> name) ---\n");
    for (uint32_t i = 0; i < wireTypes.size() && i < 30; i++) {
        std::printf("  %2u : %s\n", i, strList[wireTypes[i].getName()].cStr());
    }

    // Sample one INT tile's first few wires + their intent.
    uint32_t shown = 0;
    for (uint32_t t = 0; t < tileList.size() && shown < 1; t++) {
        auto tile = tileList[t];
        std::string tname = strList[tile.getName()].cStr();
        if (tname.rfind("INT_X", 0) != 0) continue;
        auto tt = tileTypeList[tile.getType()];
        std::printf("--- sample tile %s (type %s), tileType wires=%u pips=%u ---\n",
                    tname.c_str(), strList[tt.getName()].cStr(),
                    tt.getWires().size(), tt.getPips().size());
        shown++;
    }

    ::munmap(p, sz);
    ::close(fd);
    return 0;
}
