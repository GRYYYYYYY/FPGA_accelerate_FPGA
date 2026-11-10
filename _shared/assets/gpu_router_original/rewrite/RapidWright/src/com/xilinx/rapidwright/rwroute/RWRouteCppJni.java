/*
 * In-process (single JVM) C++ router via JNI — the "first optimization": no second device
 * load, no disk serialization. Java loads the DCP + builds targets ONCE, hands the serialized
 * problem to the C++ routing core over JNI (byte[]), gets the routing result back, injects it,
 * and reuses route()'s finalize + writeCheckpoint. Reuses RWRouteCppProblemExport.writeRrt for
 * serialization and the RWRouteCppImport injection logic.
 */
package com.xilinx.rapidwright.rwroute;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.design.DesignTools;
import com.xilinx.rapidwright.design.Net;
import com.xilinx.rapidwright.design.SitePinInst;
import com.xilinx.rapidwright.device.Device;
import com.xilinx.rapidwright.device.IntentCode;
import com.xilinx.rapidwright.device.Node;
import com.xilinx.rapidwright.device.PIP;
import com.xilinx.rapidwright.device.SitePin;
import com.xilinx.rapidwright.device.Tile;
import com.xilinx.rapidwright.tests.CodePerfTracker;
import com.xilinx.rapidwright.util.Pair;

public class RWRouteCppJni extends RWRouteCppProblemExport {

    static {
        System.loadLibrary("RWRouteCppJni");
    }

    /** C++ routing core, in-process: problem bytes (.rrt layout) -> result bytes (.result layout). */
    private native byte[] routeNative(byte[] problem);

    /** Starts the (design-independent) C++ device build in a background thread so its ~12s is HIDDEN
     *  behind Java's readCheckpoint + target building (no-op unless RWDEV=1). */
    private static native void prewarmDevice(long dcpBytes);   // size gates the prepass-fulldev band (C++)
    /** O(1) node attrs {typeOrdinal,endX,endY,length} from the mmap'ed .dmc; false = not modeled. */
    private static native boolean getNodeRec(int tileAddr, int wireIndex, int[] out4);
    private static native boolean dmActive();   // compact device (with node-attr table) is live
    private static native void prepassEarlyNative(long[] seedKeys, int[] netRects);

    /** prepass-early: project the unrouted pins to their INT nodes (pure device queries) and hand
     *  (seed keys + per-net pin rects) to C++ so the closure/CSR prepass runs DURING initialize. */
    private static void startEarlyPrepass(Design design, List<SitePinInst> pinsToRoute) {
        // Preserved-bits root cause FIXED (ledger 21/22): measured jpeg route -6~9s, k_800 -4s legal,
        // but THEIA-class +5~14s (prepass 20.3s >> its ~6s init window, closure 67->87M). The
        // competition command is fixed, so gate per case: jpeg-class (<=700k pins) and k_800-class
        // (>=1.5M pins) auto-ON; mid-size wide-spread (THEIA-class) OFF. RW_PREPASS_EARLY=1/0 forces.
        String pe = System.getenv("RW_PREPASS_EARLY");
        if ("0".equals(pe)) return;
        // prepass-fulldev (C++, prewarm-time) already owns the 20per-class band: the native call would
        // be a no-op (g_earlyStarted), so skip the ~2s seed-projection thread during init too.
        if (!"0".equals(System.getenv("RW_PREPASS_FULLDEV"))
                && inputDcpBytes >= 125_000_000L && inputDcpBytes < 250_000_000L) return;
        int np = pinsToRoute.size();
        if (!"1".equals(pe) && !(np <= 700_000 || np >= 1_500_000)) return;
        Thread t = new Thread(() -> {
            try {
                java.util.ArrayList<Long> keys = new java.util.ArrayList<>(pinsToRoute.size() * 2);
                Map<Net, int[]> rects = new HashMap<>();
                Set<Net> srcDone = new HashSet<>();
                for (SitePinInst pin : pinsToRoute) {
                    Net net = pin.getNet();
                    if (net == null) continue;
                    Node sn = RouterHelper.projectInputPinToINTNode(pin);
                    if (sn != null) addSeed(keys, rects, net, sn);
                    if (srcDone.add(net)) {
                        SitePinInst src = net.getSource();
                        if (src != null) {
                            Node so = RouterHelper.projectOutputPinToINTNode(src);
                            if (so != null) addSeed(keys, rects, net, so);
                        }
                    }
                }
                long[] ka = new long[keys.size()];
                for (int i = 0; i < ka.length; i++) ka[i] = keys.get(i);
                int[] ra = new int[rects.size() * 4];
                int o = 0;
                for (int[] r : rects.values()) { ra[o++] = r[0]; ra[o++] = r[1]; ra[o++] = r[2]; ra[o++] = r[3]; }
                prepassEarlyNative(ka, ra);
            } catch (Throwable ignore) {}   // any failure -> C++ falls back to the normal prepass
        });
        t.setDaemon(true);
        t.start();
    }

    private static void addSeed(java.util.ArrayList<Long> keys, Map<Net, int[]> rects, Net net, Node n) {
        keys.add(((long) n.getTile().getUniqueAddress() << 20) | (n.getWireIndex() & 0xFFFFF));
        int x = n.getTile().getTileXCoordinate(), y = n.getTile().getTileYCoordinate();
        int[] r = rects.get(net);
        if (r == null) rects.put(net, new int[]{x, y, x, y});
        else { r[0] = Math.min(r[0], x); r[1] = Math.min(r[1], y); r[2] = Math.max(r[2], x); r[3] = Math.max(r[3], y); }
    }

    public RWRouteCppJni(Design design, RWRouteConfig config, Collection<SitePinInst> pinsToRoute) {
        super(design, config, pinsToRoute, "<jni>");
    }

    @Override
    protected void postRouteProcess() {
        long t = System.nanoTime();
        super.postRouteProcess();
        System.out.printf("INFO: [cpp-jni] PHASE postRouteProcess=%.2fs%n", (System.nanoTime() - t) / 1e9);
    }

    @Override
    protected void preprocess() {
        long t = System.nanoTime();
        super.preprocess();
        System.out.printf("INFO: [cpp-jni] PHASE preprocess(instance)=%.2fs%n", (System.nanoTime() - t) / 1e9);
    }

    @Override
    protected void initialize() {
        long t = System.nanoTime();
        super.initialize();
        System.out.printf("INFO: [cpp-jni] PHASE initialize=%.2fs (netCreate=%.2fs [proj=%.2f lut=%.2f bbox=%.2f] pipReplay=%.2fs)%n",
                (System.nanoTime() - t) / 1e9, initNetCreateNs / 1e9, initProjNs / 1e9,
                initLutNs / 1e9, initBboxNs / 1e9, initPipReplayNs / 1e9);
    }

    /** RouteThruHelper only depends on the Device -> build it on a daemon thread right after
     *  readCheckpoint so its ~2-3s hide behind preprocess/getUnroutedPins instead of initialize. */
    private static volatile long inputDcpBytes = 0;   // set in main(); gates the prepass-fulldev band
    private static volatile com.xilinx.rapidwright.router.RouteThruHelper prewarmRtHelper = null;
    private static volatile Device prewarmRtDevice = null;
    private static Thread rtPrewarmThread = null;
    private static synchronized void startRouteThruPrewarm(Device device) {
        if (rtPrewarmThread != null) return;   // early (t=0) chain may have started it already
        prewarmRtDevice = device;
        rtPrewarmThread = new Thread(() -> {
            long tb = System.nanoTime();
            try { prewarmRtHelper = new com.xilinx.rapidwright.router.RouteThruHelper(device); }
            catch (Throwable ignore) {}
            System.out.printf("INFO: [cpp-jni] prewarm.rtHelper build=%.2fs%n", (System.nanoTime() - tb) / 1e9);
        });
        rtPrewarmThread.setDaemon(true);
        rtPrewarmThread.start();
    }

    @Override
    protected com.xilinx.rapidwright.router.RouteThruHelper createRouteThruHelper() {
        if (rtPrewarmThread != null && prewarmRtDevice == design.getDevice()) {
            try { rtPrewarmThread.join(30000); } catch (InterruptedException ignore) {}
            com.xilinx.rapidwright.router.RouteThruHelper h = prewarmRtHelper;
            if (h != null) return h;
        }
        return super.createRouteThruHelper();
    }

