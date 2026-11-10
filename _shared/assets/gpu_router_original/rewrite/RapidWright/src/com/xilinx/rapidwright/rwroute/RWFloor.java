/*
 * Measures the unavoidable "I/O floor" of any approach: device load + readCheckpoint +
 * writeCheckpoint, with NO routing. The gap between this floor and a full Java PartialRouter
 * run is the maximum time the C++ router could ever save. Run end-to-end with /usr/bin/time.
 */
package com.xilinx.rapidwright.rwroute;

import com.xilinx.rapidwright.design.Design;

public class RWFloor {
    public static void main(String[] args) {
        if (args.length < 2) { System.out.println("USAGE: <in.dcp> <out.dcp>"); return; }
        long t0 = System.nanoTime();
        Design design = Design.readCheckpoint(args[0]);
        long t1 = System.nanoTime();
        design.writeCheckpoint(args[1]);
        long t2 = System.nanoTime();
        System.out.printf("FLOOR: readCheckpoint(+deviceLoad)=%.3fs  writeCheckpoint=%.3fs  sum=%.3fs%n",
                (t1 - t0) / 1e9, (t2 - t1) / 1e9, (t2 - t0) / 1e9);
    }
}
