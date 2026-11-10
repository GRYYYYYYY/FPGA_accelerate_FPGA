/*
 * Harness (addition to RapidWright tree) for the pure-C++ RWRoute port.
 *
 * RWRouteCppProblemExport runs PartialRouter up to (but not including) the iterative
 * routing loop, then serialises everything the pure-C++ router needs to reproduce that
 * loop into a little-endian binary ".rrt" file:
 *   - routing config scalars (post auto-tune),
 *   - device arrays (INT-Y -> SLR index, Laguna columns),
 *   - a bounding-box-bounded node "universe": each node's precomputed RouteNode attributes
 *     plus its RAW allowed-tile downhill adjacency (the C++ side re-applies the dynamic
 *     isExcluded()/isAccessible() filters during routing, just like getChildren()),
 *   - the fully-built nets/connections (sources, sinks, alt-sinks, bounding boxes, and any
 *     already-reconstructed routing for partially-routed nets).
 * The C++ router consumes this, routes, and writes a ".result" consumed by RWRouteCppImport.
 */
package com.xilinx.rapidwright.rwroute;

import java.io.BufferedOutputStream;
import java.io.ByteArrayOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.design.Net;
import com.xilinx.rapidwright.design.SitePinInst;
import com.xilinx.rapidwright.device.Device;
import com.xilinx.rapidwright.device.IntentCode;
import com.xilinx.rapidwright.device.Node;
import com.xilinx.rapidwright.device.Tile;
import com.xilinx.rapidwright.device.TileTypeEnum;
import com.xilinx.rapidwright.tests.CodePerfTracker;
import com.xilinx.rapidwright.util.Utils;

public class RWRouteCppProblemExport extends PartialRouter {

    private final String rrtFileName;

    public RWRouteCppProblemExport(Design design, RWRouteConfig config, Collection<SitePinInst> pinsToRoute,
                                   String rrtFileName) {
        super(design, config, pinsToRoute, false);
        this.rrtFileName = rrtFileName;
    }

    /** Little-endian primitive writer. */
    private static final class LE {
        private final OutputStream os;
        private byte[] a; private int n;   // buffer mode: unsynchronized (ByteArrayOutputStream locks
                                           // a monitor PER BYTE -- the 350MB parallel sections paid
                                           // ~350M monitor ops, ~2.5s of the 3.4s serialize)
        LE(OutputStream os) { this.os = os; }
        LE(int cap) { this.os = null; this.a = new byte[cap]; }
        private void ensure(int k) { if (n + k > a.length) a = Arrays.copyOf(a, Math.max(a.length << 1, n + k)); }
        void i8(int v) throws IOException { if (a != null) { ensure(1); a[n++] = (byte) v; } else os.write(v & 0xFF); }
        void i16(int v) throws IOException {
            if (a != null) { ensure(2); a[n++] = (byte) v; a[n++] = (byte) (v >> 8); }
            else { os.write(v & 0xFF); os.write((v >> 8) & 0xFF); }
        }
        void i32(int v) throws IOException {
            if (a != null) { ensure(4); a[n++] = (byte) v; a[n++] = (byte) (v >> 8); a[n++] = (byte) (v >> 16); a[n++] = (byte) (v >> 24); }
            else { os.write(v & 0xFF); os.write((v >> 8) & 0xFF); os.write((v >> 16) & 0xFF); os.write((v >> 24) & 0xFF); }
        }
        void f32(float f) throws IOException { i32(Float.floatToRawIntBits(f)); }
        void raw(byte[] b) throws IOException {
            if (a != null) { ensure(b.length); System.arraycopy(b, 0, a, n, b.length); n += b.length; }
            else os.write(b, 0, b.length);
        }
        void magic(String m) throws IOException { for (int i = 0; i < 4; i++) i8(m.charAt(i)); }
        byte[] data() { return Arrays.copyOf(a, n); }
    }

    /** A node in the exported universe, with a dense id. */
    private static final class NInfo {
        int id;
        RouteNode rnode;
        boolean expanded;       // adjacency materialised (node was within the bounding box)
        boolean createdAtInit;  // existed in routingGraph before our materialisation BFS
        int[] childIds;         // raw allowed-tile downhill candidates (getChildren order)
    }