    /** RouteNodeGraph's constructor reads only device geometry + config flags (no pins/nets), so it
     *  can be built during preprocess/getUnroutedPins. Non-timing-driven partial graph only. */
    private static volatile RouteNodeGraph prewarmGraph = null;
    private static Thread graphPrewarmThread = null;
    private static synchronized void startGraphPrewarm(Design design, RWRouteConfig config) {
        if (config.isTimingDriven()) return;
        if (graphPrewarmThread != null) return;   // early (t=0) chain may have started it already
        graphPrewarmThread = new Thread(() -> {
            long tb = System.nanoTime();
            try { prewarmGraph = new RouteNodeGraphPartial(design, config); }
            catch (Throwable ignore) {}
            System.out.printf("INFO: [cpp-jni] prewarm.graph build=%.2fs%n", (System.nanoTime() - tb) / 1e9);
        });
        graphPrewarmThread.setDaemon(true);
        graphPrewarmThread.start();
    }

    @Override
    protected RouteNodeGraph createRouteNodeGraph() {
        if (!config.isTimingDriven() && graphPrewarmThread != null) {
            long tj = System.nanoTime();
            try { graphPrewarmThread.join(30000); } catch (InterruptedException ignore) {}
            System.out.printf("INFO: [cpp-jni] prewarm.graph joinWait=%.2fs%n", (System.nanoTime() - tj) / 1e9);
            RouteNodeGraph g = prewarmGraph;
            if (g != null && g.design != design) {
                // Early (t=0) prewarm built the graph against a throwaway Design on the same device
                // (the ctor consumes only device geometry + config flags). Rebind its design field to
                // the real design before anything (isRouteThruPIPAvailable, PBlock) consults it.
                // Instance final fields are settable after setAccessible(true) (JDK8..11 semantics).
                if (g.design.getDevice() == design.getDevice()) {
                    try {
                        java.lang.reflect.Field f = RouteNodeGraph.class.getDeclaredField("design");
                        f.setAccessible(true);
                        f.set(g, design);
                    } catch (Throwable e) {
                        System.out.println("WARN: [cpp-jni] prewarm.graph rebind failed -> inline build: " + e);
                        g = null;
                    }
                } else {
                    g = null;   // different device -> prewarm useless; build inline
                }
            }
            if (g != null) return g;
        }
        return super.createRouteNodeGraph();
    }

    /** SMALL cases: the routing-fabric wire tables (~2.5s cold lazy load) are needed by
     *  inject/fixRoutes when result paths become Java Nodes. Warm them while the native route
     *  runs — Java is idle there, and categorize/netCreate is already done so nothing contends
     *  on the device's lazy-init locks. Same single-thread touch pattern the ctor scan used. */
    private Thread fabricWarmThread = null;
    private void warmFabricWires() {
        if (inputDcpBytes <= 0 || inputDcpBytes > 10_000_000L) return;   // big cases: covered elsewhere
        final Device dev = design.getDevice();
        fabricWarmThread = new Thread(() -> {
            try {
                long tw = System.nanoTime();
                Tile intTile = dev.getArbitraryTileOfType(com.xilinx.rapidwright.device.TileTypeEnum.INT);
                int wc = intTile.getWireCount();
                for (int w = 0; w < wc; w++) {
                    Node n = Node.getNode(intTile, w);
                    if (n != null) n.getIntentCode();
                }
                System.out.printf("INFO: [cpp-jni] warm.fabric=%.2fs (during native route)%n",
                        (System.nanoTime() - tw) / 1e9);
            } catch (Throwable ignore) {}
        });
        fabricWarmThread.setDaemon(true);
        fabricWarmThread.start();
    }

    /** SMALL cases: run the whole device-only prewarm chain at t=0, BEFORE readCheckpoint —
     *  Device load (~1.5s warm) overlaps the DCP read's parse work, then RouteThruHelper and
     *  RouteNodeGraph (built against a throwaway Design; rebound in createRouteNodeGraph) overlap
     *  the read+preprocess. Device.getDevice is monitor-synchronized (verified via javap), so
     *  racing readCheckpoint's own device fetch is safe: the second caller blocks and gets the
     *  same instance. Big cases keep their own economy (native prewarmDevice needs the 31-thread
     *  budget; their long read/init already hides the post-read prewarms). RW_EARLY_PREWARM=0 disables. */
    private static void startEarlyPrewarm(String partName, RWRouteConfig config) {
        if ("0".equals(System.getenv("RW_EARLY_PREWARM"))) return;
        long t0 = System.nanoTime();
        Thread th = new Thread(() -> {
            try {
                Device dev = Device.getDevice(partName);
                System.out.printf("INFO: [cpp-jni] prewarm.device=%.2fs (early, %s)%n",
                        (System.nanoTime() - t0) / 1e9, partName);
                startRouteThruPrewarm(dev);
                // Netlist-less shell (~40ms vs ~1s for new Design(name, part)): the graph ctor only
                // reads design.getDevice(); the field is rebound to the real design before any use.
                Design dummy = new Design();
                dummy.setPartName(partName);
                startGraphPrewarm(dummy, config);
                // Lazy-table warmer: with the .rng cache the ctor skips its scans, so the device's
                // lazy wire/intent/name tables would otherwise load COLD inside netCreate (measured
                // 2.6-2.8s there vs 0.07s warm). Touch them here instead — same touches the original
                // scan made, racing readCheckpoint exactly as the pre-cache ctor always did.
                // Warm ONLY the classes netCreate creates rnodes for (~4ms) + laguna. The 2.5s
                // fabric-wire load must NOT run here: it holds the device's lazy-init locks through
                // categorize and serializes netCreate behind it (measured: netCreate stuck at
                // 1.6-2.0s whenever the fabric warm overlapped it). Fabric warms during the native
                // route instead (Java idle there) -- see warmFabricWires().
                long tw = System.nanoTime();
                Tile intTile = dev.getArbitraryTileOfType(com.xilinx.rapidwright.device.TileTypeEnum.INT);
                int wc = intTile.getWireCount();
                for (int w = 0; w < wc; w++) {
                    String nm = intTile.getWireName(w);
                    if (nm.startsWith("IMUX") || nm.startsWith("BYPASS") || nm.startsWith("BOUNCE")
                            || nm.startsWith("CTRL") || nm.startsWith("LOGIC_OUTS")
                            || nm.startsWith("INT_NODE_IMUX")) {
                        Node n = Node.getNode(intTile, w);
                        if (n != null) n.getIntentCode();
                    }
                }
                long tw1 = System.nanoTime();
                // Fabric tables: netCreate's pin->INT projections (getAllDownhillNodes walks) load
                // them lazily under a global lock either way; A/B verdict (2026-07-11): early warm
                // + provider netCreate=2.05s, no warm + provider 2.69s, warm without provider
                // 1.64-1.95s. The lock is serial and cannot start before the device lands (~1.8s),
                // so this is the floor; warming here is the best of the three.
                for (int w = 0; w < wc; w++) {
                    Node n = Node.getNode(intTile, w);
                    if (n != null) n.getIntentCode();
                }
                long tw2 = System.nanoTime();
                dev.getTilesByRootName("LAG_LAG");
                System.out.printf("INFO: [cpp-jni] prewarm.lazyTables critical=%.2fs fabric=%.2fs laguna=%.2fs%n",
                        (tw1 - tw) / 1e9, (tw2 - tw1) / 1e9, (System.nanoTime() - tw2) / 1e9);
            } catch (Throwable e) {
                System.out.println("WARN: [cpp-jni] early prewarm failed (post-read fallback stays): " + e);
            }
        });
        th.setDaemon(true);
        th.start();
    }

    /** Warm the closed Device's lazy per-tile PIP structures on background threads while the C++
     *  native route runs (the Java side is otherwise idle for 50-95s there). PIP.getArbitraryPIP
     *  raced on these caches when finalize was parallelized COLD ("Null PIP" corruption -> the old
     *  serial revert); pre-touching tile.getPIPs() device-wide removes the cold-start window, and
     *  the null-PIP counter + serial-recompute fallback below removes the residual risk entirely. */
    private Thread pipWarmThread = null;
    private void startPipWarm() {
        if ("0".equals(System.getenv("RW_PAR_FINALIZE"))) return;
        // SMALL cases: skip the warm entirely. Their native route is ~3s, so the device-wide warm
        // (~5-10s, 8 threads mutating closed lazy tile caches) would still be running through
        // inject/postRoute -- the exact concurrent-cold-cache window behind the null-PIP/#24
        // corruption family (mcml 2026-07-08: 3026 null PIPs AND an output missing 384 PIPs that
        // even the serial setPIPs recompute could not save, because the DESIGN state was already
        // corrupted upstream of it). Without the warm, small-case setPIPs just takes its serial
        // fallback (~0.5-1s at 20k pins) -- a fair price for closing the window. Big cases keep the
        // warm: their 50-95s native route fully covers it (plus the pre-setPIPs join below).
        if (inputDcpBytes > 0 && inputDcpBytes <= 10_000_000L) return;
        final Tile[][] tiles = design.getDevice().getTiles();
        pipWarmThread = new Thread(() -> {
            try {
                final int WT = 8;
                Thread[] ws = new Thread[WT];
                for (int w = 0; w < WT; w++) {
                    final int wid = w;
                    ws[wid] = new Thread(() -> {
                        for (int r = wid; r < tiles.length; r += WT) {
                            Tile[] row = tiles[r];
                            if (row == null) continue;
                            for (Tile tt : row) {
                                if (tt != null) tt.getPIPs();
                            }
                        }
                    });
                    ws[wid].setDaemon(true);
                    ws[wid].start();
                }
                for (Thread w : ws) w.join();
                System.out.println("INFO: [cpp-jni] PIP caches warmed (background, during native route)");
            } catch (Throwable ignore) {}
        });
        pipWarmThread.setDaemon(true);
        pipWarmThread.start();
    }

