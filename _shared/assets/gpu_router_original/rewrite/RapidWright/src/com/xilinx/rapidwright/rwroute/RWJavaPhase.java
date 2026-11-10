/*
 * Instrumented Java baseline (stock PartialRouter flow) with the SAME phase timers as RWRouteCppJni,
 * for apples-to-apples non-route-overhead comparison: readCheckpoint / routeDesign(init+route+finalize)
 * / writeCheckpoint. Routing is the unmodified PartialRouter.routeDesignWithUserDefinedArguments.
 */
package com.xilinx.rapidwright.rwroute;

import java.util.Arrays;

import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.tests.CodePerfTracker;

public class RWJavaPhase {
    public static void main(String[] args) {
        String in = args[0], out = args[1];
        String[] rwrouteArgs = Arrays.copyOfRange(args, 2, args.length);
        CodePerfTracker t = new CodePerfTracker("RWJavaPhase", true);

        long tr = System.nanoTime();
        Design design = Design.readCheckpoint(in);
        System.out.printf("INFO: [java] PHASE readCheckpoint=%.2fs%n", (System.nanoTime() - tr) / 1e9);

        long trd = System.nanoTime();
        Design routed = PartialRouter.routeDesignWithUserDefinedArguments(design, rwrouteArgs);
        System.out.printf("INFO: [java] PHASE routeDesign-total=%.2fs (init+route+finalize)%n", (System.nanoTime() - trd) / 1e9);

        long tw = System.nanoTime();
        routed.writeCheckpoint(out, t);
        System.out.printf("INFO: [java] PHASE writeCheckpoint=%.2fs%n", (System.nanoTime() - tw) / 1e9);
    }
}