    /** Long key from (tileUniqueAddress, wireIndex). */
    private static long key(Node n) {
        return (((long) n.getTile().getUniqueAddress()) << 20) | (n.getWireIndex() & 0xFFFFFL);
    }

    protected final LinkedHashMap<Long, NInfo> universe = new LinkedHashMap<>();

    private NInfo getOrAssign(RouteNode rn) {
        long k = key(rn);
        NInfo ni = universe.get(k);
        if (ni == null) {
            ni = new NInfo();
            ni.id = universe.size();
            ni.rnode = rn;
            universe.put(k, ni);
        }
        return ni;
    }

    private int idOf(RouteNode rn) {
        NInfo ni = universe.get(key(rn));
        return ni == null ? -1 : ni.id;
    }

    @Override
    public void routeIndirectConnectionsIteratively() {
        try {
            writeRrt(new BufferedOutputStream(new FileOutputStream(rrtFileName), 1 << 20));
        } catch (IOException e) {
            throw new RuntimeException("ERROR: Failed to write " + rrtFileName, e);
        }
        System.out.println("INFO: [cpp-prob] wrote " + rrtFileName + " (" + universe.size() + " nodes)");
        // Skip the rest of route() (we are not producing a DCP here).
        System.exit(0);
    }

    // Materialise the bbox-bounded device subgraph + problem and serialise to osArg.
    // Shared by the file exporter and the in-process JNI path (RWRouteCppJni).
    protected void writeRrt(OutputStream osArg) throws IOException {
        Device device = design.getDevice();

        // Snapshot the set of rnodes that exist after initialize() (+ clk/static routing).
        Set<RouteNode> initialRnodes = java.util.Collections.newSetFromMap(new IdentityHashMap<>());
        for (RouteNode rn : routingGraph.getRnodes()) {
            initialRnodes.add(rn);
        }

        // Overall bounding box = union of all indirect connections' boxes.
        int oXMin = Integer.MAX_VALUE, oXMax = Integer.MIN_VALUE;
        int oYMin = Integer.MAX_VALUE, oYMax = Integer.MIN_VALUE;
        for (Connection c : indirectConnections) {
            oXMin = Math.min(oXMin, c.getXMinBB()); oXMax = Math.max(oXMax, c.getXMaxBB());
            oYMin = Math.min(oYMin, c.getYMinBB()); oYMax = Math.max(oYMax, c.getYMaxBB());
        }
        final int xMin = oXMin, xMax = oXMax, yMin = oYMin, yMax = oYMax;

        // BFS: materialise raw allowed-tile adjacency for every node within the overall box.
        ArrayDeque<RouteNode> queue = new ArrayDeque<>();
        for (RouteNode rn : initialRnodes) {
            NInfo ni = getOrAssign(rn);
            ni.createdAtInit = true;
            if (inBox(rn, xMin, xMax, yMin, yMax) && !ni.expanded) {
                queue.add(rn);
                ni.expanded = true;  // mark queued; adjacency filled when polled
            }
        }
        while (!queue.isEmpty()) {
            RouteNode rn = queue.poll();
            NInfo ni = universe.get(key(rn));
            List<Node> downhill = rn.getAllDownhillNodes();
            List<Integer> childIds = new ArrayList<>(downhill.size());
            for (Node child : downhill) {
                if (RouteNodeGraph.isExcludedTile(child)) {
                    continue;
                }
                RouteNode crn = routingGraph.getOrCreate(child);
                NInfo cni = getOrAssign(crn);
                if (initialRnodes.contains(crn)) {
                    cni.createdAtInit = true;
                }
                childIds.add(cni.id);
                if (!cni.expanded && inBox(crn, xMin, xMax, yMin, yMax)) {
                    cni.expanded = true;
                    queue.add(crn);
                }
            }
            ni.childIds = new int[childIds.size()];
            for (int i = 0; i < childIds.size(); i++) ni.childIds[i] = childIds.get(i);
        }

        // ---- write the file ----
        try (LEStream out = new LEStream(osArg)) {
            LE w = out.w;
            w.magic("RRT1");

            // CONFIG
            w.i32(config.getMaxIterations());
            w.i32(config.getBoundingBoxExtensionX());
            w.i32(config.getBoundingBoxExtensionY());
            w.i32(config.isEnlargeBoundingBox() ? 1 : 0);
            w.i32(config.getExtensionXIncrement());
            w.i32(config.getExtensionYIncrement());
            w.i32(config.isUseBoundingBox() ? 1 : 0);
            w.f32(config.getWirelengthWeight());
            w.f32(config.getShareExponent());
            w.f32(config.getInitialPresentCongestionFactor());
            w.f32(config.getPresentCongestionMultiplier());
            w.f32(config.getHistoricalCongestionFactor());
            w.f32(config.getMaxPresentCongestionFactor());
            w.i32(maxDetourToSnapBackToPrevLagunaColumn);
            w.i32(routingGraph.SUPER_LONG_LINE_LENGTH_IN_TILES);
            w.i32(config.isUseUTurnNodes() ? 1 : 0);

            // DEVICE ARRAYS
            int numRows = routingGraph.intYToSLRIndex.length;
            w.i32(numRows);
            for (int y = 0; y < numRows; y++) w.i32(routingGraph.intYToSLRIndex[y]);
            boolean hasLaguna = routingGraph.nextLagunaColumn != null;
            w.i32(hasLaguna ? 1 : 0);
            if (hasLaguna) {
                int numCols = routingGraph.nextLagunaColumn.length;
                w.i32(numCols);
                for (int x = 0; x < numCols; x++) w.i32(routingGraph.nextLagunaColumn[x]);
                for (int x = 0; x < numCols; x++) w.i32(routingGraph.prevLagunaColumn[x]);
                for (int y = 0; y < numRows; y++) w.i8(routingGraph.intYToNorthboundLaguna[y] ? 1 : 0);
            }

            // NODES
            w.i32(universe.size());
            // Stable id order: iterate by id.
            NInfo[] byId = new NInfo[universe.size()];
            for (NInfo ni : universe.values()) byId[ni.id] = ni;
            for (NInfo ni : byId) {
                RouteNode rn = ni.rnode;
                Tile tile = rn.getTile();
                TileTypeEnum tt = tile.getTileTypeEnum();
                boolean isLaguna = Utils.isLaguna(tt);
                boolean isPinfeed = rn.getIntentCode() == IntentCode.NODE_PINFEED;
                boolean isPinbounce = rn.getIntentCode() == IntentCode.NODE_PINBOUNCE;
                boolean pinfeedLeadsToLaguna = false;
                if (isPinfeed && routingGraph.wireIndicesLeadingToLaguna != null) {
                    java.util.BitSet[] bs = routingGraph.wireIndicesLeadingToLaguna.get(tile);
                    pinfeedLeadsToLaguna = (bs != null && bs[0].get(rn.getWireIndex()));
                }
                boolean preserved = routingGraph.isPreserved(rn);
                boolean arcLocked = rn.isArcLocked();
                int flags = (ni.createdAtInit ? 1 : 0)
                        | (isLaguna ? 2 : 0)
                        | (isPinfeed ? 4 : 0)
                        | (pinfeedLeadsToLaguna ? 8 : 0)
                        | (ni.expanded ? 16 : 0)
                        | (arcLocked ? 32 : 0)
                        | (preserved ? 64 : 0)
                        | (isPinbounce ? 128 : 0);

                w.i32(tile.getUniqueAddress());
                w.i32(rn.getWireIndex());
                w.i8(rn.getType().ordinal());
                w.i8(flags);
                w.i16(rn.getBeginTileXCoordinate());
                w.i16(rn.getBeginTileYCoordinate());
                w.i16(rn.getEndTileXCoordinate());
                w.i16(rn.getEndTileYCoordinate());
                w.i16(rn.getLength());
                w.f32(safeBaseCost(rn));
                w.i32(rn.hashCode());
                RouteNode prev = rn.getPrev();
                w.i32(prev == null ? -1 : idOf(prev));
                int[] ch = ni.childIds == null ? new int[0] : ni.childIds;
                w.i32(ch.length);
                for (int cid : ch) w.i32(cid);
            }

            // NETS / CONNECTIONS
            List<NetWrapper> wrappers = new ArrayList<>(nets.values());
            w.i32(wrappers.size());
            int totalConns = 0;
            for (NetWrapper nw : wrappers) {
                w.f32(nw.getXCenter());
                w.f32(nw.getYCenter());
                w.i16(nw.getDoubleHpwl());
                w.i32(nw.getConnections().size());
                w.i32(nw.getSourceRnode() == null ? -1 : idOf(nw.getSourceRnode()));

                List<Connection> indirect = new ArrayList<>();
                for (Connection c : nw.getConnections()) {
                    if (!c.isDirect()) indirect.add(c);
                }
                w.i32(indirect.size());
                for (Connection c : indirect) {
                    totalConns++;
                    w.i32(c.hashCode());
                    w.i32(idOf(c.getSourceRnode()));
                    w.i32(idOf(c.getSinkRnode()));
                    List<RouteNode> alts = c.getAltSinkRnodes();
                    w.i32(alts.size());
                    for (RouteNode a : alts) w.i32(idOf(a));
                    w.i16(c.getXMinBB()); w.i16(c.getXMaxBB());
                    w.i16(c.getYMinBB()); w.i16(c.getYMaxBB());
                    w.i16(c.getHpwl());
                    w.i8(c.isCrossSLRnorth() ? 1 : 0);
                    w.i8(c.isCrossSLRsouth() ? 1 : 0);
                    // Already-reconstructed routing for partially-routed nets.
                    boolean routedAtInit = c.isRouted();
                    List<RouteNode> rns = c.getRnodes();
                    w.i8(routedAtInit ? 1 : 0);
                    w.i32(rns.size());
                    for (RouteNode rn : rns) w.i32(idOf(rn));
                }
            }
            System.out.println("INFO: [cpp-prob] nets=" + wrappers.size() + " indirectConns=" + totalConns
                    + " bbox=[" + xMin + "," + xMax + "]x[" + yMin + "," + yMax + "]");
        }
    }

