/*
 * Harness (addition to RapidWright tree) for the pure-C++ RWRoute port (FPGAIF path).
 *
 * RWRouteCppDeviceSidecar dumps the device-static arrays that RWRoute's RouteNodeGraph computes
 * but that the FPGAIF DeviceResources (.device) file does NOT carry: the INT-Y -> SLR-index map,
 * the next/prev Laguna column maps, the northbound-Laguna flags, the super-long-line length, and
 * the "wire indices leading to a Laguna" bitsets (needed by RouteNodeInfo's type classification and
 * isExcluded's PINFEED rule). Output is a tiny little-endian ".slr" sidecar, generated once per
 * device and consumed by the C++ router alongside the .device.
 */
package com.xilinx.rapidwright.rwroute;

import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.BitSet;
import java.util.Map;

import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.device.Tile;

public class RWRouteCppDeviceSidecar {

    private static final class LE {
        final OutputStream os;
        LE(OutputStream os) { this.os = os; }
        void i8(int v) throws IOException { os.write(v & 0xFF); }
        void i32(int v) throws IOException {
            os.write(v & 0xFF); os.write((v >> 8) & 0xFF); os.write((v >> 16) & 0xFF); os.write((v >> 24) & 0xFF);
        }
        void magic(String m) throws IOException { for (int i = 0; i < 4; i++) os.write(m.charAt(i)); }
        void str(String s) throws IOException { byte[] b = s.getBytes("UTF-8"); i32(b.length); os.write(b); }
    }

    public static void main(String[] args) throws IOException {
        if (args.length < 2) {
            System.out.println("USAGE: <device part, e.g. xcvu13p> <output.slr>");
            return;
        }
        String part = args[0];
        String out = args[1];

        // Build a RouteNodeGraph for the part (empty design is enough; it only needs the Device).
        Design design = new Design("sidecar", part);
        RWRouteConfig config = new RWRouteConfig(new String[]{"--nonTimingDriven", "--lutPinSwapping"});
        RouteNodeGraph graph = new RouteNodeGraph(design, config);

        try (OutputStream os = new BufferedOutputStream(new FileOutputStream(out), 1 << 20)) {
            LE w = new LE(os);
            w.magic("RSLR");
            w.i32(1);  // version

            int numRows = graph.intYToSLRIndex.length;
            w.i32(numRows);
            for (int y = 0; y < numRows; y++) w.i32(graph.intYToSLRIndex[y]);
            w.i32(graph.SUPER_LONG_LINE_LENGTH_IN_TILES);

            boolean hasLaguna = graph.nextLagunaColumn != null;
            w.i32(hasLaguna ? 1 : 0);
            if (hasLaguna) {
                int numCols = graph.nextLagunaColumn.length;
                w.i32(numCols);
                for (int x = 0; x < numCols; x++) w.i32(graph.nextLagunaColumn[x]);
                for (int x = 0; x < numCols; x++) w.i32(graph.prevLagunaColumn[x]);
                for (int y = 0; y < numRows; y++) w.i8(graph.intYToNorthboundLaguna[y] ? 1 : 0);

                // wireIndicesLeadingToLaguna: per Laguna-adjacent INT tile, the bs[0] (IMUX/INODE leading
                // to an SLL) and bs[1] (INT_INT/SDQ) wire indices. Keyed by tile name for the C++ side.
                Map<Tile, BitSet[]> map = graph.wireIndicesLeadingToLaguna;
                w.i32(map.size());
                for (Map.Entry<Tile, BitSet[]> e : map.entrySet()) {
                    Tile tile = e.getKey();
                    BitSet[] bs = e.getValue();
                    w.str(tile.getName());
                    w.i32(tile.getUniqueAddress());
                    writeBitSet(w, bs[0]);
                    writeBitSet(w, bs[1]);
                }
            }
        }
        System.out.println("INFO: [cpp-sidecar] wrote " + out + " (rows=" + graph.intYToSLRIndex.length
                + ", laguna=" + (graph.nextLagunaColumn != null) + ")");
    }

    private static void writeBitSet(LE w, BitSet b) throws IOException {
        w.i32(b.cardinality());
        for (int i = b.nextSetBit(0); i >= 0; i = b.nextSetBit(i + 1)) {
            w.i32(i);
        }
    }
}