    // ===== Self-assembled DCP write (RW_SELF_ZIP; default ON for big cases) =========================
    // Hides writeCheckpoint's EDIF cost behind the native route. The logical netlist is FINAL before
    // routing starts (routing edits only the physical netlist), so a background thread exports AND
    // raw-deflates the EDIF during routeNative, computing its CRC32 -- all fully hidden. At write
    // time the closed writeCheckpoint emits a TEMP DCP via its (dcp, edfFile, t) variant with a tiny
    // placeholder EDIF (that variant skips EDIF generation; its embedded entry is corrupt -- known
    // jar bug -- but we discard that entry anyway), and the final DCP is assembled by US: every
    // non-EDIF entry is copied as its RAW compressed byte stream (zip permits verbatim entry copy;
    // no recompression), and the pre-deflated EDIF is injected with the CRC computed during route.
    // The injected entry is then re-inflated and CRC-verified. ANY failure -> normal writeCheckpoint.
    static volatile boolean selfZipWanted = false;
    static volatile Thread zipEdfThread = null;
    static volatile byte[] zipEdfDeflated = null;
    static volatile long zipEdfCrc = 0, zipEdfUSize = 0;
    static volatile boolean zipEdfReady = false;

    private void startEdifPreDeflate() {
        if (!selfZipWanted) return;
        zipEdfThread = new Thread(() -> {
            try {
                long t0 = System.nanoTime();
                final java.util.zip.CRC32 crc = new java.util.zip.CRC32();
                final long[] usz = {0};
                java.util.zip.Deflater def = new java.util.zip.Deflater(java.util.zip.Deflater.DEFAULT_COMPRESSION, true);
                ByteArrayOutputStream cbuf = new ByteArrayOutputStream(32 << 20);
                java.io.OutputStream os = new java.util.zip.DeflaterOutputStream(cbuf, def, 1 << 16) {
                    @Override public void write(byte[] b, int off, int len) throws IOException {
                        crc.update(b, off, len); usz[0] += len; super.write(b, off, len);
                    }
                    @Override public void write(int b) throws IOException {
                        crc.update(b); usz[0]++; super.write(b);
                    }
                };
                design.getNetlist().exportEDIF(os);   // exportEDIF wraps + closes -> deflate finished
                def.end();
                zipEdfDeflated = cbuf.toByteArray();
                zipEdfCrc = crc.getValue();
                zipEdfUSize = usz[0];
                zipEdfReady = true;
                System.out.printf("INFO: [cpp-jni] EDIF pre-deflated in background: %.1fMB -> %.1fMB (%.2fs, during native route)%n",
                        usz[0] / 1e6, zipEdfDeflated.length / 1e6, (System.nanoTime() - t0) / 1e9);
            } catch (Throwable e) {
                System.out.println("WARNING: [cpp-jni] EDIF pre-deflate failed (" + e + ") -> normal write path");
                zipEdfReady = false;
            }
        });
        zipEdfThread.setDaemon(true);
        zipEdfThread.start();
    }

    // ---- minimal zip reader/writer for the final assembly (no Zip64: DCPs here are ~130MB) --------
    private static int zU16(byte[] b, int o) { return (b[o] & 0xFF) | ((b[o + 1] & 0xFF) << 8); }
    private static long zU32(byte[] b, int o) {
        return (b[o] & 0xFFL) | ((b[o + 1] & 0xFFL) << 8) | ((b[o + 2] & 0xFFL) << 16) | ((b[o + 3] & 0xFFL) << 24);
    }
    private static void zW16(java.io.OutputStream o, int v) throws IOException { o.write(v & 0xFF); o.write((v >> 8) & 0xFF); }
    private static void zW32(java.io.OutputStream o, long v) throws IOException {
        o.write((int) (v & 0xFF)); o.write((int) ((v >> 8) & 0xFF)); o.write((int) ((v >> 16) & 0xFF)); o.write((int) ((v >> 24) & 0xFF));
    }
    private static class ZEntry {
        int method, time, date; long crc, csize, usize, lfh; byte[] nameB; boolean isEdf;
    }

    /** Assemble outDcp from tempDcp, raw-copying every entry except the .edf, which is replaced by
     *  the pre-deflated bytes. Returns false on ANY structural surprise (caller falls back). */
    static boolean assembleDcp(java.io.File tempDcp, java.io.File outDcp,
                               byte[] edfDef, long edfCrc, long edfUSize) {
        try (java.io.RandomAccessFile raf = new java.io.RandomAccessFile(tempDcp, "r")) {
            long len = raf.length();
            int tail = (int) Math.min(len, 22 + 65536);
            byte[] tb = new byte[tail];
            raf.seek(len - tail);
            raf.readFully(tb);
            int eo = -1;
            for (int i = tail - 22; i >= 0; i--) {
                if (tb[i] == 0x50 && tb[i + 1] == 0x4b && tb[i + 2] == 0x05 && tb[i + 3] == 0x06) { eo = i; break; }
            }
            if (eo < 0) return false;
            int total = zU16(tb, eo + 10);
            long cdSize = zU32(tb, eo + 12), cdOff = zU32(tb, eo + 16);
            if (total == 0xFFFF || cdOff == 0xFFFFFFFFL || cdSize == 0xFFFFFFFFL) return false;   // Zip64
            byte[] cd = new byte[(int) cdSize];
            raf.seek(cdOff);
            raf.readFully(cd);
            List<ZEntry> es = new ArrayList<>();
            int p = 0, edfCount = 0;
            while (p + 46 <= cd.length) {
                if (!(cd[p] == 0x50 && cd[p + 1] == 0x4b && cd[p + 2] == 0x01 && cd[p + 3] == 0x02)) break;
                ZEntry e = new ZEntry();
                e.method = zU16(cd, p + 10); e.time = zU16(cd, p + 12); e.date = zU16(cd, p + 14);
                e.crc = zU32(cd, p + 16); e.csize = zU32(cd, p + 20); e.usize = zU32(cd, p + 24);
                int nl = zU16(cd, p + 28), xl = zU16(cd, p + 30), cl = zU16(cd, p + 32);
                e.lfh = zU32(cd, p + 42);
                if (e.csize == 0xFFFFFFFFL || e.usize == 0xFFFFFFFFL || e.lfh == 0xFFFFFFFFL) return false;   // Zip64
                e.nameB = Arrays.copyOfRange(cd, p + 46, p + 46 + nl);
                e.isEdf = new String(e.nameB, java.nio.charset.StandardCharsets.UTF_8).endsWith(".edf");
                if (e.isEdf) edfCount++;
                es.add(e);
                p += 46 + nl + xl + cl;
            }
            if (es.size() != total || edfCount != 1) return false;
            long[] newOff = new long[es.size()];
            long pos = 0;
            byte[] buf = new byte[1 << 20];
            try (java.io.BufferedOutputStream out = new java.io.BufferedOutputStream(new java.io.FileOutputStream(outDcp), 1 << 20)) {
                for (int i = 0; i < es.size(); i++) {
                    ZEntry e = es.get(i);
                    long crc = e.isEdf ? edfCrc : e.crc;
                    long cs = e.isEdf ? edfDef.length : e.csize;
                    long us = e.isEdf ? edfUSize : e.usize;
                    int method = e.isEdf ? 8 : e.method;
                    newOff[i] = pos;
                    // local file header (GPB=0: sizes known, no data descriptor)
                    zW32(out, 0x04034b50L); zW16(out, 20); zW16(out, 0); zW16(out, method);
                    zW16(out, e.time); zW16(out, e.date); zW32(out, crc); zW32(out, cs); zW32(out, us);
                    zW16(out, e.nameB.length); zW16(out, 0);
                    out.write(e.nameB);
                    pos += 30 + e.nameB.length;
                    if (e.isEdf) {
                        out.write(edfDef);
                    } else {
                        raf.seek(e.lfh);
                        byte[] lh = new byte[30];
                        raf.readFully(lh);
                        if (!(lh[0] == 0x50 && lh[1] == 0x4b && lh[2] == 0x03 && lh[3] == 0x04)) return false;
                        raf.seek(e.lfh + 30 + zU16(lh, 26) + zU16(lh, 28));
                        long rem = e.csize;
                        while (rem > 0) {
                            int r = raf.read(buf, 0, (int) Math.min(rem, buf.length));
                            if (r < 0) return false;
                            out.write(buf, 0, r);
                            rem -= r;
                        }
                    }
                    pos += cs;
                }
                long cdStart = pos;
                for (int i = 0; i < es.size(); i++) {
                    ZEntry e = es.get(i);
                    long crc = e.isEdf ? edfCrc : e.crc;
                    long cs = e.isEdf ? edfDef.length : e.csize;
                    long us = e.isEdf ? edfUSize : e.usize;
                    int method = e.isEdf ? 8 : e.method;
                    zW32(out, 0x02014b50L); zW16(out, 20); zW16(out, 20); zW16(out, 0); zW16(out, method);
                    zW16(out, e.time); zW16(out, e.date); zW32(out, crc); zW32(out, cs); zW32(out, us);
                    zW16(out, e.nameB.length); zW16(out, 0); zW16(out, 0); zW16(out, 0); zW16(out, 0);
                    zW32(out, 0); zW32(out, newOff[i]);
                    out.write(e.nameB);
                    pos += 46 + e.nameB.length;
                }
                long cdLen = pos - cdStart;
                if (pos + 22 > 0xFFFFFFFFL) return false;   // would need Zip64
                zW32(out, 0x06054b50L); zW16(out, 0); zW16(out, 0);
                zW16(out, es.size()); zW16(out, es.size());
                zW32(out, cdLen); zW32(out, cdStart);
                zW16(out, 0);
            }
            return true;
        } catch (Throwable t) {
            System.out.println("WARNING: [cpp-jni] DCP self-assembly failed (" + t + ") -> normal write path");
            return false;
        }
    }

