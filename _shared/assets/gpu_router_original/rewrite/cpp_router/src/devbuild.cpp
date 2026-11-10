// Rebuild the FULL xcvu13p routing graph in pure C++ from the compact RDV3 device file.
// RDV3 = per-tile node-forming connection PATTERN (deduped) + per-type PIPs + tile grid.
// Each tile applies ITS OWN pattern via union-find -> exact reconstruction. Validates vs ground truth.
// Build: g++ -O3 -std=c++17 -pthread -march=native src/devbuild.cpp -o build/devbuild
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <vector>
#include <thread>
#include <atomic>
#include <chrono>
#include <algorithm>
#include <unordered_map>
#include <utility>
using clk = std::chrono::steady_clock;
static double sec(clk::time_point t){ return std::chrono::duration<double>(clk::now()-t).count(); }

// AoS per-node record (32 bytes): one cache line holds 2 nodes; reading a child's full attrs = 1 miss.
struct NodeRec { int64_t baseKey; float baseCost; int32_t hash;
                 int16_t bx,by,ex,ey,len; uint8_t type,flags4; uint8_t _pad[4]; };
static long rssKB(){ FILE*f=fopen("/proc/self/status","r"); if(!f)return -1; char l[256]; long kb=-1;
    while(fgets(l,sizeof l,f)) if(!strncmp(l,"VmRSS:",6)){ sscanf(l+6,"%ld",&kb); break;} fclose(f); return kb; }
struct Rd { const uint8_t* p;
    uint8_t u8(){return *p++;}
    int16_t i16(){int16_t v=(int16_t)((p[0]<<8)|p[1]); p+=2; return v;}
    int32_t i32(){int32_t v=(int32_t)((uint32_t)p[0]<<24|(uint32_t)p[1]<<16|(uint32_t)p[2]<<8|p[3]); p+=4; return v;}
    int64_t i64(){int64_t v=0; for(int i=0;i<8;i++) v=(v<<8)|p[i]; p+=8; return v;}
};
static std::vector<int32_t> par; static std::vector<uint8_t> rnk;
static inline int32_t find(int32_t x){ while(par[x]!=x){ par[x]=par[par[x]]; x=par[x]; } return x; }
static inline void unite(int32_t a,int32_t b){ a=find(a); b=find(b); if(a==b)return;
    if(rnk[a]<rnk[b]) std::swap(a,b); par[b]=a; if(rnk[a]==rnk[b]) rnk[a]++; }

