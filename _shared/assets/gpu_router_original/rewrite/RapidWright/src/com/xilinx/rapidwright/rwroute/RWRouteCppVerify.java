/*
 * Fast legality gate for a routed DCP: UNROUTED (sink pins not reachable over their net's PIPs)
 * and shorts (a PIP used by more than one net) -- the exact same gate RWRouteCppCheck applies,
 * minus the wirelength metric (not needed for the gate). Two uses:
 *   1) IN-PROCESS post-write self-verification from RWRouteCppJni.main(): the device, JIT and page
 *      cache are already warm, so re-reading the written DCP and checking costs ~20s instead of the
 *      ~80s a fresh checker JVM needs on a big case (device load + cold JIT + serial walks).
 *   2) Standalone main() for A/B validation against RWRouteCppCheck (counts must match exactly).
 * The per-net walks are parallel: DesignTools.updatePinsIsRouted(Net) touches only that net's pins
 * plus read-only device state, and the PIP-overlap check reduces each PIP to a primitive long key
 * (tile,startWire,endWire) instead of a HashMap<PIP,Set<Net>> of ~14M entries.
 */
package com.xilinx.rapidwright.rwroute;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.design.DesignTools;
import com.xilinx.rapidwright.design.Net;
import com.xilinx.rapidwright.design.NetTools;
import com.xilinx.rapidwright.design.SitePinInst;
import com.xilinx.rapidwright.device.PIP;

public class RWRouteCppVerify {

    public static final class Result {
        public int nets, sinks, routed, unrouted;
        public long shorts, totalPips;
        public double readS, walkS, shortS;
        public boolean legal() { return unrouted == 0 && shorts == 0; }
        public String checkLine(String path) {
            return String.format("CHECK %s: nets=%d sinks=%d routed=%d UNROUTED=%d shorts(PIPoverlaps)=%d totalPIPs=%d",
                    path, nets, sinks, routed, unrouted, shorts, totalPips);
        }
    }

    // (tile,startWire,endWire) -> primitive key. Tile unique address needs 18 bits on xcvu13p
    // (~206k tiles), wire indices fit 17 bits each; 52 bits total. Within-net duplicates are removed
    // per net, so any key that appears >1 times globally was contributed by >=2 distinct nets = short.
    private static long pipKey(PIP p) {
        return (((long) p.getTile().getUniqueAddress()) << 34)
                | (((long) (p.getStartWireIndex() & 0x1FFFF)) << 17)
                | (p.getEndWireIndex() & 0x1FFFF);
    }

    /** Read-only mirror of DesignTools.updatePinsIsRouted(Net): identical reachability semantics
     *  (BFS over NetTools.getNodeTrees following PIPs, sink = reached iff its connected node is hit),
     *  but never touches SitePinInst.isRouted -- so it can run CONCURRENTLY with writeCheckpoint
     *  (both sides are then read-only over the physical netlist). Counting is strictly over
     *  net.getSinkPins() -- the same membership the external checker uses; counting !isOutPin over
     *  getPins() instead was measured ONE pin higher on mcml_RLE (a false verify alarm -> a wasted
     *  serial retry). Returns (sinks<<32)|routed. */
    private static long routedSinksReadOnly(Net net) {
        List<SitePinInst> sinkPins = net.getSinkPins();
        int sinks = sinkPins.size();
        int routed = 0;
        if (net.hasPIPs() && sinks > 0) {
            Set<SitePinInst> sinkSet = Collections.newSetFromMap(new IdentityHashMap<>());
            sinkSet.addAll(sinkPins);
            java.util.Map<com.xilinx.rapidwright.device.Node, SitePinInst> node2spi = new java.util.HashMap<>();
            for (SitePinInst spi : net.getPins()) node2spi.put(spi.getConnectedNode(), spi);
            Set<NetTools.NodeTree> visited = Collections.newSetFromMap(new IdentityHashMap<>());
            java.util.Queue<NetTools.NodeTree> queue = new java.util.ArrayDeque<>();
            for (NetTools.NodeTree node : NetTools.getNodeTrees(net)) {
                if (node.fanouts.isEmpty()) continue;   // skip source pins with no fanout
                queue.add(node);
            }
            while (!queue.isEmpty()) {
                NetTools.NodeTree node = queue.poll();
                SitePinInst spi = node2spi.remove(node);
                if (spi != null && sinkSet.contains(spi)) routed++;
                for (NetTools.NodeTree fanout : node.fanouts) {
                    if (fanout.multiplyDriven && !visited.add(fanout)) continue;
                    queue.add(fanout);
                }
            }
        }
        return ((long) sinks << 32) | (routed & 0xFFFFFFFFL);
    }