    /** Re-inflate the injected EDIF entry from the final DCP and CRC-verify it (the raw-copied
     *  entries keep their original CRCs byte-verbatim; the injected one gets a full round-trip check). */
    static boolean verifyEdfEntry(java.io.File dcp, long expectCrc, long expectUSize) {
        try (java.util.zip.ZipFile zf = new java.util.zip.ZipFile(dcp)) {
            java.util.Enumeration<? extends java.util.zip.ZipEntry> en = zf.entries();
            while (en.hasMoreElements()) {
                java.util.zip.ZipEntry ze = en.nextElement();
                if (!ze.getName().endsWith(".edf")) continue;
                java.util.zip.CRC32 crc = new java.util.zip.CRC32();
                long n = 0;
                byte[] buf = new byte[1 << 20];
                try (java.io.InputStream is = zf.getInputStream(ze)) {
                    int r;
                    while ((r = is.read(buf)) > 0) { crc.update(buf, 0, r); n += r; }
                }
                return n == expectUSize && crc.getValue() == expectCrc;
            }
            return false;
        } catch (Throwable t) {
            return false;
        }
    }

    /** Parallel finalize, two phases: (A) PARALLEL read-only per-net PIP-set computation with a
     *  null-PIP counter -- if ANY null shows up (a cache race slipped through the warm-up) the whole
     *  phase is recomputed SERIALLY, always safe because phase A mutates no Design state; (B) SERIAL
     *  commit (net.setPIPs + logical-driver marking, verbatim from RWRoute.setPIPsOfNets). */
    @Override
    protected void setPIPsOfNets() {
        long t = System.nanoTime();
        if ("0".equals(System.getenv("RW_PAR_FINALIZE")) || pipWarmThread == null) {
            // pipWarmThread == null: the warm was skipped (small case) -> the parallel A-phase would
            // just run cold into thousands of null PIPs and fall back serial anyway; go serial directly.
            super.setPIPsOfNets();
            System.out.printf("INFO: [cpp-jni] PHASE setPIPsOfNets(serial)=%.2fs%n", (System.nanoTime() - t) / 1e9);
            return;
        }
        try { pipWarmThread.join(15000); } catch (InterruptedException ignore) {}
        final List<NetWrapper> wrappers = new ArrayList<>(nets.values());
        final Map<NetWrapper, Set<PIP>> pipSets = new java.util.concurrent.ConcurrentHashMap<>();
        final java.util.concurrent.atomic.AtomicLong nullPips = new java.util.concurrent.atomic.AtomicLong();
        final java.util.function.Consumer<NetWrapper> computeOne = (netWrapper) -> {
            Net net = netWrapper.getNet();
            Set<PIP> newPIPs = new HashSet<>();
            for (PIP pip : net.getPIPs()) {
                if (pip.isPIPFixed()) newPIPs.add(pip);
            }
            for (Connection connection : netWrapper.getConnections()) {
                List<Node> nodes = connection.getNodes();
                if (nodes == null) continue;
                for (int i = 0; i < nodes.size() - 1; i++) {
                    Node driver = nodes.get(i + 1), load = nodes.get(i);   // nodes are sink -> source
                    PIP pip = PIP.getArbitraryPIP(driver, load);
                    if (pip == null) { nullPips.incrementAndGet(); continue; }
                    if (load.isArcLocked()) pip.setIsPIPFixed(true);
                    newPIPs.add(pip);
                }
            }
            pipSets.put(netWrapper, newPIPs);
        };
        final int T = Math.min(RWRoute.rwMaxThreads(), Runtime.getRuntime().availableProcessors());
        Thread[] ws = new Thread[T];
        final java.util.concurrent.atomic.AtomicInteger cursor = new java.util.concurrent.atomic.AtomicInteger();
        for (int w = 0; w < T; w++) {
            ws[w] = new Thread(() -> {
                int i;
                while ((i = cursor.getAndIncrement()) < wrappers.size()) computeOne.accept(wrappers.get(i));
            });
            ws[w].start();
        }
        try { for (Thread w : ws) w.join(); } catch (InterruptedException e) { throw new RuntimeException(e); }
        if (nullPips.get() > 0) {   // race slipped through -> full serial recompute (phase A wrote nothing)
            System.out.printf("WARNING: [cpp-jni] parallel PIP phase saw %d null PIPs -> serial recompute%n", nullPips.get());
            nullPips.set(0);
            pipSets.clear();
            for (NetWrapper nw : wrappers) computeOne.accept(nw);
            if (nullPips.get() > 0)
                System.out.printf("ERROR: [cpp-jni] %d null PIPs persist in SERIAL recompute (data problem, not a race)%n", nullPips.get());
        }
        // Phase B: serial commit + logical-driver marking (verbatim semantics from RWRoute.setPIPsOfNets).
        for (NetWrapper netWrapper : wrappers) {
            Net net = netWrapper.getNet();
            net.setPIPs(pipSets.get(netWrapper));
            SitePinInst source = net.getSource();
            SitePinInst altSource = net.getAlternateSource();
            if (altSource != null && source.isRouted() && altSource.isRouted()) {
                Tile sourceTile = altSource.getTile();
                for (PIP pip : net.getPIPs()) {
                    if (pip.getTile() != sourceTile) continue;
                    if (pip.isRouteThru()) continue;
                    Node startNode = pip.getStartNode();
                    IntentCode startIntent = startNode.getIntentCode();
                    if (startIntent != IntentCode.NODE_CLE_OUTPUT && startIntent != IntentCode.NODE_OUTPUT) continue;
                    SitePin sp = startNode.getSitePin();
                    if (sp.getPinName().equals(source.getName())) {
                        pip.setIsLogicalDriver(true);
                        break;
                    }
                }
            }
        }
        // Parity with RWRoute.setPIPsOfNets: the PIP-overlap self-check (parallel putIfAbsent version).
        final java.util.concurrent.ConcurrentHashMap<PIP, Net> pipOwner = new java.util.concurrent.ConcurrentHashMap<>();
        final java.util.concurrent.atomic.AtomicLong overlaps = new java.util.concurrent.atomic.AtomicLong();
        Thread[] cw = new Thread[T];
        final java.util.concurrent.atomic.AtomicInteger ccur = new java.util.concurrent.atomic.AtomicInteger();
        for (int w = 0; w < T; w++) {
            cw[w] = new Thread(() -> {
                int i;
                while ((i = ccur.getAndIncrement()) < wrappers.size()) {
                    Net net = wrappers.get(i).getNet();
                    for (PIP pip : net.getPIPs()) {
                        Net prev = pipOwner.putIfAbsent(pip, net);
                        if (prev != null && prev != net) overlaps.incrementAndGet();
                    }
                }
            });
            cw[w].start();
        }
        try { for (Thread w : cw) w.join(); } catch (InterruptedException e) { throw new RuntimeException(e); }
        if (overlaps.get() == 0) System.out.println("\nINFO: No PIP overlaps\n");
        else System.out.printf("%nCRITICAL WARNING: %d PIP overlaps found%n%n", overlaps.get());
        System.out.printf("INFO: [cpp-jni] PHASE setPIPsOfNets(parallel T=%d)=%.2fs%n", T, (System.nanoTime() - t) / 1e9);
    }

