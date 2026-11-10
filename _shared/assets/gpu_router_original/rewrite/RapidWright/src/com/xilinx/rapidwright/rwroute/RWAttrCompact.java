/*
 * Exports the COMPACT per-node attribute data (ATC1, ~tens of MB) that replaces the 2.9GB per-node
 * .attrs: a per-(tile-type, base-wire) TEMPLATE {type,length,endX-off,endY-off,baseCost,flags4} +
 * per-node EXCEPTIONS (nodes whose attrs differ — truncated long-lines + laguna) + per-tile
 * tileX/tileY (for beginXY). C++ reconstructs each node's full RouteNodeInfo exactly from this +
 * the hashCode formula  Node.hashCode() = tileAddr*31 + wire + 961  (verified). NO 2.9GB dump.
 * Format ATC1 (big-endian): magic, nTiles, tileX[nTiles] i16, tileY[nTiles] i16,
 *   nTypes, per type {ordinal i32, wireCount i32, per wire: valid u8 + type u8 + len i16 + exoff i16
 *   + eyoff i16 + baseCost f32 + flags4 u8}, nExceptions i64, per exc {key i64 + same 6 fields}.
 */
package com.xilinx.rapidwright.rwroute;

import java.io.BufferedOutputStream;
import java.io.DataOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.device.Device;
import com.xilinx.rapidwright.device.IntentCode;
import com.xilinx.rapidwright.device.Node;
import com.xilinx.rapidwright.device.Tile;
import com.xilinx.rapidwright.device.TileTypeEnum;
import com.xilinx.rapidwright.util.Utils;

public class RWAttrCompact {
    static final int MAGIC = 0x41544331; // ATC1
    static final class A { int type, len, bxoff, byoff, exoff, eyoff, flags4; float baseCost;
        boolean eq(A o){ return type==o.type&&len==o.len&&bxoff==o.bxoff&&byoff==o.byoff&&exoff==o.exoff&&eyoff==o.eyoff&&flags4==o.flags4
                && Float.floatToRawIntBits(baseCost)==Float.floatToRawIntBits(o.baseCost); } }

    static int flags4(Node n, Tile t, RouteNodeGraph g) {
        boolean isLag = Utils.isLaguna(t.getTileTypeEnum());
        boolean pf = n.getIntentCode()==IntentCode.NODE_PINFEED;
        boolean pb = n.getIntentCode()==IntentCode.NODE_PINBOUNCE;
        boolean leads=false;
        if (pf && g.wireIndicesLeadingToLaguna!=null) { java.util.BitSet[] bs=g.wireIndicesLeadingToLaguna.get(t);
            leads = bs!=null && bs[0].get(n.getWireIndex()); }
        return (isLag?1:0)|(pf?2:0)|(leads?4:0)|(pb?8:0);
    }
    static A attrs(Node n, Tile t, RouteNodeGraph g) {
        RouteNode rn = g.getOrCreate(n); A a = new A();
        a.type = rn.getType().ordinal(); a.len = rn.getLength();
        a.bxoff = rn.getBeginTileXCoordinate() - t.getTileXCoordinate();
        a.byoff = rn.getBeginTileYCoordinate() - t.getTileYCoordinate();
        a.exoff = rn.getEndTileXCoordinate() - t.getTileXCoordinate();
        a.eyoff = rn.getEndTileYCoordinate() - t.getTileYCoordinate();
        a.baseCost = RWRouteCppProblemExport.safeBaseCost(rn); a.flags4 = flags4(n, t, g);
        return a;
    }