    // Flags for the lazy format / getChildrenPacked (low 5 bits shared with child records).
    protected int nodeFlags(RouteNode rn, boolean createdAtInit) {
        Tile tile = rn.getTile();
        boolean isLaguna = Utils.isLaguna(tile.getTileTypeEnum());
        boolean isPinfeed = rn.getIntentCode() == IntentCode.NODE_PINFEED;
        boolean isPinbounce = rn.getIntentCode() == IntentCode.NODE_PINBOUNCE;
        boolean pinfeedLeadsToLaguna = false;
        if (isPinfeed && routingGraph.wireIndicesLeadingToLaguna != null) {
            java.util.BitSet[] bs = routingGraph.wireIndicesLeadingToLaguna.get(tile);
            pinfeedLeadsToLaguna = (bs != null && bs[0].get(rn.getWireIndex()));
        }
        boolean preserved = routingGraph.isPreserved(rn);
        return (isLaguna ? 1 : 0) | (isPinfeed ? 2 : 0) | (pinfeedLeadsToLaguna ? 4 : 0)
                | (isPinbounce ? 8 : 0) | (preserved ? 16 : 0)
                | (rn.isArcLocked() ? 32 : 0) | (createdAtInit ? 64 : 0);
    }

    // Lazy (RRT2) serialization: config + device arrays + SEED nodes (initial rnodes only,
    // with attrs + existing-route prev) + nets/connections by KEY. NO bbox materialisation,
    // NO adjacency — the C++ side pulls children on demand via getChildrenPacked(). This removes
    // the slow whole-bbox materialise that dominated the JNI-A measurement.
    protected void writeRrtLazy(OutputStream osArg) throws IOException {
        try (LEStream out = new LEStream(osArg)) {
            LE w = out.w;
            w.magic("RRT2");

            // CONFIG (identical layout to RRT1)
            w.i32(config.getMaxIterations());
            w.i32(config.getBoundingBoxExtensionX());
            w.i32(config.getBoundingBoxExtensionY());
            w.i32(config.isEnlargeBoundingBox() ? 1 : 0);
            w.i32(config.getExtensionXIncrement());
            w.i32(config.getExtensionYIncrement());
            w.i32(config.isUseBoundingBox() ? 1 : 0);
            w.f32(config.getWirelengthWeight());
            w.f32(config.getShareExponent());
            w.f32(config.getInitialPresentCongestionFactor());
            w.f32(config.getPresentCongestionMultiplier());
            w.f32(config.getHistoricalCongestionFactor());
            w.f32(config.getMaxPresentCongestionFactor());
            w.i32(maxDetourToSnapBackToPrevLagunaColumn);
            w.i32(routingGraph.SUPER_LONG_LINE_LENGTH_IN_TILES);
            w.i32(config.isUseUTurnNodes() ? 1 : 0);

            // DEVICE ARRAYS
            int numRows = routingGraph.intYToSLRIndex.length;
            w.i32(numRows);
            for (int y = 0; y < numRows; y++) w.i32(routingGraph.intYToSLRIndex[y]);
            boolean hasLaguna = routingGraph.nextLagunaColumn != null;
            w.i32(hasLaguna ? 1 : 0);
            if (hasLaguna) {
                int numCols = routingGraph.nextLagunaColumn.length;
                w.i32(numCols);
                for (int x = 0; x < numCols; x++) w.i32(routingGraph.nextLagunaColumn[x]);
                for (int x = 0; x < numCols; x++) w.i32(routingGraph.prevLagunaColumn[x]);
                for (int y = 0; y < numRows; y++) w.i8(routingGraph.intYToNorthboundLaguna[y] ? 1 : 0);
            }

            // SEEDS = initial rnodes (sources/sinks/alt-sinks/existing-route nodes). This is the BULK of the
            // problem bytes (~all created rnodes). PARALLELIZED (32-cap) the same way: each seed record is
            // self-contained (read-only getters of stored fields), chunks serialize concurrently into
            // per-thread buffers concatenated IN ORDER -> byte-identical to serial. Device build is done by
            // now (hidden behind read+init), so this is the ONLY parallel region active -> <=32 threads.
            final List<RouteNode> seeds = new ArrayList<>();
            for (RouteNode rn : routingGraph.getRnodes()) seeds.add(rn);
            w.i32(seeds.size());
            final int nS = seeds.size();
            int PS = Math.max(1, Math.min(RWRoute.rwMaxThreads(), Runtime.getRuntime().availableProcessors()));
            long _ts = System.nanoTime();
            if (nS < 1024 || PS == 1) {
                for (RouteNode rn : seeds) writeSeed(w, rn);
            } else {
                final byte[][] parts = new byte[PS][];
                Thread[] th = new Thread[PS];
                final int chunk = (nS + PS - 1) / PS;
                for (int t = 0; t < PS; t++) {
                    final int lo = t * chunk, hi = Math.min(nS, lo + chunk), ti = t;
                    th[t] = new Thread(() -> {
                        try {
                            LE lw = new LE(1 << 20);          // unsynchronized buffer (see LE)
                            for (int i = lo; i < hi; i++) writeSeed(lw, seeds.get(i));
                            parts[ti] = lw.data();
                        } catch (IOException e) { throw new RuntimeException(e); }
                    });
                    th[t].start();
                }
                for (Thread x : th) { try { x.join(); } catch (InterruptedException e) { throw new RuntimeException(e); } }
                for (byte[] p : parts) if (p != null) w.raw(p);   // concatenate IN ORDER (byte-identical)
            }
            System.err.printf("INFO: [cpp-prob] serializeSeeds seeds=%d threads=%d %.2fs%n", nS,
                    (nS < 1024 || PS == 1) ? 1 : PS, (System.nanoTime() - _ts) / 1e9);

            // NETS / CONNECTIONS (node refs by KEY = tileUniqueAddress, wireIndex).
            // PARALLELIZED (32-cap): every net record is self-contained (all getters are read-only on the
            // now-stable design), so chunks of wrappers serialize concurrently into per-thread buffers that
            // are concatenated IN ORDER -> byte-identical to the serial output. The device build is finished
            // by now (hidden behind read+init), so this is the ONLY parallel region active -> <=32 threads.
            List<NetWrapper> wrappers = new ArrayList<>(nets.values());
            w.i32(wrappers.size());
            int nW = wrappers.size();
            int P = Math.max(1, Math.min(RWRoute.rwMaxThreads(), Runtime.getRuntime().availableProcessors()));
            long _tn = System.nanoTime();
            if (nW < 1024 || P == 1) {
                for (NetWrapper nw : wrappers) writeWrapper(w, nw);   // small: serial (parallel overhead not worth it)
            } else {
                final byte[][] parts = new byte[P][];
                final int[] partNets = new int[P];
                final int[] partConns = new int[P];
                Thread[] th = new Thread[P];
                final int chunk = (nW + P - 1) / P;
                for (int t = 0; t < P; t++) {
                    final int lo = t * chunk, hi = Math.min(nW, lo + chunk), ti = t;
                    th[t] = new Thread(() -> {
                        try {
                            LE lw = new LE(1 << 20);          // unsynchronized buffer (see LE)
                            int cc = 0;
                            for (int i = lo; i < hi; i++) {
                                writeWrapper(lw, wrappers.get(i));
                                for (Connection c : wrappers.get(i).getConnections())
                                    if (!c.isDirect()) cc++;   // the stream carries INDIRECT conns only
                            }
                            parts[ti] = lw.data();
                            partNets[ti] = hi - lo;
                            partConns[ti] = cc;
                        } catch (IOException e) { throw new RuntimeException(e); }
                    });
                    th[t].start();
                }
                for (Thread x : th) { try { x.join(); } catch (InterruptedException e) { throw new RuntimeException(e); } }
                // Chunk table so the C++ NETS parse can go P-wide (magic = NaN bit pattern: a legacy
                // reader position holds xCenter here, which is never NaN -> unambiguous versioning).
                w.i32(0xFFC0DE01);
                w.i32(P);
                for (int t = 0; t < P; t++) {
                    w.i32(partNets[t]);
                    w.i32(partConns[t]);
                    w.i32(parts[t] == null ? 0 : parts[t].length);
                }
                for (byte[] p : parts) if (p != null) w.raw(p);   // concatenate IN ORDER (byte-identical)
            }
            System.err.printf("INFO: [cpp-prob] serializeNets nets=%d threads=%d %.2fs%n", nW,
                    (nW < 1024 || P == 1) ? 1 : P, (System.nanoTime() - _tn) / 1e9);

            // PRESERVE: all preserved node keys (design-specific) so the C++ device model can set
            // the preserved bit without per-node JNI. Enumerated from RouteNodeGraph.preservedMap.
            writePreserve(w);
        }
    }

