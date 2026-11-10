/*
 * Exports a compact device file (RDV3) for xcvu13p so pure-C++ can rebuild the FULL routing graph
 * EXACTLY (104M nodes / 485M edges). Key fix over earlier attempts: node-forming connections are
 * captured PER TILE (= getWireConnections MINUS intra-tile PIP pairs) and tiles are deduped by their
 * exact connection PATTERN (not by tile-type, which is too coarse and over-merges). Each tile applies
 * ITS OWN pattern, so reconstruction is exact by construction; dedup keeps it compact (RapidWright's
 * .dat does the same, hence 12 MB for a 100M-node graph). PIPs are per-tile-type constant (stored once).
 * Generated ONCE offline (device-static, like xcvu13p_db.dat).
 */
package com.xilinx.rapidwright.rwroute;

import java.io.BufferedOutputStream;
import java.io.DataOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import com.xilinx.rapidwright.device.Device;
import com.xilinx.rapidwright.device.Node;
import com.xilinx.rapidwright.device.PIP;
import com.xilinx.rapidwright.device.Tile;
import com.xilinx.rapidwright.device.TileTypeEnum;
import com.xilinx.rapidwright.device.Wire;
import com.xilinx.rapidwright.util.Utils;

public class RWDeviceCompactExport {
    static final int MAGIC = 0x52445633; // "RDV3"