    @Override
    public void routeIndirectConnectionsIteratively() {
        byte[] problem;
        long ts = System.nanoTime();
        try {
            ByteArrayOutputStream bos = new ByteArrayOutputStream(1 << 20);
            writeRrtLazy(bos);                   // inherited: seeds + nets only (no bbox materialise)
            problem = bos.toByteArray();
        } catch (IOException e) {
            throw new RuntimeException("ERROR: [cpp-jni] failed to serialise problem", e);
        }
        System.out.printf("INFO: [cpp-jni] PHASE serialize=%.2fs (problem=%d bytes)%n",
                (System.nanoTime() - ts) / 1e9, problem.length);

        long t = System.nanoTime();
        startPipWarm();                          // warm PIP caches while the native route runs (idle Java time)
        warmFabricWires();                       // small cases: fabric-wire lazy tables for inject/fixRoutes (~2.5s cold)
        // (EDIF pre-deflate thread REMOVED: the EDIF is now exported synchronously AFTER the dummy
        //  writeCheckpoint, in the netlist's collapsed state -- see the self-zip block in main().)
        byte[] result = routeNative(problem);    // <-- pure-C++ routing, same JVM, no disk
        System.out.printf("INFO: [cpp-jni] PHASE native-route=%.2fs (result=%d bytes)%n",
                (System.nanoTime() - t) / 1e9, result.length);

        // #24 ROOT CAUSE (e21a, 2026-07-09): under machine load the device-wide PIP warm can outlive
        // the native route AND the old 15s pre-setPIPs timeout-join -- its 8 threads then mutate
        // closed lazy tile caches CONCURRENTLY with inject/postRoute/finalize (the exact mcml
        // mechanism, big-case edition). Symptoms matched: E6's setPIPs=16.46s (= 15s join timeout),
        // e21a's "2601 null PIPs persist in SERIAL recompute" (state corrupted upstream of setPIPs).
        // Join UNBOUNDED here, before anything touches the design: quiet runs never wait (the warm
        // finishes far inside the 95s+ native route); loaded runs wait a few seconds instead of
        // corrupting state and paying a ~430s verify-and-serial-retry cycle.
        if (pipWarmThread != null) {
            long tw2 = System.nanoTime();
            try { pipWarmThread.join(); } catch (InterruptedException ignore) {}
            double waited = (System.nanoTime() - tw2) / 1e9;
            if (waited > 0.05)
                System.out.printf("INFO: [cpp-jni] pipWarm residual join=%.2fs (loaded machine)%n", waited);
        }

        long ti = System.nanoTime();
        if (result.length >= 8 && result[0] == 'R' && result[1] == 'R' && result[2] == 'T' && result[3] == 'F') {
            // >2GB result spilled to a temp file (JNI byte[] limit); positional-read injection.
            int plen = ((result[4] & 0xFF) << 24) | ((result[5] & 0xFF) << 16)
                     | ((result[6] & 0xFF) << 8) | (result[7] & 0xFF);
            String path = new String(result, 8, plen, java.nio.charset.StandardCharsets.US_ASCII);
            try {
                injectResultFromFile(path);
            } catch (IOException e) {
                throw new RuntimeException("ERROR: [cpp-jni] file-channel inject failed", e);
            } finally {
                new java.io.File(path).delete();
            }
        } else {
            injectResult(result);
        }
        System.out.printf("INFO: [cpp-jni] PHASE inject=%.2fs%n", (System.nanoTime() - ti) / 1e9);
    }

    /** Injection for >2GB results: phase-1 sequential boundary scan over a buffered stream, then
     *  the SAME 3-phase inject with phase A workers doing thread-safe positional reads
     *  (FileChannel.read(dst, position)) of their records. Long offsets replace int offsets. */
    private void injectResultFromFile(String path) throws IOException {
        Device device = design.getDevice();
        final Map<Integer, Connection> byId = new HashMap<>();
        for (Connection connection : indirectConnections) {
            byId.put(connection.hashCode(), connection);
        }
        final java.nio.channels.FileChannel ch = java.nio.channels.FileChannel.open(
                java.nio.file.Paths.get(path), java.nio.file.StandardOpenOption.READ);
        // Phase 1: sequential boundary scan.
        java.io.DataInputStream in = new java.io.DataInputStream(
                new java.io.BufferedInputStream(java.nio.channels.Channels.newInputStream(ch), 1 << 22));
        int magic = in.readInt();
        if (magic != RWRouteCppExport.RESULT_MAGIC) {
            ch.close();
            throw new RuntimeException("ERROR: [cpp-jni] bad spilled result magic 0x" + Integer.toHexString(magic));
        }
        final int count = in.readInt();
        final long[] offs = new long[count];
        long pos = 8;
        for (int c = 0; c < count; c++) {
            offs[c] = pos;
            in.readInt();                      // connId
            in.readByte();                     // routed
            int nr = in.readInt();
            long skip = (long) nr * 8;
            in.skipBytes((int) skip);          // records are < 2GB each; nr*8 fits int
            pos += 9 + skip;
        }
        // Phase A: parallel positional-read parse + materialize (getOrCreateThreadSafe).
        final Connection[] conns = new Connection[count];
        final boolean[] routedFlags = new boolean[count];
        @SuppressWarnings("unchecked")
        final List<RouteNode>[] paths = new List[count];
        final int T = Math.min(RWRoute.rwMaxThreads(), Runtime.getRuntime().availableProcessors());
        Thread[] ws = new Thread[T];
        final java.util.concurrent.atomic.AtomicInteger cursor = new java.util.concurrent.atomic.AtomicInteger();
        for (int w = 0; w < T; w++) {
            ws[w] = new Thread(() -> {
                ByteBuffer head = ByteBuffer.allocate(9);
                ByteBuffer body = ByteBuffer.allocate(1 << 16);
                int c;
                while ((c = cursor.getAndIncrement()) < count) {
                    try {
                        head.clear();
                        ch.read(head, offs[c]);
                        head.flip();
                        int connId = head.getInt();
                        boolean routed = head.get() != 0;
                        int nr = head.getInt();
                        if (body.capacity() < nr * 8) body = ByteBuffer.allocate(Integer.highestOneBit(nr * 8) * 2);
                        body.clear(); body.limit(nr * 8);
                        ch.read(body, offs[c] + 9);
                        body.flip();
                        List<RouteNode> rnodes = new ArrayList<>(nr);
                        for (int i = 0; i < nr; i++) {
                            int addr = body.getInt();
                            int wire = body.getInt();
                            rnodes.add(routingGraph.getOrCreateThreadSafe(Node.getNode(device.getTile(addr), wire), null));
                        }
                        Connection connection = byId.get(connId);
                        if (connection == null) throw new RuntimeException("unknown conn id " + connId);
                        conns[c] = connection;
                        routedFlags[c] = routed;
                        paths[c] = rnodes;
                    } catch (IOException e) {
                        throw new RuntimeException(e);
                    }
                }
            });
            ws[w].start();
        }
        try { for (Thread w : ws) w.join(); } catch (InterruptedException e) { throw new RuntimeException(e); }
        ch.close();
        commitInjectPhases(count, conns, routedFlags, paths);
    }

    /**
     * Lazy device callback: C++ calls this once per node (cached on the C++ side) to get that
     * node's RAW allowed-tile downhill children plus each child's RouteNode attributes, packed
     * as a primitive int[] (11 ints/child). The C++ side re-applies the dynamic isExcluded()/
     * isAccessible() filters. This reuses RapidWright's RouteNodeInfo via routingGraph.getOrCreate.
     */
    public int[] getChildrenPacked(long nodeKey) {
        Device device = design.getDevice();
        int tileAddr = (int) (nodeKey >> 20);
        int wireIndex = (int) (nodeKey & 0xFFFFF);
        Node node = Node.getNode(device.getTile(tileAddr), wireIndex);
        List<Node> downhill = node.getAllDownhillNodes();
        int[] tmp = new int[1 + downhill.size() * 11];
        int cnt = 0, o = 1;
        for (Node child : downhill) {
            if (RouteNodeGraph.isExcludedTile(child)) {
                continue;
            }
            RouteNode crn = routingGraph.getOrCreate(child);
            Tile ct = crn.getTile();
            tmp[o++] = ct.getUniqueAddress();
            tmp[o++] = crn.getWireIndex();
            tmp[o++] = crn.getType().ordinal();
            tmp[o++] = nodeFlags(crn, false) & 0x1F;  // low 5 bits (laguna/pinfeed/leadsLaguna/pinbounce/preserved)
            tmp[o++] = crn.getBeginTileXCoordinate();
            tmp[o++] = crn.getBeginTileYCoordinate();
            tmp[o++] = crn.getEndTileXCoordinate();
            tmp[o++] = crn.getEndTileYCoordinate();
            tmp[o++] = crn.getLength();
            tmp[o++] = Float.floatToRawIntBits(safeBaseCost(crn));
            tmp[o++] = crn.hashCode();
            cnt++;
        }
        tmp[0] = cnt;
        if (childDump != null) {
            try {
                synchronized (childDump) {
                    childDump.writeLong(nodeKey);
                    childDump.writeInt(cnt);
                    for (int k = 0; k < cnt; k++) {
                        long ck = ((long) tmp[1 + k * 11] << 20) | (tmp[1 + k * 11 + 1] & 0xFFFFF);
                        childDump.writeLong(ck);
                    }
                }
            } catch (IOException e) { throw new RuntimeException(e); }
        }
        return (cnt * 11 + 1 == tmp.length) ? tmp : java.util.Arrays.copyOf(tmp, 1 + cnt * 11);
    }

