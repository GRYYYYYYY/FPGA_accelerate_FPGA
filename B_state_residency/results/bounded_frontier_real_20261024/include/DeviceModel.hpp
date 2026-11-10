// Pure-C++ device model, COMPACT: builds the routing graph + per-node attrs IN RAM from the small
// shippable files (.rdv graph templates ~8MB zstd, .atc attr template+exceptions ~0.7MB zstd) — no
// 7.69GB .flat, no setup. Node identity via per-tile pattern union-find; attrs assembled from the
// per-(type,wire) template + exceptions + tile coords + the verified hashCode formula
// (tileAddr*31+wire+961). getChildrenPacked then emits the same 11-int/child packet from RAM arrays.
#pragma once
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <vector>
#include <unordered_map>
#include <chrono>
#include <thread>
#include <atomic>
#include <algorithm>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

namespace dev {
struct NodeRec { int64_t baseKey; float baseCost; int32_t hash;
                 int16_t bx,by,ex,ey,len; uint8_t type,flags4; uint8_t _pad[4]; };
static_assert(sizeof(NodeRec) == 32, "NodeRec layout is persisted in .dmc dumps");

class DeviceModel {
    struct Rd { const uint8_t* p;
        uint8_t  u8(){return *p++;}
        int16_t  i16(){int16_t v=(int16_t)((p[0]<<8)|p[1]); p+=2; return v;}
        int32_t  i32(){int32_t v=(int32_t)((uint32_t)p[0]<<24|(uint32_t)p[1]<<16|(uint32_t)p[2]<<8|p[3]); p+=4; return v;}
        int64_t  i64(){int64_t v=0; for(int i=0;i<8;i++) v=(v<<8)|p[i]; p+=8; return v;}
    };
    std::vector<int32_t> par; std::vector<uint8_t> rnk;
    inline int32_t find(int32_t x){ while(par[x]!=x){ par[x]=par[par[x]]; x=par[x]; } return x; }
    inline int32_t findRO(int32_t x) const { while(par[x]!=x) x=par[x]; return x; }  // read-only (parallel-safe)
    template<class F> static void par32(int64_t n, F f){
        // The device build runs in a background thread CONCURRENTLY with Java's single-threaded
        // readCheckpoint/init, so cap its workers at 31 -> 31 build workers + 1 main = 32 total (hard rule).
        // RWDEV_BUILD_THREADS overrides (also lets it use fewer to contend less; build still hides behind read+init).
        static const int T0 = []{ const char* mt=std::getenv("RW_MAX_THREADS"); int cap=mt?std::atoi(mt):48; if(cap<2)cap=2;
            const char* e=std::getenv("RWDEV_BUILD_THREADS"); int v=e?std::atoi(e):cap-1;
            if(v<1)v=1; if(v>cap)v=cap; return v; }();
        int T=std::min(T0,(int)std::thread::hardware_concurrency()); if(T<1)T=1; if(n<100000)T=1;
        std::vector<std::thread> th; int64_t ch=(n+T-1)/T;
        for(int t=0;t<T;t++) th.emplace_back([=,&f]{ int64_t lo=(int64_t)t*ch, hi=std::min(n,lo+ch); for(int64_t i=lo;i<hi;i++) f(i); });
        for(auto&x:th) x.join();
    }
    inline void unite(int32_t a,int32_t b){ a=find(a); b=find(b); if(a==b)return;
        if(rnk[a]<rnk[b]){int32_t t=a;a=b;b=t;} par[b]=a; if(rnk[a]==rnk[b]) rnk[a]++; }
    static std::vector<uint8_t> readFile(const char* p){ FILE* f=fopen(p,"rb"); if(!f){perror(p);return {};}
        fseek(f,0,SEEK_END); long n=ftell(f); fseek(f,0,SEEK_SET); std::vector<uint8_t> b(n);
        if(fread(b.data(),1,n,f)!=(size_t)n){} fclose(f); return b; }
public:
    int64_t nTiles=0, nNodes=0, totW=0, nSrc=0;
    std::vector<int64_t> wb; std::vector<int32_t> srcIdOf; std::vector<int64_t> srcOff;
    std::vector<int32_t> srcKids; std::vector<NodeRec> nrec;
    std::vector<int32_t> nodeIdOf;   // per wire: dense node id at the node's BASE wire, else -1
    // Pointer views actually served by getChildrenPacked: RAM build -> the vectors' data;
    // mmap load -> file-backed pages (lazy paging = near-zero load cost for small designs).
    const int64_t* wbP=nullptr; const int32_t* srcIdOfP=nullptr; const int64_t* srcOffP=nullptr;
    const int32_t* srcKidsP=nullptr; const NodeRec* nrecP=nullptr; const int32_t* nodeIdOfP=nullptr;

