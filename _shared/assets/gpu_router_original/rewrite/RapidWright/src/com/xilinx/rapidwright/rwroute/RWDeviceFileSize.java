/*
 * Measures the size of a COMPACT C++ device file (the "like .dat" option): tile-type templates
 * (deduped across the grid) + the tile grid + per-type wire/PIP/wire-connection counts. This is
 * what C++ needs to lazily reconstruct nodes (getAllDownhillNodes) + RouteNodeInfo, mirroring how
 * RapidWright's 12 MB .dat represents a 100M+ node graph compactly.
 */
package com.xilinx.rapidwright.rwroute;

import java.util.HashMap;
import java.util.Map;
import java.util.TreeMap;

import com.xilinx.rapidwright.device.Device;
import com.xilinx.rapidwright.device.Tile;
import com.xilinx.rapidwright.device.TileTypeEnum;
import com.xilinx.rapidwright.device.Wire;

public class RWDeviceFileSize {
    public static void main(String[] args) {
        String part = args.length > 0 ? args[0] : "xcvu13p-fhgb2104-2-e";
        Device device = Device.getDevice(part);

        // per type: {wireCount, pipCount, wireConnCount} computed once from a representative tile
        Map<TileTypeEnum, long[]> tmpl = new HashMap<>();
        Map<TileTypeEnum, Long> tileCnt = new TreeMap<>();
        long totalTiles = 0;

        for (Tile t : device.getAllTiles()) {
            TileTypeEnum tt = t.getTileTypeEnum();
            totalTiles++;
            tileCnt.merge(tt, 1L, Long::sum);
            if (!tmpl.containsKey(tt)) {
                int wc = t.getWireCount();
                int pc = t.getPIPs().size();
                long conn = 0;
                for (int w = 0; w < wc; w++) {
                    java.util.List<Wire> wcs = t.getWireConnections(w);
                    if (wcs != null) conn += wcs.size();
                }
                tmpl.put(tt, new long[]{wc, pc, conn});
            }
        }

        long sumWires = 0, sumPips = 0, sumConns = 0;
        for (long[] v : tmpl.values()) { sumWires += v[0]; sumPips += v[1]; sumConns += v[2]; }

        System.out.printf("distinct tile types=%d   total tiles=%d%n", tmpl.size(), totalTiles);
        System.out.printf("template totals (deduped per type): wires=%d  pips=%d  wireConns=%d%n",
                sumWires, sumPips, sumConns);

        // compact-file size: templates (wire 4B + pip 4B + conn 4-8B) + grid (tile 8-12B)
        for (int connB : new int[]{4, 6, 8}) {
            long tmplBytes = sumWires * 4 + sumPips * 4 + sumConns * (long) connB;
            long gridBytes = totalTiles * 10;
            System.out.printf("EST compact file @%dB/conn: templates %.1f MB + grid %.1f MB = %.1f MB%n",
                    connB, tmplBytes / 1e6, gridBytes / 1e6, (tmplBytes + gridBytes) / 1e6);
        }

        // biggest tile types by total wire-connections (templates that dominate)
        System.out.println("--- top tile types by tiles*? (routing-relevant) ---");
        long[] intV = tmpl.get(TileTypeEnum.INT);
        if (intV != null)
            System.out.printf("INT: wires=%d pips=%d wireConns=%d  (x %d tiles)%n",
                    intV[0], intV[1], intV[2], tileCnt.get(TileTypeEnum.INT));
        for (Map.Entry<TileTypeEnum, Long> e : tileCnt.entrySet()) {
            if (e.getValue() > 1000) {
                long[] v = tmpl.get(e.getKey());
                System.out.printf("  %-22s count=%-8d wires=%d pips=%d conns=%d%n",
                        e.getKey(), e.getValue(), v[0], v[1], v[2]);
            }
        }
    }
}