    @SuppressWarnings("unchecked")
    private void writePreserve(LE w) throws IOException {
        try {
            java.lang.reflect.Field f = RouteNodeGraph.class.getDeclaredField("preservedMap");
            f.setAccessible(true);
            java.util.concurrent.atomic.AtomicReferenceArray<Object> map =
                    (java.util.concurrent.atomic.AtomicReferenceArray<Object>) f.get(routingGraph);
            java.util.List<int[]> keys = new java.util.ArrayList<>();
            for (int addr = 0; addr < map.length(); addr++) {
                Object arr = map.get(addr);
                if (arr == null) continue;
                int len = java.lang.reflect.Array.getLength(arr);
                for (int wi = 0; wi < len; wi++)
                    if (java.lang.reflect.Array.get(arr, wi) != null) keys.add(new int[]{addr, wi});
            }
            w.i32(keys.size());
            for (int[] k : keys) { w.i32(k[0]); w.i32(k[1]); }
            System.out.println("INFO: [cpp-prob] preserved nodes = " + keys.size());
        } catch (ReflectiveOperationException e) {
            throw new RuntimeException("ERROR: cannot enumerate preservedMap", e);
        }
    }

    private static void writeKey(LE w, RouteNode rn) throws IOException {
        if (rn == null) { w.i32(-1); w.i32(-1); }
        else { w.i32(rn.getTile().getUniqueAddress()); w.i32(rn.getWireIndex()); }
    }