    public static void main(String[] args) throws IOException {
        String part = args.length > 0 ? args[0] : "xcvu13p-fhgb2104-2-e";
        String out = args.length > 1 ? args[1] : "/tmp/xcvu13p.rdv";

        long t0 = System.nanoTime();
        Device device = Device.getDevice(part);
        int nRows = device.getRows(), nCols = device.getColumns();
        System.out.printf("device loaded %.2fs grid=%dx%d%n", (System.nanoTime() - t0) / 1e9, nRows, nCols);

        Set<TileTypeEnum> allowedSet = new HashSet<>(Utils.getLagunaTileTypes());
        allowedSet.add(TileTypeEnum.INT);

        // index tiles by uniqueAddress; assign type indices
        int maxAddr = -1;
        for (Tile t : device.getAllTiles()) maxAddr = Math.max(maxAddr, t.getUniqueAddress());
        int nTiles = maxAddr + 1;
        Tile[] tileByAddr = new Tile[nTiles];
        for (Tile t : device.getAllTiles()) tileByAddr[t.getUniqueAddress()] = t;

        Map<TileTypeEnum, Integer> typeIdx = new HashMap<>();
        List<TileTypeEnum> types = new ArrayList<>();
        for (Tile t : device.getAllTiles())
            if (!typeIdx.containsKey(t.getTileTypeEnum())) { typeIdx.put(t.getTileTypeEnum(), types.size()); types.add(t.getTileTypeEnum()); }
        int nT = types.size();

        // per-type wireCount + PIPs (PIPs are tile-type constant)
        int[] typeWC = new int[nT];
        int[][] pipS = new int[nT][], pipE = new int[nT][]; byte[][] pipB = new byte[nT][];
        for (int ti = 0; ti < nT; ti++) {
            List<Tile> sample = new ArrayList<>();
            for (Tile t : device.getAllTiles()) if (t.getTileTypeEnum() == types.get(ti)) { sample.add(t); if (sample.size() > 64) break; }
            Tile rep = sample.get(0);
            for (Tile t : sample) { if (t.getWireCount() > rep.getWireCount()) rep = t; if (t.getPIPs().size() > rep.getPIPs().size()) rep = t; }
            typeWC[ti] = rep.getWireCount();
            ArrayList<PIP> pips = rep.getPIPs();
            int[] ps = new int[pips.size()], pe = new int[pips.size()]; byte[] pb = new byte[pips.size()];
            for (int p = 0; p < pips.size(); p++) { PIP pip = pips.get(p); ps[p] = pip.getStartWireIndex(); pe[p] = pip.getEndWireIndex(); pb[p] = (byte) (pip.isBidirectional() ? 1 : 0); }
            pipS[ti] = ps; pipE[ti] = pe; pipB[ti] = pb;
        }

        // per-tile pattern (deduped): node-forming conns [w(16) dx(16) dy(16) tw(16)] + isBase bitset.
        // isBase[w] = (w is the canonical base wire of its node in this tile) -> seeds routing-node ids.
        long t1 = System.nanoTime();
        int[] tilePattern = new int[nTiles]; Arrays.fill(tilePattern, -1);
        Map<Long, List<Integer>> byHash = new HashMap<>();
        List<long[]> patterns = new ArrayList<>();
        List<byte[]> patBase = new ArrayList<>();   // per pattern: packed isBase bits (length ceil(wc/8))
        long totalConns = 0;
        int done = 0;
        for (int a = 0; a < nTiles; a++) {
            Tile t = tileByAddr[a]; if (t == null) continue;
            int wc = t.getWireCount();
            Set<Long> pipPairs = new HashSet<>();
            for (PIP pip : t.getPIPs()) { int x = pip.getStartWireIndex(), y = pip.getEndWireIndex();
                pipPairs.add(((long) x << 32) | (y & 0xFFFFFFFFL)); pipPairs.add(((long) y << 32) | (x & 0xFFFFFFFFL)); }
            ArrayList<Long> cl = new ArrayList<>();
            byte[] base = new byte[(wc + 7) >> 3];
            int col = t.getColumn(), row = t.getRow();
            for (int w = 0; w < wc; w++) {
                Node n = Node.getNode(t, w);
                if (n != null && n.getTile() == t && n.getWireIndex() == w) base[w >> 3] |= (1 << (w & 7));
                for (Wire cw : t.getWireConnections(w)) {
                    Tile ct = cw.getTile(); int twi = cw.getWireIndex();
                    if (ct == t && pipPairs.contains(((long) w << 32) | (twi & 0xFFFFFFFFL))) continue; // PIP, not node-forming
                    int dx = ct.getColumn() - col, dy = ct.getRow() - row;
                    cl.add(((long) (w & 0xFFFF) << 48) | ((long) (dx & 0xFFFF) << 32) | ((long) (dy & 0xFFFF) << 16) | (twi & 0xFFFF));
                }
            }
            long[] arr = new long[cl.size()];
            for (int i = 0; i < arr.length; i++) arr[i] = cl.get(i);
            Arrays.sort(arr);
            long h = 1469598103934665603L;
            for (long v : arr) { h ^= v; h *= 1099511628211L; }
            for (byte bb : base) { h ^= (bb & 0xFF); h *= 1099511628211L; }
            List<Integer> cands = byHash.get(h);
            int pid = -1;
            if (cands != null) for (int c : cands) if (Arrays.equals(patterns.get(c), arr) && Arrays.equals(patBase.get(c), base)) { pid = c; break; }
            if (pid < 0) { pid = patterns.size(); patterns.add(arr); patBase.add(base); byHash.computeIfAbsent(h, k -> new ArrayList<>()).add(pid); totalConns += arr.length; }
            tilePattern[a] = pid;
            if (++done % 100000 == 0) System.out.printf("  ...%d tiles, %d patterns%n", done, patterns.size());
        }
        System.out.printf("patterns: %.1fs  %d distinct patterns, %d unique conns%n",
                (System.nanoTime() - t1) / 1e9, patterns.size(), totalConns);

        // ground truth
        long t2 = System.nanoTime(); long expNodes = 0, expEdges = 0;
        for (Tile tile : device.getAllTiles()) {
            if (!allowedSet.contains(tile.getTileTypeEnum())) continue;
            int wc = tile.getWireCount();
            for (int w = 0; w < wc; w++) { Node n = Node.getNode(tile, w);
                if (n == null || n.getTile() != tile || n.getWireIndex() != w) continue; expNodes++;
                for (Node dn : n.getAllDownhillNodes()) if (!RouteNodeGraph.isExcludedTile(dn)) expEdges++; }
        }
        System.out.printf("ground-truth: nodes=%d edges=%d (%.1fs)%n", expNodes, expEdges, (System.nanoTime() - t2) / 1e9);

        // write
        long t3 = System.nanoTime();
        try (DataOutputStream o = new DataOutputStream(new BufferedOutputStream(new FileOutputStream(out), 1 << 22))) {
            o.writeInt(MAGIC);
            o.writeInt(nRows); o.writeInt(nCols); o.writeInt(nTiles); o.writeInt(nT); o.writeInt(patterns.size());
            o.writeLong(expNodes); o.writeLong(expEdges);
            for (int ti = 0; ti < nT; ti++) {
                o.writeByte(allowedSet.contains(types.get(ti)) ? 1 : 0);
                o.writeInt(typeWC[ti]);
                o.writeInt(pipS[ti].length);
                for (int p = 0; p < pipS[ti].length; p++) { o.writeShort(pipS[ti][p]); o.writeShort(pipE[ti][p]); o.writeByte(pipB[ti][p]); }
            }
            for (int pi = 0; pi < patterns.size(); pi++) {
                long[] pat = patterns.get(pi); byte[] base = patBase.get(pi);
                o.writeInt(pat.length); for (long v : pat) o.writeLong(v);
                o.writeInt(base.length); o.write(base);
            }
            for (int a = 0; a < nTiles; a++) {
                Tile t = tileByAddr[a];
                if (t == null) { o.writeShort(-1); o.writeShort(0); o.writeShort(0); o.writeInt(-1); }
                else { o.writeShort(typeIdx.get(t.getTileTypeEnum())); o.writeShort(t.getColumn()); o.writeShort(t.getRow()); o.writeInt(tilePattern[a]); }
            }
        }
        System.out.printf("WROTE %s %.2f MB (%.2fs)%n", out, new java.io.File(out).length() / 1e6, (System.nanoTime() - t3) / 1e9);
    }
}
