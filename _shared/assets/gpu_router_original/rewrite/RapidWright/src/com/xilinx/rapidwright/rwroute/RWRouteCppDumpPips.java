/*
 * Harness (addition to RapidWright tree) for the pure-C++ RWRoute port.
 *
 * RWRouteCppDumpPips loads a DCP and prints, for every net (sorted by name), the sorted
 * set of its PIPs. Running it on two DCPs and diffing the outputs is a logical (order-
 * independent) equivalence check of the routing, used to verify the C++ port reproduces
 * the golden routing.
 */
package com.xilinx.rapidwright.rwroute;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.design.Net;
import com.xilinx.rapidwright.device.PIP;

public class RWRouteCppDumpPips {

    public static void main(String[] args) throws IOException {
        if (args.length < 1) {
            System.out.println("USAGE: <input.dcp> [output.txt]");
            return;
        }
        Design design = Design.readCheckpoint(args[0]);

        List<Net> nets = new ArrayList<>(design.getNets());
        nets.sort((a, b) -> a.getName().compareTo(b.getName()));

        PrintWriter out = (args.length >= 2)
                ? new PrintWriter(new BufferedWriter(new FileWriter(args[1])))
                : new PrintWriter(System.out);

        long totalPips = 0;
        for (Net net : nets) {
            List<String> pipStrings = new ArrayList<>();
            for (PIP pip : net.getPIPs()) {
                pipStrings.add(pip.toString());
            }
            Collections.sort(pipStrings);
            totalPips += pipStrings.size();
            out.print(net.getName());
            out.print('\t');
            out.print(pipStrings.size());
            for (String s : pipStrings) {
                out.print('\t');
                out.print(s);
            }
            out.print('\n');
        }
        out.flush();
        if (args.length >= 2) {
            out.close();
        }
        System.err.println("INFO: [cpp-dumppips] nets=" + nets.size() + " totalPips=" + totalPips);
    }
}