    // Serialize ONE seed rnode record (self-contained; read-only getters of stored fields) — used by the
    // parallel SEEDS loop. Instance method because nodeFlags() reads the routing graph (read-only).
    private void writeSeed(LE w, RouteNode rn) throws IOException {
        Tile tile = rn.getTile();
        w.i32(tile.getUniqueAddress());
        w.i32(rn.getWireIndex());
        w.i8(rn.getType().ordinal());
        w.i32(nodeFlags(rn, true));
        w.i16(rn.getBeginTileXCoordinate());
        w.i16(rn.getBeginTileYCoordinate());
        w.i16(rn.getEndTileXCoordinate());
        w.i16(rn.getEndTileYCoordinate());
        w.i16(rn.getLength());
        w.f32(safeBaseCost(rn));
        w.i32(rn.hashCode());
        RouteNode prev = rn.getPrev();
        if (prev == null) { w.i32(-1); w.i32(-1); }
        else { w.i32(prev.getTile().getUniqueAddress()); w.i32(prev.getWireIndex()); }
    }

    // Serialize ONE net record (self-contained; all getters read-only) — used by the parallel NETS loop.
    private static void writeWrapper(LE w, NetWrapper nw) throws IOException {
        w.f32(nw.getXCenter());
        w.f32(nw.getYCenter());
        w.i16(nw.getDoubleHpwl());
        w.i32(nw.getConnections().size());
        writeKey(w, nw.getSourceRnode());
        List<Connection> indirect = new ArrayList<>();
        for (Connection c : nw.getConnections()) if (!c.isDirect()) indirect.add(c);
        w.i32(indirect.size());
        for (Connection c : indirect) {
            w.i32(c.hashCode());
            writeKey(w, c.getSourceRnode());
            writeKey(w, c.getSinkRnode());
            List<RouteNode> alts = c.getAltSinkRnodes();
            w.i32(alts.size());
            for (RouteNode a : alts) writeKey(w, a);
            w.i16(c.getXMinBB()); w.i16(c.getXMaxBB());
            w.i16(c.getYMinBB()); w.i16(c.getYMaxBB());
            w.i16(c.getHpwl());
            w.i8(c.isCrossSLRnorth() ? 1 : 0);
            w.i8(c.isCrossSLRsouth() ? 1 : 0);
            w.i8(c.isRouted() ? 1 : 0);
            List<RouteNode> rns = c.getRnodes();
            w.i32(rns.size());
            for (RouteNode rn : rns) writeKey(w, rn);
        }
    }

