/*
 * Harness (addition to RapidWright tree) for the pure-C++ RWRoute port.
 *
 * RWRouteCppExport runs the real PartialRouter (non-timing-driven) up to the end of
 * the iterative routing loop, then serializes the per-connection routing result to a
 * binary ".result" file. It then lets route() finish (LUT pin swap + finalize) and
 * writes the golden DCP. The companion RWRouteCppImport re-injects the ".result" into
 * a freshly-loaded design and reproduces the DCP, proving the serialization + finalize
 * path (Milestone M0) independently of the C++ router.
 */
package com.xilinx.rapidwright.rwroute;

import java.io.BufferedOutputStream;
import java.io.DataOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;

import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.design.Net;
import com.xilinx.rapidwright.design.SitePinInst;
import com.xilinx.rapidwright.device.Node;
import com.xilinx.rapidwright.tests.CodePerfTracker;

public class RWRouteCppExport extends PartialRouter {

    /** Magic for the ".result" file: 'R','W','R','1' */
    static final int RESULT_MAGIC = 0x52575231;

    private final String resultFileName;

    public RWRouteCppExport(Design design, RWRouteConfig config, Collection<SitePinInst> pinsToRoute,
                            String resultFileName) {
        super(design, config, pinsToRoute, false);
        this.resultFileName = resultFileName;
    }

    @Override
    public void routeIndirectConnectionsIteratively() {
        // Run the real iterative router.
        super.routeIndirectConnectionsIteratively();
        // Capture each connection's routing path BEFORE postRouteProcess() mutates it
        // (LUT pin swap updates the sink rnode based on rnodes.get(0)).
        try {
            dumpResults();
        } catch (IOException e) {
            throw new RuntimeException("ERROR: Failed to write result file " + resultFileName, e);
        }
    }

    private void dumpResults() throws IOException {
        int swappedSources = 0;
        try (DataOutputStream out = new DataOutputStream(
                new BufferedOutputStream(new FileOutputStream(resultFileName)))) {
            out.writeInt(RESULT_MAGIC);
            out.writeInt(indirectConnections.size());
            for (Connection connection : indirectConnections) {
                out.writeInt(connection.hashCode());
                out.writeBoolean(connection.isRouted());
                List<RouteNode> rnodes = connection.getRnodes();
                out.writeInt(rnodes.size());
                for (RouteNode rnode : rnodes) {
                    out.writeInt(rnode.getTile().getUniqueAddress());
                    out.writeInt(rnode.getWireIndex());
                }
                if (!rnodes.isEmpty()) {
                    RouteNode usedSource = rnodes.get(rnodes.size() - 1);
                    if (usedSource != connection.getSourceRnode()) {
                        swappedSources++;
                    }
                }
            }
        }
        System.out.println("INFO: [cpp-export] wrote " + indirectConnections.size()
                + " indirect connection results to " + resultFileName
                + " (" + swappedSources + " with swapped sources)");
    }

    public static void main(String[] args) {
        if (args.length < 3) {
            System.out.println("USAGE: <input.dcp> <output.dcp> <output.result> [rwroute args...]");
            return;
        }
        String inputDcp = args[0];
        String routedDcp = args[1];
        String resultFile = args[2];
        String[] rwrouteArgs = Arrays.copyOfRange(args, 3, args.length);

        CodePerfTracker t = new CodePerfTracker("RWRouteCppExport", true);
        Design design = Design.readCheckpoint(inputDcp);

        RWRouteConfig config = new RWRouteConfig(rwrouteArgs);
        preprocess(design);
        List<SitePinInst> pinsToRoute = getUnroutedPins(design);

        RWRouteCppExport router = new RWRouteCppExport(design, config, pinsToRoute, resultFile);
        Design routed = routeDesign(router);

        routed.writeCheckpoint(routedDcp, t);
        System.out.println("\nINFO: [cpp-export] Wrote golden routed design\n " + routedDcp + "\n");
    }
}
