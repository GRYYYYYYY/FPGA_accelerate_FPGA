package com.xilinx.rapidwright.rwroute;

import java.util.Arrays;
import java.util.List;
import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.design.SitePinInst;
import com.xilinx.rapidwright.interchange.Interchange;

/** Load a real placed interchange design, then use the supplied RRT1 exporter. */
public class RealInterchangeExport extends RWRouteCppProblemExport {
    public RealInterchangeExport(Design design, RWRouteConfig config,
                                 List<SitePinInst> pins, String output) {
        super(design, config, pins, output);
    }
    public static void main(String[] args) {
        if (args.length < 3) throw new IllegalArgumentException("logical.netlist physical.phys output.rrt [router args]");
        Design design = Interchange.readInterchangeDesign(args[0], args[1], null, false, null);
        System.out.println("B_REAL_DESIGN part=" + design.getPartName() + " nets=" + design.getNets().size());
        RWRouteConfig config = new RWRouteConfig(Arrays.copyOfRange(args, 3, args.length));
        preprocess(design);
        List<SitePinInst> pins = getUnroutedPins(design);
        routeDesign(new RealInterchangeExport(design, config, pins, args[2]));
    }
}
