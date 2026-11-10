/*
 * Harness (addition to RapidWright tree) for the pure-C++ RWRoute port.
 *
 * RWRouteCppImport loads a design fresh, rebuilds the routing targets via the normal
 * PartialRouter.initialize() path, then -- instead of running the iterative router --
 * injects a per-connection routing result (produced by RWRouteCppExport, or later by
 * the C++ router) and lets route() finish (LUT pin swap + finalize) and write the DCP.
 */
package com.xilinx.rapidwright.rwroute;

import java.io.BufferedInputStream;
import java.io.DataInputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.design.SitePinInst;
import com.xilinx.rapidwright.device.Device;
import com.xilinx.rapidwright.device.Node;
import com.xilinx.rapidwright.device.Tile;
import com.xilinx.rapidwright.tests.CodePerfTracker;
import com.xilinx.rapidwright.util.Pair;

public class RWRouteCppImport extends PartialRouter {

    /** One connection's injected routing: rnode identities (sink -> source) + routed flag. */
    static final class ConnResult {
        boolean routed;
        int[] addr;
        int[] wire;
    }

    private final Map<Integer, ConnResult> resultsById;

    public RWRouteCppImport(Design design, RWRouteConfig config, Collection<SitePinInst> pinsToRoute,
                            Map<Integer, ConnResult> resultsById) {
        super(design, config, pinsToRoute, false);
        this.resultsById = resultsById;
    }

    @Override
    public void routeIndirectConnectionsIteratively() {
        if (resultsById.size() != indirectConnections.size()) throw new RuntimeException("Missing/extra connection results");
        Device device = design.getDevice();

        Map<Integer, Connection> byId = new HashMap<>();
        for (Connection connection : indirectConnections) {
            byId.put(connection.hashCode(), connection);
        }

        int injected = 0;
        int swappedSources = 0;
        for (Map.Entry<Integer, ConnResult> e : resultsById.entrySet()) {
            Connection connection = byId.get(e.getKey());
            if (connection == null) {
                throw new RuntimeException("ERROR: [cpp-import] result references unknown connection id " + e.getKey());
            }
            ConnResult r = e.getValue();

            List<RouteNode> rnodes = new ArrayList<>(r.addr.length);
            for (int i = 0; i < r.addr.length; i++) {
                Tile tile = device.getTile(r.addr[i]);
                Node node = Node.getNode(tile, r.wire[i]);
                RouteNode rnode = routingGraph.getOrCreate(node);
                rnodes.add(rnode);
            }

            if (!rnodes.isEmpty()) {
                RouteNode usedSource = rnodes.get(rnodes.size() - 1);
                if (usedSource != connection.getSourceRnode()) {
                    // The exporter swapped to the alternate output pin during routing; reproduce it.
                    Pair<SitePinInst, RouteNode> altSourceAndRnode = connection.getOrCreateAlternateSource(routingGraph);
                    if (altSourceAndRnode == null || altSourceAndRnode.getSecond() != usedSource) {
                        throw new RuntimeException("ERROR: [cpp-import] cannot reconcile swapped source for connection "
                                + connection.hashCode());
                    }
                    connection.setSource(altSourceAndRnode.getFirst());
                    connection.setSourceRnode(altSourceAndRnode.getSecond());
                    swappedSources++;
                }
            }

            connection.setRnodes(rnodes);
            connection.setRouted(r.routed);

            // Replicate RWRoute.updateUsersAndPresentCongestionCost(): increment the user
            // (NetWrapper) count on the rnodes used by this routed connection, so that the
            // finalize path (fixRoutes -> ripUp -> decrementUser) sees consistent occupancy.
            if (r.routed && !rnodes.isEmpty()) {
                List<RouteNode> toIncrement = rnodes;
                RouteNode sinkRnode = rnodes.get(0);
                if (sinkRnode == connection.getSinkRnode() && !connection.hasAltSinks()) {
                    // Exclusive sink was already incremented at creation; source excluded too.
                    toIncrement = rnodes.subList(1, rnodes.size() - 1);
                }
                NetWrapper netWrapper = connection.getNetWrapper();
                for (RouteNode rnode : toIncrement) {
                    rnode.incrementUser(netWrapper);
                }
            }
            injected++;
        }

        System.out.println("INFO: [cpp-import] injected " + injected + " connection results ("
                + swappedSources + " with swapped sources)");
    }

    private static Map<Integer, ConnResult> readResults(String resultFile) throws IOException {
        Map<Integer, ConnResult> map = new HashMap<>();
        try (DataInputStream in = new DataInputStream(
                new BufferedInputStream(new FileInputStream(resultFile)))) {
            int magic = in.readInt();
            if (magic != 0x52575231) {
                throw new IOException("Bad result magic: 0x" + Integer.toHexString(magic));
            }
            int count = in.readInt();
            for (int c = 0; c < count; c++) {
                int connId = in.readInt();
                ConnResult r = new ConnResult();
                r.routed = in.readBoolean();
                int n = in.readInt();
                r.addr = new int[n];
                r.wire = new int[n];
                for (int i = 0; i < n; i++) {
                    r.addr[i] = in.readInt();
                    r.wire[i] = in.readInt();
                }
                if (map.put(connId, r) != null) throw new IOException("Duplicate connection id");
            }
        }
        return map;
    }


    public static void main(String[] args) {
        try {
        if (args.length != 5) throw new IllegalArgumentException("logical physical result output.phys output.dcp");
        Map<Integer, ConnResult> results = readResults(args[2]);
        Design design = com.xilinx.rapidwright.interchange.Interchange.readInterchangeDesign(args[0], args[1], null, false, null);
        RWRouteConfig config = new RWRouteConfig(new String[]{"--nonTimingDriven", "--fixBoundingBox"});
        preprocess(design);
        List<SitePinInst> pinsToRoute = getUnroutedPins(design);
        Design routed = routeDesign(new RWRouteCppImport(design, config, pinsToRoute, results));
        com.xilinx.rapidwright.interchange.PhysNetlistWriter.writePhysNetlist(routed, args[3]);
        com.xilinx.rapidwright.interchange.PhysNetlistReader.CHECK_CONSTANT_ROUTING_AND_NET_NAMING = false;
        com.xilinx.rapidwright.interchange.PhysNetlistReader.CHECK_AND_CREATE_LOGICAL_CELL_IF_NOT_PRESENT = false;
        com.xilinx.rapidwright.interchange.PhysNetlistReader.VALIDATE_MACROS_PLACED_FULLY = false;
        com.xilinx.rapidwright.interchange.PhysNetlistReader.CHECK_MACROS_CONSISTENT = false;
        Design original = com.xilinx.rapidwright.interchange.PhysNetlistReader.readPhysNetlist(args[1]);
        Design reloaded = com.xilinx.rapidwright.interchange.PhysNetlistReader.readPhysNetlist(args[3]);
        com.xilinx.rapidwright.design.compare.DesignComparator comparator = new com.xilinx.rapidwright.design.compare.DesignComparator();
        comparator.setComparePIPs(net -> net.isStaticNet() || net.isClockNet());
        int differences = comparator.compareDesigns(original, reloaded);
        System.out.println("B_PHYSICAL_COMPARISON differences=" + differences);
        if (differences != 0) throw new RuntimeException("Placement/site/static/clock differences after reinjection");
        routed.writeCheckpoint(args[4]);
        System.out.println("B_ROUNDTRIP_PASS injected=" + results.size());
        } catch (Exception error) { throw new RuntimeException("Physical reinjection failed", error); }
    }
}