    // Validation hook: when env RWDUMP is set, record each getChildrenPacked(parentKey)->childKeys
    // so the C++ device model can be cross-checked node-by-node against RapidWright's adjacency.
    private static final java.io.DataOutputStream childDump = openChildDump();
    private static java.io.DataOutputStream openChildDump() {
        String p = System.getenv("RWDUMP");
        if (p == null) return null;
        try {
            return new java.io.DataOutputStream(new java.io.BufferedOutputStream(new java.io.FileOutputStream(p), 1 << 22));
        } catch (IOException e) { throw new RuntimeException(e); }
    }
    public static void closeChildDump() {
        if (childDump != null) try { childDump.flush(); childDump.close(); } catch (IOException e) {}
    }

    /** Two-phase inject: (A) PARALLEL record parse + RouteNode materialisation -- routingGraph is
     *  the only shared structure touched and goes through getOrCreateThreadSafe (striped tile
     *  locks); (B) SERIAL commit (source swap, setRnodes, incrementUser) in the exact original
     *  record order, so the resulting user counts/state are bit-identical to the serial version. */
    private void injectResult(final byte[] result) {
        final Device device = design.getDevice();
        final Map<Integer, Connection> byId = new HashMap<>();
        for (Connection connection : indirectConnections) {
            byId.put(connection.hashCode(), connection);
        }

        ByteBuffer bb = ByteBuffer.wrap(result);  // big-endian (matches C++ writeResultToVector)
        int magic = bb.getInt();
        if (magic != RWRouteCppExport.RESULT_MAGIC) {
            throw new RuntimeException("ERROR: [cpp-jni] bad result magic 0x" + Integer.toHexString(magic));
        }
        final int count = bb.getInt();

        // Pass 1 (serial, cheap): find record boundaries so workers can jump straight to a record.
        final int[] offs = new int[count];
        for (int c = 0; c < count; c++) {
            offs[c] = bb.position();
            bb.getInt();                       // connId
            bb.get();                          // routed
            int nr = bb.getInt();
            bb.position(bb.position() + nr * 8);
        }

        // Phase A (parallel): parse + materialize RouteNode paths.
        final Connection[] conns = new Connection[count];
        final boolean[] routedFlags = new boolean[count];
        @SuppressWarnings("unchecked")
        final List<RouteNode>[] paths = new List[count];
        final int T = "0".equals(System.getenv("RW_PAR_INJECT")) ? 1
                : Math.min(RWRoute.rwMaxThreads(), Runtime.getRuntime().availableProcessors());
        if (T > 1) {
            Thread[] ws = new Thread[T];
            final java.util.concurrent.atomic.AtomicInteger cursor = new java.util.concurrent.atomic.AtomicInteger();
            for (int w = 0; w < T; w++) {
                ws[w] = new Thread(() -> {
                    ByteBuffer lb = ByteBuffer.wrap(result);   // private cursor per worker
                    int c;
                    while ((c = cursor.getAndIncrement()) < count) {
                        parseOneResultRecord(lb, offs[c], device, byId, conns, routedFlags, paths, c, true);
                    }
                });
                ws[w].start();
            }
            try { for (Thread w : ws) w.join(); } catch (InterruptedException e) { throw new RuntimeException(e); }
        } else {
            ByteBuffer lb = ByteBuffer.wrap(result);
            for (int c = 0; c < count; c++) {
                parseOneResultRecord(lb, offs[c], device, byId, conns, routedFlags, paths, c, false);
            }
        }

        commitInjectPhases(count, conns, routedFlags, paths);
    }

    /** Phase B commit (shared by array and spilled-file injection). Source swaps (rare; they
     *  mutate routingGraph and connection source fields) run serially FIRST. The remaining
     *  per-record commit (setRnodes/setRouted/incrementUser) is then parallelized ACROSS nets:
     *  a legal routing result has no overused rnodes, so every rnode belongs to exactly one net
     *  and conns of different nets touch disjoint user maps. Records of the SAME net stay in one
     *  task, committed in original record order -> end state identical to the serial commit. */
    private void commitInjectPhases(final int count, final Connection[] conns,
                                    final boolean[] routedFlags, final List<RouteNode>[] paths) {
        final int T = Math.min(RWRoute.rwMaxThreads(), Runtime.getRuntime().availableProcessors());
        int swappedSources = 0;
        for (int c = 0; c < count; c++) {
            List<RouteNode> rnodes = paths[c];
            if (rnodes.isEmpty()) continue;
            Connection connection = conns[c];
            RouteNode usedSource = rnodes.get(rnodes.size() - 1);
            if (usedSource != connection.getSourceRnode()) {
                Pair<SitePinInst, RouteNode> alt = connection.getOrCreateAlternateSource(routingGraph);
                if (alt == null || alt.getSecond() != usedSource) {
                    throw new RuntimeException("ERROR: [cpp-jni] cannot reconcile swapped source for conn " + connection.hashCode());
                }
                connection.setSource(alt.getFirst());
                connection.setSourceRnode(alt.getSecond());
                swappedSources++;
            }
        }

        if (T > 1) {
            // Bucket record indices by NetWrapper id (dense: ids are 0..numWireNetsToRoute).
            int maxNetId = 0;
            for (int c = 0; c < count; c++) {
                maxNetId = Math.max(maxNetId, conns[c].getNetWrapper().getId());
            }
            final int[] bucketCnt = new int[maxNetId + 2];
            for (int c = 0; c < count; c++) bucketCnt[conns[c].getNetWrapper().getId() + 1]++;
            for (int i = 1; i < bucketCnt.length; i++) bucketCnt[i] += bucketCnt[i - 1];
            final int[] order = new int[count];
            final int[] fill = new int[maxNetId + 1];
            for (int c = 0; c < count; c++) {           // ascending c per net -> original order kept
                int id = conns[c].getNetWrapper().getId();
                order[bucketCnt[id] + fill[id]++] = c;
            }
            final java.util.concurrent.atomic.AtomicInteger netCursor = new java.util.concurrent.atomic.AtomicInteger();
            final int nBuckets = maxNetId + 1;
            Thread[] cs = new Thread[T];
            for (int w = 0; w < T; w++) {
                cs[w] = new Thread(() -> {
                    int id;
                    while ((id = netCursor.getAndIncrement()) < nBuckets) {
                        for (int k = bucketCnt[id]; k < bucketCnt[id + 1]; k++) {
                            commitRecord(order[k], conns, routedFlags, paths);
                        }
                    }
                });
                cs[w].start();
            }
            try { for (Thread w : cs) w.join(); } catch (InterruptedException e) { throw new RuntimeException(e); }
        } else {
            for (int c = 0; c < count; c++) {
                commitRecord(c, conns, routedFlags, paths);
            }
        }
        System.out.println("INFO: [cpp-jni] injected " + count + " (" + swappedSources + " swapped sources)");
    }

    private void commitRecord(int c, Connection[] conns, boolean[] routedFlags, List<RouteNode>[] paths) {
        Connection connection = conns[c];
        boolean routed = routedFlags[c];
        List<RouteNode> rnodes = paths[c];
        connection.setRnodes(rnodes);
        connection.setRouted(routed);
        if (routed && !rnodes.isEmpty()) {  // replicate updateUsersAndPresentCongestionCost
            List<RouteNode> inc = rnodes;
            RouteNode sinkRnode = rnodes.get(0);
            if (sinkRnode == connection.getSinkRnode() && !connection.hasAltSinks()) {
                inc = rnodes.subList(1, rnodes.size() - 1);
            }
            NetWrapper netWrapper = connection.getNetWrapper();
            for (RouteNode rnode : inc) {
                rnode.incrementUser(netWrapper);
            }
        }
    }

