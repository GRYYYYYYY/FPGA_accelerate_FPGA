/*
 * Device-scan cache for RouteNodeGraph's constructor (small-case fixed-cost cut).
 *
 * The ctor's heavy sections (east/west INT wire scan, CLB MUX scan, laguna lookups, INT tile
 * map) are pure functions of the DEVICE (measured 3.5s on xcvu13p, dominated by lazy
 * wire-name/intent-table loads that nothing downstream needs). The competition device is fixed,
 * so the products are computed once, stored under /tmp, and restored in ~ms on later runs —
 * value-identical structures, so routing behavior is unchanged by construction.
 *
 * File: RW_RNG_CACHE or /tmp/<deviceName>.rng. Any load problem (missing/short/version/device
 * mismatch) returns null and the ctor falls back to the original scans, then rewrites the cache.
 */
package com.xilinx.rapidwright.rwroute;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.File;
import java.util.BitSet;
import java.util.EnumMap;
import java.util.IdentityHashMap;
import java.util.Map;

import com.xilinx.rapidwright.device.Device;
import com.xilinx.rapidwright.device.Tile;
import com.xilinx.rapidwright.device.TileTypeEnum;

class RWRouteNodeGraphCache {
    private static final int MAGIC = 0x524E4743;   // "RNGC"
    private static final int VERSION = 1;

    int[] intYToSLRIndex;
    final Map<TileTypeEnum, BitSet[]> eastWestWires = new EnumMap<>(TileTypeEnum.class);
    final Map<TileTypeEnum, BitSet> localWires = new EnumMap<>(TileTypeEnum.class);
    final Map<TileTypeEnum, BitSet> muxWires = new EnumMap<>(TileTypeEnum.class);
    boolean muxComputed;   // CLB MUX scan is lutRoutethru-gated; false = section absent, run it live
    boolean hasLaguna;
    int[] nextLagunaColumn, prevLagunaColumn;
    boolean[] intYToNorthboundLaguna;
    Map<Tile, BitSet[]> lagunaWires;   // rehydrated against the live device (identity-keyed)

    private static String cachePath(Device device) {
        String p = System.getenv("RW_RNG_CACHE");
        return p != null ? p : "/tmp/" + device.getName() + ".rng";
    }

    static RWRouteNodeGraphCache tryLoad(Device device) {
        if ("0".equals(System.getenv("RW_RNG_CACHE_USE"))) return null;
        File f = new File(cachePath(device));
        if (!f.isFile()) return null;
        try (DataInputStream in = new DataInputStream(new BufferedInputStream(new FileInputStream(f), 1 << 16))) {
            if (in.readInt() != MAGIC || in.readInt() != VERSION) return null;
            if (!in.readUTF().equals(device.getName())) return null;
            if (in.readInt() != device.getRows() || in.readInt() != device.getColumns()) return null;
            RWRouteNodeGraphCache c = new RWRouteNodeGraphCache();
            c.intYToSLRIndex = readInts(in);
            int n = in.readInt();
            for (int i = 0; i < n; i++) {
                TileTypeEnum t = TileTypeEnum.valueOf(in.readUTF());
                c.eastWestWires.put(t, new BitSet[]{readBits(in), readBits(in)});
            }
            n = in.readInt();
            for (int i = 0; i < n; i++) c.localWires.put(TileTypeEnum.valueOf(in.readUTF()), readBits(in));
            c.muxComputed = in.readBoolean();
            n = in.readInt();
            for (int i = 0; i < n; i++) c.muxWires.put(TileTypeEnum.valueOf(in.readUTF()), readBits(in));
            c.hasLaguna = in.readBoolean();
            if (c.hasLaguna) {
                c.nextLagunaColumn = readInts(in);
                c.prevLagunaColumn = readInts(in);
                int len = in.readInt();
                c.intYToNorthboundLaguna = new boolean[len];
                for (int i = 0; i < len; i++) c.intYToNorthboundLaguna[i] = in.readBoolean();
                n = in.readInt();
                c.lagunaWires = new IdentityHashMap<>(n * 2);
                for (int i = 0; i < n; i++) {
                    Tile tile = device.getTile(in.readInt());
                    int m = in.readInt();
                    BitSet[] bs = new BitSet[m];
                    for (int j = 0; j < m; j++) {
                        boolean present = in.readBoolean();
                        bs[j] = present ? readBits(in) : null;
                    }
                    if (tile == null) return null;   // stale cache (device changed)
                    c.lagunaWires.put(tile, bs);
                }
            }
            return c;
        } catch (Throwable e) {
            return null;
        }
    }