    // Build everything in RAM from the compact .rdv (graph) + .atc (attrs). Returns seconds.
    double load(const char* rdvPath, const char* atcPath){
        auto t0=std::chrono::steady_clock::now();
        std::vector<uint8_t> buf=readFile(rdvPath); if(buf.empty()) return -1;
        Rd rd{buf.data()};
        if((uint32_t)rd.i32()!=0x52445633u){ fprintf(stderr,"bad rdv magic\n"); return -1; }
        int nRows=rd.i32(),nCols=rd.i32(); nTiles=rd.i32(); int nT=rd.i32(),nPat=rd.i32();
        int64_t expNodes=rd.i64(); rd.i64();
        std::vector<int> typeWC(nT); std::vector<uint8_t> typeAllowed(nT);
        std::vector<std::vector<int16_t>> pS(nT),pE(nT);
        for(int ti=0;ti<nT;ti++){ typeAllowed[ti]=rd.u8(); typeWC[ti]=rd.i32(); int np=rd.i32();
            pS[ti].resize(np); pE[ti].resize(np);
            for(int p=0;p<np;p++){ pS[ti][p]=rd.i16(); pE[ti][p]=rd.i16(); rd.u8(); } }
        std::vector<int64_t> patOff(nPat+1,0); std::vector<int64_t> patData;
        std::vector<int64_t> baseOff(nPat+1,0); std::vector<uint8_t> baseData;
        for(int i=0;i<nPat;i++){ int cc=rd.i32(); patOff[i+1]=patOff[i]+cc; for(int c=0;c<cc;c++) patData.push_back(rd.i64());
            int bl=rd.i32(); baseOff[i+1]=baseOff[i]+bl; for(int b=0;b<bl;b++) baseData.push_back(rd.u8()); }
        std::vector<int16_t> tType(nTiles),tCol(nTiles),tRow(nTiles); std::vector<int32_t> tPat(nTiles);
        for(int a=0;a<nTiles;a++){ tType[a]=rd.i16(); tCol[a]=rd.i16(); tRow[a]=rd.i16(); tPat[a]=rd.i32(); }
        // grid + wirebase + union-find
        std::vector<int> gridAddr((size_t)nRows*nCols,-1);
        for(int a=0;a<nTiles;a++) if(tType[a]>=0) gridAddr[(size_t)tRow[a]*nCols+tCol[a]]=a;
        wb.assign(nTiles+1,0); for(int a=0;a<nTiles;a++){int wc=tType[a]>=0?typeWC[tType[a]]:0; wb[a+1]=wb[a]+wc;}
        totW=wb[nTiles]; par.resize(totW); for(int64_t i=0;i<totW;i++)par[i]=(int32_t)i; rnk.assign(totW,0);
        for(int a=0;a<nTiles;a++){int pid=tPat[a]; if(pid<0)continue; int col=tCol[a],row=tRow[a]; int64_t base=wb[a];
            for(int64_t c=patOff[pid];c<patOff[pid+1];c++){int64_t pk=patData[c];
                int w=(uint16_t)((pk>>48)&0xFFFF);int dx=(int16_t)((pk>>32)&0xFFFF);int dy=(int16_t)((pk>>16)&0xFFFF);int tw=(uint16_t)(pk&0xFFFF);
                int bc=col+dx,br=row+dy; if(bc<0||bc>=nCols||br<0||br>=nRows)continue;
                int ta=gridAddr[(size_t)br*nCols+bc]; if(ta<0)continue; unite((int32_t)(base+w),(int32_t)(wb[ta]+tw)); } }
        // dense ids + base keys (+ per-BASE-wire node id for O(1) key->NodeRec lookups)
        std::vector<int32_t> denseId(totW,-1); nNodes=0; std::vector<int64_t> baseKeyOf;
        nodeIdOf.assign(totW,-1);
        for(int a=0;a<nTiles;a++){int ty=tType[a]; if(ty<0||!typeAllowed[ty])continue; int pid=tPat[a]; if(pid<0)continue;
            int wc=typeWC[ty]; int64_t base=wb[a]; const uint8_t* bb=&baseData[baseOff[pid]];
            for(int w=0;w<wc;w++) if(bb[w>>3]&(1<<(w&7))){int32_t r=find((int32_t)(base+w));
                if(denseId[r]<0){denseId[r]=(int32_t)nNodes++; baseKeyOf.push_back(((int64_t)a<<20)|w);}
                nodeIdOf[base+w]=denseId[r]; } }
        if(nNodes!=expNodes) fprintf(stderr,"WARN nNodes %ld != exp %ld\n",(long)nNodes,(long)expNodes);
        // children keyed by component root (routing + source-pin parents). PARALLEL (read-only findRO
        // + atomics; union-find tree is now final so par[] is read-only here -> no path-compression race).
        // markSrc: parallel-mark roots that have an allowed child (benign races: all write 1)
        std::vector<uint8_t> hasChild(totW,0);
        par32(nTiles,[&](int64_t a){ int ty=tType[a]; if(ty<0)return; int np=pS[ty].size();
            for(int p=0;p<np;p++){ int32_t e=denseId[findRO((int32_t)(wb[a]+pE[ty][p]))]; if(e>=0) hasChild[findRO((int32_t)(wb[a]+pS[ty][p]))]=1; } });
        srcIdOf.assign(totW,-1); int32_t nSrc=0;
        for(int64_t w=0;w<totW;w++) if(par[w]==(int32_t)w && hasChild[w]) srcIdOf[w]=nSrc++;
        std::vector<std::atomic<int64_t>> deg(nSrc); for(auto&d:deg) d.store(0,std::memory_order_relaxed);
        par32(nTiles,[&](int64_t a){ int ty=tType[a]; if(ty<0)return; int np=pS[ty].size();
            for(int p=0;p<np;p++){ int32_t e=denseId[findRO((int32_t)(wb[a]+pE[ty][p]))]; if(e>=0) deg[srcIdOf[findRO((int32_t)(wb[a]+pS[ty][p]))]].fetch_add(1,std::memory_order_relaxed); } });
        srcOff.assign(nSrc+1,0); for(int i=0;i<nSrc;i++) srcOff[i+1]=srcOff[i]+deg[i].load(std::memory_order_relaxed);
        srcKids.resize(srcOff[nSrc]);
        std::vector<std::atomic<int64_t>> cur(nSrc); for(int i=0;i<nSrc;i++) cur[i].store(srcOff[i],std::memory_order_relaxed);
        par32(nTiles,[&](int64_t a){ int ty=tType[a]; if(ty<0)return; int np=pS[ty].size();
            for(int p=0;p<np;p++){ int32_t e=denseId[findRO((int32_t)(wb[a]+pE[ty][p]))]; if(e>=0) srcKids[cur[srcIdOf[findRO((int32_t)(wb[a]+pS[ty][p]))]].fetch_add(1,std::memory_order_relaxed)]=e; } });
        // sort each node's children -> DETERMINISTIC output (parallel atomic-cursor fill order is racy)
        par32(nSrc,[&](int64_t s){ std::sort(srcKids.begin()+srcOff[s], srcKids.begin()+srcOff[s+1]); });
        // remap srcIdOf to wire->srcId for ALL wires (parallel into separate s2, then swap)
        { std::vector<int32_t> s2(totW);
          par32(totW,[&](int64_t w){ s2[w]=srcIdOf[findRO((int32_t)w)]; });
          srcIdOf.swap(s2); }

        // ---- attrs from .atc (template + exceptions + coords + hashCode formula) ----
        struct AA{ uint8_t type,flags4,valid; int16_t len,bxoff,byoff,exoff,eyoff; float bc; };
        std::vector<uint8_t> ab=readFile(atcPath); Rd ar{ab.data()};
        if((uint32_t)ar.i32()!=0x41544331u){ fprintf(stderr,"bad atc magic\n"); return -1; }
        int aTiles=ar.i32(); std::vector<int16_t> tX(aTiles),tY(aTiles);
        for(int a=0;a<aTiles;a++) tX[a]=ar.i16(); for(int a=0;a<aTiles;a++) tY[a]=ar.i16();
        int nty=ar.i32(); std::unordered_map<int,std::vector<AA>> tmplByWC;
        for(int t=0;t<nty;t++){ ar.i32(); int wc=ar.i32(); std::vector<AA> v(wc);
            for(int w=0;w<wc;w++){ AA a{}; a.valid=ar.u8(); if(a.valid){ a.type=ar.u8(); a.len=ar.i16(); a.bxoff=ar.i16(); a.byoff=ar.i16();
                a.exoff=ar.i16(); a.eyoff=ar.i16(); int b=ar.i32(); memcpy(&a.bc,&b,4); a.flags4=ar.u8(); } v[w]=a; } tmplByWC[wc]=std::move(v); }
        int64_t nexc=ar.i64(); std::unordered_map<int64_t,AA> exc; exc.reserve(nexc*2);
        for(int64_t i=0;i<nexc;i++){ int64_t k=ar.i64(); AA a{}; a.valid=1; a.type=ar.u8(); a.len=ar.i16(); a.bxoff=ar.i16(); a.byoff=ar.i16();
            a.exoff=ar.i16(); a.eyoff=ar.i16(); int b=ar.i32(); memcpy(&a.bc,&b,4); a.flags4=ar.u8(); exc[k]=a; }
        nrec.resize(nNodes);
        par32(nNodes,[&](int64_t id){ int64_t bk=baseKeyOf[id]; int tile=(int)(bk>>20), wire=(int)(bk&0xFFFFF);
            AA a; auto eit=exc.find(bk);   // exc/tmplByWC are read-only here -> concurrent reads safe
            if(eit!=exc.end()) a=eit->second;
            else { int wc=typeWC[tType[tile]]; auto it=tmplByWC.find(wc); a=it->second[wire]; }
            NodeRec& R=nrec[id]; R.baseKey=bk; R.baseCost=a.bc; R.hash=tile*31+wire+961;
            R.bx=(int16_t)(tX[tile]+a.bxoff); R.by=(int16_t)(tY[tile]+a.byoff);
            R.ex=(int16_t)(tX[tile]+a.exoff); R.ey=(int16_t)(tY[tile]+a.eyoff);
            R.len=a.len; R.type=a.type; R.flags4=a.flags4; });
        // free build temporaries
        par.clear(); par.shrink_to_fit(); rnk.clear(); rnk.shrink_to_fit();
        this->nSrc = (int64_t) srcOff.size() - 1;   // NB: a local nSrc shadows the member here
        wbP = wb.data(); srcIdOfP = srcIdOf.data(); srcOffP = srcOff.data();
        srcKidsP = srcKids.data(); nrecP = nrec.data(); nodeIdOfP = nodeIdOf.data();
        return std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
    }