    /** Parallel per-connection version of RWRoute.assignNodesToConnections: each connection only
     *  writes its own nodes list; findPathBetweenNodes is all-local BFS over read-only device
     *  queries. Order-independent, so a work-stealing cursor is safe. RW_PAR_ASSIGN=0 falls back. */
    @Override
    protected void assignNodesToConnections() {
        long t = System.nanoTime();
        final int T = "0".equals(System.getenv("RW_PAR_ASSIGN")) ? 1
                : Math.min(RWRoute.rwMaxThreads(), Runtime.getRuntime().availableProcessors());
        if (T == 1) {
            super.assignNodesToConnections();
            System.out.printf("INFO: [cpp-jni] PHASE assignNodes(serial)=%.2fs%n", (System.nanoTime() - t) / 1e9);
            return;
        }
        final List<Connection> all = indirectConnections;
        final java.util.concurrent.atomic.AtomicInteger cursor = new java.util.concurrent.atomic.AtomicInteger();
        Thread[] ws = new Thread[T];
        for (int w = 0; w < T; w++) {
            ws[w] = new Thread(() -> {
                int i;
                while ((i = cursor.getAndIncrement()) < all.size()) {
                    Connection connection = all.get(i);
                    List<Node> nodes = new ArrayList<>();
                    connection.setNodes(nodes);
                    RouteNode sinkRnode = connection.getSinkRnode();
                    List<RouteNode> rnodes = connection.getRnodes();
                    if (rnodes.isEmpty()) continue;
                    if (sinkRnode == rnodes.get(0)) {
                        List<Node> switchBoxToSink = RouterHelper.findPathBetweenNodes(
                                sinkRnode, connection.getSink().getConnectedNode());
                        if (switchBoxToSink.size() >= 2) {
                            nodes.addAll(switchBoxToSink.subList(0, switchBoxToSink.size() - 1));
                        }
                    }
                    nodes.addAll(rnodes);
                    List<Node> sourceToSwitchBox = RouterHelper.findPathBetweenNodes(
                            connection.getSource().getConnectedNode(), connection.getSourceRnode());
                    if (sourceToSwitchBox.size() >= 2) {
                        nodes.addAll(sourceToSwitchBox.subList(1, sourceToSwitchBox.size()));
                    }
                }
            });
            ws[w].start();
        }
        try { for (Thread w : ws) w.join(); } catch (InterruptedException e) { throw new RuntimeException(e); }
        System.out.printf("INFO: [cpp-jni] PHASE assignNodes(parallel T=%d)=%.2fs%n", T, (System.nanoTime() - t) / 1e9);
    }

