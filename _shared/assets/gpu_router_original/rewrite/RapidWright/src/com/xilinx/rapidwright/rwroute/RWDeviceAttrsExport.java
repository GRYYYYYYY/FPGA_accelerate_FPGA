/*
 * Offline per-node RouteNodeInfo dump (device-static): for every routing node (INT/Laguna base node)
 * computes the EXACT attrs RWRouteCppJni.getChildrenPacked emits — type, device-static flags
 * (laguna/pinfeed/leadsLaguna/pinbounce; NOT preserved which is design-specific), begin/end XY,
 * length, baseCost, hashCode — via the real RapidWright RouteNodeGraph. Correct-by-construction
 * (no logic re-port). The C++ device model reads this instead of calling JNI per node.
 * Format ATR1 (big-endian): magic, count, then per node {baseKey:i64, type:u8, flags4:u8,
 * beginX:i16, beginY:i16, endX:i16, endY:i16, length:i16, baseCost:f32, hashCode:i32}.
 */
package com.xilinx.rapidwright.rwroute;

import java.io.BufferedOutputStream;
import java.io.DataOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.BitSet;
import java.util.HashSet;
import java.util.Set;

import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.device.Device;
import com.xilinx.rapidwright.device.IntentCode;
import com.xilinx.rapidwright.device.Node;
import com.xilinx.rapidwright.device.Tile;
import com.xilinx.rapidwright.device.TileTypeEnum;
import com.xilinx.rapidwright.util.Utils;

public class RWDeviceAttrsExport {
    public static void main(String[] args) throws IOException {
        String part = args.length > 0 ? args[0] : "xcvu13p-fhgb2104-2-e";
        String out = args.length > 1 ? args[1] : "/tmp/xcvu13p.attrs";

        long t0 = System.nanoTime();
        Design design = new Design("dummy", part);
        RWRouteConfig config = new RWRouteConfig(new String[]{"--nonTimingDriven", "--lutPinSwapping"});
        RouteNodeGraph graph = new RouteNodeGraph(design, config);
        Device device = design.getDevice();
        System.out.printf("graph built %.2fs%n", (System.nanoTime() - t0) / 1e9);

        Set<TileTypeEnum> allowed = new HashSet<>(Utils.getLagunaTileTypes());
        allowed.add(TileTypeEnum.INT);

        long t1 = System.nanoTime();
        long count = 0, done = 0;
        try (DataOutputStream o = new DataOutputStream(new BufferedOutputStream(new FileOutputStream(out), 1 << 23))) {
            o.writeInt(0x41545231);  // ATR1
            o.writeLong(0);          // count placeholder
            for (Tile tile : device.getAllTiles()) {
                if (!allowed.contains(tile.getTileTypeEnum())) continue;
                int wc = tile.getWireCount();
                for (int w = 0; w < wc; w++) {
                    Node n = Node.getNode(tile, w);
                    if (n == null || n.getTile() != tile || n.getWireIndex() != w) continue;  // base node only
                    RouteNode rn = graph.getOrCreate(n);
                    // device-static flags (exclude preserved bit16 — design-specific)
                    boolean isLaguna = Utils.isLaguna(tile.getTileTypeEnum());
                    boolean isPinfeed = n.getIntentCode() == IntentCode.NODE_PINFEED;
                    boolean isPinbounce = n.getIntentCode() == IntentCode.NODE_PINBOUNCE;
                    boolean leadsLaguna = false;
                    if (isPinfeed && graph.wireIndicesLeadingToLaguna != null) {
                        BitSet[] bs = graph.wireIndicesLeadingToLaguna.get(tile);
                        leadsLaguna = (bs != null && bs[0].get(w));
                    }
                    int flags4 = (isLaguna ? 1 : 0) | (isPinfeed ? 2 : 0) | (leadsLaguna ? 4 : 0) | (isPinbounce ? 8 : 0);
                    long baseKey = ((long) tile.getUniqueAddress() << 20) | (w & 0xFFFFF);
                    o.writeLong(baseKey);
                    o.writeByte(rn.getType().ordinal());
                    o.writeByte(flags4);
                    o.writeShort(rn.getBeginTileXCoordinate());
                    o.writeShort(rn.getBeginTileYCoordinate());
                    o.writeShort(rn.getEndTileXCoordinate());
                    o.writeShort(rn.getEndTileYCoordinate());
                    o.writeShort(rn.getLength());
                    o.writeFloat(rn.getBaseCost());
                    o.writeInt(rn.hashCode());
                    count++;
                    if (++done % 10000000 == 0) System.out.printf("  ...%d nodes (%.0fs)%n", done, (System.nanoTime() - t1) / 1e9);
                }
            }
        }
        // patch count
        try (java.io.RandomAccessFile raf = new java.io.RandomAccessFile(out, "rw")) {
            raf.seek(4); raf.writeLong(count);
        }
        System.out.printf("WROTE %s  count=%d  %.2f MB  (%.1fs)%n",
                out, count, new java.io.File(out).length() / 1e6, (System.nanoTime() - t1) / 1e9);
    }
}
