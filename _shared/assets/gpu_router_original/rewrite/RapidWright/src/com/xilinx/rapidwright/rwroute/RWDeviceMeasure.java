/*
 * Measures the PER-RUN device overhead that any router pays, to compare Java's current path
 * against a hypothetical pure-C++ device model:
 *   (1) Device.getDevice() cold load time (deserialize xcvu13p_db.dat) + resulting Java heap.
 *   (2) Size of the routing graph actually needed (INT + Laguna base nodes + their allowed-tile
 *       downhill edges) -> estimated C++ device-file size on disk and flat in-RAM footprint.
 * This answers: is a C++ device file (generated once offline, loaded per case like Java's .dat)
 * cheaper to load than Java's device path, and how big is it.
 */
package com.xilinx.rapidwright.rwroute;

import java.util.HashSet;
import java.util.Set;

import com.xilinx.rapidwright.device.Device;
import com.xilinx.rapidwright.device.Node;
import com.xilinx.rapidwright.device.Tile;
import com.xilinx.rapidwright.device.TileTypeEnum;
import com.xilinx.rapidwright.util.Utils;

public class RWDeviceMeasure {
    public static void main(String[] args) {
        String part = args.length > 0 ? args[0] : "xcvu13p-fhgb2104-2-e";
        Runtime rt = Runtime.getRuntime();

        // (1) cold device load = the per-run overhead Java pays (deserialize the .dat)
        long t0 = System.nanoTime();
        Device device = Device.getDevice(part);
        long t1 = System.nanoTime();
        System.gc();
        long memAfterLoad = rt.totalMemory() - rt.freeMemory();
        System.out.printf("DEVICE LOAD (%s): %.3f s   heapUsed=%.2f GB%n",
                part, (t1 - t0) / 1e9, memAfterLoad / 1e9);
        System.out.flush();

        // (2) enumerate the routing graph: base nodes in INT/Laguna tiles + allowed-tile downhill edges
        Set<TileTypeEnum> allowed = new HashSet<>(Utils.getLagunaTileTypes());
        allowed.add(TileTypeEnum.INT);

        long t2 = System.nanoTime();
        long nodeCount = 0, edgeCount = 0, intTiles = 0, lagTiles = 0, maxDownhill = 0, scannedTiles = 0;
        for (Tile tile : device.getAllTiles()) {
            TileTypeEnum tt = tile.getTileTypeEnum();
            if (!allowed.contains(tt)) continue;
            if (tt == TileTypeEnum.INT) intTiles++; else lagTiles++;
            int wc = tile.getWireCount();
            for (int w = 0; w < wc; w++) {
                Node n = Node.getNode(tile, w);
                if (n == null) continue;
                if (n.getTile() != tile || n.getWireIndex() != w) continue;  // count each node once at its base
                nodeCount++;
                long dh = 0;
                for (Node dn : n.getAllDownhillNodes()) {
                    if (!RouteNodeGraph.isExcludedTile(dn)) { edgeCount++; dh++; }
                }
                if (dh > maxDownhill) maxDownhill = dh;
            }
            if (++scannedTiles % 20000 == 0) {
                System.out.printf("  ...scanned %d allowed tiles, nodes=%d edges=%d (%.0f s)%n",
                        scannedTiles, nodeCount, edgeCount, (System.nanoTime() - t2) / 1e9);
                System.out.flush();
            }
        }
        long t3 = System.nanoTime();
        System.gc();
        long memAfterScan = rt.totalMemory() - rt.freeMemory();
        System.out.printf("ROUTING GRAPH: nodes=%d  edges=%d  (INT tiles=%d, Laguna tiles=%d)%n",
                nodeCount, edgeCount, intTiles, lagTiles);
        System.out.printf("  scan=%.1f s  maxDownhill=%d  avgDownhill=%.1f  heapAfterScan=%.2f GB%n",
                (t3 - t2) / 1e9, maxDownhill, (double) edgeCount / Math.max(1, nodeCount), memAfterScan / 1e9);

        // C++ device-file size: per node a packed record + concatenated int32 child ids
        for (int recBytes : new int[]{24, 28, 32}) {
            long nB = nodeCount * (long) recBytes;
            long eB = edgeCount * 4L;
            System.out.printf("EST C++ device file @%dB/node: nodes %.0f MB + edges %.0f MB = %.2f GB%n",
                    recBytes, nB / 1e6, eB / 1e6, (nB + eB) / 1e9);
        }
    }
}