int main(int argc,char**argv){
    const char* path=argc>1?argv[1]:"/tmp/xcvu13p.rdv";
    auto t0=clk::now();
    FILE*f=fopen(path,"rb"); if(!f){perror("open");return 1;}
    fseek(f,0,SEEK_END); long fsz=ftell(f); fseek(f,0,SEEK_SET);
    std::vector<uint8_t> buf(fsz); if(fread(buf.data(),1,fsz,f)!=(size_t)fsz){perror("read");return 1;} fclose(f);
    Rd rd{buf.data()};
    if((uint32_t)rd.i32()!=0x52445633u){ fprintf(stderr,"bad magic\n"); return 1; }
    int nRows=rd.i32(),nCols=rd.i32(),nTiles=rd.i32(),nT=rd.i32(),nPat=rd.i32();
    long expNodes=rd.i64(),expEdges=rd.i64();
    std::vector<int> typeWC(nT); std::vector<uint8_t> typeAllowed(nT);
    std::vector<std::vector<int16_t>> pS(nT),pE(nT); std::vector<std::vector<uint8_t>> pB(nT);
    for(int ti=0;ti<nT;ti++){ typeAllowed[ti]=rd.u8(); typeWC[ti]=rd.i32(); int np=rd.i32();
        pS[ti].resize(np); pE[ti].resize(np); pB[ti].resize(np);
        for(int p=0;p<np;p++){ pS[ti][p]=rd.i16(); pE[ti][p]=rd.i16(); pB[ti][p]=rd.u8(); } }
    // patterns: flattened conns + isBase bitset
    std::vector<int64_t> patOff(nPat+1,0); std::vector<int64_t> patData;
    std::vector<int64_t> baseOff(nPat+1,0); std::vector<uint8_t> baseData;
    for(int i=0;i<nPat;i++){ int cc=rd.i32(); patOff[i+1]=patOff[i]+cc; for(int c=0;c<cc;c++) patData.push_back(rd.i64());
        int bl=rd.i32(); baseOff[i+1]=baseOff[i]+bl; for(int b=0;b<bl;b++) baseData.push_back(rd.u8()); }
    std::vector<int16_t> tType(nTiles),tCol(nTiles),tRow(nTiles); std::vector<int32_t> tPat(nTiles);
    for(int a=0;a<nTiles;a++){ tType[a]=rd.i16(); tCol[a]=rd.i16(); tRow[a]=rd.i16(); tPat[a]=rd.i32(); }
    printf("LOAD: %.3fs file=%.2fMB grid=%dx%d nTiles=%d nT=%d nPat=%d exp nodes=%ld edges=%ld\n",
           sec(t0),fsz/1e6,nRows,nCols,nTiles,nT,nPat,expNodes,expEdges);

    auto t1=clk::now();
    std::vector<int> gridAddr((size_t)nRows*nCols,-1);
    for(int a=0;a<nTiles;a++) if(tType[a]>=0) gridAddr[(size_t)tRow[a]*nCols+tCol[a]]=a;
    std::vector<int64_t> wb(nTiles+1,0);
    for(int a=0;a<nTiles;a++){ int wc=tType[a]>=0?typeWC[tType[a]]:0; wb[a+1]=wb[a]+wc; }
    int64_t totW=wb[nTiles];
    printf("grid+wirebase: %.3fs totalWires=%ld\n",sec(t1),totW);

    // union-find from per-tile patterns
    auto t2=clk::now();
    par.resize(totW); for(int64_t i=0;i<totW;i++) par[i]=(int32_t)i; rnk.assign(totW,0);
    int64_t applied=0,oob=0;
    for(int a=0;a<nTiles;a++){ int pid=tPat[a]; if(pid<0) continue; int col=tCol[a],row=tRow[a]; int64_t base=wb[a];
        for(int64_t c=patOff[pid];c<patOff[pid+1];c++){ int64_t pk=patData[c];
            int w=(uint16_t)((pk>>48)&0xFFFF); int dx=(int16_t)((pk>>32)&0xFFFF); int dy=(int16_t)((pk>>16)&0xFFFF); int tw=(uint16_t)(pk&0xFFFF);
            int bc=col+dx, br=row+dy; if(bc<0||bc>=nCols||br<0||br>=nRows){ oob++; continue; }
            int ta=gridAddr[(size_t)br*nCols+bc]; if(ta<0){ oob++; continue; }
            unite((int32_t)(base+w),(int32_t)(wb[ta]+tw)); applied++; } }
    printf("union-find: %.3fs (%ld unions, %ld oob-skipped)\n",sec(t2),applied,oob);

    // seed routing-node ids ONLY from allowed-base wires (tile allowed AND pattern says w is node base)
    auto t3=clk::now();
    std::vector<int32_t> denseId(totW,-1); int64_t nNodes=0;
    std::vector<int64_t> baseKeyOf;   // dense id -> base key (tileAddr<<20|wire), for cross-check
    for(int a=0;a<nTiles;a++){ int ty=tType[a]; if(ty<0||!typeAllowed[ty]) continue; int pid=tPat[a]; if(pid<0) continue;
        int wc=typeWC[ty]; int64_t base=wb[a]; const uint8_t* bb=&baseData[baseOff[pid]];
        for(int w=0;w<wc;w++) if(bb[w>>3]&(1<<(w&7))){ int32_t r=find((int32_t)(base+w));
            if(denseId[r]<0){ denseId[r]=(int32_t)nNodes++; baseKeyOf.push_back(((int64_t)a<<20)|w); } } }
    printf("dense ids: %.3fs nNodes=%ld %s(exp %ld)\n",sec(t3),(long)nNodes,nNodes==expNodes?"OK ":"DIFF ",expNodes);
    auto nodeOf=[&](int a,int w)->int32_t{ return denseId[find((int32_t)(wb[a]+w))]; };

    // ---- VALIDATE-ATTRS: assemble NodeRec from compact .atc (template+exceptions+coords+hash formula)
    //      and compare EVERY field to the known-correct per-node .attrs (ATR1). Usage: --validateattrs <atc> <attrs>
    if(argc>4 && !strcmp(argv[2],"--validateattrs")){
        struct AA{ uint8_t type,flags4,valid; int16_t len,bxoff,byoff,exoff,eyoff; float bc; };
        // read .atc
        FILE* cf=fopen(argv[3],"rb"); if(!cf){perror("atc");return 1;}
        fseek(cf,0,SEEK_END); long cz=ftell(cf); fseek(cf,0,SEEK_SET);
        std::vector<uint8_t> cb(cz); if(fread(cb.data(),1,cz,cf)!=(size_t)cz){return 1;} fclose(cf);
        Rd cr{cb.data()}; if((uint32_t)cr.i32()!=0x41544331u){fprintf(stderr,"bad atc magic\n");return 1;}
        int aTiles=cr.i32();
        std::vector<int16_t> tX(aTiles),tY(aTiles);
        for(int a=0;a<aTiles;a++) tX[a]=cr.i16();
        for(int a=0;a<aTiles;a++) tY[a]=cr.i16();
        int nty=cr.i32(); std::unordered_map<int,std::vector<AA>> tmplByWC;
        for(int t=0;t<nty;t++){ cr.i32(); int wc=cr.i32(); std::vector<AA> v(wc);
            for(int w=0;w<wc;w++){ AA a{}; a.valid=cr.u8(); if(a.valid){ a.type=cr.u8(); a.len=cr.i16(); a.bxoff=cr.i16(); a.byoff=cr.i16(); a.exoff=cr.i16(); a.eyoff=cr.i16();
                int b=cr.i32(); memcpy(&a.bc,&b,4); a.flags4=cr.u8(); } v[w]=a; } tmplByWC[wc]=std::move(v); }
        int64_t nexc=cr.i64(); std::unordered_map<int64_t,AA> exc; exc.reserve(nexc*2);
        for(int64_t i=0;i<nexc;i++){ int64_t k=cr.i64(); AA a{}; a.valid=1; a.type=cr.u8(); a.len=cr.i16(); a.bxoff=cr.i16(); a.byoff=cr.i16(); a.exoff=cr.i16(); a.eyoff=cr.i16();
            int b=cr.i32(); memcpy(&a.bc,&b,4); a.flags4=cr.u8(); exc[k]=a; }
        printf("atc loaded: %d tiles, %d templates, %ld exceptions\n",aTiles,nty,(long)nexc);
        // read .attrs (ATR1) reference, compare on the fly
        FILE* af=fopen(argv[4],"rb"); if(!af){perror("attrs");return 1;}
        fseek(af,0,SEEK_END); long az=ftell(af); fseek(af,0,SEEK_SET);
        std::vector<uint8_t> ab(az); if(fread(ab.data(),1,az,af)!=(size_t)az){return 1;} fclose(af);
        Rd ar{ab.data()}; if((uint32_t)ar.i32()!=0x41545231u){fprintf(stderr,"bad attrs\n");return 1;}
        int64_t ac=ar.i64();
        long ok=0, badType=0,badFlags=0,badLen=0,badBX=0,badEX=0,badEY=0,badBC=0,badHash=0,noTmpl=0;
        for(int64_t i=0;i<ac;i++){ int64_t bk=ar.i64(); uint8_t rty=ar.u8(),rfl=ar.u8();
            int16_t rbx=ar.i16(),rby=ar.i16(),rex=ar.i16(),rey=ar.i16(),rln=ar.i16(); int32_t rbcb=ar.i32(); int32_t rhc=ar.i32();
            int tile=(int)(bk>>20), wire=(int)(bk&0xFFFFF);
            // assemble from .atc
            AA a; auto eit=exc.find(bk);
            if(eit!=exc.end()) a=eit->second;
            else { int ty=tile<nTiles?tType[tile]:-1; int wc=(ty>=0)?typeWC[ty]:-1; auto tit=tmplByWC.find(wc);
                   if(tit==tmplByWC.end()||wire>=(int)tit->second.size()||!tit->second[wire].valid){ noTmpl++; continue; } a=tit->second[wire]; }
            int abx=tX[tile]+a.bxoff, aby=tY[tile]+a.byoff, aex=tX[tile]+a.exoff, aey=tY[tile]+a.eyoff;
            int ahash=tile*31+wire+961;
            float rbc; memcpy(&rbc,&rbcb,4);
            bool good=true;
            if(a.type!=rty){badType++;good=false;} if((a.flags4)!=(rfl&0xF)){badFlags++;good=false;}
            if(a.len!=rln){badLen++;good=false;} if(abx!=rbx){badBX++;good=false;} if(aex!=rex){badEX++;good=false;}
            if(aey!=rey){badEY++;good=false;} if(memcmp(&a.bc,&rbc,4)){badBC++;good=false;} if(ahash!=rhc){badHash++;good=false;}
            if(good) ok++;
        }
        printf("VALIDATE-ATTRS: total=%ld  EXACT=%ld (%.4f%%)\n",(long)ac,ok,100.0*ok/ac);
        printf("  mismatches: type=%ld flags=%ld len=%ld beginX=%ld endX=%ld endY=%ld baseCost=%ld hash=%ld noTemplate=%ld\n",
               badType,badFlags,badLen,badBX,badEX,badEY,badBC,badHash,noTmpl);
        return 0;
    }

    // ---- DUMPFLAT mode: build srcIdOf + srcChildren CSR + per-node attrs, write one mmap-able flat
    //      file (FLT1) so the runtime loads with ZERO build (lazy page-in). Usage: <rdv> --dumpflat <attrs> <out>
    const char* dumpAttrs = (argc>3 && !strcmp(argv[2],"--dumpflat")) ? argv[3] : nullptr;
    const char* dumpOut   = (argc>4 && !strcmp(argv[2],"--dumpflat")) ? argv[4] : nullptr;
    if(dumpOut){
        auto tb=clk::now();
        std::vector<int32_t> rootSrcId(totW,-1); int32_t nSrc=0;
        auto mark=[&](int32_t r){ if(rootSrcId[r]<0) rootSrcId[r]=nSrc++; };
        for(int a=0;a<nTiles;a++){int ty=tType[a]; if(ty<0)continue; int np=pS[ty].size();
            for(int p=0;p<np;p++){ int32_t e=nodeOf(a,pE[ty][p]); if(e>=0) mark(find((int32_t)(wb[a]+pS[ty][p])));
                if(pB[ty][p]){int32_t s=nodeOf(a,pS[ty][p]); if(s>=0) mark(find((int32_t)(wb[a]+pE[ty][p])));} } }
        std::vector<int64_t> deg(nSrc,0);
        for(int a=0;a<nTiles;a++){int ty=tType[a]; if(ty<0)continue; int np=pS[ty].size();
            for(int p=0;p<np;p++){ int32_t e=nodeOf(a,pE[ty][p]); if(e>=0) deg[rootSrcId[find((int32_t)(wb[a]+pS[ty][p]))]]++;
                if(pB[ty][p]){int32_t s=nodeOf(a,pS[ty][p]); if(s>=0) deg[rootSrcId[find((int32_t)(wb[a]+pE[ty][p]))]]++;} } }
        std::vector<int64_t> srcOff(nSrc+1,0); for(int i=0;i<nSrc;i++) srcOff[i+1]=srcOff[i]+deg[i];
        std::vector<int32_t> srcKids(srcOff[nSrc]); std::vector<int64_t> cur(srcOff.begin(),srcOff.end()-1);
        for(int a=0;a<nTiles;a++){int ty=tType[a]; if(ty<0)continue; int np=pS[ty].size();
            for(int p=0;p<np;p++){ int32_t e=nodeOf(a,pE[ty][p]); if(e>=0) srcKids[cur[rootSrcId[find((int32_t)(wb[a]+pS[ty][p]))]]++]=e;
                if(pB[ty][p]){int32_t s=nodeOf(a,pS[ty][p]); if(s>=0) srcKids[cur[rootSrcId[find((int32_t)(wb[a]+pE[ty][p]))]]++]=s;} } }
        std::vector<int32_t> srcIdOf(totW);
        for(int64_t w=0;w<totW;w++) srcIdOf[w]=rootSrcId[find((int32_t)w)];
        printf("flat build: %.3fs nSrc=%d kids=%ld\n",sec(tb),nSrc,(long)srcKids.size());
        // per-node AoS records from ATR1 (one contiguous 32B record per node = cache-friendly child reads)
        std::vector<NodeRec> nrec(nNodes);
        for(int64_t id=0;id<nNodes;id++){ nrec[id]=NodeRec{}; nrec[id].baseKey=baseKeyOf[id]; }
        { FILE* af=fopen(dumpAttrs,"rb"); if(!af){perror("attrs");return 1;}
          fseek(af,0,SEEK_END); long az=ftell(af); fseek(af,0,SEEK_SET);
          std::vector<uint8_t> ab(az); if(fread(ab.data(),1,az,af)!=(size_t)az){return 1;} fclose(af);
          Rd ar{ab.data()}; if((uint32_t)ar.i32()!=0x41545231u){fprintf(stderr,"bad attrs\n");return 1;}
          int64_t ac=ar.i64();
          for(int64_t i=0;i<ac;i++){ int64_t bk=ar.i64(); uint8_t ty=ar.u8(),fl=ar.u8();
            int16_t bx=ar.i16(),by=ar.i16(),ex=ar.i16(),ey=ar.i16(),ln=ar.i16(); int32_t bcb=ar.i32(); int32_t hc=ar.i32();
            int ptile=(int)(bk>>20),pw=(int)(bk&0xFFFFF);
            int32_t id=(ptile>=0&&ptile<nTiles&&tType[ptile]>=0&&pw<typeWC[tType[ptile]])?nodeOf(ptile,pw):-1;
            if(id<0)continue; NodeRec&R=nrec[id]; R.type=ty;R.flags4=fl;R.bx=bx;R.by=by;R.ex=ex;R.ey=ey;R.len=ln;R.hash=hc;
            memcpy(&R.baseCost,&bcb,4); } }
        // write FLT2 (native-endian, 8-aligned). header: magic,nTiles,nNodes,totW,nSrc + 5 array byte-offsets
        FILE* o=fopen(dumpOut,"wb"); if(!o){perror("out");return 1;}
        auto wr=[&](const void*p,size_t n){ fwrite(p,1,n,o); size_t pad=(8-(n&7))&7; uint64_t z=0; if(pad) fwrite(&z,1,pad,o); };
        uint64_t hdr[16]={0x32544C46u,(uint64_t)nTiles,(uint64_t)nNodes,(uint64_t)totW,(uint64_t)nSrc};
        fwrite(hdr,sizeof(uint64_t),16,o);  // 16 slots: 5 meta + 5 offsets
        std::vector<uint64_t> off;
        auto put=[&](const void*p,size_t n){ off.push_back((uint64_t)ftell(o)); wr(p,n); };
        put(wb.data(),(nTiles+1)*8);
        put(srcIdOf.data(),(size_t)totW*4);
        put(srcOff.data(),(size_t)(nSrc+1)*8);
        put(srcKids.data(),srcKids.size()*4);
        put(nrec.data(),(size_t)nNodes*sizeof(NodeRec));
        fseek(o,5*sizeof(uint64_t),SEEK_SET); fwrite(off.data(),sizeof(uint64_t),off.size(),o);
        fclose(o);
        printf("WROTE FLAT(AoS) %s %.2f GB (NodeRec=%zuB)\n",dumpOut,(double)off.back()/1e9,sizeof(NodeRec));
        return 0;
    }

    // ---- CROSS-CHECK mode: compare device-model children (by key) vs Java getChildrenPacked dump ----
    // dump format (big-endian): repeated { parentKey:i64, cnt:i32, childKey[cnt]:i64 }
    const char* checkPath = (argc>2 && !strcmp(argv[2],"--check") && argc>3) ? argv[3] : nullptr;
    if(checkPath){
        FILE* cf=fopen(checkPath,"rb"); if(!cf){ perror("check open"); return 1; }
        fseek(cf,0,SEEK_END); long cz=ftell(cf); fseek(cf,0,SEEK_SET);
        std::vector<uint8_t> cb(cz); if(fread(cb.data(),1,cz,cf)!=(size_t)cz){perror("read");return 1;} fclose(cf);
        // collect each dumped parent's component root -> getChildren works for ANY node (routing OR source pin)
        std::unordered_map<int32_t,std::vector<int64_t>> kidsByRoot;   // root -> child base keys
        std::vector<std::pair<int64_t,int32_t>> parents;               // (parentKey, root)
        std::vector<std::vector<int64_t>> javaKidsAll;
        { Rd cr{cb.data()}; const uint8_t* cend=cb.data()+cz;
          while(cr.p<cend){ int64_t pk=cr.i64(); int cnt=cr.i32(); std::vector<int64_t> jk(cnt);
            for(int i=0;i<cnt;i++) jk[i]=cr.i64();
            int ptile=(int)(pk>>20), pw=(int)(pk&0xFFFFF);
            int32_t root=-1;
            if(ptile>=0&&ptile<nTiles&&tType[ptile]>=0&&pw<typeWC[tType[ptile]]) root=find((int32_t)(wb[ptile]+pw));
            parents.push_back({pk,root}); javaKidsAll.push_back(std::move(jk));
            if(root>=0) kidsByRoot.emplace(root,std::vector<int64_t>()); } }
        // one PIP pass: for each PIP, attribute child (allowed dst) to its SRC component root (incl. pins)
        for(int a=0;a<nTiles;a++){ int ty=tType[a]; if(ty<0) continue; int np=pS[ty].size();
            for(int p=0;p<np;p++){ int sw=pS[ty][p], ew=pE[ty][p];
                int32_t sr=find((int32_t)(wb[a]+sw)); int32_t e=nodeOf(a,ew);
                if(e>=0){ auto it=kidsByRoot.find(sr); if(it!=kidsByRoot.end()) it->second.push_back(baseKeyOf[e]); }
                if(pB[ty][p]){ int32_t er=find((int32_t)(wb[a]+ew)); int32_t s2=nodeOf(a,sw);
                    if(s2>=0){ auto it=kidsByRoot.find(er); if(it!=kidsByRoot.end()) it->second.push_back(baseKeyOf[s2]); } } } }
        long nodes=0, okNodes=0, missing=0, extra=0, badParent=0;
        for(size_t i=0;i<parents.size();i++){ nodes++;
            int32_t root=parents[i].second;
            if(root<0){ badParent++; continue; }
            std::vector<int64_t> dev=kidsByRoot[root];
            std::sort(dev.begin(),dev.end()); dev.erase(std::unique(dev.begin(),dev.end()),dev.end());
            std::vector<int64_t> jk=javaKidsAll[i];
            std::sort(jk.begin(),jk.end()); jk.erase(std::unique(jk.begin(),jk.end()),jk.end());
            if(dev==jk) okNodes++;
            else { for(int64_t k:jk) if(!std::binary_search(dev.begin(),dev.end(),k)) missing++;
                   for(int64_t k:dev) if(!std::binary_search(jk.begin(),jk.end(),k)) extra++; }
        }
        printf("CROSS-CHECK (any parent: routing+source): nodes=%ld exact=%ld (%.4f%%)  missing-kids=%ld extra-kids=%ld badParent=%ld\n",
               nodes, okNodes, 100.0*okNodes/nodes, missing, extra, badParent);
        return 0;
    }

    // adjacency CSR (parallel) via per-type PIPs
    std::vector<std::atomic<int32_t>> deg(nNodes);
    std::vector<int64_t> rowPtr(nNodes+1); std::vector<int32_t> colIdx;
    int hw=std::thread::hardware_concurrency(); int tries[]={1,24,96}; int64_t rawEdges=0;
    for(int k=0;k<3;k++){ int T=tries[k]; if(T>hw)T=hw; auto ta=clk::now();
        for(auto&d:deg) d.store(0,std::memory_order_relaxed);
        auto A=[&](int a0,int a1){ for(int a=a0;a<a1;a++){ int ty=tType[a]; if(ty<0) continue; int np=pS[ty].size();
            for(int p=0;p<np;p++){ int32_t s=nodeOf(a,pS[ty][p]); if(s<0) continue; int32_t e=nodeOf(a,pE[ty][p]); if(e<0) continue;
                deg[s].fetch_add(1,std::memory_order_relaxed); if(pB[ty][p]) deg[e].fetch_add(1,std::memory_order_relaxed);} } };
        { std::vector<std::thread> th; int ch=(nTiles+T-1)/T; for(int t=0;t<T;t++) th.emplace_back(A,t*ch,std::min(nTiles,(t+1)*ch)); for(auto&x:th)x.join(); }
        double tA=sec(ta); auto tf=clk::now();
        rowPtr[0]=0; for(int64_t i=0;i<nNodes;i++) rowPtr[i+1]=rowPtr[i]+deg[i].load(std::memory_order_relaxed);
        rawEdges=rowPtr[nNodes]; if((int64_t)colIdx.size()<rawEdges) colIdx.resize(rawEdges);
        std::vector<std::atomic<int64_t>> cur(nNodes); for(int64_t i=0;i<nNodes;i++) cur[i].store(rowPtr[i],std::memory_order_relaxed);
        auto B=[&](int a0,int a1){ for(int a=a0;a<a1;a++){ int ty=tType[a]; if(ty<0) continue; int np=pS[ty].size();
            for(int p=0;p<np;p++){ int32_t s=nodeOf(a,pS[ty][p]); if(s<0) continue; int32_t e=nodeOf(a,pE[ty][p]); if(e<0) continue;
                colIdx[cur[s].fetch_add(1,std::memory_order_relaxed)]=e; if(pB[ty][p]) colIdx[cur[e].fetch_add(1,std::memory_order_relaxed)]=s;} } };
        { std::vector<std::thread> th; int ch=(nTiles+T-1)/T; for(int t=0;t<T;t++) th.emplace_back(B,t*ch,std::min(nTiles,(t+1)*ch)); for(auto&x:th)x.join(); }
        printf("ADJ T=%-2d: degree %.3fs + fill %.3fs = %.3fs rawEdges=%ld\n",T,tA,sec(tf),tA+sec(tf),(long)rawEdges);
    }
    auto tdd=clk::now(); std::atomic<int64_t> distinct{0}; int T=hw;
    auto dd=[&](int64_t n0,int64_t n1){ int64_t loc=0; for(int64_t n=n0;n<n1;n++){ int64_t b=rowPtr[n],e=rowPtr[n+1];
        std::sort(colIdx.begin()+b,colIdx.begin()+e); int64_t u=(e>b)?1:0; for(int64_t i=b+1;i<e;i++) if(colIdx[i]!=colIdx[i-1])u++; loc+=u;} distinct.fetch_add(loc); };
    { std::vector<std::thread> th; int64_t ch=(nNodes+T-1)/T; for(int t=0;t<T;t++) th.emplace_back(dd,(int64_t)t*ch,std::min(nNodes,(int64_t)(t+1)*ch)); for(auto&x:th)x.join(); }
    printf("dedup: %.3fs distinctEdges=%ld %s(exp %ld)\n",sec(tdd),(long)distinct.load(),distinct.load()==expEdges?"OK ":"DIFF ",expEdges);
    printf("PEAK RSS: %.2f GB\n",rssKB()/1.048576e6);
    return 0;
}