    /** Legality gate on the IN-MEMORY design (post-setPIPs state == exactly what writeCheckpoint
     *  serializes). Read-only by construction (see routedSinksReadOnly) -> may overlap the write.
     *  Same counting semantics as check()/RWRouteCppCheck: signal nets only for sinks, all nets for
     *  PIP totals, cross-net PIP-overlap count for shorts. */
    public static Result checkInMemory(Design design, int threads) throws InterruptedException {
        final Result r = new Result();
        final List<Net> nets = new ArrayList<>(design.getNets());
        r.nets = nets.size();
        final int n = nets.size();
        final int T = Math.max(1, Math.min(threads, n));
        final long[][] perNetKeys = new long[n][];
        final AtomicInteger cursor = new AtomicInteger(0);
        final AtomicLong pipsTotal = new AtomicLong(0);
        final int[] sinkCnt = new int[T], routedCnt = new int[T];
        Thread[] pool = new Thread[T];
        final Throwable[] fail = new Throwable[1];
        for (int w = 0; w < T; w++) {
            final int wi = w;
            pool[w] = new Thread(() -> {
                try {
                    int chunk;
                    while ((chunk = cursor.getAndAdd(64)) < n) {
                        int hi = Math.min(n, chunk + 64);
                        for (int i = chunk; i < hi; i++) {
                            Net net = nets.get(i);
                            List<PIP> pips = net.getPIPs();
                            pipsTotal.addAndGet(pips.size());
                            if (!pips.isEmpty()) {
                                long[] keys = new long[pips.size()];
                                for (int k = 0; k < keys.length; k++) keys[k] = pipKey(pips.get(k));
                                Arrays.sort(keys);
                                int m = 0;
                                for (int k = 0; k < keys.length; k++)
                                    if (m == 0 || keys[k] != keys[m - 1]) keys[m++] = keys[k];
                                perNetKeys[i] = (m == keys.length) ? keys : Arrays.copyOf(keys, m);
                            }
                            if (net.isStaticNet() || net.isClockNet()) continue;
                            if (net.getSource() == null) continue;
                            long sr = routedSinksReadOnly(net);
                            sinkCnt[wi] += (int) (sr >>> 32);
                            routedCnt[wi] += (int) sr;
                        }
                    }
                } catch (Throwable e) {
                    synchronized (fail) { if (fail[0] == null) fail[0] = e; }
                }
            }, "rw-verify-mem-" + w);
            pool[w].start();
        }
        for (Thread th : pool) th.join();
        if (fail[0] != null) throw new RuntimeException("in-memory verify worker failed", fail[0]);
        for (int w = 0; w < T; w++) { r.sinks += sinkCnt[w]; r.routed += routedCnt[w]; }
        r.unrouted = r.sinks - r.routed;
        r.totalPips = pipsTotal.get();
        long total = 0;
        for (long[] k : perNetKeys) if (k != null) total += k.length;
        long[] all = new long[(int) total];
        int off = 0;
        for (int i = 0; i < n; i++) {
            long[] k = perNetKeys[i];
            if (k == null) continue;
            System.arraycopy(k, 0, all, off, k.length);
            off += k.length;
            perNetKeys[i] = null;
        }
        Arrays.parallelSort(all);
        long overlaps = 0;
        for (int i = 0; i < all.length; ) {
            int j = i + 1;
            while (j < all.length && all[j] == all[i]) j++;
            if (j - i > 1) overlaps++;
            i = j;
        }
        r.shorts = overlaps;
        return r;
    }

