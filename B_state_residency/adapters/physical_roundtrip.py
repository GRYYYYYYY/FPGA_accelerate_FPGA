"""Reinject frozen C++ paths into the original placed design, preserving source snapshots."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
from prepare_real import ROOT,UPSTREAM,RUNTIME,JAVA_BIN,sha


MAIN=r'''
    public static void main(String[] args) {
        try {
        if (args.length != 5) throw new IllegalArgumentException("logical physical result output.phys output.dcp");
        Map<Integer, ConnResult> results = readResults(args[2]);
        Design design = com.xilinx.rapidwright.interchange.Interchange.readInterchangeDesign(args[0], args[1], null, false, null);
        com.xilinx.rapidwright.interchange.PhysNetlistWriter.writePhysNetlist(design, args[3]+".loaded.phys");
        RWRouteConfig config = new RWRouteConfig(new String[]{"--nonTimingDriven", "--fixBoundingBox"});
        preprocess(design);
        com.xilinx.rapidwright.interchange.PhysNetlistWriter.writePhysNetlist(design, args[3]+".preprocessed.phys");
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
        try (java.io.PrintStream report = new java.io.PrintStream(args[4]+".physical_diff.txt")) { comparator.printDiffReport(report); }
        System.out.println("B_PHYSICAL_COMPARISON differences=" + differences);
        for (String stage : new String[]{"loaded", "preprocessed"}) {
            Design snapshot = com.xilinx.rapidwright.interchange.PhysNetlistReader.readPhysNetlist(args[3]+"."+stage+".phys");
            com.xilinx.rapidwright.design.compare.DesignComparator check = new com.xilinx.rapidwright.design.compare.DesignComparator();
            check.setComparePIPs(net -> net.isStaticNet() || net.isClockNet());
            int count = check.compareDesigns(original, snapshot);
            System.out.println("B_PHYSICAL_STAGE stage="+stage+" differences="+count);
            try (java.io.PrintStream report = new java.io.PrintStream(args[4]+"."+stage+"_diff.txt")) { check.printDiffReport(report); }
        }
        routed.writeCheckpoint(args[4]);
        if (differences != 0) throw new RuntimeException("Placement/site/static/clock differences after reinjection");
        System.out.println("B_ROUNDTRIP_PASS injected=" + results.size());
        } catch (Exception error) { throw new RuntimeException("Physical reinjection failed", error); }
    }
}
'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dataset');parser.add_argument('logical',type=Path);parser.add_argument('physical',type=Path);parser.add_argument('result',type=Path)
    parser.add_argument('--output',type=Path);args=parser.parse_args()
    directory=(args.output or ROOT/'results'/('physical_'+args.dataset+'_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))).resolve()
    directory.mkdir(parents=True,exist_ok=False)
    source=UPSTREAM/'RapidWright/src/com/xilinx/rapidwright/rwroute/RWRouteCppImport.java'
    text=source.read_text();index=text.index('    public static void main(String[] args) {')
    text=text[:index]+MAIN
    text=text.replace('RWRouteCppExport.RESULT_MAGIC','0x52575231')
    anchor='        Device device = design.getDevice();'
    if text.count(anchor)!=1:raise ValueError('Importer injection anchor mismatch')
    text=text.replace(anchor,'        if (resultsById.size() != indirectConnections.size()) throw new RuntimeException("Missing/extra connection results");\n'+anchor)
    text=text.replace('                map.put(connId, r);','                if (map.put(connId, r) != null) throw new IOException("Duplicate connection id");')
    generated=directory/'RWRouteCppImport.java';generated.write_text(text)
    classes=directory/'java';classes.mkdir();jar=RUNTIME/'rapidwright.jar'
    files=[source,generated,jar,args.logical.resolve(),args.physical.resolve(),args.result.resolve(),Path(__file__).resolve()]
    record={'status':'building','dataset':args.dataset,'files':{str(p):sha(p) for p in files},
            'scope':'Reinjection plus placement/site/static/clock comparison; Vivado route/DRC must be checked separately'}
    manifest=directory/'manifest.json'
    def save():manifest.write_text(json.dumps(record,indent=2)+'\n')
    save()
    try:
        command=[str(JAVA_BIN/'javac'),'-cp',str(jar),'-d',str(classes),str(generated)]
        record['compile_command']=command
        with (directory/'build.log').open('w') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        command=['taskset','-c','24-31',str(JAVA_BIN/'java'),'-Xmx48g','-XX:ActiveProcessorCount=8','-cp',f'{classes}:{jar}',
                 'com.xilinx.rapidwright.rwroute.RWRouteCppImport',str(args.logical.resolve()),str(args.physical.resolve()),str(args.result.resolve()),
                 str(directory/'routed.phys'),str(directory/'routed.dcp')]
        record.update(status='running',command=command);save()
        with (directory/'roundtrip.log').open('w') as log:
            process=subprocess.run(command,env=dict(os.environ,RAPIDWRIGHT_PATH=str(RUNTIME)),stdout=log,stderr=subprocess.STDOUT,timeout=1200)
        record['exit_code']=process.returncode
        if process.returncode:raise RuntimeError('Reinjection or physical comparison failed; inspect roundtrip.log')
        if 'B_ROUNDTRIP_PASS' not in (directory/'roundtrip.log').read_text():raise ValueError('No successful physical reinjection receipt')
        record['outputs']={str(p):sha(p) for p in [directory/'routed.phys',directory/'routed.dcp']}
        record['status']='passed'
    except Exception as error:
        record['status']='failed';record['error']=str(error);raise
    finally:save()
    print(directory,flush=True)


if __name__=='__main__':main()
