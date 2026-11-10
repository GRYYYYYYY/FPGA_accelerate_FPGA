/*
 * Correctness checker for a routed DCP: reports opens (sink pins not fully routed) and shorts
 * (PIPs used by more than one net), plus net/PIP/wirelength stats. Used to validate the C++/JNI
 * router output: a correct result has 0 shorts and the SAME set of routed sink pins as the Java
 * baseline (and ideally 0 unrouted). Writes a per-net "routed sink pin" list to a side file so two
 * DCPs can be diffed for exact route-completeness equivalence.
 */
package com.xilinx.rapidwright.rwroute;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.design.DesignTools;
import com.xilinx.rapidwright.design.Net;
import com.xilinx.rapidwright.design.SitePinInst;
import com.xilinx.rapidwright.device.Node;
import com.xilinx.rapidwright.device.PIP;

public class RWRouteCppCheck {
    public static void main(String[] args) throws IOException {
        if (args.length < 1) { System.out.println("USAGE: <routed.dcp> [routedpins.txt]"); return; }
        Design design = Design.readCheckpoint(args[0]);
        DesignTools.updatePinsIsRouted(design);  // (re)derive SitePinInst.isRouted() from PIPs

        // Total wirelength, computed post-hoc from the DCP using RWRoute's exact node-length
        // definition (RouteNode.getLength over the de-duplicated nodes of each signal net,
        // excluding non-INT tiles). This is the SAME metric RWRoute prints as "Total wirelength:",
        // computed uniformly for any router's output so base/variants are directly comparable.
        RouteNodeGraph rng = new RouteNodeGraph(design, new RWRouteConfig(new String[]{"--nonTimingDriven"}));
        long totalWL = 0;

        int totalSinks = 0, routedSinks = 0, unroutedSinks = 0;
        long totalPips = 0;
        List<String> routedPinLines = new ArrayList<>();
        List<Net> nets = new ArrayList<>(design.getNets());
        nets.sort((a, b) -> a.getName().compareTo(b.getName()));
        for (Net net : nets) {
            totalPips += net.getPIPs().size();
            if (net.isStaticNet() || net.isClockNet()) continue;
            if (net.getSource() == null) continue;  // source-less OOC nets are not routable
            for (Node node : new HashSet<>(RouterHelper.getNodesOfNet(net))) {
                if (RouteNodeGraph.isExcludedTile(node)) continue;
                totalWL += RouteNode.getLength(node, rng);
            }
            List<String> routedPins = new ArrayList<>();
            for (SitePinInst spi : net.getSinkPins()) {
                totalSinks++;
                if (spi.isRouted()) { routedSinks++; routedPins.add(spi.getName()); }
                else unroutedSinks++;
            }
            Collections.sort(routedPins);
            StringBuilder sb = new StringBuilder(net.getName());
            for (String p : routedPins) sb.append('\t').append(p);
            routedPinLines.add(sb.toString());
        }

        // Shorts: a PIP used by more than one net.
        Map<PIP, Set<Net>> usage = new HashMap<>();
        for (Net net : design.getNets()) {
            for (PIP p : net.getPIPs()) {
                usage.computeIfAbsent(p, k -> new HashSet<>()).add(net);
            }
        }
        int overlaps = 0;
        for (Set<Net> s : usage.values()) if (s.size() > 1) overlaps++;

        System.out.printf("CHECK %s: nets=%d sinks=%d routed=%d UNROUTED=%d shorts(PIPoverlaps)=%d totalPIPs=%d wl=%d%n",
                args[0], nets.size(), totalSinks, routedSinks, unroutedSinks, overlaps, totalPips, totalWL);
        System.out.println("Total wirelength: " + totalWL);

        if (args.length >= 2) {
            try (PrintWriter out = new PrintWriter(new BufferedWriter(new FileWriter(args[1])))) {
                for (String line : routedPinLines) out.println(line);
            }
        }
    }
}