    public static Result check(Design design, int threads) throws InterruptedException {
        final Result r = new Result();
        final List<Net> nets = new ArrayList<>(design.getNets());
        r.nets = nets.size();
        final int n = nets.size();
        final int T = Math.max(1, Math.min(threads, n));

        // Pass 1 (parallel over nets): per-net isRouted derivation + per-net deduped PIP keys.
        final long[][] perNetKeys = new long[n][];
        final AtomicInteger cursor = new AtomicInteger(0);
        final AtomicLong pipsTotal = new AtomicLong(0);
        final int[] sinkCnt = new int[T], routedCnt = new int[T], unroutedCnt = new int[T];
        Thread[] pool = new Thread[T];
        final Throwable[] fail = new Throwable[1];
        for (int w = 0; w < T; w++) {
            final int wi = w;
            pool[w] = new Thread(() -> {
                try {
                    int chunk;
                    while ((chunk = cursor.getAndAdd(64)) < n) {
                        int hi = Math.min(n, chunk + 64);
                        for (int i = chunk; i < hi; i++) {
                            Net net = nets.get(i);
                            List<PIP> pips = net.getPIPs();
                            pipsTotal.addAndGet(pips.size());
                            if (!pips.isEmpty()) {
                                long[] keys = new long[pips.size()];
                                for (int k = 0; k < keys.length; k++) keys[k] = pipKey(pips.get(k));
                                Arrays.sort(keys);
                                int m = 0;                      // in-place dedupe within the net
                                for (int k = 0; k < keys.length; k++)
                                    if (m == 0 || keys[k] != keys[m - 1]) keys[m++] = keys[k];
                                perNetKeys[i] = (m == keys.length) ? keys : Arrays.copyOf(keys, m);
                            }
                            Set<NetTools.NodeTree> visited =
                                    Collections.newSetFromMap(new IdentityHashMap<>());
                            DesignTools.updatePinsIsRouted(net, visited);
                            if (net.isStaticNet() || net.isClockNet()) continue;
                            if (net.getSource() == null) continue;   // source-less OOC nets are not routable
                            for (SitePinInst spi : net.getSinkPins()) {
                                sinkCnt[wi]++;
                                if (spi.isRouted()) routedCnt[wi]++;
                                else unroutedCnt[wi]++;
                            }
                        }
                    }
                } catch (Throwable e) {
                    synchronized (fail) { if (fail[0] == null) fail[0] = e; }
                }
            }, "rw-verify-" + w);
            pool[w].start();
        }
        for (Thread th : pool) th.join();
        if (fail[0] != null) throw new RuntimeException("verify worker failed", fail[0]);
        for (int w = 0; w < T; w++) { r.sinks += sinkCnt[w]; r.routed += routedCnt[w]; r.unrouted += unroutedCnt[w]; }
        r.totalPips = pipsTotal.get();

        // Pass 2: global overlap count. Keys are already deduped per net -> sort all, every value
        // occurring >1 times was used by >=2 nets (same "PIP overlap" the external checker counts).
        long total = 0;
        for (long[] k : perNetKeys) if (k != null) total += k.length;
        long[] all = new long[(int) total];
        int off = 0;
        for (int i = 0; i < n; i++) {
            long[] k = perNetKeys[i];
            if (k == null) continue;
            System.arraycopy(k, 0, all, off, k.length);
            off += k.length;
            perNetKeys[i] = null;
        }
        Arrays.parallelSort(all);
        long overlaps = 0;
        for (int i = 0; i < all.length; ) {
            int j = i + 1;
            while (j < all.length && all[j] == all[i]) j++;
            if (j - i > 1) overlaps++;
            i = j;
        }
        r.shorts = overlaps;
        return r;
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 1) { System.out.println("USAGE: <routed.dcp>"); return; }
        long t0 = System.nanoTime();
        Design design = Design.readCheckpoint(args[0]);
        long t1 = System.nanoTime();
        Result r = check(design, RWRoute.rwMaxThreads());
        long t2 = System.nanoTime();
        System.out.println("VERIFY: " + r.checkLine(args[0]));
        System.out.printf("VERIFY-PHASES read=%.2fs check=%.2fs%n", (t1 - t0) / 1e9, (t2 - t1) / 1e9);
    }
}