    // ---- .dmc: flat on-disk image of the built model, mmap'ed back in ~ms. The build itself is a
    // 12.5s union-find over ~500M wires; small cases can't hide that, but they touch only a tiny
    // slice of the arrays -> file-backed lazy paging makes the compact device essentially free.
    // Header carries the source .rdv/.atc sizes as an identity proxy: regenerate after gen-device.
    struct DmcHdr { uint32_t magic, version; int64_t nTiles, nNodes, totW, nSrc, nKids;
                    int64_t rdvBytes, atcBytes;
                    uint64_t offWb, offSrcIdOf, offSrcOff, offSrcKids, offNrec, offNodeIdOf, fileBytes; };
    static constexpr uint32_t DMC_MAGIC = 0x444D4331u, DMC_VERSION = 2;   // v2: + nodeIdOf array
    static int64_t fileBytesOf(const char* p){ struct stat st{}; return ::stat(p,&st)==0 ? (int64_t)st.st_size : -1; }

    // Write the current (RAM-built) model to path. Returns seconds, or -1 on failure.
    double dumpTo(const char* path, const char* rdvPath, const char* atcPath){
        auto t0=std::chrono::steady_clock::now();
        if (!wbP || nNodes<=0) return -1;
        auto align64=[](uint64_t o){ return (o+63)&~uint64_t(63); };
        DmcHdr h{}; h.magic=DMC_MAGIC; h.version=DMC_VERSION;
        h.nTiles=nTiles; h.nNodes=nNodes; h.totW=totW; h.nSrc=nSrc; h.nKids=(int64_t)srcKids.size();
        h.rdvBytes=fileBytesOf(rdvPath); h.atcBytes=fileBytesOf(atcPath);
        uint64_t o=align64(sizeof(DmcHdr));
        h.offWb=o;       o=align64(o+sizeof(int64_t)*(nTiles+1));
        h.offSrcIdOf=o;  o=align64(o+sizeof(int32_t)*totW);
        h.offSrcOff=o;   o=align64(o+sizeof(int64_t)*(nSrc+1));
        h.offSrcKids=o;  o=align64(o+sizeof(int32_t)*h.nKids);
        h.offNrec=o;     o=align64(o+sizeof(NodeRec)*nNodes);
        h.offNodeIdOf=o; o=align64(o+sizeof(int32_t)*totW);
        h.fileBytes=o;
        std::string tmp=std::string(path)+".tmp";
        FILE* f=fopen(tmp.c_str(),"wb"); if(!f){perror(tmp.c_str()); return -1;}
        auto put=[&](uint64_t off,const void* p,size_t n){ fseeko(f,(off_t)off,SEEK_SET); return fwrite(p,1,n,f)==n; };
        bool ok = put(0,&h,sizeof h)
               && put(h.offWb, wb.data(), sizeof(int64_t)*(nTiles+1))
               && put(h.offSrcIdOf, srcIdOf.data(), sizeof(int32_t)*totW)
               && put(h.offSrcOff, srcOff.data(), sizeof(int64_t)*(nSrc+1))
               && put(h.offSrcKids, srcKids.data(), sizeof(int32_t)*h.nKids)
               && put(h.offNrec, nrec.data(), sizeof(NodeRec)*nNodes)
               && put(h.offNodeIdOf, nodeIdOf.data(), sizeof(int32_t)*totW);
        { uint8_t z=0; ok = put(h.fileBytes-1, &z, 1) && ok; }   // pad to declared size (loader checks it)
        ok = (fclose(f)==0) && ok;
        if(!ok || ::rename(tmp.c_str(), path)!=0){ ::unlink(tmp.c_str()); return -1; }
        return std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
    }

