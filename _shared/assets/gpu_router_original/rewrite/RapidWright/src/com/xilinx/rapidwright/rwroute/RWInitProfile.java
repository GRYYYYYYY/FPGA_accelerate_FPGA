/*
 * Profiles where the time goes BEFORE the routing loop: readCheckpoint(+device load),
 * preprocess, getUnroutedPins, RouteNodeGraph construction (the device-static eastWest/Laguna
 * setup), and RouteThruHelper construction. This pinpoints the ~3.3s "Initialization" chunk.
 */
package com.xilinx.rapidwright.rwroute;

import java.util.List;

import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.design.SitePinInst;
import com.xilinx.rapidwright.router.RouteThruHelper;

public class RWInitProfile {
    static long t;
    static void mark(String label) {
        long now = System.nanoTime();
        System.out.printf("  %-34s %7.3f s%n", label, (now - t) / 1e9);
        t = now;
    }

    public static void main(String[] args) {
        String in = args[0];
        long t0 = System.nanoTime();

        t = System.nanoTime();
        Design design = Design.readCheckpoint(in);
        mark("readCheckpoint (+device load)");

        PartialRouter.preprocess(design);
        mark("preprocess");

        List<SitePinInst> pins = PartialRouter.getUnroutedPins(design);
        mark("getUnroutedPins (n=" + pins.size() + ")");

        RWRouteConfig config = new RWRouteConfig(new String[]{"--nonTimingDriven", "--lutPinSwapping"});
        mark("RWRouteConfig");

        RouteNodeGraph graph = new RouteNodeGraph(design, config);
        mark("RouteNodeGraph ctor (eastWest+Laguna)");

        RouteThruHelper rth = new RouteThruHelper(design.getDevice());
        mark("RouteThruHelper ctor");

        // Build the full PartialRouter init (determineRoutingTargets etc.) for completeness.
        PartialRouter router = new PartialRouter(design, config, pins, false);
        mark("PartialRouter ctor");
        router.initialize();
        mark("router.initialize() [full init incl. its own graph+targets+preserve]");

        System.out.printf("  %-34s %7.3f s%n", "TOTAL (read..init)", (System.nanoTime() - t0) / 1e9);
        // keep refs alive
        if (graph == null || rth == null || router == null) System.out.println("x");
    }
}