    protected static float safeBaseCost(RouteNode rn) {
        // getBaseCost() asserts non-EXCLUSIVE_SOURCE; sources are never queried for base cost.
        return (rn.getType() == RouteNodeType.EXCLUSIVE_SOURCE) ? 0.4f : rn.getBaseCost();
    }

    private static boolean inBox(RouteNode rn, int xMin, int xMax, int yMin, int yMax) {
        int x = rn.getEndTileXCoordinate();
        int y = rn.getEndTileYCoordinate();
        return x >= xMin && x <= xMax && y >= yMin && y <= yMax;
    }

    private static final class LEStream implements AutoCloseable {
        final OutputStream os;
        final LE w;
        LEStream(OutputStream os_) {
            os = os_;
            w = new LE(os);
        }
        @Override public void close() throws IOException { os.flush(); os.close(); }
    }

    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("USAGE: <input.dcp> <output.rrt> [rwroute args...]");
            return;
        }
        String inputDcp = args[0];
        String rrtFile = args[1];
        String[] rwrouteArgs = Arrays.copyOfRange(args, 2, args.length);

        CodePerfTracker t = new CodePerfTracker("RWRouteCppProblemExport", true);
        Design design = Design.readCheckpoint(inputDcp);

        RWRouteConfig config = new RWRouteConfig(rwrouteArgs);
        preprocess(design);
        List<SitePinInst> pinsToRoute = getUnroutedPins(design);

        RWRouteCppProblemExport router = new RWRouteCppProblemExport(design, config, pinsToRoute, rrtFile);
        routeDesign(router);  // exits inside routeIndirectConnectionsIteratively()
        t.stop();
    }
}