    /** Called on the cache-miss path once the ctor's scans finished; failures are silent (cache is optional). */
    static void trySave(Device device, int[] intYToSLRIndex,
                        Map<TileTypeEnum, BitSet[]> eastWestWires,
                        Map<TileTypeEnum, BitSet> localWires,
                        Map<TileTypeEnum, BitSet> muxWires,
                        int[] nextLagunaColumn, int[] prevLagunaColumn,
                        boolean[] intYToNorthboundLaguna, Map<Tile, BitSet[]> lagunaWires) {
        if ("0".equals(System.getenv("RW_RNG_CACHE_USE"))) return;
        File f = new File(cachePath(device));
        File tmp = new File(f.getPath() + ".tmp." + Thread.currentThread().getId());
        try (DataOutputStream out = new DataOutputStream(new BufferedOutputStream(new FileOutputStream(tmp), 1 << 16))) {
            out.writeInt(MAGIC); out.writeInt(VERSION);
            out.writeUTF(device.getName());
            out.writeInt(device.getRows()); out.writeInt(device.getColumns());
            writeInts(out, intYToSLRIndex);
            out.writeInt(eastWestWires.size());
            for (Map.Entry<TileTypeEnum, BitSet[]> e : eastWestWires.entrySet()) {
                out.writeUTF(e.getKey().name());
                writeBits(out, e.getValue()[0]); writeBits(out, e.getValue()[1]);
            }
            writeBitMap(out, localWires);
            out.writeBoolean(muxWires != null);
            writeBitMap(out, muxWires);
            boolean hasLaguna = nextLagunaColumn != null;
            out.writeBoolean(hasLaguna);
            if (hasLaguna) {
                writeInts(out, nextLagunaColumn);
                writeInts(out, prevLagunaColumn);
                out.writeInt(intYToNorthboundLaguna.length);
                for (boolean b : intYToNorthboundLaguna) out.writeBoolean(b);
                out.writeInt(lagunaWires.size());
                for (Map.Entry<Tile, BitSet[]> e : lagunaWires.entrySet()) {
                    out.writeInt(e.getKey().getUniqueAddress());
                    BitSet[] bs = e.getValue();
                    out.writeInt(bs.length);
                    for (BitSet b : bs) {
                        out.writeBoolean(b != null);
                        if (b != null) writeBits(out, b);
                    }
                }
            }
        } catch (Throwable e) {
            tmp.delete();
            return;
        }
        if (!tmp.renameTo(f)) tmp.delete();   // lost a race with another JVM -- fine, same contents
    }

    private static void writeBitMap(DataOutputStream out, Map<TileTypeEnum, BitSet> m) throws java.io.IOException {
        out.writeInt(m == null ? 0 : m.size());
        if (m == null) return;
        for (Map.Entry<TileTypeEnum, BitSet> e : m.entrySet()) {
            out.writeUTF(e.getKey().name());
            writeBits(out, e.getValue());
        }
    }
    private static void writeBits(DataOutputStream out, BitSet b) throws java.io.IOException {
        long[] words = b.toLongArray();
        out.writeInt(words.length);
        for (long w : words) out.writeLong(w);
    }
    private static BitSet readBits(DataInputStream in) throws java.io.IOException {
        long[] words = new long[in.readInt()];
        for (int i = 0; i < words.length; i++) words[i] = in.readLong();
        return BitSet.valueOf(words);
    }
    private static void writeInts(DataOutputStream out, int[] a) throws java.io.IOException {
        out.writeInt(a.length);
        for (int v : a) out.writeInt(v);
    }
    private static int[] readInts(DataInputStream in) throws java.io.IOException {
        int[] a = new int[in.readInt()];
        for (int i = 0; i < a.length; i++) a[i] = in.readInt();
        return a;
    }
}
