/*
 * Diagnoses whether the per-tile-TYPE "wire -> node-base offset" template is actually constant
 * across all tiles of a type (the assumption RWDeviceCompactExport relies on). For each type it
 * builds the rep template (max-non-null tile) then checks a large sample of that type's tiles,
 * counting wires whose actual (dx,dy,baseWire) differs. Reports the worst offenders so we know if
 * the fidelity gap is laguna/edge-only (fixable with exceptions) or pervasive (needs union-find).
 */
package com.xilinx.rapidwright.rwroute;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.xilinx.rapidwright.device.Device;
import com.xilinx.rapidwright.device.Node;
import com.xilinx.rapidwright.device.Tile;
import com.xilinx.rapidwright.device.TileTypeEnum;

public class RWDeviceTemplateCheck {
    public static void main(String[] args) {
        String part = args.length > 0 ? args[0] : "xcvu13p-fhgb2104-2-e";
        Device device = Device.getDevice(part);

        Map<TileTypeEnum, List<Tile>> byType = new HashMap<>();
        for (Tile t : device.getAllTiles())
            byType.computeIfAbsent(t.getTileTypeEnum(), k -> new ArrayList<>()).add(t);

        long totalWiresChecked = 0, totalMismatch = 0;
        // collect per-type mismatch
        List<String> rows = new ArrayList<>();
        for (Map.Entry<TileTypeEnum, List<Tile>> e : byType.entrySet()) {
            TileTypeEnum tt = e.getKey();
            List<Tile> tiles = e.getValue();
            // rep = max non-null nodes among a sample (same heuristic as exporter)
            Tile rep = null; int best = -1; int sample = Math.min(tiles.size(), 64);
            for (int s = 0; s < sample; s++) {
                Tile c = tiles.get((int) ((long) s * tiles.size() / sample));
                int wc = c.getWireCount(), nn = 0;
                for (int w = 0; w < wc; w++) if (Node.getNode(c, w) != null) nn++;
                if (nn > best) { best = nn; rep = c; }
            }
            int wc = rep.getWireCount();
            int[] dx = new int[wc], dy = new int[wc], bw = new int[wc];
            for (int w = 0; w < wc; w++) {
                Node n = Node.getNode(rep, w);
                if (n == null) { bw[w] = Integer.MIN_VALUE; continue; }
                dx[w] = n.getTile().getColumn() - rep.getColumn();
                dy[w] = n.getTile().getRow() - rep.getRow();
                bw[w] = n.getWireIndex();
            }
            // check against a sample of tiles
            int checkTiles = Math.min(tiles.size(), 4000);
            long mism = 0, checked = 0;
            for (int s = 0; s < checkTiles; s++) {
                Tile t = tiles.get((int) ((long) s * tiles.size() / checkTiles));
                for (int w = 0; w < wc; w++) {
                    Node n = Node.getNode(t, w);
                    checked++;
                    int adx, ady, abw;
                    if (n == null) { adx = 0; ady = 0; abw = Integer.MIN_VALUE; }
                    else { adx = n.getTile().getColumn() - t.getColumn(); ady = n.getTile().getRow() - t.getRow(); abw = n.getWireIndex(); }
                    if (adx != dx[w] || ady != dy[w] || abw != bw[w]) mism++;
                }
            }
            totalWiresChecked += checked; totalMismatch += mism;
            if (mism > 0)
                rows.add(String.format("%-24s tiles=%-7d checked=%-6d wire-mismatch=%d (%.2f%%)",
                        tt, tiles.size(), checkTiles, mism, 100.0 * mism / checked));
        }
        rows.sort((a, b) -> {
            long ma = Long.parseLong(a.replaceAll(".*wire-mismatch=(\\d+).*", "$1"));
            long mb = Long.parseLong(b.replaceAll(".*wire-mismatch=(\\d+).*", "$1"));
            return Long.compare(mb, ma);
        });
        System.out.println("=== per-type template mismatches (sampled) ===");
        for (String r : rows) System.out.println(r);
        System.out.printf("TOTAL sampled wires=%d  mismatches=%d (%.3f%%)%n",
                totalWiresChecked, totalMismatch, 100.0 * totalMismatch / totalWiresChecked);
    }
}