    // mmap a .dmc written by dumpTo. Returns seconds (~ms), or -1 (caller falls back).
    double loadMmap(const char* path, const char* rdvPath, const char* atcPath){
        auto t0=std::chrono::steady_clock::now();
        int fd=::open(path,O_RDONLY); if(fd<0) return -1;
        struct stat st{}; if(fstat(fd,&st)!=0 || (size_t)st.st_size<sizeof(DmcHdr)){ ::close(fd); return -1; }
        void* base=::mmap(nullptr,(size_t)st.st_size,PROT_READ,MAP_SHARED,fd,0);
        ::close(fd);                                  // mapping keeps its own reference
        if(base==MAP_FAILED) return -1;
        const DmcHdr& h=*(const DmcHdr*)base;
        if(h.magic!=DMC_MAGIC || h.version!=DMC_VERSION || h.fileBytes!=(uint64_t)st.st_size ||
           h.rdvBytes!=fileBytesOf(rdvPath) || h.atcBytes!=fileBytesOf(atcPath)){
            ::munmap(base,(size_t)st.st_size); return -1;   // stale vs current .rdv/.atc -> rebuild path
        }
        nTiles=h.nTiles; nNodes=h.nNodes; totW=h.totW; nSrc=h.nSrc;
        const uint8_t* b=(const uint8_t*)base;
        wbP=(const int64_t*)(b+h.offWb); srcIdOfP=(const int32_t*)(b+h.offSrcIdOf);
        srcOffP=(const int64_t*)(b+h.offSrcOff); srcKidsP=(const int32_t*)(b+h.offSrcKids);
        nrecP=(const NodeRec*)(b+h.offNrec); nodeIdOfP=(const int32_t*)(b+h.offNodeIdOf);
        return std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
    }