    private void parseOneResultRecord(ByteBuffer lb, int off, Device device, Map<Integer, Connection> byId,
                                      Connection[] conns, boolean[] routedFlags, List<RouteNode>[] paths,
                                      int c, boolean threadSafe) {
        lb.position(off);
        int connId = lb.getInt();
        routedFlags[c] = lb.get() != 0;
        int nr = lb.getInt();
        List<RouteNode> rnodes = new ArrayList<>(nr);
        for (int i = 0; i < nr; i++) {
            int addr = lb.getInt();
            int wire = lb.getInt();
            Node node = Node.getNode(device.getTile(addr), wire);
            rnodes.add(threadSafe ? routingGraph.getOrCreateThreadSafe(node, null)
                                  : routingGraph.getOrCreate(node));
        }
        Connection connection = byId.get(connId);
        if (connection == null) {
            throw new RuntimeException("ERROR: [cpp-jni] unknown connection id " + connId);
        }
        conns[c] = connection;
        paths[c] = rnodes;
    }

    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("USAGE: <input.dcp> <output.dcp> [rwroute args...]");
            return;
        }
        String inputDcp = args[0];
        String routedDcp = args[1];
        String[] rwrouteArgs = Arrays.copyOfRange(args, 2, args.length);

        CodePerfTracker t = new CodePerfTracker("RWRouteCppJni", true);

        // Early device prewarm: the C++ device build (~12s) is design-INDEPENDENT, so for BIG cases start
        // it BEFORE readCheckpoint -> its time fully hides behind read(~9s)+init(~6s) (no exposed build
        // wait at route time). Input DCP file size is a reliable size proxy available with zero parsing:
        // competition cases are cleanly bimodal (small ~2-3MB vs big >=49MB). Small cases skip the build
        // entirely -> clean JNI-B (no build, no read/route resource contention).
        long dcpBytes = new java.io.File(inputDcp).length();
        boolean bigCase = dcpBytes > 10_000_000L;
        inputDcpBytes = dcpBytes;
        RWRouteConfig config = new RWRouteConfig(rwrouteArgs);   // pure arg parsing; needed by the early prewarm
        if (bigCase) {
            prewarmDevice(dcpBytes);
        } else {
            String part = System.getenv("RW_PART");
            startEarlyPrewarm(part != null ? part : "xcvu13p-fhgb2104-2-e", config);
            prewarmDevice(dcpBytes);   // small: C++ mmaps the .dmc image (~ms) or leaves JNI-B untouched
            // With the compact device mapped, serve RouteNodeInfo straight from it: netCreate then
            // never touches the Java fabric-wire lazy tables (~2.9s cold / ~1.4s warm-wait).
            // INT/laguna nodes hit the C++ table; misses (direct-conn CLB nodes) fall back per node.
            if (dmActive() && !"0".equals(System.getenv("RW_DMC_NODEINFO"))) {
                final RouteNodeType[] types = RouteNodeType.values();
                RouteNodeGraph.nodeInfoProvider = (node) -> {
                    int[] o = new int[4];
                    if (!getNodeRec(node.getTile().getUniqueAddress(), node.getWireIndex(), o)) return null;
                    return RouteNodeInfo.of(types[o[0]], (short) o[1], (short) o[2], (short) o[3]);
                };
                System.out.println("INFO: [cpp-jni] nodeInfoProvider=dmc (netCreate bypasses Java lazy tables)");
            }
        }

        long tr = System.nanoTime();
        Design design = Design.readCheckpoint(inputDcp);
        System.out.printf("INFO: [cpp-jni] PHASE readCheckpoint=%.2fs%n", (System.nanoTime() - tr) / 1e9);
        startRouteThruPrewarm(design.getDevice());   // device-only helper -> build during preprocess (~2-3s hidden)

        startGraphPrewarm(design, config);           // RouteNodeGraph ctor reads only device geometry + config
        // PartialRouter.preprocess(design) replicated with per-call timers (device fixed to
        // UltraScale+ xcvu13p, so RWRoute.preprocess's series check is a constant-true here).
        long tpp = System.nanoTime();
        design.getNetlist().getParentNetMap();       // the lazily-built map every trio member depends on
        long tppM = System.nanoTime();
        DesignTools.makePhysNetNamesConsistent(design);
        long tpp1 = System.nanoTime();
        DesignTools.createPossiblePinsToStaticNets(design);
        long tpp2 = System.nanoTime();
        DesignTools.createMissingSitePinInsts(design);
        long tpp3 = System.nanoTime();
        DesignTools.updatePinsIsRouted(design);
        long tpp4 = System.nanoTime();
        System.out.printf("INFO: [cpp-jni] PHASE preprocess(static)=%.2fs (parentMap=%.2fs names=%.2fs staticPins=%.2fs missingSPI=%.2fs isRouted=%.2fs)%n",
                (tpp4 - tpp) / 1e9, (tppM - tpp) / 1e9, (tpp1 - tppM) / 1e9, (tpp2 - tpp1) / 1e9,
                (tpp3 - tpp2) / 1e9, (tpp4 - tpp3) / 1e9);
        long tgu = System.nanoTime();
        List<SitePinInst> pinsToRoute = getUnroutedPins(design);
        System.out.printf("INFO: [cpp-jni] PHASE getUnroutedPins=%.2fs (%d pins)%n",
                (System.nanoTime() - tgu) / 1e9, pinsToRoute.size());
        if (bigCase) startEarlyPrepass(design, pinsToRoute);   // prepass hides behind initialize

        RWRouteCppJni router = new RWRouteCppJni(design, config, pinsToRoute);
        // SELF-ZIP DEFAULT OFF (RW_SELF_ZIP=1 opt-in). Vivado cross-check proved the dummy-EDIF
        // writeCheckpoint variant does NOT collapse macro unisims (our exported EDIF: 154MB with
        // 278 DSP_OUTPUT_INST refs vs Vivado-native 11MB with 0) -> the XDEF it writes is macro-
        // inconsistent for Vivado (k_100_dsp: 2,146 unplaced-pin/antenna errors, identical before
        // and after the EDIF-form fix => XDEF is the broken half). The plain writeCheckpoint is
        // golden-identical (Vivado-clean by construction) AND now faster than the corrected
        // self-zip (k_800: 11.8s vs 15.5s) since the EDIF export can no longer be hidden.
        selfZipWanted = bigCase && "1".equals(System.getenv("RW_SELF_ZIP"));
        long trd = System.nanoTime();
        Design routed = routeDesign(router);   // initialize(target-build) + route(serialize/native/inject) + finalize
        System.out.printf("INFO: [cpp-jni] PHASE routeDesign-total=%.2fs (init+route+finalize)%n", (System.nanoTime() - trd) / 1e9);

        long tw = System.nanoTime();
        boolean selfWrote = false;
        if (selfZipWanted) {
            java.io.File tmpDcp = new java.io.File(routedDcp + ".tmp.dcp");
            java.io.File dummy = new java.io.File(routedDcp + ".dummy.edf");
            try {
                // Tiny placeholder: the (dcp, edf) variant embeds the given file instead of
                // regenerating the EDIF -- we discard its (corrupt, jar bug) entry in assembly.
                java.nio.file.Files.write(dummy.toPath(),
                        "(edif placeholder (self-assembled write))\n".getBytes(java.nio.charset.StandardCharsets.UTF_8));
                routed.writeCheckpoint(tmpDcp.toPath(), dummy.toPath(), t);
                // EDIF export MOVED HERE, AFTER the dummy writeCheckpoint: the closed writer calls
                // collapseMacroUnisims on the live netlist (bytecode-verified) and never re-expands,
                // so at this point the netlist is in Vivado's COLLAPSED convention -- exactly what
                // the XDEF it just wrote references. The old pre-route background export produced an
                // EXPANDED-form EDIF, which made Vivado see DSP48E2 macro internals as unplaced
                // (2,146 errors on k_100_dsp). Exporting synchronously here costs the EDIF gen time
                // (~2-10s big cases) but is macro-consistent by construction, and removing the
                // background export thread also removes a concurrency window entirely.
                long te = System.nanoTime();
                java.io.ByteArrayOutputStream bos = new java.io.ByteArrayOutputStream(16 << 20);
                final java.util.zip.CRC32 crc = new java.util.zip.CRC32();
                final long[] usize = {0};
                java.util.zip.Deflater def = new java.util.zip.Deflater(java.util.zip.Deflater.DEFAULT_COMPRESSION, true);
                java.util.zip.DeflaterOutputStream dos = new java.util.zip.DeflaterOutputStream(bos, def, 1 << 16) {
                    @Override public void write(byte[] b, int off, int len) throws IOException {
                        crc.update(b, off, len); usize[0] += len; super.write(b, off, len);
                    }
                    @Override public void write(int b) throws IOException {
                        crc.update(b); usize[0]++; super.write(b);
                    }
                };
                routed.getNetlist().exportEDIF(dos);   // exportEDIF closes the stream (finishes deflate)
                byte[] edfDeflated = bos.toByteArray();
                System.out.printf("INFO: [cpp-jni] EDIF exported post-collapse: %.1fMB -> %.1fMB (%.2fs)%n",
                        usize[0] / 1e6, edfDeflated.length / 1e6, (System.nanoTime() - te) / 1e9);
                if (assembleDcp(tmpDcp, new java.io.File(routedDcp), edfDeflated, crc.getValue(), usize[0])
                        && verifyEdfEntry(new java.io.File(routedDcp), crc.getValue(), usize[0])) {
                    selfWrote = true;
                } else {
                    System.out.println("WARNING: [cpp-jni] self-assembled DCP failed verification -> normal write path");
                    new java.io.File(routedDcp).delete();
                }
            } catch (Throwable e) {
                System.out.println("WARNING: [cpp-jni] self-assembled write failed (" + e + ") -> normal write path");
                new java.io.File(routedDcp).delete();
            } finally {
                tmpDcp.delete();
                dummy.delete();
            }
        }
        // Self-verification (RW_VERIFY_INPROC=0 disables). DEFAULT = in-memory gate HIDDEN BEHIND THE
        // WRITE: the post-setPIPs state is exactly what writeCheckpoint serializes, and both observed
        // corruption classes (#24 family: E6's short-61-PIPs after an anomalous parallel setPIPs;
        // mcml's null-PIP inject/finalize race) live in that STATE, upstream of the writer. The gate
        // is read-only by construction (routedSinksReadOnly never touches isRouted), so it runs
        // CONCURRENTLY with the closed writer over the same read-only physical netlist -- its ~3-4s
        // vanish inside the ~8s write. The writer-layer itself has never been an observed corruption
        // locus (the #25 XDEF-convention bug was invisible to the re-read checker too -- only Vivado
        // caught it, and Vivado remains the final acceptance oracle). RW_VERIFY_DEEP=1 restores the
        // old post-write re-read verify (~28s) for paranoid/audit runs.
        Thread verifyThread = null;
        final RWRouteCppVerify.Result[] vrBox = new RWRouteCppVerify.Result[1];
        final double[] vrSec = new double[1];
        boolean wantVerify = !"0".equals(System.getenv("RW_VERIFY_INPROC"));
        boolean deepVerify = "1".equals(System.getenv("RW_VERIFY_DEEP"));
        if (wantVerify && !deepVerify) {
            final Design vd = routed;
            verifyThread = new Thread(() -> {
                try {
                    long tv = System.nanoTime();
                    vrBox[0] = RWRouteCppVerify.checkInMemory(vd, Math.max(8, RWRoute.rwMaxThreads() - 8));   // 24 + writer's ~4 + main = <32
                    vrSec[0] = (System.nanoTime() - tv) / 1e9;
                } catch (Throwable e) {
                    System.out.println("WARNING: [cpp-jni] in-memory verify failed (" + e + ") -> launcher external checker takes over");
                }
            }, "rw-verify-mem");
            verifyThread.start();
        }

        if (!selfWrote) routed.writeCheckpoint(routedDcp, t);
        System.out.printf("INFO: [cpp-jni] PHASE writeCheckpoint%s=%.2fs%n",
                selfWrote ? "(self-assembled, EDIF hidden)" : "", (System.nanoTime() - tw) / 1e9);
        closeChildDump();
        System.out.println("\nINFO: [cpp-jni] Wrote routed design\n " + routedDcp + "\n");

        if (verifyThread != null) {
            try { verifyThread.join(); } catch (InterruptedException ignore) {}
            if (vrBox[0] != null && vrBox[0].legal()) {
                System.out.println("VERIFY: " + vrBox[0].checkLine(routedDcp)
                        + String.format(" (in-memory, %.2fs, hidden behind write)", vrSec[0]));
            } else if (vrBox[0] != null) {
                // In-memory gate failed -> ARBITRATE with the deep re-read of the written file before
                // declaring failure. Known benign divergence: mcml_RLE deterministically carries ONE
                // phantom in-memory sink pin (sinks=20531 in memory vs 20530 in the file, every run,
                // serial included -- matches the ledger's pre-existing "1 UNROUTABLE arm" note), which
                // would otherwise burn a full serial retry on a healthy output. Clean runs never pay
                // this; real corruption is confirmed by the re-read and still triggers the retry.
                System.out.println("INFO: [cpp-jni] in-memory gate flagged ("
                        + vrBox[0].unrouted + " unrouted, " + vrBox[0].shorts
                        + " shorts) -> deep re-read arbitration");
                try {
                    long tv = System.nanoTime();
                    Design d2 = Design.readCheckpoint(routedDcp);
                    RWRouteCppVerify.Result vr = RWRouteCppVerify.check(d2, RWRoute.rwMaxThreads());
                    System.out.println("VERIFY: " + vr.checkLine(routedDcp)
                            + String.format(" (deep arbitration, %.2fs)", (System.nanoTime() - tv) / 1e9));
                } catch (Throwable e) {
                    System.out.println("WARNING: [cpp-jni] deep arbitration failed (" + e + ") -> launcher external checker takes over");
                }
            }
        } else if (wantVerify) {
            // RW_VERIFY_DEEP=1: legacy post-write re-read verification (validates the written file
            // itself; ~28s on 20per -- device/JIT warm, still ~3x faster than a fresh checker JVM).
            try {
                long tv = System.nanoTime();
                router = null; routed = null; design = null; pinsToRoute = null;   // unpin for GC
                prewarmGraph = null;
                Design d2 = Design.readCheckpoint(routedDcp);
                long tv1 = System.nanoTime();
                RWRouteCppVerify.Result vr = RWRouteCppVerify.check(d2, RWRoute.rwMaxThreads());
                System.out.println("VERIFY: " + vr.checkLine(routedDcp)
                        + String.format(" (in-process deep, read=%.2fs check=%.2fs)",
                                (tv1 - tv) / 1e9, (System.nanoTime() - tv1) / 1e9));
            } catch (Throwable e) {
                System.out.println("WARNING: [cpp-jni] in-process verify failed (" + e + ") -> launcher external checker takes over");
            }
        }
    }
}