    public static void main(String[] args) throws IOException {
        String part = args.length>0?args[0]:"xcvu13p-fhgb2104-2-e";
        String out  = args.length>1?args[1]:"/tmp/xcvu13p.atc";
        Design design = new Design("dummy", part);
        RouteNodeGraph g = new RouteNodeGraph(design, new RWRouteConfig(new String[]{"--nonTimingDriven","--lutPinSwapping"}));
        Device device = design.getDevice();
        java.util.Set<TileTypeEnum> allowed = new java.util.HashSet<>(Utils.getLagunaTileTypes());
        allowed.add(TileTypeEnum.INT);

        int maxAddr=-1; for (Tile t: device.getAllTiles()) maxAddr=Math.max(maxAddr,t.getUniqueAddress());
        int nTiles=maxAddr+1;
        short[] tileX=new short[nTiles], tileY=new short[nTiles];
        for (Tile t: device.getAllTiles()){ tileX[t.getUniqueAddress()]=(short)t.getTileXCoordinate(); tileY[t.getUniqueAddress()]=(short)t.getTileYCoordinate(); }

        // per-type template (rep = tile with most base nodes)
        Map<TileTypeEnum,List<Tile>> byType=new HashMap<>();
        for (Tile t: device.getAllTiles()) if (allowed.contains(t.getTileTypeEnum()))
            byType.computeIfAbsent(t.getTileTypeEnum(),k->new ArrayList<>()).add(t);
        Map<TileTypeEnum,A[]> tmpl=new HashMap<>();
        long t0=System.nanoTime();
        for (Map.Entry<TileTypeEnum,List<Tile>> e: byType.entrySet()){
            List<Tile> tiles=e.getValue(); Tile rep=tiles.get(0); int best=-1;
            for (int s=0;s<Math.min(tiles.size(),64);s++){ Tile c=tiles.get((int)((long)s*tiles.size()/64));
                int nn=0; for(int w=0;w<c.getWireCount();w++){Node n=Node.getNode(c,w); if(n!=null&&n.getTile()==c&&n.getWireIndex()==w)nn++;}
                if(nn>best){best=nn;rep=c;} }
            A[] m=new A[rep.getWireCount()];
            for (int w=0;w<rep.getWireCount();w++){ Node n=Node.getNode(rep,w);
                if(n!=null&&n.getTile()==rep&&n.getWireIndex()==w) m[w]=attrs(n,rep,g); }
            tmpl.put(e.getKey(), m);
        }
        System.out.printf("templates built %.1fs%n",(System.nanoTime()-t0)/1e9);

        // exceptions
        long t1=System.nanoTime(); long nodes=0, except=0, done=0;
        List<long[]> exc=new ArrayList<>(); // {key, packed-attrs hi/lo} — we store explicitly below
        List<A> excA=new ArrayList<>(); List<Long> excK=new ArrayList<>();
        for (Tile t: device.getAllTiles()){
            if (!allowed.contains(t.getTileTypeEnum())) continue;
            A[] m=tmpl.get(t.getTileTypeEnum());
            for (int w=0;w<t.getWireCount();w++){ Node n=Node.getNode(t,w);
                if(n==null||n.getTile()!=t||n.getWireIndex()!=w) continue; nodes++;
                A a=attrs(n,t,g);
                A tv = (w<m.length)?m[w]:null;
                if(tv==null || !tv.eq(a)){ except++; excK.add(((long)t.getUniqueAddress()<<20)|(w&0xFFFFF)); excA.add(a); }
                if(++done%20000000==0) System.out.printf("  ...%d nodes, %d exc%n",done,except);
            }
        }
        System.out.printf("scan %.1fs  NODES=%d EXCEPTIONS=%d (%.2f%%)%n",(System.nanoTime()-t1)/1e9,nodes,except,100.0*except/nodes);

        // write ATC1
        List<TileTypeEnum> types=new ArrayList<>(tmpl.keySet());
        try (DataOutputStream o=new DataOutputStream(new BufferedOutputStream(new FileOutputStream(out),1<<22))) {
            o.writeInt(MAGIC); o.writeInt(nTiles);
            for (int a=0;a<nTiles;a++) o.writeShort(tileX[a]);
            for (int a=0;a<nTiles;a++) o.writeShort(tileY[a]);
            o.writeInt(types.size());
            for (TileTypeEnum ty: types){ A[] m=tmpl.get(ty);
                o.writeInt(ty.ordinal()); o.writeInt(m.length);
                for (A a: m){ if(a==null){ o.writeByte(0); } else { o.writeByte(1);
                    o.writeByte(a.type); o.writeShort(a.len); o.writeShort(a.bxoff); o.writeShort(a.byoff); o.writeShort(a.exoff); o.writeShort(a.eyoff); o.writeFloat(a.baseCost); o.writeByte(a.flags4); } }
            }
            o.writeLong(except);
            for (int i=0;i<excK.size();i++){ A a=excA.get(i);
                o.writeLong(excK.get(i)); o.writeByte(a.type); o.writeShort(a.len); o.writeShort(a.bxoff); o.writeShort(a.byoff); o.writeShort(a.exoff); o.writeShort(a.eyoff); o.writeFloat(a.baseCost); o.writeByte(a.flags4); }
        }
        System.out.printf("WROTE %s  %.1f MB  (tiles %d, exceptions %d)%n",
                out, new java.io.File(out).length()/1e6, nTiles, except);
    }
}