    // O(1) node attrs by canonical base (tile,wire); false if outside the modeled INT/laguna set.
    // out4 = { RouteNodeType ordinal, endTileX, endTileY, length } — exactly Java's RouteNodeInfo
    // (the .atc these come from was exported from Java RouteNode.getType()/getEnd*/getLength()).
    bool getNodeAttr(int tileAddr, int wire, int out4[4]) const {
        if(!nodeIdOfP || tileAddr<0 || tileAddr>=nTiles) return false;
        int64_t wcnt = wbP[tileAddr+1]-wbP[tileAddr];
        if(wire<0 || wire>=wcnt) return false;
        int32_t id = nodeIdOfP[wbP[tileAddr]+wire];
        if(id<0) return false;
        const NodeRec& R = nrecP[id];
        if((int)(R.baseKey>>20)!=tileAddr || (int)(R.baseKey&0xFFFFF)!=wire) return false;   // not the base wire
        out4[0]=R.type; out4[1]=R.ex; out4[2]=R.ey; out4[3]=R.len;
        return true;
    }

    // Same 11-int/child packet as RWRouteCppJni.getChildrenPacked; preserved bit set by the router at intern.
    void getChildrenPacked(long key, std::vector<int>& out){
        int ptile=(int)(key>>20), pw=(int)(key&0xFFFFF);
        if(ptile<0||ptile>=nTiles||pw>=(int)(wbP[ptile+1]-wbP[ptile])){ if(out.empty())out.resize(1); out[0]=0; return; }
        int64_t w=wbP[ptile]+pw; int32_t srcId=srcIdOfP[w];
        if(srcId<0){ if(out.empty())out.resize(1); out[0]=0; return; }
        int64_t b=srcOffP[srcId], e=srcOffP[srcId+1]; int cnt=(int)(e-b);
        size_t need=1+(size_t)cnt*11; if(out.size()<need) out.resize(need);
        out[0]=cnt; int o=1;
        for(int64_t c=b;c<e;c++){ int32_t id=srcKidsP[c]; const NodeRec& R=nrecP[id];
            long long bk=(long long)R.baseKey; int bcb; memcpy(&bcb,&R.baseCost,4);
            out[o++]=(int)(bk>>20); out[o++]=(int)(bk&0xFFFFF); out[o++]=R.type; out[o++]=R.flags4;
            out[o++]=R.bx; out[o++]=R.by; out[o++]=R.ex; out[o++]=R.ey;
            out[o++]=R.len; out[o++]=bcb; out[o++]=R.hash;
        }
    }
};
} // namespace dev
